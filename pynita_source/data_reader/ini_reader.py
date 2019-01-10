"""
Read in settings from configuration file *.ini
Created on Jun 4, 2018
@author: Leyang Feng
@email: feng@american.edu
@Project: pynita
License:  
Copyright (c) 
"""

import os
from configobj import ConfigObj

class ConfigReader:

    def __init__(self, ini):

        c = ConfigObj(ini)

        p = c['Project']

        # project dirs
        self.root = p['RootDir']
        self.ProjectName = p['ProjectName']
        self.ptsFn = p['ptsFn']
        self.stackdateFn = p['stackdateFn']
        self.stackFn = p['stackFn']
        self.OutDir = self.createDir(os.path.join(self.root, p['OutputFolder']))
        self.OutputFolder = self.createDir(os.path.join(self.OutDir, self.ProjectName))

        # see if modules are in config file
        try:
            v = c['VI']
        except KeyError:
            v = False

        try:
            np = c['NITAParameters']
        except KeyError:
            np = False

        try:
            mp = c['MetricsParameters']
        except KeyError:
            mp = False
            
        try:
            po = c['ParameterOpmSet']
        except KeyError:
            po = False

        # module level settings
        # module VI
        if v is not False:
            self.user_vi = v['user_vi'].lower()
            # TODO: add value check in here 
        else:
            raise RuntimeError('ERROR: VI module not found')
        
        # module NITAParameters
        if np is not False: 
            doy_limits = [int(item) for item in np['doy_limits']]
            doy_limits = [doy_limits[i:i+2] for i in range(0, len(doy_limits), 2)]
            self.param_nita = {'value_limits': [float(item) for item in np['value_limits']],
                                'doy_limits': doy_limits,
                                'date_limits': [int(item) for item in np['date_limits']], 
                                'bail_thresh': float(np['bail_thresh']), 
                                'noise_thresh': float(np['noise_thresh']),
                                'penalty': float(np['penalty']),
                                'filt_dist': int(np['filt_dist']),
                                'pct': float(np['pct']),
                                'max_complex': int(np['max_complex']),
                                'min_complex': int(np['min_complex']),
                                'filter_opt': np['filter_opt']}
            # TODO: add value check in here
        else: 
            raise RuntimeError('ERROR: [NITAParameters] module not found')
        
        # module MetricsParameters
        if mp is not False:
            self.param_metric = {'vi_change_thresh': float(mp['vi_change_thresh']),
                                 'run_thresh': int(mp['run_thresh']),
                                 'time_step': float(mp['time_step'])}
            # TODO: add value check in here
        else:
            raise RuntimeError('ERROR: [MetricsParameters] module not found')

        # module ParameterOpmSet
        if po is not False:
            self.param_opm_set = {'bail_thresh_set': [float(item) for item in po['bail_thresh_set']],
                                  'noise_thresh_set': [float(item) for item in po['noise_thresh_set']],
                                  'penalty_set': [float(item) for item in po['penalty_set']],
                                  'filt_dist_set': [int(item) for item in po['filt_dist_set']],
                                  'pct_set': [float(item) for item in po['pct_set']],
                                  'max_complex_set': [int(item) for item in po['max_complex_set']],
                                  'min_complex_set': [int(item) for item in po['min_complex_set']], 
                                  'filter_opt_set': [po['filter_opt_set']]}

            # TODO: add value check in here
        else:
            raise RuntimeError('ERROR: [ParameterOpmSet] module not found')

    def createDir(self, pth):
        """
        Check to see if the target path is exists.
        """
        if os.path.isdir(pth) is False:
            os.mkdir(pth)
        return pth
        