import json
import os
import pandas as pd
import numpy as np
import seaborn as sbn
import matplotlib as mpl

from datetime import datetime, timedelta
from scipy.stats import poisson
from matplotlib import pyplot as plt

from const2 import STATE, STATES, NUM_STATES, COLORS, TRANS

# mpl.style.use('paper')

#DATE_FORMAT = '%d/%m/%Y'
DATE_FORMAT = '%Y/%m/%d'


def p_t(H_val, M_val, k, x0):
    """probability of going to hospital
    depends on the number of vacant beds H_val - M_val
    and logistic function parameters, k (controls steepiness) and x0
    """
    x = H_val - M_val
    if x > 0:
        return 1 / (1 + np.exp(-k * (x - x0)))
    else:
        return 0


def pr_IM_long(T, t, data,  k, x0):
    """
    probability of transitting from I at time T-t to M at time T
    """
    p_T = p_t(data[T, STATE.H], data[T, STATE.M], k, x0)
    if p_T == 0:
        return 0
    p_T_minus_t_list = np.array([p_t(data[T-i, STATE.H], data[T-i, STATE.M], k, x0) for i in range(1, t)])
    p = np.prod(1-p_T_minus_t_list) * p_T
    return p


def truncated_poisson(x, mu, min_x, max_x):
    assert x == int(x)
    x = int(x)
    assert x <= max_x
    all_probas = np.array([poisson.pmf(xi, mu) for xi in range(min_x, max_x+1)])
    all_probas /= all_probas.sum()
    assert np.isclose(all_probas.sum(), 1)
    return all_probas[x-min_x]


def pr_EI_long(t, mu_ei, k):
    assert t >= 1
    return truncated_poisson(t, mu_ei, 1, k)


def pr_MO_long(t, mu_mo, k):
    assert t >= 1
    return truncated_poisson(t, mu_mo, 1, k)


