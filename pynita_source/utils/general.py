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

#allows user to enter date in multiple ways
def try_parsing_date(text):
    for fmt in ('%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d', '%Y%m%d', '%m/%d/%Y',
                '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y','%d.%m.%Y'):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

def SystemIndexBreaker(system_index_str):
    #options:
    #1. pass 'sat' identifier parameter into function
    #2. encode a new field in the EE csv output that included a satellite identifier
    #3. parse existing field(s) to find discrete flag <-- let's try this one

    #list of potential landsat identifiers that could be found in system:index field
    landsat_flags = ['LT05','LE07','LC08']
    
    if landsat_flags[0] in system_index_str or \
        landsat_flags[1] in system_index_str or \
        landsat_flags[2] in system_index_str:
        
        # A few words to myself: 
        # The str is constructed as x..._x_Lxxx_pathrow_yyyymmdd_xxx..._xxx
        # First attempt was accessing desired parts by index after splitting 
        # But, the number of parts before 'Lxxx' and after 'yyyymmdd' can vary 
        # So, the approch is to identify the location of letter 'L' (assumming
        # letter 'L' only ocurr once in the str) then use substring method. 
        
        sat_index = system_index_str.find('L') 

        sensor = system_index_str[sat_index : sat_index + 4]
        pathrow = system_index_str[sat_index + 5 : sat_index + 11]
        yyyymmdd = system_index_str[sat_index + 12 : sat_index + 20]
        yyyy = yyyymmdd[0:4]
        #mm = yyyymmdd[4:6]
        #dd = yyyymmdd[6:8]

        dt = datetime.datetime.strptime(yyyymmdd,'%Y%m%d')
        doy = dt.timetuple().tm_yday
        date_dist = int(yyyy) * 1000 + round(1000 * doy/365)
        
    else:
        sensor = 'sentinel2'
        pathrow = system_index_str.split('_')[2]
        yyyymmdd = system_index_str[:8]
        yyyy = yyyymmdd[0:4]
        #mm = yyyymmdd[4:6]
        #dd = yyyymmdd[6:8]
        dt = datetime.datetime.strptime(yyyymmdd,'%Y%m%d')
        doy = dt.timetuple().tm_yday
        date_dist = int(yyyy) * 1000 + round(1000 * doy/365)
            
    return sensor, pathrow, yyyymmdd, doy, date_dist


#this function is called if the user has only loaded a csv with one column
#containing dates (i.e., no system:index)
def ConvertDateCol(yyyymmdd):
    #options:
    #1. pass 'sat' identifier parameter into function
    #2. encode a new field in the EE csv output that included a satellite identifier
    #3. parse existing field(s) to find discrete flag <-- let's try this one
        
        dt = try_parsing_date(yyyymmdd)
        #dt = datetime.datetime.strptime(yyyymmdd,'%Y-%m-%d')
        yyyy = dt.timetuple().tm_year
        doy = dt.timetuple().tm_yday
        date_dist = int(yyyy) * 1000 + round(1000 * doy/365)
  
        return yyyymmdd, doy, date_dist
