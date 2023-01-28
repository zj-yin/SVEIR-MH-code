#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')




import pickle as pkl
import math
import pandas as pd
from datetime import  datetime, timedelta
from copy import copy
import numpy as np
from core2 import  do_simulation
from helpers2 import Params, plot_total, T, data2df, enhance_total, save_to_json, save_bundle, makedir_if_not_there
from const2 import  STATE



p0_time = T('2020/2/13')

bed_info_raw = [
    (p0_time, 7535)]

pkl.dump(bed_info_raw, open('data/bed_info_raw.pkl', 'wb'))
# number of new beds at  some days
bed_info = [((d-p0_time).days, n) for d, n in bed_info_raw]
pkl.dump(bed_info, open('data/bed_info.pkl', 'wb'))

'''
lockdown_time =T('2020/3/15')
params_before = pkl.load(open('params_before_lockdown.pkl', 'rb'))
params_after= pkl.load(open('params_after_lockdown.pkl', 'rb'))

total_days = 360
days_before_ld  = (lockdown_time -  p0_time).days
offset = 14
n_offsets = 10

days_offsets = list(range(offset, offset*n_offsets+1, offset))
fine_grained_alpha = [(0, params_before.alpha), (days_before_ld, params_after.alpha)]
fine_grained_alpha += [
    (days_before_ld + i, params_after.alpha) for i in days_offsets
]
fine_grained_beta = [(0, params_before.beta), (days_before_ld, params_after.beta)]
fine_grained_beta += [
    (days_before_ld + i, params_after.beta) for i in days_offsets
]

'''

offset = 1
n_offsets = 775
days_offsets = list(range(offset, offset*n_offsets+1, offset))
total_days =775
params_before = pkl.load(open('params_before_lockdown.pkl', 'rb'))
lockdown_time =T('2020/3/15')
days_before_ld  = (lockdown_time -  p0_time).days
fine_grained_alpha = [(0, params_before.alpha), (days_before_ld, params_before.alpha/3.85)]
fine_grained_beta = [(0, params_before.beta), (days_before_ld, params_before.beta/3.85)]
for i in days_offsets:
    if (days_before_ld + i)<=110:
        fine_grained_alpha += [(days_before_ld + i, params_before.alpha/3.85)]
        fine_grained_beta += [(days_before_ld + i, params_before.beta/3.85)]
    else:
        if (days_before_ld + i)<=265:
            fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.72)]
            fine_grained_beta += [(days_before_ld + i, params_before.beta/2.72)]
        else:
            if (days_before_ld + i)<=350:
                fine_grained_alpha += [(days_before_ld + i, params_before.alpha/3.65)]
                fine_grained_beta += [(days_before_ld + i, params_before.beta/3.65)]
            else:
                if (days_before_ld + i)<=358:
                    fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.86)]
                    fine_grained_beta += [(days_before_ld + i, params_before.beta/2.86)]
                else:
                    if (days_before_ld + i)<=392:
                        fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.7)]
                        fine_grained_beta += [(days_before_ld + i, params_before.beta/2.7)]
                    else:
                        if (days_before_ld + i)<=455:
                            fine_grained_alpha += [(days_before_ld + i, params_before.alpha/3.3)]
                            fine_grained_beta += [(days_before_ld + i, params_before.beta/3.3)]
                        else:
                            if (days_before_ld + i)<=656:
                                fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.85)]
                                fine_grained_beta += [(days_before_ld + i, params_before.beta/2.85)]
                            else:
                                if (days_before_ld + i)<=687:
                                    fine_grained_alpha += [(days_before_ld + i, params_before.alpha/1.65)]
                                    fine_grained_beta += [(days_before_ld + i, params_before.beta/1.65)]
                                else:
                                    if (days_before_ld + i)<=746:
                                        fine_grained_alpha += [(days_before_ld + i, params_before.alpha/3.6)]
                                        fine_grained_beta += [(days_before_ld + i, params_before.beta/3.6)]
                                    else:
                                        fine_grained_alpha += [(days_before_ld + i, params_before.alpha/1.8)]
                                        fine_grained_beta += [(days_before_ld + i, params_before.beta/1.8)]

         
params = Params(
    total_population=params_before.total_population,initial_num_E=params_before.initial_num_E,
    initial_num_I=params_before.initial_num_I,
    initial_num_M=params_before.initial_num_M,  
	initial_num_V1=params_before.initial_num_V1,
	initial_num_V2=params_before.initial_num_V2,
	initial_num_EV1=params_before.initial_num_EV1,
    mu_ei=params_before.mu_ei,
    mu_mo=params_before.mu_mo,
	mev1_mo=params_before.mev1_mo,
	mv2_mo=params_before.mv2_mo,
    k_days=params_before.k_days,
    x0_pt=params_before.x0_pt,
    alpha=fine_grained_alpha,
    beta=fine_grained_beta,
    stages=[days_before_ld] + [(days_before_ld + i) for i in range(offset, offset*n_offsets+1, offset)])
	
total, delta, increase, trans_data, stats = do_simulation(total_days, bed_info, params, p0_time=p0_time, verbose=0)
makedir_if_not_there(f'output/tbl/start2end/')
save_bundle([total, delta, increase, trans_data], p0_time, total_days,f'output/tbl/start2end/')
path = f'output/tbl/start2end/stats.txt'
save_to_json(stats, path)