#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 16:31:28 2018

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
#
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
#
from pynita_ui import mainV12, popup3, resource_logos
from pynita_source import *
#

class popWindow(QtWidgets.QMainWindow, popup3.Ui_MainWindow):
    def __init__(self, parent=None):
        super(popWindow,self).__init__()
        self.setupUi(self)
        self.setWindowTitle('pyNITA - Optimization') 

class MyQtApp(QtWidgets.QMainWindow, mainV12.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyQtApp,self).__init__()
        self.setupUi(self)
        self.setWindowTitle('pyNITA - Version 1.0')
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
        #
        self.objectid_radioButton.toggled.connect(self.Step2b_lineEdit.setEnabled)
        self.objectid_radioButton.toggled.connect(self.Visualize_radioButton.setEnabled)
        self.objectid_radioButton.toggled.connect(self.DrawTraj_radioButton.setEnabled)
        self.objectid_radioButton.toggled.connect(self.Step2b_pushButton.setEnabled) 
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
        #
        self.Step3c_radioButton.toggled.connect(self.Step3c_lineEdit.setEnabled)
        self.Step3c_radioButton.toggled.connect(self.Step3c_pushButton.setEnabled)
        self.Step3c_lineEdit.textChanged.connect(lambda: self.Step3c_pushButton.setEnabled(True))
        self.Step3c_pushButton.clicked.connect(self.step3c_runImageStackMetrics)
        self.Step3c_pushButton.released.connect(lambda: self.Step4a_pushButton.setEnabled(True))
        #
        self.Step4a_pushButton.clicked.connect(self.step4_PlotAndSave)
        #
        self.plotAll.setChecked(False) 
        self.plotAll.stateChanged.connect(self.onState1ChangePrincipal)
        self.plotCheckboxes = [self.plot2, self.plot3, self.plot4, self.plot5, self.plot6, self.plot7, 
                               self.plot8, self.plot9, self.plot10, self.plot10, self.plot11, self.plot12,
                               self.plot13, self.plot14, self.plot15, self.plot16]
        for plotCheckbox in self.plotCheckboxes:
            plotCheckbox.stateChanged.connect(self.onState1Change)
        #
        self.saveAll.setChecked(False)
        self.saveAll.stateChanged.connect(self.onState2ChangePrincipal)
        self.saveCheckboxes = [self.save2, self.save3, self.save4, self.save5, self.save6, self.save7, 
                               self.save8, self.save9, self.save10, self.save10, self.save11, self.save12,
                               self.save13, self.save14, self.save15, self.save16]
        for saveCheckbox in self.saveCheckboxes:
            saveCheckbox.stateChanged.connect(self.onState2Change)
           
    def step1a_selectWD(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self,'Select Working Directory',expanduser('~'), options=options)
        if folder_path:
            self.Step1a_lineEdit.setText(folder_path)
            self.Step1a_lineEdit.setEnabled(True)
            
    def step1a_loadWD(self):
        name = self.Step1a_lineEdit.text()
        if not name:
            QtWidgets.QMessageBox.about(self, 'text','Oops!..Select Workding Directory')
        else:
            os.chdir(name)
            self.Step1a_pushButton.setEnabled(False)
            QtWidgets.QMessageBox.about(self, 'text','Working Directory: '+'<br>'+name)
        
    def step1b_selectUserConfigFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, ext = QtWidgets.QFileDialog.getOpenFileName(self, 'Select User Configuration File','','*.ini', options=options)
        if file_path:
            self.Step1b_lineEdit.setText(file_path)
            self.Step1b_lineEdit.setEnabled(True)
    
    def step1b_loadUserConfigFile(self):
        name = self.Step1b_lineEdit.text()
        if name:
            config_name = self.Step1b_lineEdit.text()
            config = ConfigObj(config_name)
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
        np = config['NITAParameters']
        mp = config['MetricsParameters']
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
        config.write()
        # 
        self.Step1b_lineEdit.setText(fileName)
        self.step1b_loadUserConfigFile()
        self.Step1c_buttonBox.setEnabled(False)
        #
        QtWidgets.QMessageBox.about(self, 'text','Wohooo!..Parameters Saved to User Configuration File')
        
    def step1c_restoreDefaults(self):
        self.step1b_loadUserConfigFile()
        self.Step1c_buttonBox.setEnabled(False)
    
    def step2a_selectPointsFile(self):
        name = self.Step1b_lineEdit.text()
        if name:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, ext = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Points Extration File','','*.csv', options=options)
            if file_path:
                self.Step2a_lineEdit.setText(file_path)
                self.Step2a_lineEdit.setEnabled(True)
        else:
            QtWidgets.QMessageBox.about(self, 'text','Oops!..Select User Config File (Step1)')
            
    def step2a_loadPointsFile(self):
        name = self.Step2a_lineEdit.text()
        if name:
            config_name = self.Step1b_lineEdit.text()
            config = ConfigObj(config_name)
            config['Project']['ptsFn'] = name
            config.write()
            QtWidgets.QMessageBox.about(self, 'text','Points Extraction File: '+'<br>'+name)
            #
            self.Step2a_pushButton.setEnabled(False)
    
    def step2b_plotNITApoints_drawTraj(self):
        IDs = self.Step2b_lineEdit.text()
        IDs = [x.strip(' ') for x in IDs.split(",")]
        global nita
        config_name = self.Step1b_lineEdit.text()
        nita = nitaObj(config_name)
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
            if self.Visualize_radioButton.isChecked() == True:
                # Load NITA points
                nita.loadPts(info_column='Name')
                # Plot for selected OBJECTIDs 
                nita.runPts([int(item) for item in obj_ids], plot=True, max_plot=50, showdata='fit', colorbar=False, plot_title=True)
            if self.DrawTraj_radioButton.isChecked() == True:
                nita.loadPts(info_column='Name')
                # Plot trajectories for selected OBJECTIDs 
                nita.drawPts([int(item) for item in obj_ids], plot_title=True)
            #
            nita.stopLog()
        else:
            QtWidgets.QMessageBox.about(self, 'text','Error! Enter OBJECTIDs')
        
    def step2c_loadParameterSet(self):
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
        cell = self.Step2c_tableWidget.item(row,col).text()
        return [x.strip(' ') for x in cell.split(",")]
    
    def step2c_saveChanges(self):
        name = self.Step1b_lineEdit.text()
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
            #   
            self.Step1b_lineEdit.setText(fileName)
            self.step1b_loadUserConfigFile()
            self.Step2c_buttonBox.setEnabled(False)
            #
            QtWidgets.QMessageBox.about(self, 'text','Wohooo!..Parameter Set Saved to User Configuration File')
            
    def step2c_restoreDefaults(self):
        name = self.Step1b_lineEdit.text()
        if name:
            self.Step2c_loadParameterSet()
            self.Step2c_buttonBox.setEnabled(False)
    
    def step2d_runParameterOptimization(self):
        self.Step2d_pushButton.setEnabled(False)
        #
        nita.startLog()
        nita.setOpmParams()
        #
        if self.Step2d_lineEdit.text() == '' or int(self.Step2d_lineEdit.text()) < 2:
            QtWidgets.QMessageBox.about(self, 'text','Error!'+'<br> Minimum = 2'+'<br>Maximum = Check number of cores available on your computer and specify accordingly')
        else:
            n_workers = int(self.Step2d_lineEdit.text())
            #
            opt_out = nita.paramOpm(parallel=True, workers=n_workers)
            #
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
        config.write()
        self.step1b_loadUserConfigFile()
        #        
        QtWidgets.QMessageBox.about(self, 'text','Wohooo!..Optimized Parameters Saved to User Configuration File')
            
    def step3a_selectImageStackFile(self):
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
            nita = nitaObj(config_name)
        else:
            QtWidgets.QMessageBox.about(self, 'text','Oops! Select Image Stack and Dates File')
    
    def step3c_runImageStackMetrics(self):
        self.Step3c_pushButton.setEnabled(False)
        config_name = self.Step1b_lineEdit.text()
        global nita
        nita = nitaObj(config_name)
        nita.startLog()
        # load image stack 
        nita.loadStack()
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
    
    @QtCore.pyqtSlot(int)
    def onclick(self,event):
        global ix, iy
        ix, iy = event.xdata, event.ydata
        print('x = %d, y = %d'%(ix, iy))
        results_dic = nita.getPixelResults([int(ix), int(iy)])
        results_dic = nita.runPixel([int(ix), int(iy)], use_compute_mask=False, plot=True, showdata='fit', colorbar=True)

    
    @QtCore.pyqtSlot(int)
    def onState1ChangePrincipal(self, state):
        if state == QtCore.Qt.Checked:
            for plotCheckbox in self.plotCheckboxes:
                plotCheckbox.blockSignals(True)
                plotCheckbox.setCheckState(state)
                plotCheckbox.blockSignals(False)
                
    @QtCore.pyqtSlot(int)
    def onState2ChangePrincipal(self, state):
        if state == QtCore.Qt.Checked:
            for saveCheckbox in self.saveCheckboxes:
                saveCheckbox.blockSignals(True)
                saveCheckbox.setCheckState(state)
                saveCheckbox.blockSignals(False)

    @QtCore.pyqtSlot(int)
    def onState1Change(self, state):
        self.plotAll.blockSignals(True)
        self.plotAll.setChecked(QtCore.Qt.Unchecked)
        self.plotAll.blockSignals(False)
    
    @QtCore.pyqtSlot(int)
    def onState2Change(self, state):
        self.saveAll.blockSignals(True)
        self.saveAll.setChecked(QtCore.Qt.Unchecked)
        self.saveAll.blockSignals(False)
        
    def step4_PlotAndSave(self):
        if self.plot10.isChecked() == True or self.save10.isChecked() == True:
            valChange_date1 = self.Step4_ValueChange_Date1.text()
            valChange_date2 = self.Step4_ValueChange_Date2.text()
            title = 'Value Change -'+valChange_date1+' to '+valChange_date2
            label = 'VI Units'
            if valChange_date1 and valChange_date2:
                nita.MI_valueChange(start_date=int(valChange_date1), end_date=int(valChange_date2), option='diff', plot=self.plot10.isChecked(), 
                                    save=self.save10.isChecked(), fn='valuechange2.tif', title = title, label=label)
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
        
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    qt_app = MyQtApp()
    qt_app.show()
    app.exec_()

