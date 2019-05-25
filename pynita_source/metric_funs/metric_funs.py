"""
xxx
Created on Jun 5, 2018
@author: Leyang Feng
@email: feng@american.edu
@Project: pynita
License:  
Copyright (c) 
"""

import numpy as np 
from scipy import ndimage
import matplotlib.pyplot as plt

def computMetrics_wrapper(tuple_input_args):
    results_dic, vi_change_thresh, run_thresh, time_step = tuple_input_args
    return computeMetrics(results_dic, vi_change_thresh, run_thresh, time_step)


def computeMetrics(results_dic, vi_change_thresh, run_thresh, time_step):
    
    # ---
    # 1. extract information from results_dic
    knots = results_dic['final_knots'];
    coeffs = results_dic['final_coeffs'];
    rises = results_dic['rises'];
    #runs = results_dic['runs'];
    runs_in_days = results_dic['runs_days'];
    
    if type(knots) is not 'int':
    
        try:
            # ---
            # 2. interpolation 
            knot_first = np.floor(knots[0]/1000)
            knot_last = np.floor(knots[-1]/1000)+1
            all_knots_dis = np.sort(np.unique(np.concatenate((np.arange(knot_first, knot_last+1, time_step) * 1000, knots))))
            all_knots_dis = all_knots_dis[(all_knots_dis >= knots[0]) & (all_knots_dis <= knots[-1])]
            all_coeffs_interp = np.interp(all_knots_dis, knots, coeffs) 
            interp_pts = np.column_stack((all_knots_dis, all_coeffs_interp)) # output 
            
            # ---
            # 3. change percent and slope calculation 
            change_percent = rises/abs(coeffs[0:-1])
            dist_flags = (change_percent<vi_change_thresh) & (runs_in_days<=run_thresh)
            dist_bin = [1 if flag else 0 for flag in dist_flags]
            label, num_features = ndimage.label(dist_bin)
            
            # 4. disturbance detection
            dist_locs = []
            for i in range(num_features):
                label_val = i + 1 
                locs = np.where(label == label_val)[0]
                dist_locs.append((locs[0], locs[-1]+1))
            
            # ---
            # 5. disturbance metric calculation 
            # 5.a no disturbance 
            if len(dist_locs) == 0: 
                num_dist = 0
                cum_mag_dist = np.nan
                dist_date_before = np.nan
                dist_date_nadir = np.nan
                dist_duration = np.nan
                dist_slope = np.nan
                dist_coeff_nadir = np.nan
                post_dist_slope = np.nan
                post_dist_mag = np.nan
                dist_mag = np.nan
                dist_coeff_before = np.nan
            # 5.b get metrics for largest disturbance as default 
            else: 
                num_dist = len(dist_locs) # output 
                
                dist_mags = []
                for dist_loc in dist_locs:
                    coeff_st = coeffs[dist_loc[0]]
                    coeff_ed = coeffs[dist_loc[1]]
                    mag = coeff_st-coeff_ed
                    dist_mags.append(mag)
                cum_mag_dist = sum(dist_mags) # output 
                
                dist_mags = np.array(dist_mags)
                dist_idx = int(np.where(dist_mags==dist_mags.min())[0])            
                dist_loc = dist_locs[dist_idx]
                
                dist_date_before = knots[dist_loc[0]] # output 
                dist_date_nadir = knots[dist_loc[1]] # output 
                dist_duration = dist_date_nadir - dist_date_before # output
                
                dist_coeff_before = coeffs[dist_loc[0]] # output 
                dist_coeff_nadir = coeffs[dist_loc[1]] # output 
                dist_mag = dist_coeff_before - dist_coeff_nadir # output 
                
                dist_slope = -dist_mag/dist_duration # output 
                
                # first 'recovery' or just first segment after default disturbance 
                if dist_loc[1] == (len(knots)-1): # the case that the disturbance is the last sagment 
                    post_dist_slope = np.nan # output 
                    post_dist_mag = np.nan
                else:
                    next_loc = [dist_loc[1], dist_loc[1]+1]
                    post_dist_mag = coeffs[next_loc[1]] - coeffs[next_loc[0]] # output 
                    post_dist_slope = post_dist_mag / (knots[next_loc[1]] - knots[next_loc[0]]) # output 
                      
        except:
            num_dist = np.nan
            cum_mag_dist = np.nan
            dist_date_before = np.nan
            dist_date_nadir = np.nan
            dist_duration = np.nan
            dist_slope = np.nan
            dist_coeff_nadir = np.nan
            post_dist_slope = np.nan
            post_dist_mag =np.nan
            dist_mag = np.nan
            dist_coeff_before = np.nan
            interp_pts = np.nan
    
    else: 
        num_dist = np.nan
        cum_mag_dist = np.nan
        dist_date_before = np.nan
        dist_date_nadir = np.nan
        dist_duration = np.nan
        dist_slope = np.nan
        dist_coeff_nadir = np.nan
        post_dist_slope = np.nan
        post_dist_mag =np.nan
        dist_mag = np.nan
        dist_coeff_before = np.nan
        interp_pts = np.nan
        
    metrics_dic = {'num_dist': num_dist,
                   'cum_mag_dist': cum_mag_dist,
                   'dist_date_before': dist_date_before, 
                   'dist_date_nadir': dist_date_nadir, 
                   'dist_duration': dist_duration, 
                   'dist_slope': dist_slope,
                   'dist_mag': dist_mag,
                   'dist_coeff_before': dist_coeff_before,
                   'dist_coeff_nadir': dist_coeff_nadir,
                   'post_dist_slope': post_dist_slope,
                   'post_dist_mag': post_dist_mag,
                   'interp_pts': interp_pts}
        
    return metrics_dic

