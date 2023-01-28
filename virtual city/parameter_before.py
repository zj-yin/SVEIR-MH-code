# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 20:16:07 2020

@author: Server
"""



import pickle as pkl
from helpers2 import Params, T, get_T1_and_T2, R0, makedir_if_not_there


params = Params(
    initial_num_I=0, 
    initial_num_E=1,
    initial_num_M=0,

    alpha=(3.3e-08+3.8170000000000004e-08+3.355e-08+4.6200000000000003e-08+2.4e-08+3.315e-08)/6,
    beta=(5.4e-09+3.817e-09+6.71e-09+5.39e-09+3.2000000000000005e-09+3.3150000000000002e-09)/6, 
 
    #alpha=3.763*1e-08, beta=4.4805* 1e-09, #four region average#
    mu_ei=6, mu_mo=10,
    k_days=int(14),
    x0_pt=10000
)

pkl.dump(
    params,
    open('output/params_before_lockdown.pkl', 'wb')
)