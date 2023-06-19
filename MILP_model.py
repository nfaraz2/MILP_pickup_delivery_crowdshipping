# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 17:22:46 2023

@author: nfaraz2
"""
import pandas as pd
import numpy as np
from docplex.mp.model import Model
import time
import os
import pickle


#%%Model formulation

def milp_model (instance, n_crs, n_req):
    
    DIRECT =r'C:/Users/nfaraz2/Box/saved_data/Revision/CPLEX/'+str(n_crs)+'crs'+str(n_req)+'req/temp/publish/data_'+str(instance)+'.xlsx'
    pay_rate = 0.25
    EPTV = 0.1
    M = 100000
    
    K=n_crs
    J_plus = n_req
    J_minus = n_req
    J = J_plus+J_minus
    N = J+K
 
    
    dtt = pd.read_excel(DIRECT, sheet_name = 'dtt_matrix', index_col = 0)
    dtt = np.array(dtt).astype(float)
    
    req_df = pd.read_excel(DIRECT, sheet_name = 'req_df', index_col = 0)
    crs_df = pd.read_excel(DIRECT, sheet_name = 'crs_df', index_col = 0)
    
    ept = req_df['EPT']
    ldt = req_df['LDT']
    
    eat = crs_df['EAT']
    lat = crs_df['LAT']
    cap = crs_df['Cap']
    q = crs_df['f']
    w = crs_df['g']
    
    
    #model
    MILP_model = Model('MILP')
    
   
    #binary decision variable
    x = MILP_model.binary_var_matrix(dtt.shape[0],dtt.shape[1],name='x')
    y = MILP_model.binary_var_matrix(dtt.shape[0],dtt.shape[1],name='y')
    T = MILP_model.continuous_var_list(N, name = 'T')
    E = MILP_model.continuous_var_list(N, name = 'E')
    
    
    #constraint
    #Routing constraints
    MILP_model.add_constraints((sum(x[i,j] for i in range(dtt.shape[0])) == 1 for j in range(dtt.shape[1])), names = 'RC-A4')
    MILP_model.add_constraints((sum(x[i,j] for j in range(dtt.shape[0])) == 1 for i in range(dtt.shape[1])), names = 'RC-A5')
    MILP_model.add_constraints((y[k,i]<=(y[k,j]+(1-x[i,j])) for i in range(N) for j in range(N) for k in range(N) \
                                if i!=k and i!=(N-1) and j!=2*J_plus), names = "RC-A6")
    MILP_model.add_constraints((y[k,i]>=(y[k,j]+(-1+x[i,j])) for i in range(N) for j in range(N) for k in range(N) \
                                if i!=k and i!=(N-1) and j!=2*J_plus), names = "RC-A7")
    MILP_model.add_constraints((x[i,j]<=y[i,j] for i in range(N) for j in range (N)), names = "RC-A8")
    MILP_model.add_constraints((y[i,i] == 0 for i in range(N)), names = "RC-A9")
    MILP_model.add_constraints((y[i,i+J_plus] == 1 for i in range(J_plus)), names = "RC-A10")
    MILP_model.add_constraints((y[i+J_plus,i] == 0 for i in range(J_plus)), names = "RC-A11")
    MILP_model.add_constraints((y[i,j] == y[i+J_plus,j] for i in range(J_plus) for j in range(J,N)), names = "RC-A12")
    MILP_model.add_constraints((y[i,j] == 1 for i in range(J,N) for j in range(J,N) if i<j), names = "RC-A13")
    MILP_model.add_constraints((y[i,j] == 0 for i in range(J,N) for j in range(J,N) if i>j), names = "RC-A14")
    
    #Capacity constraint
    MILP_model.add_constraints(((w[j]+sum(w[i]*y[i,j] for i in range(N)))<=(sum(q[k]*y[k,j] for k in range(J,N))) for j in range(J_plus)), names = "CC-A15")
    
    #Time constraints
    MILP_model.add_constraints((T[i]+E[i]+dtt[i,j]+1<=T[j]+(1-x[i,j])*M for i in range(N) for j in range(J)), names = 'TC-A16')
    MILP_model.add_constraints((T[i]+E[i]+dtt[i,j]+1>=T[j]+(-1+x[i,j])*M for i in range(N) for j in range(J)), names = 'TC-A17')
    MILP_model.add_constraints((T[j]+1<=ldt[j] for j in range(J_plus, 2*J_plus)), names = 'TC-A18')
    # MILP_model.add_constraints((T[j]>=ept[j] for j in range(J_plus)), names = 'TC-A19')
    MILP_model.add_constraints((T[j]<=T[J_plus+j] for j in range(J_plus)), names = 'TC-A20')
    MILP_model.add_constraints((T[i]+1-lat[k]<=(1-x[i,k+1])*M for i in range(J_plus,2*J_plus) for k in range(J,N) if k !=(N-1)), names = "TC-A21")
    MILP_model.add_constraints((T[i]+1-lat[N-1]<=(1-x[i,J])*M for i in range(J_plus, 2*J_plus)), names = "TC-A22")
    MILP_model.add_constraints((T[k]>=eat[k] for k in range(J,N)), names = "TC-A23")
    
    #Non-negativity
    MILP_model.add_constraints((T[i]>=0 for i in range(N)), names = 'NN-A26')
    MILP_model.add_constraints((E[j]==0 for j in range(J_minus,N)), names = 'AA28')
    #EPTV
    MILP_model.add_constraints((E[j]>=0 for j in range(J_plus)), names = "EPTV1")
    MILP_model.add_constraints((E[j]>=(ept[j]-T[j]) for j in range(J_plus)), names = "EPTV2")
    
    #objective function
    obj_fn = sum((dtt[i,j]+1)*pay_rate*x[i,j] for i in range(N) for j in range(J)) + sum((EPTV+pay_rate)*E[j] for j in range(J_plus))
    
    MILP_model.set_objective('min',obj_fn)
    
    # MILP_model.print_information()
    
    # print(MILP_model.export_as_lp_string())
    s = time.process_time()
    MILP_model.solve()
    cpu_time = time.process_time()-s
    
    sol_time = MILP_model.solve_details.time
    
    
    obj_value = MILP_model.objective_value
    print(instance,obj_value, sol_time, '\n' )
    return (obj_value,sol_time,cpu_time )


#%% Model run

# running instances with 2 crowdsourcee and 4 requests

instance = 0 # there are 37 instances starting from 0 to 36
n_crs= 2
n_req = 4

obj_value,sol_time,cpu_time = milp_model (instance, n_crs, n_req)
