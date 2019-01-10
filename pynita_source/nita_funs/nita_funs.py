#%%
import numpy as np
import pandas as pd
import copy
import math
from scipy import stats, signal
import matplotlib.pyplot as plt

#%%
def filterLimits(x, y, doy_vec, value_limits, date_limits, doy_limits):
   
    # ---
    # (1)
    if sum(date_limits) == 0:
        x = x
        y = y
        doy_vec = doy_vec
    else:
        if (date_limits[0] == -9999) & (date_limits[1] != -9999):
            start_date = x[0]
            end_date = date_limits[1]
        elif (date_limits[0] != -9999) & (date_limits[1] == 9999):
            start_date = date_limits[0]
            end_date = x[-1]
        else:
            start_date = date_limits[0]
            end_date = date_limits[-1]
    
        date_flags = (x >= start_date) & (x <= end_date)
        x = x[date_flags]
        y = y[date_flags]
        doy_vec = doy_vec[date_flags]
    
    # ---
    # (2)
    doy_flags = np.full(doy_vec.shape, False, dtype=bool)
    for doy_limit in doy_limits:
        doy_flag_it = (doy_vec >= doy_limit[0]) & (doy_vec <= doy_limit[1])
        doy_flags = doy_flags | doy_flag_it
    
    x = x[doy_flags]
    y = y[doy_flags]
    doy_vec = doy_vec[doy_flags]
    
    # ---
    # (3)
    non_nan_flags = ~np.isnan(y)
    x = x[non_nan_flags]
    y = y[non_nan_flags]
    doy_vec = doy_vec[non_nan_flags]
    
    # ---
    # (4)
    value_flags = np.logical_and(y >= value_limits[0], y <= value_limits[1]) 
    x = x[value_flags]
    y = y[value_flags]
    doy_vec = doy_vec[value_flags]
    
    return x, y, doy_vec

#%%
def distancePointEdge(points, edge):
    # Python implementation of MATLAB function distancePointEdge created by David Legland 
    
    # edge shoud be in the format of [x0, y0, x1, y1]
    # pts should be in the format of [[x1, y1],
    #                                 [x2, y2],
    #                                   ...   
    #                                 [xn,yn]]
    
    edge = np.array(edge).reshape((4,1))
    points = np.array(points) 
    
    if edge.shape != (4,1):
        raise ValueError('in-valid edge shape!')
     
    if points.shape[1] != 2:
        raise ValueError('in-valid points shape!')
        
    # direction vector of each edge
    dx = edge[2] - edge[0]
    dy = edge[3] - edge[1]

    # compute position of points projected on the supporting line
    # (Size of tp is the max number of edges or points)   
    delta = dx * dx + dy * dy
    tp = ((points[:, 0] - edge[0]) * dx + (points[:, 1] - edge[1]) *dy) / delta


    # change position to ensure projected point is located on the edge
    tp[tp < 0] = 0;
    tp[tp > 1] = 1;

    # coordinates of projected point
    p0 = np.column_stack((edge[0] + tp * dx, edge[1] + tp * dy))

    # compute distance between point and its projection on the edge
    dist = np.sqrt((points[:,0] - p0[:,0]) ** 2 + (points[:,1] - p0[:,1]) ** 2);

    return dist 

#%%
def calDistance(knot_set, coeff_set, pts):
    
    pts = np.array(pts) 
    
    dist_mat = np.empty((pts.shape[0],0))
    for i in range(0,len(knot_set)-1):
        edge = [knot_set[i], coeff_set[i], knot_set[i+1], coeff_set[i+1]]
        dist_mat_i = distancePointEdge(pts, edge)
        dist_mat = np.column_stack((dist_mat, dist_mat_i))
    
    return dist_mat

#%%
def calMae(dist):
    dist = dist.min(axis=1)
    mae = dist.mean()
    return mae

