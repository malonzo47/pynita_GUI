"""
Created on Jun 4, 2018
@author: Leyang Feng
@email: feng@american.edu
@Project: pynita
License:  
Copyright (c) 
"""
#import sys
import numpy as np
import time  
import copy
from multiprocessing import Pool
import matplotlib.pyplot as plt
from tqdm import tqdm

from .data_reader.data_loader import dataLoader
from .data_reader.ini_reader import ConfigReader
from .data_writer import data_writer_funs as dw
from .nita_funs import nita_funs as nf
from .metric_funs import metric_funs as mf
from .utils import logging as lg

class nitaObj:
    
    def __init__(self, ini):
        self.cfg = ConfigReader(ini)     
        self.pts = None
        self.stack = None
        self.stack_dates = None
        self.stack_doy = None
        self.stack_prj = None
        self.compute_mask = None 

    def updateConfig(self, ini):
        '''
        Update the configuration, if ini file has been modified and saved via GUI.
        If update was required, remove saved stack computation.
        :param ini:
        :return:
        '''
        config_new = ConfigReader(ini)
        needUpdate = self.cfg.updateData(config_new)
        if needUpdate:
            print("needed update")
            self.cfg = config_new
            self.pts = None
            self.stack = None
            self.stack_dates = None
            self.stack_doy = None
            self.stack_prj = None
            self.compute_mask = None


    def startLog(self):
        '''
        Setup and start log
        :return:
        '''
        self.log = True
        self.logger = lg.setupLogger(self.cfg)
        self.logger.info('Start logging...')
        
    def stopLog(self):
        '''
        Stop logging.
        :return:
        '''
        if self.log:
            self.logger.info('End logging...')
            lg.closeLogger(self.logger)
            
    def loadPts(self, info_column='none', full_table=False):
        '''
        Load points from csv file via dataloader.
        :param info_column: extra columns to be loaded, set as 'Name' for GUI
        :param full_table: boolean, whether to load full table
        :return:
        '''
        dl = dataLoader(self.cfg)
        self.pts = dl.load_pts(info_column, full_table)
        
        # properties
        self.pts_OBJECTIDs = list(set(self.pts.OBJECTID))
        self.pts_count = len(self.pts_OBJECTIDs)
        self.ref_pts = dl.ref_tb        
        
        if self.log:
            self.logger.info('Points file ' + self.cfg.ptsFn + ' loaded.')

    def loadRef(self):
        '''
        Load reference table for points data, to show metadata.
        :return:
        '''
        dl = dataLoader(self.cfg)
        return dl.load_ref()

    def loadStack(self):
        '''
        Load image stack from dataloader
        :return:
        '''
        dl = dataLoader(self.cfg)
        
        FUN_start_time = time.time()
        self.stack, self.stack_dates, self.stack_doy, self.stack_prj, self.stack_geotransform = dl.load_stack()
        FUN_end_time = time.time() 
        
        # properties, display shape of stack
        self.stack_shape = '{0} rows {1} columns {2} layers'.format(self.stack.shape[1], self.stack.shape[2], self.stack.shape[0])
        
        if self.log:
            self.logger.info('Stack file ' + self.cfg.stackFn + ' loaded. {}s used.'.format(round(FUN_end_time - FUN_start_time, 4)))
            
    def setMask(self, user_mask):
        '''
        Set up user mask to select points
        :param user_mask: matrix consisting of 0 and 1 whether to use given point.
        :return:
        '''
        if type(user_mask).__name__ != 'ndarray':
            print('convert user_mask into numpy array')
            user_mask = np.array(user_mask)    
        
        if sum(np.unique(user_mask)) != 1:
            raise RuntimeError('only accept mask as matrix containing 1 or 0, \nplease re-prepare your mask')
        
        self.compute_mask = user_mask
    
        if self.log:
            self.logger.info('User compute mask set.')
            
    def runPts(self, OBJECTIDs, 
               plot=True, max_plot=25, 
               showdata='fit', colorbar=True, plot_title=True, **param_dic):
        '''
        run from list of OBJECTIDs and plot the data points.
        :param OBJECTIDs: list of OBJECTID's to show or [9999] to show all OBJECTID's
        :param plot: boolean, whether to plot or not.
        :param max_plot: maximum number of plots to show
        :param showdata:
        :param colorbar: boolean, whether to show colorbar
        :param plot_title: boolean, whether to show title
        :param param_dic: parameter dictionary for running points, check default dictionary for list of params.
        :return:
        '''
        
        # check to see if pts are loaded 
        if type(self.pts).__name__ == 'NoneType':
            raise RuntimeError('pts not loaded yet')
        
        default_param_dic = copy.deepcopy(self.cfg.param_nita)
        user_vi = self.cfg.user_vi
        compute_mask = True
        
        if param_dic is not None:       
            keys = param_dic.keys()
            wrong_names = [key for key in keys if not key in default_param_dic.keys()]
            
            if len(wrong_names) == 0:
                for key, value in param_dic.items():
                    default_param_dic[key] = value
                    print(key)
            else:
                raise RuntimeError('ERROR: Wrong parameter name!')
        
        if OBJECTIDs == [9999]:
            OBJECTIDs = list(set(self.pts['OBJECTID']))
        
