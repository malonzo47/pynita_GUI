"""
say something
Created on Jun 5, 2018
@author: Leyang Feng
@email: feng@american.edu
@Project: pynita
License:  
Copyright (c) 
"""
import datetime 

def SystemIndexBreaker(system_index_str):
    
    # A few words to myself: 
    # The str is constructed as x..._x_Lxxx_pathrow_yyyymmdd_xxx..._xxx
    # First attempt was accessing desired parts by index after splitting 
    # But, the number of parts before 'Lxxx' and after 'yyyymmdd' can vary 
    # So, the approch is to identify the location of letter 'L' (assumming
    # letter 'L' only ocurr once in the str) then use substring method. 
    
    L_index = system_index_str.find('L') 
    
    sensor = system_index_str[L_index : L_index + 4]
    pathrow = system_index_str[L_index + 5 : L_index + 11]
    yyyymmdd = system_index_str[L_index + 12 : L_index + 20]
    yyyy = yyyymmdd[0:4]
    #mm = yyyymmdd[4:6]
    #dd = yyyymmdd[6:8]
    
    dt = datetime.datetime.strptime(yyyymmdd,'%Y%m%d')
    doy = dt.timetuple().tm_yday
    date_dist = int(yyyy) * 1000 + round(1000 * doy/365)
    
    return sensor, pathrow, yyyymmdd, doy, date_dist
