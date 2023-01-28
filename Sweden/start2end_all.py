# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 16:51:21 2022

@author: yzj
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 17:28:24 2022

@author: yzj
"""

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


p0_time = T('2020/4/11')

bed_info_raw = [
    (p0_time, 30183)]

pkl.dump(bed_info_raw, open('data/bed_info_raw.pkl', 'wb'))
# number of new beds at  some days
bed_info = [((d-p0_time).days, n) for d, n in bed_info_raw]
pkl.dump(bed_info, open('data/bed_info.pkl', 'wb'))


params_before = pkl.load(open('output_test/params_before_lockdown.pkl', 'rb'))


offset = 1
n_offsets = 800
days_offsets = list(range(offset, offset*n_offsets+1, offset))
total_days =800


lockdown_time =T('2020/6/11')
days_before_ld  = (lockdown_time -  p0_time).days
fine_grained_alpha = [(0, params_before.alpha), (days_before_ld, params_before.alpha/2.26)]
fine_grained_beta = [(0, params_before.beta), (days_before_ld, params_before.beta/2.26)]
for i in days_offsets:
    if (days_before_ld + i)<=115:
        fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.26)]
        fine_grained_beta += [(days_before_ld + i, params_before.beta/2.26)]
    else:
        if (days_before_ld + i)<=244:
            fine_grained_alpha += [(days_before_ld + i, params_before.alpha/1.5)]
            fine_grained_beta += [(days_before_ld + i, params_before.beta/1.5)]
        else:
            if (days_before_ld + i)<=287:
                fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.3)]
                fine_grained_beta += [(days_before_ld + i, params_before.beta/2.3)]
            else:
                if (days_before_ld + i)<=361:
                    fine_grained_alpha += [(days_before_ld + i, params_before.alpha/1.7)]
                    fine_grained_beta += [(days_before_ld + i, params_before.beta/1.7)]
                else:
                    if (days_before_ld + i)<=419:
                        fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.3)]
                        fine_grained_beta += [(days_before_ld + i, params_before.beta/2.3)]
                    else:
                        if (days_before_ld + i)<=564:
                            fine_grained_alpha += [(days_before_ld + i, params_before.alpha/1.8)]
                            fine_grained_beta += [(days_before_ld + i, params_before.beta/1.8)]
                        else:
                            if (days_before_ld + i)<=650:
                                fine_grained_alpha += [(days_before_ld + i, params_before.alpha/1)]
                                fine_grained_beta += [(days_before_ld + i, params_before.beta/1)]
                            else:
                                if (days_before_ld + i)<=681:
                                    fine_grained_alpha += [(days_before_ld + i, params_before.alpha/2.6)]
                                    fine_grained_beta += [(days_before_ld + i, params_before.beta/2.6)]
                    
                    
                    
                        
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
makedir_if_not_there(f'output/tbl/start2end_all/')
save_bundle([total, delta, increase, trans_data], p0_time, total_days,f'output/tbl/start2end_all/')
path = f'output/tbl/start2end_all/stats.txt'
save_to_json(stats, path)