#        OBJECTIDs = OBJECTIDs[0:max_plot]
        OBJECTIDs = OBJECTIDs[0:]
        
        subplots_ncol = int(min(np.ceil(np.sqrt(len(OBJECTIDs))),5))
        subplots_nrow = int(min(np.ceil(len(OBJECTIDs)/subplots_ncol),5))
        
        if plot:
            fig, ax = plt.subplots(nrows=subplots_nrow, ncols=subplots_ncol)
            ax = np.array(ax)
            plt.tight_layout()

        
        for OBJECTID in OBJECTIDs:
            
            i = OBJECTIDs.index(OBJECTID)
              
            pt_OBJECTID = copy.deepcopy(self.pts.loc[self.pts['OBJECTID'] == OBJECTID])
            pt_OBJECTID = pt_OBJECTID.sort_values(by=['date_dist'])
            try:
                px = pt_OBJECTID[user_vi].values
            except IndexError:
                raise RuntimeError("Selected user_vi doesn't exist in your data.")
            date_vec = pt_OBJECTID['date_dist'].values
            doy_vec = pt_OBJECTID['doy'].values
            
            if len(px) == 0:
                plt.close()
                raise RuntimeError('in-valid one or more OBJECTID(s)') 
            
            results_dic = nf.nita_px(px, date_vec, doy_vec, 
                                     default_param_dic['value_limits'], default_param_dic['doy_limits'], default_param_dic['date_limits'],
                                     default_param_dic['bail_thresh'], default_param_dic['noise_thresh'],
                                     default_param_dic['penalty'], default_param_dic['filt_dist'], default_param_dic['pct'], default_param_dic['max_complex'], default_param_dic['min_complex'],
                                     compute_mask, default_param_dic['filter_opt'])

            if plot:
                if plot_title:
                    info_line = self.ref_pts.loc[self.ref_pts['OBJECTID'] == OBJECTID]
                    title = ''.join([str(item)+' ' for item in list(info_line.values.flatten())])
                else:
                    title = ''
                    
                nf.viewNITA(px, date_vec, doy_vec, results_dic, showdata=showdata, colorbar=colorbar, title = title, fig=fig, ax=ax.flatten()[i])               
        if plot:
            plt.show()
        if self.log:
            self.logger.info('runPts start...')
            self.logger.info('OBJECTIDs run: ' + str(OBJECTIDs))
            if len(param_dic) != 0:
                self.logger.info('Updated parameters used')
            else:
                self.logger.info('Parameters in ini file used')
            for k, v in default_param_dic.items():
                self.logger.info(k + ': ' + str(v))
            self.logger.info('runPts end...')
            
        if len(OBJECTIDs) == 1:
            return results_dic  

    def runStack(self, parallel=True, workers=2, use_opm_param=False):
        '''
        Run full image stack or subset image stack, if subset is selected via GUI, and sets the computed results,
        as attribute of nita object.
        :param parallel: boolean, whether to run stack in parallel.
        :param workers: number of workers to use if parallel.
        :param use_opm_param: boolean. whether to use optimal parameters
        :return: None
        '''
        if use_opm_param:
            try:
                len(self.the_paramcombo)
            except:
                raise RuntimeError('ERROR: paramOpm not run yet!')    
        
        # ---
        # 1.
        # initialize log if wanted
        if self.log:
            self.logger.info('Project Name : {}'.format(self.cfg.ProjectName))
            self.logger.info('Output Folder: {}'.format(self.cfg.OutputFolder))
            self.logger.info('Point Data: {}'.format(self.cfg.ptsFn))
            self.logger.info('Stack Date Data: {}'.format(self.cfg.stackdateFn))
            self.logger.info('Stack Data: {}'.format(self.cfg.stackFn))
            self.logger.info('runStack start...')
            if parallel:
                self.logger.info('Parallelization enabled with {} workers'.format(workers))
            else:
                self.logger.info('No-Parallelization enabled')
            FUN_start_time = time.time()
            self.logger.info('Stack start time: {}'.format(time.asctime(time.localtime(FUN_start_time))))
            self.logger.info('Parameters in ini file used')
        
        # ---
        # 2.
        # check if the stack is loaded  
        if type(self.stack).__name__ == 'NoneType':
            raise RuntimeError('stack not loaded yet')
        
        # ---
        # 3. 
        # check if the mask exists
        # if non-existence (setMask() method never called), assign 'global' compute_mask as True (for each pixel in the stack)
        # if set, check dimension 
        if type(self.compute_mask).__name__ != 'ndarray':
            compute_mask = np.ones(self.stack.shape[1:3])
        else:
            compute_mask = self.compute_mask
            if compute_mask.shape != self.stack.shape[1:3]:
                raise RuntimeError('ERROR: user_mask dimensions does not match stack dimensions! \nUse setMask() to reset')
        
        # ---
        # 4.         
        # reduce dimension and generate reference vectors 
        # the read-in image stack is t-n-m so reduce to t-(n*m)
        #                            | | |              |   |
        #                            a b c              a   d
        # along (d), the (b) would become b1, b1, b1,..., b2, b2, b2......, bn, bn, bn,.....
        # while c wile become c1, c2, ..., cn, c1, c2, ..., cn, ......, c1, c2, ..., cn  
        stack_shape = self.stack.shape # (t, n, m)
        stack_2d = self.stack.reshape((stack_shape[0], stack_shape[1]*stack_shape[2]))
        stack_2d_shape = stack_2d.shape
        #t_vec = np.arange(0, stack_shape[0]) 
        #nm_vec = np.arange(0, stack_2d.shape[1])
        #n_vec = np.floor_divide(nm_vec, stack_shape[2])
        #m_vec = np.mod(nm_vec, stack_shape[2])
        
        # reduce dimension for compute mask 
        compute_mask_1d = compute_mask.flatten()
        
        # ---
        # 5. 
        # 5.a   
        if use_opm_param:
            param_dic = copy.deepcopy(self.cfg.the_paramcombo)
        else:
            param_dic = copy.deepcopy(self.cfg.param_nita)    
                       
        if parallel:
            # For running data in parallel, each point in the stack can be run individually,
            # and so for each worker thread it takes in a chunk of chunksize (1000) points for a single run.
            # after it finishes one chunk, another chunk is provided to the thread.
            # This makes sure no redundant copies of data are made during each iteration.
            # pack other arguments into a dic
            param_dic['date_vec'] = self.stack_dates
            param_dic['doy_vec'] = self.stack_doy
        
            iterable = [(stack_2d[:, i], compute_mask_1d[i], param_dic, i) for i in range(stack_2d_shape[1])]
        
            pool = Pool(workers)
            results_dics_1d = []
            max_len = len(iterable)
            for iter in tqdm(pool.imap(nf.nita_stack_tuple_wrapper, iterable, chunksize=1000), total = max_len):
                results_dics_1d.append(iter)
            pool.close()
            pool.join()
        
        # ---
        # 5.b
        if not parallel:
            
             date_vec = self.stack_dates   
             doy_vec = self.stack_doy
             
             results_dics_1d = []
             for i in tqdm(range(stack_2d_shape[1])):
                 compute_mask_run = compute_mask_1d[i]
                 compute_mask_run = compute_mask_run == 1
                    
                 px = stack_2d[:, i]
                    
                 results_dic = nf.nita_px(px, date_vec, doy_vec, 
                                          param_dic['value_limits'], param_dic['doy_limits'], param_dic['date_limits'],
                                          param_dic['bail_thresh'], param_dic['noise_thresh'],
                                          param_dic['penalty'], param_dic['filt_dist'], param_dic['pct'], param_dic['max_complex'], param_dic['min_complex'],
                                          compute_mask_run, param_dic['filter_opt'])
                 
                 results_dics_1d.append(results_dic)
            
        # ---
        # 6. 
        self.stack_results = results_dics_1d
        
        if self.log:
            FUN_end_time = time.time()
            self.logger.info('Stack end time: {}'.format(time.asctime(time.localtime(FUN_end_time))))
            self.logger.info('Stack running time (seconds): {}'.format(FUN_end_time - FUN_start_time))

    def getPixelResults(self, xy_pair):
        '''
        Retrieves results_dictionary for given x,y point if stack is computed else
        raises error
        :param xy_pair: (x, y) pixel, whose results to retrieve.
        :return: dict, results dictionary.
        '''
        # check if self.stack_results exists 
        try:
            type(self.stack_results)
        except AttributeError:
            raise RuntimeError('stack results not calculated yet!')        

        n = xy_pair[1]
        m = xy_pair[0]
        
        stack_shape = self.stack.shape # (t, n, m)
        nm_vec = np.arange(0,  stack_shape[1]*stack_shape[2])
        n_vec = np.floor_divide(nm_vec, stack_shape[2])
        m_vec = np.mod(nm_vec, stack_shape[2])
        
        pixel_idx = int(nm_vec[(n_vec == n) & (m_vec == m)])
        
        results_dic = self.stack_results[pixel_idx]

        return results_dic 
    
    def runPixel(self, xy_pair, 
                 use_compute_mask=False, 
                 plot=True, showdata='fit', colorbar=True, 
                 **nita_parameters):
        '''
        Run a single pixel from the stack, present in (x,y) pair.
        :param xy_pair: (x, y) pixel, whose results to retrieve.
        :param use_compute_mask: boolean, whether to use compute mask for the data
        :param plot: boolean, whether to plot the data point from given pixel
        :param showdata:
        :param colorbar: boolean, show color bar or not
        :param nita_parameters: list of parameter dictionary configuration to use for running a single nita point.
        :return:
        '''
        # get n and m 
        n = xy_pair[1]
        m = xy_pair[0]
        
        # get the compute mask value 
        if use_compute_mask:
            if type(self.compute_mask).__name__ != 'ndarray':
                compute_mask = True
            else:
                compute_mask_mat = self.compute_mask
                if compute_mask_mat.shape != self.stack.shape[1:3]:
                    raise RuntimeError('ERROR: user_mask dimensions does not match stack dimensions! \nUse setMask() to reset')
                else:
                    compute_mask = compute_mask_mat[n, m]
        else:
            compute_mask = True         

        # get the nita parameters
        param_dic = copy.deepcopy(self.cfg.param_nita)     
        
        if len(nita_parameters) != 0:       
            keys = nita_parameters.keys()
            wrong_names = [key for key in keys if not key in param_dic.keys()]
            
            if len(wrong_names) == 0:
                for key, value in nita_parameters.items():
                    param_dic[key] = value
            else:
                raise RuntimeError('ERROR: Wrong parameter name!')
                   
        # get data and run 
        date_vec = self.stack_dates   
        doy_vec = self.stack_doy
        px = self.stack[:, n, m]
        
        results_dic = nf.nita_px(px, date_vec, doy_vec, 
                                 param_dic['value_limits'], param_dic['doy_limits'], param_dic['date_limits'],
                                 param_dic['bail_thresh'], param_dic['noise_thresh'],
                                 param_dic['penalty'], param_dic['filt_dist'], param_dic['pct'], param_dic['max_complex'], param_dic['min_complex'],
                                 compute_mask, param_dic['filter_opt'])
        
        if plot:
            nf.viewNITA(px, date_vec, doy_vec, results_dic, showdata=showdata, colorbar=colorbar)
        
        if self.log:
            self.logger.info('runPixel start...')
            self.logger.info('Pixel location: x = {0}, y = {1}'.format(xy_pair[0], xy_pair[1]))
            if len(nita_parameters) != 0:
                self.logger.info('Updated parameters used')
            else:
                self.logger.info('Parameters in ini file used')
            for k, v in param_dic.items():
                self.logger.info(k + ': ' + str(v))
            self.logger.info('runPixel end...')
        
        return results_dic    
    
    def computeStackMetrics(self, parallel=True, workers=2):
        
        # check if self.stack_results exists 
        try:
            type(self.stack_results)
        except AttributeError:
            raise RuntimeError('stack results not calculated yet!')
        
        if self.log:
            self.logger.info('computeStackMetrics start...')
            if parallel:
                self.logger.info('Parallelization enabled with {} workers'.format(workers))
            else:
                self.logger.info('No-Parallelization enabled')
            FUN_start_time = time.time()
            self.logger.info('computeStackMetrics start time: {}'.format(time.asctime(time.localtime(FUN_start_time))))
            self.logger.info('Parameters in ini file used')        
        
        if parallel:
            
            iterable = [(results_dic, self.cfg.param_metric['vi_change_thresh'], self.cfg.param_metric['run_thresh'], self.cfg.param_metric['time_step']) for results_dic in self.stack_results]
            pool = Pool(workers)
            max_len = len(iterable)
            metrics_dics_1d = []
            for iter in tqdm(pool.imap(mf.computMetrics_wrapper, iterable, chunksize=3000), total=max_len):
                metrics_dics_1d.append(iter)
                # print("\rCompleted running stack {:.2f}%".format(i*100/max_len))
            pool.close()
            pool.join()
        
        if not parallel: 
            metrics_dics_1d = []
            for results_dic in self.stack_results:
                metrics_dic = mf.computeMetrics(results_dic, self.cfg.param_metric['vi_change_thresh'], self.cfg.param_metric['run_thresh'], self.cfg.param_metric['time_step'])
                metrics_dics_1d.append(metrics_dic)
        
        self.stack_metrics = metrics_dics_1d

        if self.log:
            FUN_end_time = time.time()
            self.logger.info('computeStackMetrics end time: {}'.format(time.asctime(time.localtime(FUN_end_time))))
            self.logger.info('computeStackMetrics running time (seconds): {}'.format(FUN_end_time - FUN_start_time))

    def getPixelMetrics(self, xy_pair):
        
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')        

        n = xy_pair[1]
        m = xy_pair[0]
        
        stack_shape = self.stack.shape # (t, n, m)
        nm_vec = np.arange(0,  stack_shape[1]*stack_shape[2])
        n_vec = np.floor_divide(nm_vec, stack_shape[2])
        m_vec = np.mod(nm_vec, stack_shape[2])
        
        pixel_idx = int(nm_vec[(n_vec == n) & (m_vec == m)])
        
        metrics_dic = self.stack_metrics[pixel_idx]

        return metrics_dic 
    
    def computeMetrics(self, results_dic, **metric_parameters):
        
        param_dic = copy.deepcopy(self.cfg.param_metric)
        
        if len(metric_parameters) != 0:       
            keys = metric_parameters.keys()
            wrong_names = [key for key in keys if not key in param_dic.keys()]
            
            if len(wrong_names) == 0:
                for key, value in metric_parameters.items():
                    param_dic[key] = value
            else:
                raise RuntimeError('ERROR: Wrong parameter name!')

        metrics_dic = mf.computeMetrics(results_dic, param_dic['vi_change_thresh'], param_dic['run_thresh'], param_dic['time_step'])
     
        if self.log:
            self.logger.info('computeMetrics start...')
            if len(metric_parameters) != 0:
                self.logger.info('Updated parameters used')
            else:
                self.logger.info('Parameters in ini file used')
            for k, v in param_dic.items():
                self.logger.info(k + ': ' + str(v))
            self.logger.info('computeMetrics end...')
            
        return metrics_dic
    
    def MI_complexity(self, plot=True, save=True, fn='complexity.tif', title = 'title', label='label'):
        
        # check if self.stack_results exists 
        try:
            type(self.stack_results)
        except AttributeError:
            raise RuntimeError('stack results not calculated yet!')
        
        vals_1d = mf.MI_complexity(self.stack_results)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)
        
        if self.log:
            self.logger.info('Metrics image - complexity. Filename: {0}. Saved: {1}'.format(fn, str(save)))
    
    def MI_distDate(self, option='middle', plot=True, save=True, fn='distdate.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_distDate(self.stack_metrics, option=option)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)               
        if self.log:
            self.logger.info('Metrics image - distrubance date. Filename: {0}. Saved: {1}'.format(fn, str(save)))
     
    def MI_distDuration(self, plot=True, save=True, fn='distduration.tif', title = 'title', label='label'):

        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_distDuration(self.stack_metrics)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)           

        if self.log:
            self.logger.info('Metrics image - distrubance duration. Filename: {0}. Saved: {1}'.format(fn, str(save)))
     
    def MI_distMag(self, plot=True, save=True, fn='distMag.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_distMag(self.stack_metrics)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)

        if self.log:
            self.logger.info('Metrics image - disturbance magnitude. Filename: {0}. Saved: {1}'.format(fn, str(save)))
    
    def MI_distSlope(self, plot=True, save=True, fn='distSlope.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_distSlope(self.stack_metrics)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)

        if self.log:
            self.logger.info('Metrics image - disturbance slope. Filename: {0}. Saved: {1}'.format(fn, str(save)))

    def MI_linearError(self, plot=True, save=True, fn='linerror.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_results)
        except AttributeError:
            raise RuntimeError('stack results not calculated yet!')
            
        vals_1d = mf.MI_linearError(self.stack_results)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)

        if self.log:
            self.logger.info('Metrics image - linear error. Filename: {0}. Saved: {1}'.format(fn, str(save)))

    def MI_noise(self, plot=True, save=True, fn='noise.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_results)
        except AttributeError:
            raise RuntimeError('stack results not calculated yet!')
            
        vals_1d = mf.MI_noise(self.stack_results)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)

        if self.log:
            self.logger.info('Metrics image - noise. Filename: {0}. Saved: {1}'.format(fn, str(save)))

    def MI_bailcut(self, plot=True, save=True, fn='bailcut.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_results)
        except AttributeError:
            raise RuntimeError('stack results not calculated yet!')
            
        vals_1d = mf.MI_bailcut(self.stack_results)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)     

        if self.log:
            self.logger.info('Metrics image - bailcut. Filename: {0}. Saved: {1}'.format(fn, str(save)))

    def MI_postDistSlope(self, plot=True, save=True, fn='postdistslope.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_postDistSlope(self.stack_metrics)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)
    
        if self.log:
            self.logger.info('Metrics image - post disturbance slope. Filename: {0}. Saved: {1}'.format(fn, str(save)))    

    def MI_postDistMag(self, plot=True, save=True, fn='postdistmag.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_postDistMag(self.stack_metrics)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)

        if self.log:
            self.logger.info('Metrics image - post disturbance magnitude. Filename: {0}. Saved: {1}'.format(fn, str(save)))
            
    def MI_head(self, plot=True, save=True, fn='head.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_results)
        except AttributeError:
            raise RuntimeError('stack results not calculated yet!')
            
        vals_1d = mf.MI_head(self.stack_results)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)    

        if self.log:
            self.logger.info('Metrics image - head. Filename: {0}. Saved: {1}'.format(fn, str(save)))

    def MI_tail(self, plot=True, save=True, fn='tail.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_results)
        except AttributeError:
            raise RuntimeError('stack results not calculated yet!')
            
        vals_1d = mf.MI_tail(self.stack_results)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)                
        if self.log:
            self.logger.info('Metrics image - tail. Filename: {0}. Saved: {1}'.format(fn, str(save)))            

    def MI_dateValue(self, value_date, plot=True, save=True, fn='datevalue.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_dateValue(self.stack_metrics, value_date)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)                

        if self.log:
            self.logger.info('Metrics image - date value. Filename: {0}. Saved: {1}'.format(fn, str(save)))
             
    def MI_valueChange(self, start_date=-9999, end_date=9999, option='diff', 
                       plot=True, save=True, fn='valuechange.tif', title = 'title', label='label'):
        
        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_valueChange(self.stack_metrics, start_date = start_date, end_date = end_date, option=option)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)                

        if self.log:
            self.logger.info('Metrics image - value change. Filename: {0}. Saved: {1}'.format(fn, str(save)))
     
    def MI_recovery(self, time_passed, option='diff', plot=True, save=True, fn='recovery.tif', title = 'title', label='label'):

        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_recovery(self.stack_metrics,time_passed, option=option)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)               
  
        if self.log:
            self.logger.info('Metrics image - recovery. Filename: {0}. Saved: {1}'.format(fn, str(save)))

    def MI_recoveryCmp(self, time_passed, plot=True, save=True, fn='recovery.tif', title = 'title', label='label'):

        # check if self.stack_metrics exists 
        try:
            type(self.stack_metrics)
        except AttributeError:
            raise RuntimeError('stack metrics not calculated yet!')
            
        vals_1d = mf.MI_recoveryCmp(self.stack_metrics,time_passed)
        stack_shape = self.stack.shape
        vals_2d = vals_1d.reshape(stack_shape[1:3])
        vals_2d_adj = mf.stretchMI(vals_2d)
        
        if plot: 
            mf.plotMI(vals_2d_adj, title, label)
        
        if save:
            dw.saveMI(vals_2d, self.stack_prj, self.stack_geotransform,
                      self.cfg.OutputFolder, fn)        
           
        if self.log:
            self.logger.info('Metrics image - recovery comparison. Filename: {0}. Saved: {1}'.format(fn, str(save)))            
            
    def setOpmParams(self, **param_dic):
        '''
        Forms an exhaustive list of possible parameter configurations, from given parameter dictionary list
        for selecting optimal parameters.
        :param param_dic: parameter dictionary object which consists of list of configuration for a given type of
                          parameter, as a key value pair.
        :return:
        '''
        default_param_dic = copy.deepcopy(self.cfg.param_opm_set)
        default_param_dic['value_limits'] = [self.cfg.param_nita['value_limits']]
        default_param_dic['doy_limits'] = [self.cfg.param_nita['doy_limits']]
        default_param_dic['date_limits'] = [self.cfg.param_nita['date_limits']]
        
        keys = param_dic.keys() 
        if param_dic is not None:                   
            wrong_names = [key for key in keys if not key in default_param_dic.keys()]
            
            if len(wrong_names) == 0:
                for key, value in param_dic.items():
                    default_param_dic[key] = value
            else:
                raise RuntimeError('ERROR: Wrong parameter name!')
        
        # yes I know this is stupid
        param_combos = []
        for bail_thresh in default_param_dic['bail_thresh_set']:
            for date_limits in default_param_dic['date_limits']:
                for doy_limits in default_param_dic['doy_limits']:
                    for filt_dist in default_param_dic['filt_dist_set']:
                        for filter_opt in default_param_dic['filter_opt_set']:
                            for max_complex in default_param_dic['max_complex_set']:
                                for min_complex in default_param_dic['min_complex_set']:
                                    for noise_thresh in default_param_dic['noise_thresh_set']:
                                        for pct in default_param_dic['pct_set']:
                                            for penalty in default_param_dic['penalty_set']:
                                                for value_limits in default_param_dic['value_limits']:
                                                    param_dic_run = {'bail_thresh': bail_thresh,
                                                                     'date_limits': date_limits,
                                                                     'doy_limits': doy_limits,
                                                                     'filt_dist': filt_dist,
                                                                     'filter_opt': filter_opt,
                                                                     'max_complex': max_complex,
                                                                     'min_complex': min_complex,
                                                                     'noise_thresh': noise_thresh,
                                                                     'pct': pct, 
                                                                     'penalty': penalty,
                                                                     'value_limits': value_limits}
                                                    param_combos.append(param_dic_run)
            
        self.opm_params = default_param_dic
        self.opm_paramcombos = param_combos 
        
        if self.log:
            self.logger.info('Set optimization parameters.')
            for k, v in default_param_dic.items():
                self.logger.info(k + ': ' + str(v))
        
    def drawPts(self, OBJECTIDs, plot_title=True):
        '''
        Draw trajectories for given OBJECTIDs from the users, shows the plots for given object ID's and prompts
        user to draw trajectories.
        :param OBJECTIDs: list of OBJECTIDs
        :param plot_title: boolean, whether to plot title
        :return:
        '''
        # check to see if pts are loaded
        try:
            type(self.pts)
        except AttributeError:
            raise RuntimeError('ERROR: pts not loaded yet')

#        if self.log:
#            self.logger.info('drawPts start...')
    
        user_vi = self.cfg.user_vi
        doy_limits = self.cfg.param_nita['doy_limits']
        value_limits = self.cfg.param_nita['value_limits']
        date_limits = self.cfg.param_nita['date_limits']
        
        if OBJECTIDs == [9999]:
            OBJECTIDs = list(set(self.pts['OBJECTID']))
        
        OBJECTIDs = OBJECTIDs[0:25]
        
        handdraw_trajs = []
        for OBJECTID in OBJECTIDs:
            
            fig, ax = plt.subplots()
            try:
                plot_y = self.pts.loc[self.pts['OBJECTID'] == OBJECTID][user_vi].values
            except IndexError:
                raise RuntimeError("Selected user_vi doesn't exist in the data.")
            try:
                plot_x = self.pts.loc[self.pts['OBJECTID'] == OBJECTID]['date_dist'].values
            except IndexError:
                raise RuntimeError("Selected date_dist values are invalid.")
            try:
                plot_doy = self.pts.loc[self.pts['OBJECTID'] == OBJECTID]['doy'].values
            except IndexError:
                raise RuntimeError("Selected doy values are invalid.")
            if plot_title:
                info_line = self.ref_pts.loc[self.ref_pts['OBJECTID'] == OBJECTID]
                title = ''.join([str(item)+' ' for item in list(info_line.values.flatten())])
            else:
                title = ''
                
            plot_x, plot_y, plot_doy = nf.filterLimits(plot_x, plot_y, plot_doy, value_limits, date_limits, doy_limits)

            doy_limit =  doy_limits[0]
            mappable = ax.scatter(plot_x, plot_y, c=plot_doy, vmin=doy_limit[0], vmax=doy_limit[1])
            ax.set_xlim([plot_x.min(), plot_x.max()])
            ax.set_ylim([plot_y.min(), plot_y.max()])
            ax.set_title(title)
            plt.ylabel('VI Units')
            #
            xticks_lables = ax.get_xticks().tolist()
            xticks_lables = [str(xticks_label)[0:4] for xticks_label in xticks_lables]
            ax.set_xticklabels(xticks_lables)
            #
            fig.colorbar(mappable, label = 'Day of year')
            ginput_res = plt.ginput(n=-1, timeout=0)
            handdraw_traj = {'OBJECTID': OBJECTID,
                             'traj': ginput_res}
            handdraw_trajs.append(handdraw_traj)
        
        self.handdraw_trajs = handdraw_trajs
        
        plt.close('all')
      
        if self.log:
            self.logger.info('total {} OBJECTIDs drew: ' + str(OBJECTIDs).format(len(OBJECTIDs)))
            self.logger.info('drawPts end...')
            
    def paramOpm(self, parallel=True, workers=2):
        '''
        Find optimal parameter configuration among list of configurations. Can be run in parallel, where number of
        workers should be set to max number of parallel threads to be run.
        :param parallel: boolean, whether to use multiple workers
        :param workers: int, number of parallel threads to run
        :return: dict, best combination of parameters among possible parameter configurations entered via configobj.
        '''
        # check to see if opm_paramcombos 
        try:
            type(self.opm_paramcombos)
        except AttributeError:
            raise RuntimeError('ERROR: opm param combo not set, use setOpmParams()') 

        # check 
        try:
            type(self.handdraw_trajs)
        except AttributeError:
            raise RuntimeError('ERROR: handdraw_trajs not set, use drawPts()')
        
        if self.log:
            self.logger.info('paramOpt...')
            FUN_start_time = time.time()
            self.logger.info('paramOpt start time: {}'.format(time.asctime(time.localtime(FUN_start_time))))
            
        
        OBJECTIDs = [dic['OBJECTID'] for dic in self.handdraw_trajs]
        user_vi = self.cfg.user_vi
        compute_mask=True
        
        if not parallel: 
        
            paramcombo_rmse_mean = []
            paramcombo_rmse_median = []
            paramcombo_pct95err_mean = []
            for param_combo in self.opm_paramcombos:
                OBJETID_rmse = []
                OBJECTID_pct95_err = []
                for OBJECTID in OBJECTIDs:
                    
                    handdraw_traj = [dic['traj'] for dic in self.handdraw_trajs if dic['OBJECTID'] == OBJECTID][0]
                    
                    pt_OBJECTID = copy.deepcopy(self.pts.loc[self.pts['OBJECTID'] == OBJECTID])
                    pt_OBJECTID = pt_OBJECTID.sort_values(by=['date_dist'])
                    try:
                        px = pt_OBJECTID[user_vi].values
                    except IndexError:
                        raise RuntimeError("Selected user_vi doesn't exist in the data.")
                    try:
                        date_vec = pt_OBJECTID['date_dist'].values
                    except IndexError:
                        raise RuntimeError("Selected date_dist values are invalid.")
                    try:
                        doy_vec = pt_OBJECTID['doy'].values
                    except IndexError:
                        raise RuntimeError("Selected doy_vec values are invalid.")
                    if len(px) == 0:
                        raise RuntimeError('in-valid one or more OBJECTID(s)') 
                
                    results_dic = nf.nita_px(px, date_vec, doy_vec, 
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
                
                paramcombo_rmse_mean.append(np.mean(OBJETID_rmse))
                paramcombo_rmse_median.append(np.median(OBJETID_rmse))
                paramcombo_pct95err_mean.append(np.mean(OBJETID_rmse))
                
        if parallel:            
            iterable = [(param_combo, OBJECTIDs, self.handdraw_trajs, self.pts, user_vi, compute_mask) for param_combo in self.opm_paramcombos]
            pool = Pool(workers)
            param_opm_res = []
            for iter in tqdm(pool.imap(nf.paramcomboCmp_wrapper, iterable, chunksize=3000), total=len(iterable)):
                param_opm_res.append(iter)
            # param_opm_res = pool.starmap(nf.paramcomboCmp, iterable)
            pool.close()
            pool.join()
            paramcombo_rmse_mean = [item[0] for item in param_opm_res]
            paramcombo_rmse_median = [item[1] for item in param_opm_res]
            paramcombo_pct95err_mean = [item[2] for item in param_opm_res] 
            
        paramcombo_rmse_mean = np.array(paramcombo_rmse_mean)
        paramcombo_rmse_median = np.array(paramcombo_rmse_median)
        paramcombo_pct95err_mean = np.array(paramcombo_pct95err_mean)
            
        # save as att in case
        self.paramcombo_rmse_mean = paramcombo_rmse_mean
        self.paramcombo_rmse_median = paramcombo_rmse_median
        self.paramcombo_pct95err_mean = paramcombo_pct95err_mean

        best_paramcombo = self.opm_paramcombos[paramcombo_pct95err_mean.argmin()]
        self.the_paramcombo = best_paramcombo
               
        if self.log:
            FUN_end_time = time.time()
            self.logger.info('paramOpm end time: {}'.format(time.asctime(time.localtime(FUN_end_time))))
            self.logger.info('paramOpm running time (seconds): {}'.format(FUN_end_time - FUN_start_time))
            self.logger.info('The best parameter combo: ')
            for k, v in self.the_paramcombo.items():
                self.logger.info(k + ': ' + str(v))
				
#        for k, v in self.the_paramcombo.items():
#            print(k + ': ' + str(v))
            
        return best_paramcombo

    def subsetStack(self, tuple_pts):
        '''
        Subset the provided stack in the given range of tuple.
        :param tuple_pts: (x1, y1), (x2, y2) as top left and bottom right of stack to subset the stack.
        :return:
        '''
        x1, y1, x2, y2 = tuple_pts
        self.stack = self.stack[:, y1:y2, x1:x2]
        self.stack_shape = self.stack.shape


    def leastCloudy(self, title):
        '''
        View the least cloudy image in the stack.
        :param title: title string to show for the plot.
        :return:
        '''
        stack_shape = self.stack.shape
        image_size_xy = stack_shape[1]*stack_shape[2]
        good_px_percent = [None]*stack_shape[0]

        for i in range(stack_shape[0]):
            good_px_count = np.sum(self.stack[i, :, :] > 0)
            good_px_percent[i] = good_px_count/image_size_xy

        best_index = np.argmax(good_px_percent)
        plt.imshow(self.stack[best_index, :, :])
        # plt.matshow(self.stack[best_index, :, :], fignum=title, extent=[0, stack_shape[2], stack_shape[1], 0])
        plt.suptitle(title)
        plt.tight_layout(rect=[0, 0.15, 1, 0.95])


    def addLog(self, message=''):
        if self.log:
            self.logger.info(message)
        else:
            raise RuntimeError('ERROR: log not started. Use startLog to start.')
