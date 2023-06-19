# MILP_pickup_delivery_crowdshipping

This is a MILP formulation using DoCplex for a pickup delivery with a time window problem in the context of crowdshipping. Every crowdsourcee serves as a carrier with a limited and heterogeneous working time window, and carrying capacity. Every delivery request has a heterogeneous delivery time window and weight. 

## File description:
* problem instances: This folder contains 37 problem instances with two crowdsourcee and four delivery requests

* MILP_model: formualte the MILP model

## To run model:

Specify the number of crowdsourcee, requests, and problem instance to solve, then run the function "milp_model"

## Reference

Farazi, N. P., Zou, B., & Tulabandhula, T. (2022). Dynamic On-Demand Crowdshipping Using Constrained and Heuristics-Embedded Double Dueling Deep Q-Network. Transportation Research Part E: Logistics and Transportation Review, 166, 102890.