class Params:
    def __init__(
            self,
            # infection-related parameters:
            alpha=0.02, beta=0.01,
            mu_ei=6.0,
            mu_mo=14.0,
			mev1_mo=7.0,
			mv2_mo=1.0,
			
            mean_IM=7,
            x0_pt=10000, # k_pt=0.0001,
            k_days=14,
            l_days=7,
            # city-related
            total_population=11069533,
			initial_num_V1=0,
			initial_num_V2=0,
			initial_num_EV1=0,
            initial_num_E=100,
            initial_num_I=20,
            initial_num_M=0,
            stages=None
        ):
        
        self.total_population = total_population
        self.initial_num_V1 = initial_num_V1
        self.initial_num_V2 = initial_num_V2
        self.initial_num_EV1 = initial_num_EV1
        self.initial_num_E = initial_num_E
        self.initial_num_I = initial_num_I
        self.initial_num_M = initial_num_M
        # probability  parameters
        # S -> E

        self.alpha = alpha
        self.beta = beta

        self.alpha_array = None
        self.beta_array = None
        
        # E -> I: Poisson
        self.mu_ei = mu_ei
        
        # I -> M: geoemtric
        self.x0_pt = x0_pt
        self.mean_IM = mean_IM
        self.k_pt = np.log(mean_IM-1) / x0_pt  
        
        # M -> O: Poisson
        self.mu_mo = mu_mo
		
		# V-O
        self.mev1_mo = mev1_mo
        self.mv2_mo = mv2_mo
		
        # time window size
        self.k_days = k_days

        self.stages = stages
        self.num_stages = 1 if stages is None else (len(stages) + 1)

    def get_stage_num(self, t):
        if self.stages is None:
            return 0
        else:
            for i, time in enumerate(self.stages):
                assert time > 0
                if t < time:
                    return i
            return self.num_stages - 1
    
    def populate_alpha_array(self):
        times = np.array([t for t, _ in self.alpha])
        values = np.array([v for _, v in self.alpha])
        
        max_t = times.max()
        self.alpha_array = np.zeros(max_t+1)
        for value, t1, t2 in zip(values[:-1], times[:-1], times[1:]):
            for i in range(t1, t2):
                self.alpha_array[i] = value
        self.alpha_array[max_t:] = values[-1]
        # print(self.alpha_array)
        
    def populate_beta_array(self):
        times = np.array([t for t, _ in self.beta])
        values = np.array([v for _, v in self.beta])
        
        max_t = times.max()
        self.beta_array = np.zeros(max_t+1)
        for value, t1, t2 in zip(values[:-1], times[:-1], times[1:]):
            for i in range(t1, t2):
                self.beta_array[i] = value
        self.beta_array[max_t:] = values[-1]
        # print(self.beta_array)
        
    def alpha_func(self, t):
        if isinstance(self.alpha, float):
            return self.alpha
        elif isinstance(self.alpha, list):
            if self.alpha_array is None:
                self.populate_alpha_array()
                
            if t >= len(self.alpha_array):
                return self.alpha_array[-1]
            else:
                return self.alpha_array[t]
        else:
            raise ValueError(f'cannot understand: {self.alpha}')

    def beta_func(self, t):
        if isinstance(self.beta, float):
            return self.beta
        elif isinstance(self.beta, list):
            if self.beta_array is None:
                self.populate_beta_array()
                
            if t >= len(self.beta_array):
                return self.beta_array[-1]
            else:
                return self.beta_array[t]
        else:
            raise ValueError(f'cannot understand: {self.beta}')

    def get_alpha_beta_by_stage(self, s):
        assert s < self.num_stages
        if self.num_stages == 1:
            return self.alpha, self.beta

        if s == self.num_stages - 1:
            t = self.stages[-1]
        else:
            t = self.stages[s] - 1

        return self.alpha_func(t), self.beta_func(t)
    
    def __repr__(self):
        return f"""total_population: {self.total_population}
		initial_num_V1: {self.initial_num_V1}
		initial_num_V2: {self.initial_num_V2}
		initial_num_EV1: {self.initial_num_EV1}
        initial_num_E: {self.initial_num_E}
        initial_num_I: {self.initial_num_I}
        initial_num_M: {self.initial_num_M}

        alpha: {self.alpha}
        beta:  {self.beta}

        mu_ei: {self.mu_ei}
        mu_mo: {self.mu_mo}

        x0_pt: {self.x0_pt}
        k_pt:  {self.k_pt}
        mean_IM: {self.mean_IM}

        k_days: {self.k_days}
        """


def T(s):
    return datetime.strptime(s, DATE_FORMAT)


def get_T1_and_T2(I2OM_by_days, E2I_by_days):
    I_num_and_day_array = np.array(
        [[num, d] for num, d in zip(I2OM_by_days, range(1, len(I2OM_by_days) + 1))]
    )
    total_num_I = I_num_and_day_array[:, 0].sum()
    mean_I_days = (I_num_and_day_array[:, 0] * I_num_and_day_array[:, 1]).sum() / total_num_I
    
    E_num_and_day_array = np.array(
        [[num, d] for num, d in zip(E2I_by_days, range(1, len(E2I_by_days) + 1))]
    )
    total_num_E = E_num_and_day_array[:, 0].sum()
    mean_E_days = (E_num_and_day_array[:, 0] * E_num_and_day_array[:, 1]).sum() / total_num_E

    return mean_E_days, mean_I_days


def R0(total_population, alpha, beta, T1, T2):
    return (1 + total_population * alpha * T1) * (1 + total_population * beta * T2)


def plot_total(total):
    fig, ax = plt.subplots(1, 1)
    for color, s in zip(COLORS[1:], range(1, NUM_STATES)):
        ax.plot(total[:, s], c=color)
    fig.legend(STATES[1:])
    fig.tight_layout()
    return fig, ax