#%%
def findCandidate(dist, filt_dist, pct, 
                  y, loc_set, filter_opt='movcv'):
    
    dist = dist.min(axis=1)
    
    mov_mean = np.array(pd.Series(dist).rolling(window=filt_dist).mean())
    mov_std = np.array(pd.Series(dist).rolling(window=filt_dist).std())
    if np.isnan(mov_std).all():
        mov_std = np.ones(mov_std.shape)
    
    if filter_opt == 'movcv':
        search_series = (mov_mean / mov_std)
    if filter_opt == 'movmean':
        search_series = mov_mean
    if filter_opt == 'sgolay':
        search_series = signal.savgol_filter(dist, filt_dist, 2)
        
    invalid_ss_idx = list(set(list(range(0,filt_dist)) + 
                              list(range(len(search_series) - filt_dist, len(search_series))) + 
                              list(loc_set)))
    search_series_inner = np.delete(search_series, invalid_ss_idx, None) # the N-1 search_series got flatten in here
    
    if len(search_series_inner) == 0:
        cand_loc = -999
        coeff = -999 
    else:
        cand_loc = int(np.where(search_series.flatten() == search_series_inner.max())[0])
        cand_loc_filt = list(range(int(cand_loc - ((filt_dist - 1) / 2)), int(cand_loc + ((filt_dist - 1) / 2) + 1)))
        coeff = np.percentile(y[cand_loc_filt], pct, interpolation='midpoint')
        
    return cand_loc, coeff

#%%
def updateknotcoeffSet(knot_set, coeff_set, loc_set, x, cand_loc, coeff):
    knot_val = x[cand_loc]
    knot_set = np.unique(np.append(knot_set, knot_val))
    new_knot_loc = int(np.where(knot_set == knot_val)[0])
    coeff_set = np.insert(coeff_set, new_knot_loc, coeff)
    loc_set = np.unique(np.append(loc_set, cand_loc))

    return knot_set, coeff_set, loc_set 

#%%
def genKeepIdx(keep_knots, keep_coeffs, pts, pct, y_pos_flags):
    if len(keep_knots) - 2 > 0:
        mae_iter_ortho = maeEvaforKnotRemoval(keep_knots, keep_coeffs, pts, y_pos_flags, pct)
        mae_iter_ortho = np.array(mae_iter_ortho)
        remove_idx = mae_iter_ortho.argmin() + 1 # jump ahead since mae_iter_ortho only coresponding to inner knots 
        keep_idx = list(range(0, len(keep_knots)))
        removed = keep_idx.pop(remove_idx)
    else:
        keep_idx = [0, len(keep_knots)-1]

    return keep_idx

#%%
def maeEvaforKnotRemoval(knot_set, coeff_set, pts, y_pos_flags, pct):
    mae_iter_ortho = []
    for i in range(1, len(knot_set) - 1): # evaluating only inner knots
        remove_idx = i
        new_knot_set = np.delete(knot_set, remove_idx)
        new_coeff_set = np.delete(coeff_set, remove_idx)
        
        dist = calDistance(new_knot_set, new_coeff_set, pts)
        
        ortho_err = dist.min(axis=1)
        ortho_err[y_pos_flags] = ortho_err[y_pos_flags] * pct
        ortho_err[~y_pos_flags] = ortho_err[~y_pos_flags] * (100 - pct) 
        mae_iter_ortho.append(ortho_err.mean())
    
    return mae_iter_ortho

#%%
def calBIC(ortho_err, knot_set, penalty):
    # BIC acccumulation
    positive_flags = ortho_err > 0 # in case a value is exactly 0
    
    
    #pars = stats.lognorm.fit(ortho_err[positive_flags])
    #loglik = -1 * stats.lognorm.nnlf(pars, ortho_err[positive_flags])

    pars = stats.norm.fit(np.log(ortho_err[positive_flags]))
    loglik = -1 * stats.norm.nnlf(pars, np.log(ortho_err[positive_flags]))

    num_segs = len(knot_set)-1

    bic_remove = -2 * loglik + penalty * num_segs * math.log(len(ortho_err))
 
    return bic_remove
    
