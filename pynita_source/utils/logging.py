"""
This is the class to define logging process:
print command will write to screen and a logging file
Created on Jun 5, 2018
@author: Leyang Feng
@email: feng@american.edu
@Project: pynita
License:  
Copyright (c) 
"""
import logging
import os 

def setupLogger(cfg):
    
    # log file path 
    log_file = os.path.join(cfg.OutputFolder, 'logfile.log')
    # configure log formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # configure file handler
    file_log_handler = logging.FileHandler(log_file)
    file_log_handler.setFormatter(formatter)

    # configure stream handler
    console_log_handler = logging.StreamHandler()
    console_log_handler.setFormatter(formatter)

    # get the logger instance
    logger = logging.getLogger(__name__)

    # set the logging level
    logger.setLevel(logging.INFO)

    # add handlers
    logger.addHandler(file_log_handler)
    logger.addHandler(console_log_handler)

    return logger
        
def closeLogger(logger):
    for handler in logger.handlers:
        handler.close()