def trans2df(trans, p0_time, total_days):
    df = pd.DataFrame.from_dict({
        'date': pd.date_range(p0_time, p0_time+timedelta(days=total_days)),
		'S2V1':  trans[:, TRANS.S2V1],
		'V12EV1':  trans[:, TRANS.V12EV1],
		'S2V2':  trans[:, TRANS.S2V2],
        'S2E':  trans[:, TRANS.S2E],
        'E2I':  trans[:, TRANS.E2I],
        'I2M':  trans[:, TRANS.I2M],
        'M2O':  trans[:, TRANS.M2O],
		'EV12O':  trans[:, TRANS.EV12O],
		#'V22O':  trans[:, TRANS.V22O],
        'EbyE': trans[:, TRANS.EbyE],
        'EbyEV1': trans[:, TRANS.EbyEV1],
		'EbyI': trans[:, TRANS.EbyI],
		'EV1byE': trans[:, TRANS.EV1byE],
		'EV1byI': trans[:, TRANS.EV1byI],
		'EV1byEV1': trans[:, TRANS.EV1byEV1]
    })
    return df


def data2df(total, p0_time, total_days):
    df = pd.DataFrame.from_dict({
        'date': pd.date_range(p0_time, p0_time+timedelta(days=total_days)),
        'S': total[:, STATE.S],
		'V1': total[:, STATE.V1],
		'V2': total[:, STATE.V2],
		'EV1': total[:, STATE.EV1],
        'E': total[:, STATE.E],
        'I': total[:, STATE.I],
        'M': total[:, STATE.M],
        'O': total[:, STATE.O],
        'H': total[:, STATE.H]
    })
    return df


def enhance_total(df):
    df['EIMO'] = df['E'] + df['I'] + df['M'] + df['O']
    df['IMO'] = df['I'] + df['M'] + df['O']
    df['IM'] = df['I'] + df['M']
    return df


def total_to_csv(p0_time, total_days, total, path):
    df = data2df(total, p0_time, total_days)
    df.to_csv(path, index=None)


def plot_total(total, p0_time, total_days):
    sbn.set_style("whitegrid")
    
    def np_to_dt(d):
        return pd.to_datetime(str(d))
    
    df = data2df(total, p0_time, total_days)
    df['date_str'] = df['date'].apply(lambda d: np_to_dt(d).strftime('%y/%m/%d'))

    def process_state(state):
        subdf = df[['date', state]]
        subdf['index'] = df.index
        subdf['value'] = subdf[state].copy()
        del subdf[state]
        subdf['state'] = state
        return subdf

    # S = process_state('S')
    V1 = process_state('V1')
    V2 = process_state('V2')
    EV1 = process_state('EV1')
    E = process_state('E')
    I = process_state('I')
    M = process_state('M')
    O = process_state('O')
    H = process_state('H')
    ndf = pd.concat([V1,V2,EV1,E, I, M, O, H], ignore_index=True)

    nticks = 8
    step = int(np.floor(df.shape[0] / nticks))

    xticks = df['date_str'].index[::step].values
    xtick_labels = df['date_str'][::step].values
    print(xtick_labels)

    fig, ax = plt.subplots(1, 1)
    stuff = sbn.lineplot(
        x="index", y="value", hue='state', data=ndf, ax=ax,
        palette=['orange', 'red', 'pink', 'gray', 'blue','purple','lightblue','yellow'],
        legend=None
    )
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels, rotation=15)
    ax.set_xlabel('date')
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0,  0))
    ax.legend(stuff.lines, ['V1','V2','EV1','E', 'I', 'M', 'O', 'H'], loc='best')
    fig.tight_layout()

    return fig, ax


def save_to_json(obj, path):
    s = json.dumps(obj, indent=4, sort_keys=True)
    with open(path, 'w') as f:
        f.write(s)


def save_bundle(bundle, p0_time, total_days, dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    names = ['total', 'delta', 'increase', 'transition']
    for d, name in zip(bundle, names):
        if name == 'transition':
            df = trans2df(d, p0_time, total_days)
        else:
            df = data2df(d, p0_time, total_days)
            if name == 'total':
                df = enhance_total(df)
        df.to_csv(f'{dir_name}/{name}.csv', index=None)


def makedir_if_not_there(d):
    if not os.path.exists(d):
        os.makedirs(d)
