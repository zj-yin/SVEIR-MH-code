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
    (p0_time, 10000)]

pkl.dump(bed_info_raw, open('data/bed_info_raw.pkl', 'wb'))
# number of new beds at  some days
bed_info = [((d-p0_time).days, n) for d, n in bed_info_raw]
pkl.dump(bed_info, open('data/bed_info.pkl', 'wb'))



offset = 1
n_offsets = 720
days_offsets = list(range(offset, offset*n_offsets+1, offset))
total_days =700
params_before = pkl.load(open('output/params_before_lockdown.pkl', 'rb'))
#lockdown_time =T('2020/3/15')
T0=np.arange(40, 46, step=5)
#T0_one  = (lockdown_time -  p0_time).days
Factor_lockdown=np.arange(3.0, 3.51, step=0.5)
Factor_release=np.arange(3.0,3.51, step=0.5)
for T0_one in T0:
    #print(T0_one)
    for Factor_lockdown_one in Factor_lockdown:
        #print(T0_one)
        fine_grained_alpha = [(0, params_before.alpha), (T0_one, params_before.alpha/Factor_lockdown_one)]
        fine_grained_beta = [(0, params_before.beta), (T0_one, params_before.beta/Factor_lockdown_one)]  
        for i in days_offsets:
            if (T0_one + i)<=T0_one+56:
                fine_grained_alpha += [(T0_one + i, params_before.alpha/Factor_lockdown_one)]
                fine_grained_beta += [(T0_one + i, params_before.beta/Factor_lockdown_one)]
            else:
                for Factor_release_one in Factor_release:
                    fine_grained_alpha += [(T0_one + i, params_before.alpha/Factor_release_one)]
                    fine_grained_beta += [(T0_one + i, params_before.beta/Factor_release_one)]
                    print(T0_one,Factor_lockdown_one,Factor_release_one)
                  

                    params = Params(total_population=params_before.total_population,initial_num_E=params_before.initial_num_E,
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
                                        stages=[T0_one] + [(T0_one + j) for j in range(offset, offset*n_offsets+1, offset)])
                    total, delta, increase, trans_data, stats = do_simulation(total_days, bed_info, params, p0_time=p0_time, verbose=0)
                    makedir_if_not_there('output/tbl/56 days-73')
                    #makedir_if_not_there(f'output/tbl/no vaccination/T0-{T0_one}-factor-{Factor_lockdown_one}-{Factor_release_one}-{Factor_lockdown_one}-{Factor_release_one}/')
                    save_bundle([total, delta, increase, trans_data], p0_time, total_days,f'output/tbl/56 days-73/T0-{T0_one}-factor-{Factor_lockdown_one}-{Factor_release_one}/')
                    path = f'output/tbl/56 days-73/T0-{T0_one}-factor-{Factor_lockdown_one}-{Factor_release_one}/stats.txt'
                    save_to_json(stats, path)
                    #print (T0,Factor_lockdown_one,Factor_release_one)
                    #print(T0_one,Factor_lockdown_one,Factor_release_one)
                    #continue
                break