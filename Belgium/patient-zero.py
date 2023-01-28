#!/usr/bin/env python
# coding: utf-8



get_ipython().run_line_magic('matplotlib', 'inline')




import numpy as np
import pandas as pd
import pickle as pkl
from itertools import product
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tqdm import tqdm
from matplotlib import pyplot as plt
from datetime import timedelta
from joblib import delayed, Parallel
from copy import copy

from core import  do_simulation
from helpers import Params, T, get_T1_and_T2, R0, plot_total, save_bundle, save_to_json, makedir_if_not_there

from const import STATE, COLORS, NUM_STATES,  STATES



'''
tran_coef_before = np.array([4.28, 5.28, 5.33, 4.38, 4.13, 5.27, 5.28, 5.32, 5.15, 5.22, 4.46, 4.20, 5.17, 5.11, 4.91, 4.92, 4.87, 4.04, 4.32, 4.22 , 3.60, 2.88])
tran_coef_after = np.array([0.66 ,0.67 ,0.68 ,0.66 ,0.69 ,0.69 ,0.66 ,0.69 ,0.68 ,0.67 ,0.60 ,0.62 ,0.61 ,0.62 ,0.62 ,0.61 ,0.60 ,0.62 ,0.67 ,0.60 ,0.58 ,0.59 ,0.58 ,0.57 ,0.59 ,0.60 ,0.57 ])
infection_factor = np.mean(tran_coef_before) / np.mean(tran_coef_after)
infection_factor = np.log(infection_factor)
infection_factor
'''
infection_factor=np.float64(3.47)



params_jan27 = pkl.load(
    open('output/params_after_lockdown.pkl', 'rb')
)




params_jan27





lockdown_date = T('2020/3/21')
lockdown_date



target_E = params_jan27.initial_num_E
target_I = params_jan27.initial_num_I
target_M = params_jan27.initial_num_M

actual_I = np.array([target_I])
actual_E = np.array([target_E])
actual_M = np.array([target_M])

actual_E, actual_I, actual_M




def prepare_params(t):
    p = Params(
        alpha=[(0, infection_factor * params_jan27.alpha), (t, params_jan27.alpha)],
        beta=[(0, infection_factor * params_jan27.beta), (t, params_jan27.beta)],
        stages=[t],
        initial_num_E=1,
        initial_num_I=0,
        initial_num_M=0,
        mu_ei=params_jan27.mu_ei,
        mu_mo=params_jan27.mu_mo,
        x0_pt=params_jan27.x0_pt,
        k_days=params_jan27.k_days
    )
    return p
        




bed_info = [(0, 12955)]
def one_run(t):
    params = prepare_params(t)
    # t days **before** lockdown (Jan 23)
    # simulation finishes at Jan 27 (after lockdown for 5 days)
    # t=1, 2, 3, ... means patient zero  appeared in Jan 22, 21, 20
    p0_time = lockdown_date - timedelta(days=t)
    
    total, _, _, _, stats = do_simulation(
        t+5, bed_info, params, p0_time=p0_time,
        verbose=0
    )
    
    pred_I = np.array([total[-1, STATE.I]])
    pred_E = np.array([total[-1, STATE.E]])
    pred_M = np.array([total[-1, STATE.M]])
    
    mse_I = mean_absolute_error(actual_I,  pred_I)
    mse_E = mean_absolute_error(actual_E, pred_E)
    mse_M = mean_absolute_error(actual_M, pred_M)
    mse_IM = mean_absolute_error(actual_M + actual_I, pred_M + pred_I)
    mse_IEM = mean_absolute_error(actual_I + actual_E + actual_M,  pred_I + pred_E + pred_M)
    return (t, actual_I[0], pred_I[0], mse_I, mse_E, mse_M, mse_IM, mse_IEM, stats)




# t is the number of days back
rows = Parallel(n_jobs=1)(delayed(one_run)(t) for t in tqdm(range(20, 61)))





df = pd.DataFrame(rows, columns=('t', 'actual_I', 'pred_I', 'mse_I', 'mse_E', 'mse_M', 'mse_IM', 'mse_IEM', 'r0_info'))




df.sort_values(by='mse_I').head(10)




best_t = int(df.sort_values(by='mse_IM').iloc[0].t)
p0_time = T('2020/3/20') - timedelta(days=best_t)
print(p0_time)




makedir_if_not_there('output/tbl/p0-time/')




df.to_csv('output/tbl/p0-time/error.csv', index=False)





pkl.dump(p0_time, open('output/p0_time.pkl', 'wb'))





params = copy(params_jan27)
params.alpha = infection_factor * params.alpha
params.beta = infection_factor * params.beta
params.initial_num_E = 1
params.initial_num_I = 0
params.initial_num_M = 0

    
total, delta, increase, trans, stats = do_simulation(best_t, bed_info, params, verbose=0,  p0_time=p0_time)





makedir_if_not_there('output/tbl/before-lockdown/')




save_bundle([total, delta, increase, trans], p0_time, best_t, 'output/tbl/before-lockdown')
save_to_json(stats, 'output/tbl/before-lockdown/stat.txt')



pkl.dump(
    params,
    open('output/params_before_lockdown.pkl', 'wb')
)





fig, ax = plot_total(total, p0_time, best_t)
makedir_if_not_there('figs/')
fig.savefig('figs/before-lockdown.pdf')