#%%
##TODO: better exception handling by type
def nita_px(px, date_vec, doy_vec, 
            value_limits=[-1,1], doy_limits=[1, 365], date_limits=[-9999, 9999],
            bail_thresh=1, noise_thresh=1,
            penalty=1, filt_dist=3, pct=75, max_complex=10, min_complex=1,
            compute_mask=True, filter_opt='movcv'):
# documentation: 
#   input arguments:
#     data: 
#       px
#       date_vec 
#       doy_vec
#     constraints:
#       value_limits
#       doy_limits
#       date_limits
#       bail_thresh
#       noise_thresh      
#     numerical args:
#       penalty
#       filt_dist
#       pct
#       max_complex
#       min_complex
#     switches:
#       compute_mask
#     options:
#       filter_opt

    # ---
    # 0. check the inputs 
    unq_idx = np.unique(date_vec,return_index=True)[1]
    px = px[unq_idx] 
    date_vec = date_vec[unq_idx]
    doy_vec = doy_vec[unq_idx]
    
    try:
        
    #---
    # 0.5 prepare x and y 
        # make a copy of orignial data pairs 
    
        x = copy.deepcopy(date_vec) 
        y = copy.deepcopy(px) 
    
        x, y, doy_vec = filterLimits(x, y, doy_vec, value_limits, date_limits, doy_limits)
        
        # warning will be raised by numpy when len(y) == 1
        noise = np.median(np.absolute(np.diff(y)))
    
        diff_holder = np.diff(y)
        non_noise_flags = np.append(np.array([False]),np.absolute(diff_holder) <= noise_thresh)
        x = x[non_noise_flags]
        y = y[non_noise_flags]
        x_len = len(x)
    
        if x_len <= (filt_dist*2):
             raise ValueError('Not enough data pairs!')    
    # ---
    # 1. single line fit
        first_coeff = np.percentile(y[0:(filt_dist)], pct, interpolation='midpoint') # use 'midpoint' to mimic matlab
        last_coeff = np.percentile(y[-filt_dist:],pct, interpolation='midpoint')

        knot_set = np.array([x[0], x[-1]])      
        coeff_set = np.array([first_coeff, last_coeff])
        loc_set = np.array([0, x_len - 1])
    
        pts = np.column_stack((x, y))
    
        dist_init = calDistance(knot_set, coeff_set, pts)
        mae_lin = calMae(dist_init)

    # ---
    # 2. NITA build
        if (mae_lin/noise > bail_thresh) & compute_mask == True:
            
            mae_ortho = []
            mae_ortho.append(mae_lin)
        
            for i in range(1, max_complex):
                
                dist = calDistance(knot_set, coeff_set, pts)
                cand_loc, coeff = findCandidate(dist, filt_dist, pct, y, loc_set, filter_opt);
            
                if cand_loc == -999:
                    break
            
                knot_set, coeff_set, loc_set = updateknotcoeffSet(knot_set, coeff_set, loc_set, x, cand_loc, coeff)
                dist_new = calDistance(knot_set, coeff_set, pts)
                mae_ortho.append(calMae(dist_new))
                del dist, dist_new, cand_loc, coeff 
            
            complexity_count = len(knot_set)-1
   
    # ---
    # 3. BIC removal process
            # *_max saved as copies (useful for debugging)
            knots_max = copy.deepcopy(knot_set)
            coeffs_max = copy.deepcopy(coeff_set)
                 
            yinterp1 = np.interp(x, knot_set, coeff_set) # method linear as default
            y_pos_flags = (y - yinterp1) > 0  
             
            if complexity_count < min_complex:
                exit_count = complexity_count
            else: 
                exit_count = min_complex
        
            end_count = complexity_count - exit_count + 1
        
            mae_ortho_holder = []
            bic_remove = []
            knot_storage = []
            coeff_storage = []
        
            knot_storage.append(knot_set)
            coeff_storage.append(coeff_set) 
            dist_init = calDistance(knot_set, coeff_set, pts)
            mae_ortho_holder.append(calMae(dist_init)) 
            ortho_err = dist_init.min(axis=1)
            ortho_err[y_pos_flags] = ortho_err[y_pos_flags] * pct
            ortho_err[~y_pos_flags] = ortho_err[~y_pos_flags] * (100 - pct)
            bic_remove.append(calBIC(ortho_err, knot_set, penalty))
        
            for i in range(1, end_count):
                keep_loc = genKeepIdx(knot_set, coeff_set, pts, pct, y_pos_flags)
            
                knot_set = knot_set[keep_loc]
                coeff_set = coeff_set[keep_loc]
                knot_storage.append(knot_set)
                coeff_storage.append(coeff_set)
            
                dist = calDistance(knot_set, coeff_set, pts)
                mae_ortho_holder.append(calMae(dist))
                ortho_err = dist.min(axis=1)
                ortho_err[y_pos_flags] = ortho_err[y_pos_flags] * pct
                ortho_err[~y_pos_flags] = ortho_err[~y_pos_flags] * (100 - pct)
            
                bic_remove.append(calBIC(ortho_err, knot_set, penalty))
                del dist, ortho_err
            
            bic_idx = int(np.where(bic_remove == min(bic_remove))[0])
            knots_final = knot_storage[bic_idx]
            coeffs_final = coeff_storage[bic_idx]
            mae_final = mae_ortho_holder[bic_idx]    
            complexity_final = len(knots_final) - 1
            
        else:
            knots_final = np.array([x[0], x[-1]])      
            coeffs_final = np.array([first_coeff, last_coeff])
            mae_final = mae_lin
            complexity_final = 1
     
        rises = np.diff(coeffs_final)
        runs = np.diff(knots_final)   
        runs_days = runs / 1000 * 365
    
    except:
        complexity_final = -999
        knots_final = -999
        coeffs_final = -999
        mae_final = -999
        mae_lin = -999
        noise = -999
        rises = -999
        runs = -999
        runs_days = -999
        pts = -999

    results_dic = {'complexity': complexity_final,
                   'final_knots': knots_final,
                   'final_coeffs': coeffs_final,  
                   'mae_linear': mae_lin,
                   'mae_final': mae_final,
                   'noise': noise,
                   'rises': rises, 
                   'runs': runs,
                   'runs_days': runs_days,
                   'pts': pts}

    return results_dic    

