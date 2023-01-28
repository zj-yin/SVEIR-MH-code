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




p0_time = T('2020/2/12')

bed_info_raw = [
    (p0_time, 18114)]

pkl.dump(bed_info_raw, open('data/bed_info_raw.pkl', 'wb'))
# number of new beds at  some days
bed_info = [((d-p0_time).days, n) for d, n in bed_info_raw]
pkl.dump(bed_info, open('data/bed_info.pkl', 'wb'))


params_before = pkl.load(open('params_before_lockdown.pkl', 'rb'))


offset = 1
n_offsets = 775
days_offsets = list(range(offset, offset*n_offsets+1, offset))
total_days =775

'''
for T1 in np.arange(30,51,5):
    for T2 in np.arange(T1+14,T1+57,7):
        for F1 in [2.5, 3.0, 3.5]:
            for F2 in [1.0, 1.5, 2.0]:
'''
'''
for T1 in [30]:
    for T2 in [44]:
        for F1 in [3.5]:
            for F2 in np.arange(2.0,2.51,0.01):
'''


lockdown_time =T('2020/3/22')
days_before_ld  = (lockdown_time -  p0_time).days
fine_grained_alpha = [(0, params_before.alpha), (days_before_ld, params_before.alpha/3)]
fine_grained_beta = [(0, params_before.beta), (days_before_ld, params_before.beta/3)]
for i in days_offsets:
    if (days_before_ld + i)<=86:
        fine_grained_alpha += [(days_before_ld + i, params_before.alpha/3)]
        fine_grained_beta += [(days_before_ld + i, params_before.beta/3)]
    else:
        if (days_before_ld + i)<=306:
            fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.222)]
            fine_grained_beta += [(days_before_ld + i, params_before.beta/2.222)]
        else:
            if (days_before_ld + i)<=355:
                fine_grained_alpha += [(days_before_ld + i, params_before.alpha/3.3)]
                fine_grained_beta += [(days_before_ld + i, params_before.beta/3.3)]
            else:
                if (days_before_ld + i)<=436:
                    fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.15)]
                    fine_grained_beta += [(days_before_ld + i, params_before.beta/2.15)]
                else:
                    if (days_before_ld + i)<=482:
                        fine_grained_alpha += [(days_before_ld + i, params_before.alpha/3.35)]
                        fine_grained_beta += [(days_before_ld + i, params_before.beta/3.35)]
                    else:
                        if (days_before_ld + i)<=567:
                            fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.02)]
                            fine_grained_beta += [(days_before_ld + i, params_before.beta/2.02)]
                        else:
                            if (days_before_ld + i)<=601:
                                fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.7)]
                                fine_grained_beta += [(days_before_ld + i, params_before.beta/2.7)]
                            else:
                                if (days_before_ld + i)<=652:
                                    fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.05)]
                                    fine_grained_beta += [(days_before_ld + i, params_before.beta/2.05)]
                                else:
                                    if (days_before_ld + i)<=688:
                                        fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.9)]
                                        fine_grained_beta += [(days_before_ld + i, params_before.beta/2.9)]
                                    else:
                                        if (days_before_ld + i)<=724:
                                            fine_grained_alpha += [(days_before_ld + i, params_before.alpha/1.9)]
                                            fine_grained_beta += [(days_before_ld + i, params_before.beta/1.9)]
                                        else:
                                            fine_grained_alpha += [(days_before_ld + i, params_before.alpha/3)]
                                            fine_grained_beta += [(days_before_ld + i, params_before.beta/3)]

                                            
        
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