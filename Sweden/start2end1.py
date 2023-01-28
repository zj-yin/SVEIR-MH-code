#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().run_line_magic('matplotlib', 'inline')




import pickle as pkl
import pandas as pd
from datetime import  datetime, timedelta
from copy import copy

from core2 import  do_simulation
from helpers2 import Params, plot_total, T, data2df, enhance_total, save_to_json, save_bundle, makedir_if_not_there
from const2 import  STATE


p0_time = pkl.load(open('output_test/p0_time.pkl', 'rb'))
lockdown_time = T('2020/6/11')


# In[4]:


p0_time


# In[5]:


bed_info_raw = [(p0_time, 30183)]
	
pkl.dump(bed_info_raw, open('data/bed_info_raw.pkl', 'wb'))
# number of new beds at  some days
bed_info = [((d-p0_time).days, n) for d, n in bed_info_raw]
pkl.dump(bed_info, open('data/bed_info.pkl', 'wb'))
print(bed_info)


# In[6]:


params_before = pkl.load(
    open('output_test/params_before_lockdown.pkl', 'rb')
)

params_after = pkl.load(
    open('output/params_after_lockdown.pkl', 'rb')
)


# In[7]:


days_before_ld  = (lockdown_time -  p0_time).days
days_before_ld


# In[8]:


total_days = 360


# In[9]:


days_before_ld


# In[10]:


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


# In[11]:


params = Params(
    total_population=params_before.total_population,
    initial_num_E=params_before.initial_num_E,
    initial_num_I=params_before.initial_num_I,
    initial_num_M=params_before.initial_num_M,  
    mu_ei=params_after.mu_ei,
    mu_mo=params_after.mu_mo,
    k_days=params_after.k_days,
    x0_pt=params_after.x0_pt,
    alpha=fine_grained_alpha,
    beta=fine_grained_beta,
    stages=[days_before_ld] + [(days_before_ld + i) for i in range(offset, offset*n_offsets+1, offset)]
)

total, delta, increase, trans_data, stats = do_simulation(total_days, bed_info, params, p0_time=p0_time, verbose=0)


# In[12]:


stats


# In[13]:


params


# In[14]:


stats


# In[15]:


p0_time + timedelta(days=total_days)


# In[16]:


from helpers2 import plot_total
fig, ax = plot_total(total, p0_time, total_days)
fig.savefig('figs/start2end.pdf')


# In[2]:


makedir_if_not_there('output/tbl/start2end2')


# In[17]:


save_bundle([total, delta, increase, trans_data], p0_time, total_days, 'output/tbl/start2end2')


# In[18]:


path = 'output/tbl/start2end2/stats.txt'
save_to_json(stats, path)