#%%
# TODO: come up with a good way to arrange colorbar when doing panel plot     
def viewNITA(px, date_vec, doy_vec, 
             results_dic, 
             showdata='fit', colorbar=True, title='', 
             fig=None, ax=None):
    # decide the existence of fig and ax (only check one of them is enough)
    if type(fig).__name__ == 'NoneType':
        fig, ax = plt.subplots()

    try: 
        # grab lines and data pairs 
        if type(results_dic['final_knots']).__name__ == 'int':
            raise TypeError('nita skipped!')
        
        knot_set = results_dic['final_knots']
        coeff_set = results_dic['final_coeffs']
        bail_cut = results_dic['mae_linear'] / results_dic['noise']
        fit_pts = results_dic['pts']
        fit_count = len(fit_pts[:,0])
        if showdata == 'fit':
            plot_x = fit_pts[:,0]
            plot_y = fit_pts[:,1]
            plot_doy = np.round(((plot_x/1000 - np.floor_divide(plot_x, 1000)) * 365))
        else:
            plot_x = date_vec
            plot_y = px
            plot_doy = doy_vec
 
        # do the plotting
        mappable = ax.scatter(plot_x, plot_y, c=plot_doy)
        ax.plot(knot_set, coeff_set, 'ro', mfc='none')
        ax.plot(knot_set, coeff_set, 'r-')
        ax.set_xlim([plot_x.min(), plot_x.max()])
        ax.set_ylim([np.nanmin(plot_y), np.nanmax(plot_y)])
        ax.set_title(title) 
        xticks_lables = ax.get_xticks().tolist()
        xticks_lables = [str(xticks_label)[0:4] for xticks_label in xticks_lables]
        ax.set_xticklabels(xticks_lables)
        if colorbar:
            fig.colorbar(mappable)
        print('bail_cut = {0} \nfit_count = {1}'.format(bail_cut, fit_count))
    except TypeError:
        plt.cla()
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        ax.text(0.3, 0.3, 'something wrong in nita')
        ax.set_title(title)
    except:
        plt.cla()
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        ax.text(0.3, 0.3, 'something\'s wrong')
        ax.set_title(title)    
            