#%%
def calDistDate(metrics_dic, option='middle'):
    dist_date_before = metrics_dic['dist_date_before']
    dist_date_nadir = metrics_dic['dist_date_nadir']

    if option == 'beginning':
        dist_date = dist_date_before
    elif option == 'middle':
        dist_date = (dist_date_before + dist_date_nadir) / 2
    elif option == 'end':
        dist_date = dist_date_nadir
    else: 
        raise RuntimeError('ERROR: invalid option!')
    
    return dist_date

#%%
def dateValue(metrics_dic, value_date):
    
    interp_pts = metrics_dic['interp_pts']
    
    if np.isnan(interp_pts).any():
        real_date = np.nan
        real_value = np.nan
    else:
        start_date = interp_pts[0, 0]
        end_date = interp_pts[-1, 0]
    
        if value_date == -9999:
            real_date = start_date
            real_value = interp_pts[:, 1][np.argmin(abs(interp_pts[:, 0] - real_date))] # only first ocurrance will be returned 
        elif value_date == 9999:
            real_date = end_date
            real_value = interp_pts[:, 1][np.argmin(abs(interp_pts[:, 0] - real_date))] # only first ocurrance will be returned 
        elif (value_date>=start_date) & (value_date<=end_date):
            real_date = value_date
            real_value = interp_pts[:, 1][np.argmin(abs(interp_pts[:, 0] - real_date))] # only first ocurrance will be returned 
        else:
            if not np.isnan(value_date):
#                print('WARNNING: date not in time series, nan returned as value for given date')
#               print(str(start_date) + ' --> ' + str(value_date) + ' --> ' + str(end_date))
            real_date = value_date 
            real_value = np.nan
        
    return real_date, real_value 
    
#%%
def valueChange(metrics_dic, start_date=-9999, end_date=9999, option='diff'):
    start_date, start_value = dateValue(metrics_dic, start_date)
    end_date, end_value = dateValue(metrics_dic, end_date)
    
    if start_date > end_date:
        print(str(start_date) + ' ---> ' + str(end_date))
        raise RuntimeError('ERROR: wrong start_date/end_date')
    
    if option == 'diff':
        out_val = end_value - start_value 
    elif option == 'change_percent':
        out_val = (end_value - start_value) / start_value * 100
    else: 
        raise RuntimeError('ERROR: invalid option!')
    
    return out_val 
    
#%%
def stretchMI(vals_1d, low_high=[2, 98]):
    
    low_per = np.percentile(vals_1d, low_high[0])
    high_per = np.percentile(vals_1d, low_high[1])
    
    vals_1d_adj = vals_1d
    vals_1d_adj = np.where(vals_1d_adj<low_per, low_per, vals_1d_adj)
    vals_1d_adj = np.where(vals_1d_adj>high_per, high_per, vals_1d_adj)
    
    return vals_1d_adj

