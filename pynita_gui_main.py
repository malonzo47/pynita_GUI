#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 11:39:17 2019

@author: Praveen Noojipady
@email: noojipad@american.edu
@Project: pyNITA-GUI
License: MIT
Copyright (c)

"""
import sys
import os
import shutil
import numpy as np
from os.path import expanduser
from configobj import ConfigObj
from matplotlib import pyplot
from matplotlib.widgets import RectangleSelector, Button
#
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
#
from pynita_ui import mainV12, popup3, resource_logos
from pynita_source import *
from pynita_ui.tableV1 import pandasModel
#
import threading

# MyQtApp handles all the GUI elements, and provides controll functionality over all the GUI objects, except for
# matplotlib elements such as plots and buttons present in the plot window.

# nitaObj class encapsulates all the main algorithmic computation and holds the computed data.
# It handles the algorithm and provides main abstraction between GUI and actual data processing.

# nita object (instance of nita class) is a global object, which can be referenced from anywhere. It was probably done
# for persistence of previously computed results, but new NITA object was created whenever nita object was being called,
# since it needed to be updated whenever config was changed. In order to avoid that, nita object once created, only
# refreshes the computed stack, whenever configuration is updated.

# NOTE - NITA object will update and lose previously computed results,
#   upon any change to configuration being saved via the GUI. ##

# Subset parameters are also global context objects , since they need to be modified by both PyQT and matplotlib widgets.
# and I couldn't find a clean method to reference objects to matplotlib widgets.


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # ALlows for actual GUI scaling to occur

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # Enables 4K display rendering


class popWindow(QtWidgets.QMainWindow, popup3.Ui_MainWindow):
    def __init__(self, parent=None):
        '''
        Main popup window used to generate alerts during various parts of user workflow.
        :param parent:
        '''
        super(popWindow,self).__init__()
        self.setupUi(self)
        self.setWindowTitle('pyNITA - Optimization')

class MyQtApp(QtWidgets.QMainWindow, mainV12.Ui_MainWindow):
    def __init__(self, parent=None):
        '''
        Main QT Application class which inherits all the child widgets and attributes present in the GUI.
        Widgets include various tabs, frames, text labels, buttons etc. Allows for GUI control via the
        Model-View-Controller Architecture. Allows for manipulation of GUI objects, however actual rendering of GUI
        takes place in the pynita_UI/mainVxx.py (xx corresponds to version number)
        :param parent: None
        '''
        super(MyQtApp,self).__init__()
        self.setupUi(self)
        self.setWindowTitle('pyNITA - Version 1.0')
        # Sets up display properties, configure various GUI objects to be disabled, and get enabled only
        # when the user workflow is respected, also set-up triggers for enabling of GUI components such as radio buttons
        # etc. following the user workflow and the default global parameters for subsetting of data.
        #
        self.popwin = popWindow(self)
        #
        self.Step1a_lineEdit.textChanged.connect(lambda: self.Step1a_pushButton.setEnabled(True))
        self.Step1a_toolButton.clicked.connect(self.step1a_selectWD)
        self.Step1a_pushButton.clicked.connect(self.step1a_loadWD)
        #
        self.Step1b_lineEdit.textChanged.connect(lambda: self.Step1b_pushButton.setEnabled(True))
        self.Step1b_toolButton.clicked.connect(self.step1b_selectUserConfigFile)
        self.Step1b_pushButton.clicked.connect(self.step1b_loadUserConfigFile)
        self.Step1b_pushButton.released.connect(lambda: self.Step1c_tableWidget.setEnabled(True))
        #
        self.Step1c_tableWidget.cellChanged.connect(lambda: self.Step1c_buttonBox.setEnabled(True))
        self.Step1c_buttonBox.accepted.connect(self.step1c_saveChanges)
        self.Step1c_buttonBox.rejected.connect(self.step1c_restoreDefaults)
        #
        self.Step2a_lineEdit.textChanged.connect(lambda: self.Step2a_pushButton.setEnabled(True))
        self.Step2a_toolButton.clicked.connect(self.step2a_selectPointsFile)
        self.Step2a_pushButton.clicked.connect(self.step2a_loadPointsFile)
        self.Step2a_pushButton.released.connect(lambda: self.objectid_radioButton.setEnabled(True))
        self.Step2a_pushButton.released.connect(lambda: self.Step2opt_metadata.setEnabled(True))
        #
        self.Visualize_radioButton.setChecked(True)
        self.objectid_radioButton.toggled.connect(self.Step2b_lineEdit.setEnabled)
        self.objectid_radioButton.toggled.connect(self.Visualize_radioButton.setEnabled)
        self.objectid_radioButton.toggled.connect(self.DrawTraj_radioButton.setEnabled)
        self.objectid_radioButton.toggled.connect(self.Step2b_pushButton.setEnabled)
        #
        self.Step2opt_metadata.clicked.connect(self.step2opt_showPointMetadata)
        #
        self.Step2b_pushButton.released.connect(lambda: self.Step2c_commandLinkButton.setEnabled(True))
        self.Step2b_pushButton.clicked.connect(self.step2b_plotNITApoints_drawTraj)
        #
        self.Step2c_commandLinkButton.released.connect(lambda: self.Step2c_tableWidget.setEnabled(True))
        self.Step2c_commandLinkButton.released.connect(lambda: self.Step2d_radioButton.setEnabled(True))
        self.Step2c_tableWidget.cellChanged.connect(lambda: self.Step2c_buttonBox.setEnabled(True))
        self.Step2c_commandLinkButton.clicked.connect(self.step2c_loadParameterSet)
        self.Step2c_buttonBox.accepted.connect(lambda: self.Step2d_pushButton.setEnabled(True))
        self.Step2c_buttonBox.accepted.connect(self.step2c_saveChanges)
        self.Step2c_buttonBox.rejected.connect(self.step2c_restoreDefaults)
        #
        self.Step2d_radioButton.toggled.connect(self.Step2d_lineEdit.setEnabled)
        self.Step2d_radioButton.toggled.connect(self.Step2d_pushButton.setEnabled)
        self.Step2d_lineEdit.textChanged.connect(lambda: self.Step2d_pushButton.setEnabled(True))
        self.Step2d_pushButton.clicked.connect(self.step2d_runParameterOptimization)
        self.popwin.popup_pushButton.clicked.connect(self.Step2d_popup_saveToConfigFile)  
        #
        self.Step3a_toolButton.clicked.connect(self.step3a_selectImageStackFile) 
        self.Step3a_lineEdit.textChanged.connect(lambda: self.Step3ab_pushButton.setEnabled(True))
        self.Step3b_toolButton.clicked.connect(self.step3b_selectDatesFile)
        self.Step3b_lineEdit.textChanged.connect(lambda: self.Step3ab_pushButton.setEnabled(True))
        self.Step3b_toolButton.released.connect(lambda: self.Step3ab_pushButton.setEnabled(True))
        self.Step3ab_pushButton.clicked.connect(self.step3ab_loadImageStackAndDatesFile)
        self.Step3ab_pushButton.released.connect(lambda: self.Step3c_radioButton.setEnabled(True))
        self.Step3ab_pushButton.released.connect(lambda: self.Step3op_clearsubsetButton.setEnabled(True))
        self.Step3ab_pushButton.released.connect(lambda: self.Step3op_subsetButton.setEnabled(True))
        #
        self.Step3op_subsetButton.clicked.connect(self.step3opt_subsetData)
        self.Step3op_subsetButton.released.connect(lambda: self.Step3op_subsetButton.setEnabled(True))

        # Sets default subset parameters as None, and keeps their reference global, as they will be manipulated by
        # matplotlib GUI objects as well as pyQT GUI objects, since matplotlib doesn't allow for reference objects
        # to be passed in, the references are kept global
        global subset_x1, subset_y1, subset_y2, subset_x2
        subset_x1 = None
        subset_y1 = None
        subset_x2 = None
        subset_y2 = None
        #
        #
        # Added in the new subset and clear subset button, which manipulates global context of subset variables
        # these buttons are also disabled till stack file is not selected.
        # TODO #1 - Should remove cases where least cloudy image in stack has nan values, and remove the image
        #   from consideration.
        self.Step3op_clearsubsetButton.clicked.connect(self.step3opt_clearsubsetData)
        self.Step3op_clearsubsetButton.released.connect(lambda: self.Step3op_clearsubsetButton.setEnabled(True))
        #
        self.Step3c_radioButton.toggled.connect(self.Step3c_lineEdit.setEnabled)
        self.Step3c_radioButton.toggled.connect(self.Step3c_pushButton.setEnabled)
        self.Step3c_lineEdit.textChanged.connect(lambda: self.Step3c_pushButton.setEnabled(True))
        self.Step3c_pushButton.clicked.connect(self.step3c_runImageStackMetrics)
        self.Step3c_pushButton.released.connect(lambda: self.Step4a_pushButton.setEnabled(True))
        #
        self.Step4a_pushButton.clicked.connect(self.step4_PlotAndSave)
        #
        # # Removed plot all functionality from the user workflow, which could bog down the system when too many
        # # plots were opened at once.
        # self.plotAll.setChecked(False)
        # self.plotAll.stateChanged.connect(self.onState1ChangePrincipal)
        self.plotCheckboxes = [self.plot2, self.plot3, self.plot4, self.plot5, self.plot6, self.plot7, 
                               self.plot8, self.plot9, self.plot10, self.plot10, self.plot11, self.plot12,
                               self.plot13, self.plot14, self.plot15, self.plot16]
        # for plotCheckbox in self.plotCheckboxes:
        #     plotCheckbox.stateChanged.connect(self.onState1Change)
        #
        self.saveAll.setChecked(False)
        self.saveAll.stateChanged.connect(self.onState2ChangePrincipal)
        self.saveCheckboxes = [self.save2, self.save3, self.save4, self.save5, self.save6, self.save7, 
                               self.save8, self.save9, self.save10, self.save10, self.save11, self.save12,
                               self.save13, self.save14, self.save15, self.save16]
        for saveCheckbox in self.saveCheckboxes:
            saveCheckbox.stateChanged.connect(self.onState2Change)
    
    def test(self):
        '''
        Test using default data. This function is made for deployment test purpose
        :return:
        '''
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_messagebox)
        self.timer.start(1000)
        self.need_close = False # set to True after finishing test
        self.close_counter = 0 # count 5 seconds before finish

        ## STEP 1
        self.tabWidget.setCurrentIndex(1)

        # select working directory
        print('TEST: setting working directory')
        work_dir = os.path.join(os.getcwd(), 'demo_dataset')
        self.Step1a_lineEdit.setText(work_dir)
        self.step1a_loadWD()

        # select user configuration file
        print('TEST: setting user configuration file')
        config_file = os.path.join(os.getcwd(), 'user_configs.ini')
        self.Step1b_lineEdit.setText(config_file)
        self.step1b_loadUserConfigFile()

        ## STEP 2
        self.tabWidget.setCurrentIndex(2)

        # select points extraction file
        print('TEST: setting points extraction file')
        pts_file = os.path.join(os.getcwd(), 'input', 'oilpalm_sample_pts.csv')
        self.Step2a_lineEdit.setText(pts_file)
        self.step2a_loadPointsFile()

        # select objectids
        self.Step2b_lineEdit.setText('1:3')
        # visualize
        print('TEST: visualization trajectories')
        self.Visualize_radioButton.setChecked(True)
        self.step2b_plotNITApoints_drawTraj()
       
        # load default set
        self.Step2c_commandLinkButton.animateClick(100)
        # change parameters according to the test scenario
        print('TEST: saving custom user opts configuration')
        custom_config_file = os.path.join(os.getcwd(), 'user_configs_opt.ini')
        shutil.copy(config_file, custom_config_file)
        config = ConfigObj(custom_config_file)
        po = config['ParameterOpmSet']
        po['bail_thresh_set']   = ['0.7', '1.0']
        po['noise_thresh_set']  = ['1', '2']
        po['penalty_set']       = ['1', '3']
        po['filt_dist_set']     = ['3', '5']   
        po['pct_set']           = ['80', '90']
        po['max_complex_set']   = ['10', '15']    
        po['min_complex_set']   = ['3', '5']  
        po['filter_opt_set'] = 'sgolay'
        config.write()
        nita = nitaObj(custom_config_file)

        self.Step1b_lineEdit.setText(custom_config_file)
        self.step1b_loadUserConfigFile()

         # draw trajectories
        self.Visualize_radioButton.setChecked(False)
        self.DrawTraj_radioButton.setChecked(True)
        self.step2b_plotNITApoints_drawTraj()

        # Prallel optimization
        print('TEST: parallel optimization')
        self.Step2d_lineEdit.setText('8')
        self.step2d_runParameterOptimization()
        self.popwin.close()

        # save the optimization result
        print('TEST: parallel optimization')
        self.Step2d_popup_saveToConfigFile()

        # check the optimization result
        self.Visualize_radioButton.setChecked(True)
        self.DrawTraj_radioButton.setChecked(False)
        self.step2b_plotNITApoints_drawTraj()

        ## STEP 3
        self.tabWidget.setCurrentIndex(3)
        # select image stack file
        img_stack_file = os.path.join(os.getcwd(), 'input', 'oilpalm_sample_nbr_stack.tif')
        self.Step3a_lineEdit.setText(img_stack_file)

        # select dates file
        img_dates_file = os.path.join(os.getcwd(), 'input', 'oilpalm_sample_stack_dates.csv')
        self.Step3b_lineEdit.setText(img_dates_file)
        
        # load image stack and date files
        self.step3ab_loadImageStackAndDatesFile()
        self.step3opt_subsetData()
        
        # parallelize
        self.Step3c_lineEdit.setText('8')
        self.step3c_runImageStackMetrics()

        ## STEP 4
        self.tabWidget.setCurrentIndex(4)
        # linear error
        self.plot14.setChecked(True)
        self.step4_PlotAndSave()

        # disturbance date
        self.plot3.setChecked(True)
        self.step4_PlotAndSave()

        ## All steps done, finally wait for some seconds and close
        print('TEST: All test flow finished. Will close soon.')
        self.need_close = True
    
    def check_messagebox(self):
        '''
        Helper function for unit test
        It eliminates messageboxes and close smoothly after all test is done
        :return:
        '''
        messagebox = self.findChild(QtWidgets.QMessageBox)
        if messagebox is not None:
            messagebox.close()
        if self.need_close:
            self.close_counter += 1
            if self.close_counter == 10:
                sys.exit()
           
    def step1a_selectWD(self):
        '''
        Display dialog box for selection of working directory by the user.
        Pop-up of FileDialog, which gets selected as text-label of Step1a.
        :return:
        '''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self,'Select Working Directory',expanduser('~'), options=options)
        if folder_path:
            self.Step1a_lineEdit.setText(folder_path)
            self.Step1a_lineEdit.setEnabled(True)
            
    def step1a_loadWD(self):
        '''
        Load the selected working directory.
        :return:
        '''
        name = self.Step1a_lineEdit.text()
        if not name:
            QtWidgets.QMessageBox.about(self, 'text','Oops!..Select Workding Directory')
        else:
            os.chdir(name)
            self.Step1a_pushButton.setEnabled(False)
            QtWidgets.QMessageBox.about(self, 'text','Working Directory: '+'<br>'+name)
        
    def step1b_selectUserConfigFile(self):
        '''
        Select the user configuration ini file, and set it as step 1b text label,
        if the user configures file, it needs to selected again in order to be reloaded.
        :return:
        '''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, ext = QtWidgets.QFileDialog.getOpenFileName(self, 'Select User Configuration File','','*.ini', options=options)
        if file_path:
            self.Step1b_lineEdit.setText(file_path)
            self.Step1b_lineEdit.setEnabled(True)
    
    def step1b_loadUserConfigFile(self):
        '''
        Loads the selected user configuration ini file from above step in configobj, and writes the data from
        given config file to to step1c table widget for display and editing the values from the selected
        ini file.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        if name:
            config_name = self.Step1b_lineEdit.text()
            config = ConfigObj(config_name) # provides abstraction to config ini read file.
            #
            np = config['NITAParameters']
            mp = config['MetricsParameters']
            TW_Item = QtWidgets.QTableWidgetItem
            self.Step1c_tableWidget.setItem(0, 0, TW_Item(config['Project']['ProjectName']))
            self.Step1c_tableWidget.setItem(1, 0, TW_Item(config['VI']['user_vi'].lower()))
            self.Step1c_tableWidget.setItem(2, 0, TW_Item(", ".join(np['value_limits'])))
            self.Step1c_tableWidget.setItem(3, 0, TW_Item(", ".join(np['doy_limits'])))
            self.Step1c_tableWidget.setItem(4, 0, TW_Item(", ".join(np['date_limits'])))
            self.Step1c_tableWidget.setItem(5, 0, TW_Item(np['bail_thresh']))
            self.Step1c_tableWidget.setItem(6, 0, TW_Item(np['noise_thresh']))
            self.Step1c_tableWidget.setItem(7, 0, TW_Item(np['penalty']))
            self.Step1c_tableWidget.setItem(8, 0, TW_Item(np['filt_dist']))
            self.Step1c_tableWidget.setItem(9, 0, TW_Item(np['pct']))
            self.Step1c_tableWidget.setItem(10, 0, TW_Item(np['max_complex']))
            self.Step1c_tableWidget.setItem(11, 0, TW_Item(np['min_complex']))
            self.Step1c_tableWidget.setItem(12, 0, TW_Item(np['filter_opt']))
            self.Step1c_tableWidget.setItem(13, 0, TW_Item(mp['vi_change_thresh']))
            self.Step1c_tableWidget.setItem(14, 0, TW_Item(mp['run_thresh']))
            #
            config['Project']['RootDir'] = self.Step1a_lineEdit.text()
            config.write()
            self.Step1b_pushButton.setEnabled(False)
            self.Step1c_buttonBox.setEnabled(False)
    
    def step1c_saveChanges(self):
        '''
        User can make changes to the ini file via the interface and tablewidget in step1c, after which the
        new configuration ini file gets saved.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        #
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save User Configuration File",name,'*.ini', options=options)
        #
        if name != fileName:
            shutil.copy(name, fileName)
        else: 
            fileName = name
        #
        config = ConfigObj(fileName)
        np = config['NITAParameters']  # Nita parameter dictionary
        mp = config['MetricsParameters']  # Metric parameter dictionary

        ## Code below updates all configuration through data which is added via
        ## the GUI tableWidget.
        #
        config['Project']['ProjectName'] = self.Step1c_tableWidget.item(0, 0).text()
        config['VI']['user_vi'] = self.Step1c_tableWidget.item(1, 0).text()
        #
        cell = self.Step1c_tableWidget.item(2,0).text()
        np['value_limits'] = [x.strip(' ') for x in cell.split(",")]
        #
        cell = self.Step1c_tableWidget.item(3,0).text()
        np['doy_limits'] = [x.strip(' ') for x in cell.split(",")]
        #
        cell = self.Step1c_tableWidget.item(4,0).text()
        np['date_limits'] = [x.strip(' ') for x in cell.split(",")]
        #
        np['bail_thresh'] = self.Step1c_tableWidget.item(5, 0).text()
        np['noise_thresh'] = self.Step1c_tableWidget.item(6, 0).text()
        np['penalty'] = self.Step1c_tableWidget.item(7, 0).text()
        np['filt_dist'] = self.Step1c_tableWidget.item(8, 0).text()
        np['pct'] = self.Step1c_tableWidget.item(9, 0).text()
        np['max_complex'] = self.Step1c_tableWidget.item(10, 0).text()
        np['min_complex'] = self.Step1c_tableWidget.item(11, 0).text()
        np['filter_opt'] = self.Step1c_tableWidget.item(12, 0).text()
        mp['vi_change_thresh'] = self.Step1c_tableWidget.item(13, 0).text()
        mp['run_thresh'] = self.Step1c_tableWidget.item(14, 0).text() 
        config.write()  # save the new configuration in the file.
        # 
        self.Step1b_lineEdit.setText(fileName) # update the filename
        self.step1b_loadUserConfigFile()
        self.Step1c_buttonBox.setEnabled(False)
        #
        QtWidgets.QMessageBox.about(self, 'text','Wohooo!..Parameters Saved to User Configuration File')
        
    def step1c_restoreDefaults(self):
        '''
        Cancels the changed configuration and reloads the orignal.
        :return:
        '''
        self.step1b_loadUserConfigFile()
        self.Step1c_buttonBox.setEnabled(False)
    
    def step2a_selectPointsFile(self):
        '''
        Selects point extraction file, and sets the path to the file as part of step2a text label,
        raises QMessageBox error, if user config not specified.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        if name:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, ext = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Points Extraction File','','*.csv', options=options)
            if file_path:
                self.Step2a_lineEdit.setText(file_path)
                self.Step2a_lineEdit.setEnabled(True)
        else:
            QtWidgets.QMessageBox.about(self, 'text','Oops!..Select User Config File (Step1)')
            
    def step2a_loadPointsFile(self):
        '''
        Loads point extraction file, after point extraction file path has been specified.
        :return:
        '''
        name = self.Step2a_lineEdit.text()
        global nita  # NITA object which encapsulates the main data processing and holds the computation stack
        if name:
            config_name = self.Step1b_lineEdit.text()
            config = ConfigObj(config_name)
            config['Project']['ptsFn'] = name  # Sets the points directory in the configuration object
            config.write()  # Writes the new configuration in the ini file
            nita = nitaObj(config_name)  # Creates nita object form the updated configuration file.
            QtWidgets.QMessageBox.about(self, 'text','Points Extraction File: '+'<br>'+name)
            #
            self.Step2a_pushButton.setEnabled(False)

    def step2opt_showPointMetadata(self):
        '''
        Loads point metadata, which shows unique objectids, along with names in the points file via a reference
        table of the orignal points file. Useful for referring point objectids in the GUI.
        :return:
        '''
        global nita
        config_name = self.Step1b_lineEdit.text()
        # initializes nita object if its not present, else updates it if config is modified.
        if 'nita' not in globals():
            nita = nitaObj(config_name)
        else:
            nita.updateConfig(config_name)
        reference_table = nita.loadRef() # Loads the reference table consisting pandas dataframe with unique points
        self.view = QTableView()  # Initialize a new table
        model = pandasModel(reference_table)  # GUI interface to populate the above table view.
        self.view.setModel(model)
        self.view.resize(250, 600)
        self.view.show()
        return

    def step2b_plotNITApoints_drawTraj(self):
        '''
        Plot the selected points, where objects ids are taken via the GUI, handles both cases, where user may want
        to draw trajectories, or view the plots
        :return:
        '''
        IDs = self.Step2b_lineEdit.text()  # Get ID's via GUI
        IDs = [x.strip(' ') for x in IDs.split(",")]
        global nita
        config_name = self.Step1b_lineEdit.text()
        if 'nita' not in globals():
            nita = nitaObj(config_name)
        else:
            nita.updateConfig(config_name)
        #
        if IDs:
            #
            obj_ids=[]
            #
            for i in IDs:
                if ':' in i:
                    print(i)
                    temp=i.split(':')
                    obj_ids.extend(list(range(int(temp[0]), int(temp[1]) + 1)))
                else:
                    print(i)
                    obj_ids.append(int(i))
            obj_ids = list(set(obj_ids))
            #   
            nita.startLog()
            #
            # If visualize is selected, load points and draw the objects.
            if self.Visualize_radioButton.isChecked() == True:
                # Load NITA points
                try:
                    nita.loadPts(info_column='Name')
                except Exception as e:
                    QtWidgets.QMessageBox.about(self, 'text', str(e))
                # Plot for selected OBJECTIDs
                try:
                    nita.runPts([int(item) for item in obj_ids], plot=True, max_plot=50, showdata='fit', colorbar=False, plot_title=True)
                except Exception as e:
                    QtWidgets.QMessageBox.about(self, 'text', str(e))
            # Else allow for drawing the trajectories, for the given points.
            if self.DrawTraj_radioButton.isChecked() == True:
                nita.loadPts(info_column='Name')
                # Plot trajectories for selected OBJECTIDs
                try:
                    nita.drawPts([int(item) for item in obj_ids], plot_title=True)
                except Exception as e:
                    QtWidgets.QMessageBox.about(self, 'text', str(e))
            #
            nita.stopLog()
        else:
            QtWidgets.QMessageBox.about(self, 'text','Error! Enter OBJECTIDs')
        
    def step2c_loadParameterSet(self):
        '''
        Set up list of parameters present in configuration object to populate the tablewidget.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        if name:
            #
            config = ConfigObj(name)
            #
            po = config['ParameterOpmSet']
            TW_Item = QtWidgets.QTableWidgetItem
            #
            self.Step2c_tableWidget.setItem(0, 0, TW_Item(", ".join(po['bail_thresh_set'])))
            self.Step2c_tableWidget.setItem(1, 0, TW_Item(", ".join(po['noise_thresh_set'])))
            self.Step2c_tableWidget.setItem(2, 0, TW_Item(", ".join(po['penalty_set'])))
            self.Step2c_tableWidget.setItem(3, 0, TW_Item(", ".join(po['filt_dist_set'])))
            self.Step2c_tableWidget.setItem(4, 0, TW_Item(", ".join(po['pct_set'])))
            self.Step2c_tableWidget.setItem(5, 0, TW_Item(", ".join(po['max_complex_set'])))
            self.Step2c_tableWidget.setItem(6, 0, TW_Item(", ".join(po['min_complex_set'])))
            self.Step2c_tableWidget.setItem(7, 0, TW_Item(po['filter_opt_set']))
            self.Step2c_buttonBox.setEnabled(False)
        else:
            QtWidgets.QMessageBox.about(self, 'text','Oops!..Select User Config File (Step1)')
            
    def tableList(self,row,col):
        '''
        Return value of a specific row, col in step2c table widget.
        :param row: row index to be used
        :param col: col index to be used
        :return: list of values of cell, split by commas
        '''
        cell = self.Step2c_tableWidget.item(row,col).text()
        return [x.strip(' ') for x in cell.split(",")]
    
    def step2c_saveChanges(self):
        '''
        Save parameter configuration changes updated via tablewidget to ini file.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        global nita
        if not name:
            self.Step1c_buttonBox.setEnabled(False)
        else:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self,"Save User Configuration File",name,'*.ini', options=options)
            if name != fileName:
                shutil.copy(name, fileName)
            #
            config = ConfigObj(fileName)
            po = config['ParameterOpmSet']
            #
            po['bail_thresh_set']   = self.tableList(0,0)               
            po['noise_thresh_set']  = self.tableList(1,0)     
            po['penalty_set']       = self.tableList(2,0)     
            po['filt_dist_set']     = self.tableList(3,0)     
            po['pct_set']           = self.tableList(4,0)     
            po['max_complex_set']   = self.tableList(5,0)     
            po['min_complex_set']   = self.tableList(6,0)   
            po['filter_opt_set'] = self.Step2c_tableWidget.item(7, 0).text()
            #
            config.write()
            nita = nitaObj(fileName)
            #   
            self.Step1b_lineEdit.setText(fileName)
            self.step1b_loadUserConfigFile()
            self.Step2c_buttonBox.setEnabled(False)
            #
            QtWidgets.QMessageBox.about(self, 'text','Wohooo!..Parameter Set Saved to User Configuration File')
            
    def step2c_restoreDefaults(self):
        '''
        Reset default parameter configuration, present in the ini file, before updation.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        if name:
            self.Step2c_loadParameterSet()
            self.Step2c_buttonBox.setEnabled(False)
    
    def step2d_runParameterOptimization(self):
        '''
        Run for list of possible parameter configurations, to decide the most optimal configuration.
        :return:
        '''
        self.Step2d_pushButton.setEnabled(False)
        #
        nita.startLog()
        nita.setOpmParams()  # set list of possible optimization configurations
        #
        if self.Step2d_lineEdit.text() == '' or int(self.Step2d_lineEdit.text()) < 2:
            QtWidgets.QMessageBox.about(self, 'text','Error!'+'<br> Minimum = 2'+'<br>Maximum = Check number of cores available on your computer and specify accordingly')
        else:
            n_workers = int(self.Step2d_lineEdit.text()) # select number of workers.
            #
            try:
                opt_out = nita.paramOpm(parallel=True, workers=n_workers)  # run for all possible configurations
                # which configuration is the most optimal, and return as a dictionary.
            except Exception as e:
                QtWidgets.QMessageBox.about(self, 'Error', str(e))
                return
            # display best configuration as a popup window.
            TW_Item = QtWidgets.QTableWidgetItem
            self.popwin.popup_table.setItem(0, 0, TW_Item(str(opt_out['bail_thresh'])))
            self.popwin.popup_table.setItem(1, 0, TW_Item(str(opt_out['noise_thresh'])))
            self.popwin.popup_table.setItem(2, 0, TW_Item(str(opt_out['penalty'])))
            self.popwin.popup_table.setItem(3, 0, TW_Item(str(opt_out['filt_dist'])))
            self.popwin.popup_table.setItem(4, 0, TW_Item(str(opt_out['pct'])))
            self.popwin.popup_table.setItem(5, 0, TW_Item(str(opt_out['max_complex'])))
            self.popwin.popup_table.setItem(6, 0, TW_Item(str(opt_out['min_complex'])))
            self.popwin.popup_table.setItem(7, 0, TW_Item(opt_out['filter_opt']))
            self.popwin.show()
            #
        nita.stopLog()
    
    def Step2d_popup_saveToConfigFile(self):
        '''
        Save best configuration, among given configurations to the file.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        config = ConfigObj(name)
        np = config['NITAParameters']
        np['bail_thresh'] = self.popwin.popup_table.item(0, 0).text()
        np['noise_thresh'] = self.popwin.popup_table.item(1, 0).text()
        np['penalty'] = self.popwin.popup_table.item(2, 0).text()
        np['filt_dist'] = self.popwin.popup_table.item(3, 0).text()
        np['pct'] = self.popwin.popup_table.item(4, 0).text()
        np['max_complex'] = self.popwin.popup_table.item(5, 0).text()
        np['min_complex'] = self.popwin.popup_table.item(6, 0).text()
        np['filter_opt'] = self.popwin.popup_table.item(7, 0).text()
        config.write() # write optimal configuration to file
        global nita
        nita = nitaObj(name) # re-init nita object with optimized configuration.
        self.step1b_loadUserConfigFile()
        #        
        QtWidgets.QMessageBox.about(self, 'text','Wohooo!..Optimized Parameters Saved to User Configuration File')
            
    def step3a_selectImageStackFile(self):
        '''
        Select Image stack file from GUI.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        if name:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, ext = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Image Stack File','','*.tif', options=options)
            if file_path:
                self.Step3a_lineEdit.setText(file_path)
                self.Step3a_lineEdit.setEnabled(True)
        else:
            QtWidgets.QMessageBox.about(self, 'text','Oops!..Select User Config File (Step1)')
    
    def step3b_selectDatesFile(self):
        '''
        Select Image Dates file from GUI.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        if name:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, ext = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Image Dates File','','*.csv', options=options)
            if file_path:
                self.Step3b_lineEdit.setText(file_path)
                self.Step3b_lineEdit.setEnabled(True)
        else:
            QtWidgets.QMessageBox.about(self, 'text','Oops!..Select User Config File (Step1)') 
            
    def step3ab_loadImageStackAndDatesFile(self):
        '''
        Loads the image stack and dates file
        :return:
        '''
        name1 = self.Step3a_lineEdit.text()
        name2 = self.Step3b_lineEdit.text()
        if name1 and name2:
            config_name = self.Step1b_lineEdit.text()
            config = ConfigObj(config_name)
            config['Project']['stackFn'] = name1
            config['Project']['stackdateFn'] = name2
            config.write()
            QtWidgets.QMessageBox.about(self, 'text','Stack File:'+'<br>'+name1+'<br>;----------'+'<br>Dates File: '+'<br>'+name2)
            #
            self.Step3ab_pushButton.setEnabled(False)
            #
            global nita
            nita = nitaObj(config_name)  # reload nita object when new stack file or dates file is selected.
        else:
            QtWidgets.QMessageBox.about(self, 'text','Oops! Select Image Stack and Dates File')
    
    def step3c_runImageStackMetrics(self):
        '''
        Run image stack metrics on loaded image stack for given dates file.
        :return:
        '''
        self.Step3c_pushButton.setEnabled(False)
        config_name = self.Step1b_lineEdit.text()
        global nita
        if 'nita' not in globals():
            nita = nitaObj(config_name)
        else:
            nita.updateConfig(config_name) # update config, if new configuration is used.
        nita.startLog()
        # load image stack
        try:
            nita.loadStack()
        except Exception as e:
            QtWidgets.QMessageBox.about(self, 'Error', str(e))
            return
        # subset the image stack, if optional subset data region is provided.
        global subset_x1, subset_x2, subset_y1, subset_y2
        if subset_x2:
            subset_x1 = int(subset_x1)
            subset_x2 = int(subset_x2)
            subset_y1 = int(subset_y1)
            subset_y2 = int(subset_y2)
            nita.subsetStack((subset_x1, subset_y1, subset_x2, subset_y2))
        #
        if self.Step3c_lineEdit.text() == '' or int(self.Step3c_lineEdit.text()) < 2:
            QtWidgets.QMessageBox.about(self, 'text','Error!'+'<br> Minimum = 2'+'<br>Maximum = Check number of cores available on your computer and specify accordingly')
        else:
            n_workers = int(self.Step3c_lineEdit.text())
            nita.runStack(parallel=True, workers=n_workers)
            nita.computeStackMetrics(parallel=True, workers=n_workers)
            QtWidgets.QMessageBox.about(self, 'Metrics','Image Metrics Created!')
        #    
        nita.stopLog()

    def step3opt_subsetData(self):
        '''
        Display least cloudy image from the image stack,
        and allow user to select a subset of data.
        :return:
        '''
        config_name = self.Step1b_lineEdit.text()
        global nita
        if 'nita' not in globals():
            nita = nitaObj(config_name)
        else:
            nita.updateConfig(config_name)
        nita.startLog()
        # load image stack
        try:
            nita.loadStack()
        except Exception as e:
            QtWidgets.QMessageBox.about(self, 'Error', str(e))
            return
        nita.stopLog()
        fig, current_ax = plt.subplots()
        # fig.set_size_inches(18.5, 10.5)
        plt.subplots_adjust(bottom=0.1)
        title = 'Drag and select a rectangle to subset, then click Done.'
        #  retrieve least cloudy image
        nita.leastCloudy(title)
        # create rectangle selector, which can be used to subset the data.
        toggle_selector.RS = RectangleSelector(current_ax, subsetClick,
                                               drawtype='box', useblit=False,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive=True)
        plt.connect('key_press_event', toggle_selector)

        axdone = plt.axes([0.7, 0.05, 0.1, 0.075])
        # ip_done = InsetPosition(axdone, [-0.1, -0.5, 0.2, 0.1])
        # axdone.set_axes_locator(ip_done)
        axclear = plt.axes([0.81, 0.05, 0.1, 0.075])

        # create done and clear buttons inside the matplotlib plot.
        b_done = Button(axdone, 'Done')
        b_clear = Button(axclear, 'Clear')

        # set triggers for done and clear button as functions subsetClear and subsetClose
        b_done.on_clicked(subsetClose)
        b_clear.on_clicked(subsetClear)

        axdone._button = b_done
        axclear._button = b_clear

        # show the plot to select the subset of data.
        plt.show()
        self.toggle_save_on_subset()

    def step3opt_clearsubsetData(self):
        '''
        Clear subset data and allow for plots to be saved.
        :return:
        '''
        subsetClear(self)
        self.toggle_save_on_subset()
        return

    def toggle_save_on_subset(self):
        '''
        Switch plot saving, if image stack is subsetted, else allow plots to be saved.
        :return:
        '''
        # print("Ran toggle subset")
        global subset_x2
        for checkbox in self.saveCheckboxes:
            if subset_x2:
                checkbox.setEnabled(False)
            else:
                checkbox.setEnabled(True)
        if subset_x2:
            self.saveAll.setEnabled(False)
        else:
            self.saveAll.setEnabled(True)
        return

    @QtCore.pyqtSlot(int)
    def onclick(self,event):
        '''
        Select the single pixel on which to get pixel results.
        global ix, iy are used, referred in the matplotlib object.
        :param event:
        :return:
        '''
        global ix, iy
        ix, iy = event.xdata, event.ydata
        print('x = %d, y = %d'%(ix, iy))
        results_dic = nita.getPixelResults([int(ix), int(iy)])
        results_dic = nita.runPixel([int(ix), int(iy)], use_compute_mask=False, plot=True, showdata='fit', colorbar=True)

    
    @QtCore.pyqtSlot(int)
    def onState1ChangePrincipal(self, state):
        '''
        Check all plot checkboxes, if plot all is selected.
        Legacy function not useful now
        :param state:
        :return:
        '''
        if state == QtCore.Qt.Checked:
            for plotCheckbox in self.plotCheckboxes:
                plotCheckbox.blockSignals(True)
                plotCheckbox.setCheckState(state)
                plotCheckbox.blockSignals(False)
                
    @QtCore.pyqtSlot(int)
    def onState2ChangePrincipal(self, state):
        '''
        Check all save checkboxes, if save all is selected.
        :param state:
        :return:
        '''
        if state == QtCore.Qt.Checked:
            for saveCheckbox in self.saveCheckboxes:
                saveCheckbox.blockSignals(True)
                saveCheckbox.setCheckState(state)
                saveCheckbox.blockSignals(False)

    @QtCore.pyqtSlot(int)
    def onState1Change(self, state):
        '''
        Initial setup for plot all
        Legacy function, not useful now
        :param state:
        :return:
        '''
        self.plotAll.blockSignals(True)
        self.plotAll.setChecked(QtCore.Qt.Unchecked)
        self.plotAll.blockSignals(False)
    
    @QtCore.pyqtSlot(int)
    def onState2Change(self, state):
        '''
        Initial setup for save all
        :param state:
        :return:
        '''
        self.saveAll.blockSignals(True)
        self.saveAll.setChecked(QtCore.Qt.Unchecked)
        self.saveAll.blockSignals(False)
        
    def step4_PlotAndSave(self):
        '''
        Check which metric image is selected for plot or save, and show/save accordingly.
        :return:
        '''
        name = self.Step1b_lineEdit.text()
        if name:
            config = ConfigObj(name)
            cp = config['Project']
            outfile = os.path.join(cp['OutputFolder'],cp['ProjectName'], cp['ProjectName']+'_metadata'+'.ini')
            shutil.copy(name, outfile)
        #
        # Checks which buttons are selected, and plots/saves accordingly.
        if self.plot10.isChecked() == True or self.save10.isChecked() == True:
            valChange_date1 = self.Step4_ValueChange_Date1.text()
            valChange_date2 = self.Step4_ValueChange_Date2.text()
            title = 'Value Change -'+valChange_date1+' to '+valChange_date2
            label = 'VI Units'
            if valChange_date1 and valChange_date2:
                filename_plot = 'valuechange2_'+str(valChange_date1)+'_'+str(valChange_date2)+'.tif'
                nita.MI_valueChange(start_date=int(valChange_date1), end_date=int(valChange_date2), option='diff', plot=self.plot10.isChecked(),
                                    save=self.save10.isChecked(), fn=filename_plot, title = title, label=label)
                plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
            else:
                QtWidgets.QMessageBox.about(self, 'text','Error!..10)Specify Date Range')            
        if self.plot11.isChecked() == True or self.save11.isChecked() == True:
            spec_date = self.Step4_DateValue.text()#2005000
            if spec_date:
                title = 'Date Value - '+spec_date
                label = 'VI Units'
                nita.MI_dateValue(int(spec_date), plot=self.plot11.isChecked(), save=self.save11.isChecked(), fn='datevalue.tif', title = title, label=label)
                plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
            else:
                QtWidgets.QMessageBox.about(self,'text','Error!..11)Specify Date')   
        if self.plot2.isChecked() == True or self.save2.isChecked() == True:
            title = 'Complexity'
            label = 'Low < -- Complexity -- > High'
            nita.MI_complexity(plot=self.plot2.isChecked(), save=self.save2.isChecked(), fn='complexity.tiff', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
        if self.plot3.isChecked() == True or self.save3.isChecked() == True:
            title = 'Disturbance Date'
            label = 'Year of disturbance'
            nita.MI_distDate(option='middle', plot=self.plot3.isChecked(), save=self.save3.isChecked(), fn='distdate.tiff', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
        if self.plot4.isChecked() == True or self.save4.isChecked() == True:
            title = 'Disturbance Duration'
            label = 'Number of days'
            nita.MI_distDuration(plot=self.plot4.isChecked(), save=self.save4.isChecked(), fn='distduration.tiff', title = title, label=label)                            
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
        if self.plot5.isChecked() == True or self.save5.isChecked() == True:   
            title = 'Disturbance Magnitude'
            label = 'VI Units'
            nita.MI_distMag(plot=self.plot5.isChecked(), save=self.save5.isChecked(), fn='distMag.tif', title = title, label=label)    
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)                       
        if self.plot6.isChecked() == True or self.save6.isChecked() == True:
            title = 'Disturbance Slope'
            label = 'Slope (degrees)'
            nita.MI_distSlope(plot=self.plot6.isChecked(), save=self.save6.isChecked(), fn='distSlope.tif', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
        if self.plot7.isChecked() == True or self.save7.isChecked() == True:
            title = 'Post-Disturbance Slope'
            label = 'Slope (degrees)'
            nita.MI_postDistSlope(plot=self.plot7.isChecked(), save=self.save7.isChecked(), fn='postdistslope.tif', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)                             
        if self.plot8.isChecked() == True or self.save8.isChecked() == True:
            title = 'Post-Disturbance Magnitude'
            label = 'VI Units'
            nita.MI_postDistMag(plot=self.plot8.isChecked(), save=self.save8.isChecked(), fn='postdistmag.tif', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
        if self.plot9.isChecked() == True or self.save9.isChecked() == True:
            title = 'Value Change - Entire time period'
            label = 'VI Units'
            nita.MI_valueChange(start_date=-9999, end_date=9999, option='diff', plot=self.plot9.isChecked(), 
                                save=self.save9.isChecked(), fn='valuechange1.tif', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
        if self.plot12.isChecked() == True or self.save12.isChecked() == True:
            title = 'Recovery'
            label = 'VI Units'
            nita.MI_recovery(1, option='diff', plot=self.plot12.isChecked(), save=self.save12.isChecked(), fn='recovery.tif', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)                          
        if self.plot13.isChecked() == True or self.save13.isChecked() == True:
            title = 'RecoverCmp'
            label = 'VI Units'
            nita.MI_recoveryCmp(1, plot=self.plot13.isChecked(), save=self.save13.isChecked(), fn='recoverycmp.tif', title = title, label=label)                            
        if self.plot14.isChecked() == True or self.save14.isChecked() == True:
            title = 'Linear Error'
            label = 'Mean Absolute Error'
            nita.MI_linearError(plot=self.plot14.isChecked(), save=self.save14.isChecked(), fn='linerror.tif', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
        if self.plot15.isChecked() == True or self.save15.isChecked() == True:
            title = 'Noise'
            label = 'Forward Finite Difference'
            nita.MI_noise(plot=self.plot15.isChecked(), save=self.save15.isChecked(), fn='noise.tif', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
        if self.plot16.isChecked() == True or self.save16.isChecked() == True:
            title = 'Bailcut'
            label = 'Noise Normalized Linear Error'
            nita.MI_bailcut(plot=self.plot16.isChecked(), save=self.save16.isChecked(), fn='bailcut.tif', title = title, label=label)
            plt.figure(title).canvas.mpl_connect('button_press_event', self.onclick)
        # Check if any of the plot buttons is selected and display the figures for all the radio buttons pressed.
        plot_flag = False
        for i in range(2, 17):
            if eval('self.plot'+str(i)+'.isChecked()')==True:
                plot_flag = True
                break
        if plot_flag:
            plt.show()


def toggle_selector(event):
    '''
    Event configuration setup for subsetting matplotlib functionality.
    Rectangle selector get point selected is configured.
    :param event:
    :return:
    '''
    print(' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print(' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print(' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)

def subsetClose(self):
    '''
    Close subset without selecting points. Closes plots, and defaults to orignal data.
    :param self:
    :return:
    '''
    plt.close('all')
    print('Closing all plots')
    msgbox = QMessageBox()
    global subset_x1, subset_y1, subset_x2, subset_y2
    if subset_y2:
        msgbox.setText('({0}, {1}), ({2},{3}) are selected co-ordinates.'.format(int(subset_x1), int(subset_y1), int(subset_x2),
                                                                                 int(subset_y2)))
    else:
        msgbox.setText('Points were not selected, no subsetting will be done.')
    msgbox.exec()


def subsetClear(self):
    '''
    Clear points selected for subsetting data, if they are configured.
    :param self:
    :return:
    '''
    plt.close('all')
    print('Closing all plots')
    msgbox = QMessageBox()
    msgbox.setText('Cleared the co-ordinates')
    global subset_x1, subset_y1, subset_x2, subset_y2
    subset_x1 = subset_y1 = subset_y2 = subset_x2 = None  # set subset points as None
    msgbox.exec()
    qt_app.toggle_save_on_subset()

def subsetClick(eclick, erelease):
    '''
    Get points selected and released data from RectangleSelector
    for subset data co-ordinates and disable save option.
    :param eclick:
    :param erelease:
    :return:
    '''
    global subset_x1, subset_y1, subset_x2, subset_y2
    subset_x1, subset_y1 = eclick.xdata, eclick.ydata
    subset_x2, subset_y2 = erelease.xdata, erelease.ydata
    qt_app.toggle_save_on_subset()
    # print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    # print(" The button you used were: %s %s" % (eclick.button, erelease.button))

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    qt_app = MyQtApp()
    qt_app.show()

    # for test automation
    if(len(sys.argv) > 1 and sys.argv[1] == 'test'):
        qt_app.test()    

    app.exec_()