#%%           
def nita_stack_wrapper(stack_2d, compute_mask_1d, param_dic, i):
    
    # unpack the param_dic
    date_vec     = param_dic['date_vec']     
    doy_vec      = param_dic['doy_vec']      
    value_limits = param_dic['value_limits'] 
    doy_limits   = param_dic['doy_limits']   
    date_limits  = param_dic['date_limits']  
    bail_thresh  = param_dic['bail_thresh']  
    noise_thresh = param_dic['noise_thresh']   
    penalty      = param_dic['penalty']      
    filt_dist    = param_dic['filt_dist']    
    pct          = param_dic['pct']          
    max_complex  = param_dic['max_complex']  
    min_complex  = param_dic['min_complex']  
    filter_opt   = param_dic['filter_opt']   
    
    # decide the value of compute mask 
    compute_mask = compute_mask_1d[i]
    compute_mask = compute_mask == 1
    
    # get the value of px
    px = stack_2d[:,i]
    
    results_dic = nita_px(px, date_vec, doy_vec, 
                          value_limits, doy_limits, date_limits,
                          bail_thresh, noise_thresh,
                          penalty, filt_dist, pct, max_complex, min_complex,
                          compute_mask, filter_opt)

    return results_dic

#%%
def paramcomboCmp(param_combo, OBJECTIDs, handdraw_trajs, pts, user_vi, compute_mask):
    OBJETID_rmse = []
    OBJECTID_pct95_err = []
    for OBJECTID in OBJECTIDs:
                
        handdraw_traj = [dic['traj'] for dic in handdraw_trajs if dic['OBJECTID'] == OBJECTID][0]
                
        px = pts.loc[pts['OBJECTID'] == OBJECTID][user_vi].values
        date_vec = pts.loc[pts['OBJECTID'] == OBJECTID]['date_dist'].values
        doy_vec = pts.loc[pts['OBJECTID'] == OBJECTID]['doy'].values
            
        if len(px) == 0:
            raise RuntimeError('in-valid one or more OBJECTID(s)') 
            
        results_dic = nita_px(px, date_vec, doy_vec, 
                              param_combo['value_limits'], param_combo['doy_limits'], param_combo['date_limits'],
                              param_combo['bail_thresh'], param_combo['noise_thresh'],
                              param_combo['penalty'], param_combo['filt_dist'], param_combo['pct'], param_combo['max_complex'], param_combo['min_complex'],
                              compute_mask, param_combo['filter_opt'])
                
        nita_knots = results_dic['final_knots']
        nita_coeffs = results_dic['final_coeffs']
                
        draw_knots = [tp[0] for tp in handdraw_traj]
        draw_coeffs = [tp[1] for tp in handdraw_traj]
                
        common_start = max([nita_knots[0], draw_knots[0]])
        common_end = min([nita_knots[-1], draw_knots[-1]])
                
        nita_interp = np.interp(np.arange(common_start, common_end, 200), nita_knots, nita_coeffs)
        draw_interp = np.interp(np.arange(common_start, common_end, 200), draw_knots, draw_coeffs)
             
        sq_error = (draw_interp - nita_interp)**2
        rmse = np.sqrt(sq_error.mean())
        pct95_err = np.sqrt(np.percentile(sq_error, 95, interpolation='midpoint'))
                
        OBJETID_rmse.append(rmse)
        OBJECTID_pct95_err.append(pct95_err)
    
    return np.mean(OBJETID_rmse), np.median(OBJETID_rmse), np.mean(OBJETID_rmse)