#%%
#def plotMI(MI_2d, title, label): 
#    fig, ax = plt.subplots()  
#    mappable = ax.matshow(MI_2d)
#    fig.suptitle(title)
#    fig.colorbar(mappable, label=label)

def plotMI(MI_2d, title, label):
    mappable = plt.matshow(MI_2d,fignum=title, extent=[0, MI_2d.shape[1], MI_2d.shape[0], 0])
    plt.colorbar(mappable, label=label)
    plt.suptitle(title)
    plt.tight_layout()

#%%          
def MI_complexity(results_dics):
    values_1d = np.array([dic['complexity'] for dic in results_dics])
    
    return(values_1d)
    
#%%
def MI_distDate(metrics_dics, option='middle'):
    vals_1d = np.array([calDistDate(metrics_dic, option=option) for metrics_dic in metrics_dics])
    
    return(vals_1d)

#%%
def MI_distDuration(metrics_dics): # in days
    dist_durations = [metrics_dic['dist_duration'] for metrics_dic in metrics_dics] 
    vals_1d = np.array([np.floor(duration/1000)*365+np.mod(duration, 1000)/1000*365 for duration in dist_durations])
    
    return vals_1d

#%%
def MI_distMag(metrics_dics):
    vals_1d = np.array([dic['dist_mag'] for dic in metrics_dics])
    
    return vals_1d

#%%
def MI_distSlope(metrics_dics):
    vals_1d = np.array([dic['dist_slope'] for dic in metrics_dics])
    
    return vals_1d

#%%
def MI_linearError(results_dics):
    vals_1d = np.array([dic['mae_linear'] for dic in results_dics])
    
    return vals_1d

#%%
def MI_noise(results_dics):
    vals_1d = np.array([dic['noise'] for dic in results_dics])
    
    return vals_1d

#%%
def MI_bailcut(results_dics):
    vals_1d = np.array([(dic['mae_linear']/dic['noise']) for dic in results_dics])
    
    return vals_1d

#%%
def MI_postDistSlope(metrics_dics):
    vals_1d = np.array([dic['post_dist_slope'] for dic in metrics_dics])
    
    return vals_1d

#%%
def MI_postDistMag(metrics_dics):
    vals_1d = np.array([dic['post_dist_mag'] for dic in metrics_dics])
    
    return vals_1d

#%%
def MI_head(results_dics):
    vals_1d = np.array([dic['final_coeffs'][0] for dic in results_dics])
    
    return vals_1d

#%%
def MI_tail(results_dics):
    vals_1d = np.array([dic['final_coeffs'][-1] for dic in results_dics])
    
    return vals_1d

#%%
def MI_dateValue(metrics_dics, value_date):
    
    vals_1d = np.array([dateValue(metrics_dic, value_date)[1] for metrics_dic in metrics_dics])
    
    return vals_1d

#%%
def MI_valueChange(metrics_dics, start_date=-9999, end_date=9999, option='diff'):
    
    vals_1d = np.array([valueChange(metrics_dic, start_date=start_date, end_date=end_date, option=option) for metrics_dic in metrics_dics])
    
    return vals_1d

#%%
def MI_recovery(metrics_dics, time_passed, option='diff'):
    
    vals_1d = []
    for metrics_dic in metrics_dics: 
        start_date = metrics_dic['dist_date_nadir']
        end_date = start_date + time_passed*1000
        val = valueChange(metrics_dic, start_date=start_date, end_date=end_date, option=option)
        vals_1d.append(val)
    vals_1d = np.array(vals_1d)
    return vals_1d

#%%
def MI_recoveryCmp(metrics_dics, time_passed):
    
    vals_1d = []
    for metrics_dic in metrics_dics: 
        dist_coeff_before = metrics_dic['dist_coeff_before']
        start_date = metrics_dic['dist_date_nadir']
        end_date = start_date + time_passed*1000
        junk_output, end_date_val = dateValue(metrics_dic, end_date)
        val = end_date_val / dist_coeff_before
        vals_1d.append(val)
    vals_1d = np.array(vals_1d)
    return vals_1d
