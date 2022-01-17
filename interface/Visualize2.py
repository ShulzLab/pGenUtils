# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:12:27 2020

@author: Timothe
"""


import sys, os#, time
import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import ( NavigationToolbar2QT as NavigationToolbar)
import matplotlib

matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QGroupBox, QGridLayout, QCheckBox, QComboBox, QMenu, QSpinBox, QApplication, QStyleFactory, QFrame, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

import sqlalchemy as sql

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("__filename__"))))

from LibUtils import network, image, database_IO
import LibrairieQtDataDive.widgets as visu
from LibrairieVSDAna.ReadVSDfile import GetFrameOffset


class VisualizeGUI(QMainWindow):
    
    def __init__(self, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Visualize 2.0")
        
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.file_menu.addAction('&Hide BEH', self.Hide1)
        self.file_menu.addAction('&Hide VSD', self.Hide2)
        self.file_menu.addAction('&ShowAll', self.ShowAll,QtCore.Qt.CTRL + QtCore.Qt.Key_H)
        self.menuBar().addMenu(self.file_menu)
                       
        self.SessionDataFrame = False
        
        connect_string = network.find_activeSQL()
        self.sql_engine = sql.create_engine(connect_string)
        
        self.main_widget = QtWidgets.QWidget(self)
                
        self.VSDwidget = visu.Plot3DWidget(parent=self)
        self.BEHwidget = visu.Plot3DWidget(parent=self)
        
        self.frameOffset = 0
        
        self.BEHwidget.SupSlider.ValueChange.connect(self.Synchronize)
        
        self.SetRootfolder(network.find_favoritesRootFolder(source = kwargs.get("source", None)))
        
        l = QtWidgets.QGridLayout(self.main_widget)
        
        self.addToolBar(NavigationToolbar(self.VSDwidget.canvas, self))
        self.addToolBar(NavigationToolbar(self.BEHwidget.canvas, self))
        
        self.BuildSessionTrialBox()
        
        l.addWidget(self.SessionTrialBox, 0,0,1,2)

        l.addWidget(self.VSDwidget, 1,0,1,1)
        l.addWidget(self.BEHwidget, 1,1,1,1)
        
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
        iconfilename = os.path.join(os.path.dirname(os.path.abspath("__filename__")),r"visualizeicon_INt_icon.ico"  )
        self.setWindowIcon(QIcon(iconfilename))
        
        
        
        
    def SetRootfolder(self,folder):
        
        self.LocalPath = folder
        self.VSDwidget.rootPath = folder
        self.BEHwidget.rootPath = folder
    
    def InitSession(self):
        
        if not os.path.exists(self.LocalPath) :
            self.SetRootfolder( str(QFileDialog.getExistingDirectory(self, "Select a directory containing Behavioral Videos and MICAM folders")) )
        print(self.LocalPath)
        self.SessionDataFrame = database_IO.SessionDataframe( self.SessionBox.text() , self.LocalPath)
        
        while type(self.SessionDataFrame) == bool :
            self.SetRootfolder( str(QFileDialog.getExistingDirectory(self, "Select a directory containing Behavioral Videos and MICAM folders")) )
            self.SessionDataFrame = database_IO.SessionDataframe( self.SessionBox.text() , self.LocalPath)
                
        self.TrialNames = self.SessionDataFrame.TrialName.tolist()
        
        self.TrialSelectBox.currentIndexChanged.disconnect()
        self.TrialSelectBox.clear()
        self.TrialSelectBox.addItems(self.TrialNames)
        self.TrialSelectBox.currentIndexChanged.connect(self.LoadDatas)

    def Synchronize(self):
        
        self.VSDwidget.SupSlider.SetValueAndEmit(self.BEHwidget.frame - self.frameOffset)
        self.UpdateInfoLabel()

    def BuildSessionTrialBox(self):
        
        self.SessionTrialBox = QFrame()
        
        self.OpenButton = QPushButton("Open Video")
        self.OpenButton.clicked.connect(self.InitSession)
        self.OpenButton.setMaximumWidth(80)
        
        self.SessionBox = QLineEdit("1656")
        self.SessionBox.setMaximumWidth(80)
        self.INFOLABEL = QLabel("-")
        self.INFOLABEL.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.TrialSelectBox = QComboBox()
        self.TrialSelectBox.currentIndexChanged.connect(self.LoadDatas)
        self.TrialSelectBox.setMaximumWidth(80)
        
        self.LoadInRAM = QCheckBox("Cache data in RAM")
        self.LoadInRAM.setChecked(True)

        l = QGridLayout()
        
        l.addWidget(self.OpenButton, 0,0,1,1)
        l.addWidget(self.SessionBox, 0,1,1,1)
        l.addWidget(self.TrialSelectBox, 0,2,1,1)
        l.addWidget(self.INFOLABEL, 0,3,1,1)
        #l.addWidget(self.LoadInRAM, 0,4,1,1)
        
        l.setSpacing(2)
        l.setContentsMargins(2,2,2,2)
        self.SessionTrialBox.setLayout(l)
    
    def UpdateInfoLabel(self):
        if not type(self.SessionDataFrame) is bool:
            VSDpath = self.SessionDataFrame.at[self.TrialSelectBox.currentIndex(),"VSDpath"]
            BEHpath = self.SessionDataFrame.at[self.TrialSelectBox.currentIndex(),"BEHpath"]
            TrialName = self.SessionDataFrame.at[self.TrialSelectBox.currentIndex(),"TrialName"]
            
            self.INFOLABEL.setText(f'<b>Session</b> {self.SessionBox.text()} - <span style=" font-size:12pt; font-weight:600; color:#aa0000;">Trial {TrialName}</span> - <b>Frame</b> {self.BEHwidget.frame}<br><b>Video BEHAVIOR</b> {BEHpath}<br><b>Video VSD</b> {VSDpath}')
    
    def LoadDatas(self):

        
        VSDpath = self.SessionDataFrame.at[self.TrialSelectBox.currentIndex(),"VSDpath"]
        BEHpath = self.SessionDataFrame.at[self.TrialSelectBox.currentIndex(),"BEHpath"]
        
        self.UpdateInfoLabel()
                
        if not VSDpath == "nan":
            self.VSDwidget.LoadData(VSDpath,'VSD')
            self.frameOffset = GetFrameOffset( self.VSDwidget.signals['AI1'] )
        else :
            self.VSDwidget.SetData(np.repeat(image.Empty_img(500,500)[:,:,np.newaxis], 2, axis = 2))
            self.VSDwidget.UpdateFrame(cmap='gray')
        if not BEHpath == "nan":
            self.BEHwidget.LoadData(BEHpath,'BEH',rot = 1)
        else :
            self.VSDwidget.SetData(np.repeat(image.Empty_img(500,500)[:,:,np.newaxis], 2, axis = 2))
            self.VSDwidget.UpdateFrame(cmap='gray')
        
        
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()
        
    def Hide1(self):
        pass
        #TODO
    def Hide2(self):
        pass
        #TODO
    def ShowAll(self):
        pass
        #TODO
        
    def AssignValuesAndExit(self):
        
        print("Entered BEHI Assign")
        self.FrameArray = self.LoadThread.FrameArray
        self.LoadThread.wait = 0
        self.LoadThread.exit() 
        self.sc.update_figure(self.FrameArray[:,:,self.Frameslider.value()])
        self.Behisok = True
        
        self.CheckDataIsok()
        
    def AssignVSDValuesAndExit(self):
        
        print("Entered VSD Assign")
        self.VSDFrameArray = self.LoadVSDThread.FrameArray
        self.LoadVSDThread.wait = 0
        self.LoadVSDThread.exit() 
        self.sc_VSD.update_figure(self.VSDFrameArray[self.Frameslider.value(),:,:])
        self.VSDisok = True
        
        self.CheckDataIsok()
        
if __name__ == "__main__":
    
    progname = os.path.basename(sys.argv[0])
    qApp = QtWidgets.QApplication(sys.argv)

    aw = VisualizeGUI(source = 'server')
    aw.show()
    sys.exit(qApp.exec_())