"""
Module to load input data files
Created on Jun 5, 2018
@author: Leyang Feng
@email: feng@american.edu
@Project: pynita
License:  
Copyright (c) 
"""

import pandas as pd
import numpy as np
from osgeo import gdal
from pynita_source.utils import general 


class dataLoader:
    """The DataLoader class 
    """
    def __init__(self, cfg):
        """
        Args:
            cfg (ConfigReader class): 
        """
        self.ptsFn = cfg.ptsFn
        self.stackFn = cfg.stackFn
        self.stackdateFn = cfg.stackdateFn
        self.user_vi = cfg.user_vi.lower()
    
    def load_pts(self, info_column='none', full_table=False):
        col_names_default = ['system:index', 'OBJECTID', 'pixel_qa']
        col_names_rest = ['blue', 'green', 'nir', 'red', 'swir1', 'swir2']
        
        if full_table:
            col_names = col_names_default + col_names_rest 
        else:
            col_names = col_names_default
        
        if info_column != 'none':
            col_names.append(info_column)
        
        col_names.append(self.user_vi)        
        
        pts_path = self.ptsFn
        pts_tb_raw = pd.read_csv(pts_path)
     
        pts_tb = pts_tb_raw[col_names]
  
        sis = list(pts_tb['system:index']) # system_index_s       
        all_info = [general.SystemIndexBreaker(si) for si in sis]  
        
        pts_tb = pts_tb.assign(sensor=[item[0] for item in all_info])
        pts_tb = pts_tb.assign(pathrow=[item[1] for item in all_info])
        pts_tb = pts_tb.assign(date=[item[2] for item in all_info])
        pts_tb = pts_tb.assign(doy=[item[3] for item in all_info])
        pts_tb = pts_tb.assign(date_dist=[item[4] for item in all_info])
        pts_tb = pts_tb.drop(columns=['system:index'])

        # generate a reference table only contains ONJECTID and info_column (if provided)
        if info_column != 'none':
            self.ref_tb = pts_tb[['OBJECTID', info_column]].drop_duplicates()
        else:
            self.ref_tb = pts_tb['OBJECTID'].drop_duplicates()

        return pts_tb

    def load_stack(self): 
        stack_path = self.stackFn
        stackdate_path = self.stackdateFn
        
        # deal with stackdate first
        stackdate_tb = pd.read_csv(stackdate_path)
        sis = list(stackdate_tb['system:index']) # system_index_s       
        all_info = [general.SystemIndexBreaker(si) for si in sis]  
        doy_vec = np.array([item[3] for item in all_info])
        date_vec = np.array([item[4] for item in all_info]) # in distributed date 
        
        # then deal with stack 
        fc = gdal.Open(stack_path)
        stack = fc.ReadAsArray() # t-x-y
        prj = fc.GetProjection()
        geotransform = fc.GetGeoTransform()
        fc = None

        return stack, date_vec, doy_vec, prj, geotransform
