# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 19:55:12 2020

@author: Timothe
"""

import sys, os#, time
import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib

matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QSlider, QPushButton, QLineEdit, QLabel, QGroupBox, QGridLayout, QCheckBox, QComboBox, QMenu, QSpinBox, QApplication, QStyleFactory, QFrame , QMainWindow
from PyQt5 import QtWidgets as QrealWidgets
from PyQt5.QtCore import Qt , Signal, QThread, pyqtSignal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("__filename__"))))

from LibrairieVSDAna.ReadVSDfile import GetVSD_Data, GetVSD_FileList
from LibrairieVSDAna.masks import CreateEmptyMask, UpdateMask, MaskIN, MaskOUT, MaskCompatibility
from LibrairieVSDAna.VSDprocessing import ProcessDataExternal

from LibUtils import image, optimization, database_IO, plots

import sqlalchemy as sql
import scipy.ndimage as scp

class SuperSlider(QrealWidgets.QWidget):

    ValueChange = Signal()
    MouseReleased = Signal()

    def __init__(self, parent=None,  **kwargs):
        super(SuperSlider, self).__init__()

        l = QGridLayout(self)

        self.Slider = QSlider(Qt.Horizontal, self)
        self.Readout = QLabel("-")
        self.LeftButton = QPushButton("<")
        self.RightButton = QPushButton(">")

        self.Readout.setMaximumWidth(30)
        self.LeftButton.setMaximumWidth(20)
        self.RightButton.setMaximumWidth(20)

        if 'minimum' in kwargs :
            minimum = kwargs.get('minimum')
            self.Slider.setMinimum(minimum)

        if 'maximum' in kwargs :
            maximum = kwargs.get('maximum')
            if maximum < minimum :
                raise ValueError("Min slider value is higher than max slider value")
            else :
                self.Slider.setMaximum(maximum)

        if 'start' in kwargs :
            start = kwargs.get('start')
            if start >= minimum and start <= maximum:
                self.Slider.setValue(start)
            else :
                self.Slider.setValue(self.Slider.minimum())
        else :
            self.Slider.setValue(self.Slider.minimum())
        self.Readout.setText(str(self.Slider.value()))


        self.Slider.sliderReleased.connect(self.MouseReleased_emiter)
        self.Slider.valueChanged.connect(self.ValueChanged_emiter)

        self.LeftButton.pressed.connect(self.MoveLeft)
        self.RightButton.pressed.connect(self.MoveRight)

        l.addWidget(self.Slider,0,0,1,8)
        l.addWidget(self.Readout,0,8,1,1)
        l.addWidget(self.LeftButton,0,9,1,1)
        l.addWidget(self.RightButton,0,10,1,1)

        self.setMaximumHeight(50)
        self.setLayout(l)

    def MoveLeft(self):
        if self.Slider.value()-1 >= self.Slider.minimum():
            self.Slider.setValue(self.Slider.value()-1)
            self.MouseReleased_emiter()

    def MoveRight(self):
        if self.Slider.value()+1 <= self.Slider.maximum():
            self.Slider.setValue(self.Slider.value()+1)
            self.MouseReleased_emiter()

    def MouseReleased_emiter(self):
        ''' Punch the bag '''
        self.MouseReleased.emit()
    def ValueChanged_emiter(self):
        self.Readout.setText(str(self.Slider.value()))
        ''' Punch the bag '''
        self.ValueChange.emit()

    def SetValueAndEmit(self,value):
        self.Slider.setValue(value)
        #self.ValueChange.emit()

class CanvasHandle(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100, *args, **kwargs):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)

        self.fig.subplots_adjust(left=0.03,right=0.97,
                            bottom=0.03,top=0.97,
                            hspace=0.2,wspace=0.2)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.rc = {"axes.spines.left" : False,
                  "axes.spines.right" : False,
                  "axes.spines.bottom" : False,
                  "axes.spines.top" : False,
                  "xtick.bottom" : False,
                  "xtick.labelbottom" : False,
                  "ytick.labelleft" : False,
                  "ytick.left" : False}

class DynamicCanvas(CanvasHandle):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):

        CanvasHandle.__init__(self, *args, **kwargs)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.cbar = False
        self.EnforceType = False
        self.cbarON = False
        self.Spines = False

    def Enforce(self,Type):
        if Type == '3D' :
            self.fig.clf()
            self.cbar = False
            self.axes = self.fig.add_subplot(111, projection = '3d')
        else :
            self.fig.clf()
            self.cbar = False
            self.axes = self.fig.add_subplot(111)

        self.EnforceType = Type

    def StartTimer(self, millis = 1000):
        self.timer.start(millis)

    def StopTimer(self):
        self.timer.stop()

    def identifyDtype(self,item):

        if type(item) == dict:
            dtype = 'multi'
        else :
            if type(item) == np.ndarray or type(item) == np.ma.core.MaskedArray:
                    Shape = np.shape(item)
                    if len(Shape) == 1:
                        dtype = '1Dy'
                    else :
                        if len(Shape) == 2 and np.min(Shape) == 1:
                            dtype = '1Dy'
                        elif len(Shape) == 2 and np.min(Shape) == 2:
                            dtype = '1Dxy'
                        elif len(Shape) == 2 and np.min(Shape) > 2:
                            dtype = '2Dgrey'
                        elif len(Shape) == 3 and np.min(Shape) == 3:
                            dtype = '2Dcolor'
                        elif len(Shape) > 3 :
                            dtype = '3D'
                        else :
                            dtype = 'pass'
            elif type(item) == list :
                dtype = '1Dy'
            elif type(item) == tuple and len(item) == 2:
                dtype = '1Dxy'
            else :
                dtype = 'pass'
                raise ValueError("Datatype {} with shape {} not understood".format(type(item),np.shape(item)))

            if dtype != 'pass' and self.EnforceType is not False :
                dtype = self.EnforceType
        return dtype

    def activateColorBar(self,Bool):
        self.cbarON = Bool

    def formatDatatype(self,item,dtype,**kwargs):
        if dtype == '1Dy':
            if type(item) == list:
                X = np.arange(len(item))
            else :
                X = np.arange(np.shape(item)[0])
            self.write1Dfigure(X,item,**kwargs)
        elif dtype == '1Dxy':
            if type(item) == tuple:
                X = item[0]
                Y = item[1]
            else :
                X = item[:,0]
                Y = item[:,1]
            self.write1Dfigure(X,Y,**kwargs)
        elif dtype == '2Dgrey' or dtype == '2Dcolor':
            self.write2Dfigure(item,**kwargs)
        elif dtype == '3D':
            X, Y = np.meshgrid(np.arange(0,np.shape(item)[1]), np.arange(0,np.shape(item)[0]))
            Z = item
            self.write3Dfigure(X, Y, Z,**kwargs)
        else :
            pass




    def write1Dfigure(self,X,Y,**kwargs):

        if 'vmin' in kwargs:
            kwargs.get('vmin')
            kwargs.get('vmin')

        self.axes.plot(X,Y, **kwargs)
        self.axes.set_aspect('auto')
        self.draw()

    def write2Dfigure(self,frame,**kwargs):

        supLines = kwargs.get("Lines",None)
        cmap = kwargs.get("cmap", None)
        if cmap == "geo":
            cmap = plots.cmap_GEO()

        if self.cbarON :
            if self.cbar :
                self.cbar.remove()
            im = self.axes.imshow(frame, **kwargs)
            self.cbar = self.fig.colorbar(im, ax = self.axes )
        else :
            if self.cbar :
                self.fig.clf()
                self.axes = self.fig.add_subplot(111)
                self.cbar = False
            self.axes.imshow(frame, **kwargs)

        if supLines is not None :
            for index, row in supLines.iterrows():
                linekwargs = row.to_dict()
                linekwargs.pop("x",None)
                linekwargs.pop("y",None)
                stop = linekwargs.pop("stop",None)
                start = linekwargs.pop("start",None)
                self.axes.plot( row["x"][start:stop] , row["y"][start:stop] , **linekwargs )

        self.axes.set_aspect('equal')
        if not self.Spines :
            self.axes.axis("off")


        # self.axes.spines['right'].set_visible(False)
        # self.axes.spines['top'].set_visible(False)
        # self.axes.spines['left'].set_visible(False)
        # self.axes.spines['bottom'].set_visible(False)
        # self.axes.tick_params(axis = 'both', which = 'both,',left=False, bottom=False, labelleft = False, labelbottom=False)
        self.draw()


    def write3Dfigure(self,X, Y, Z,**kwargs):

        if 'Zmin' in kwargs :
            Zmin = kwargs.get('Zmin')
            kwargs.pop('Zmin')
        else : Zmin = False

        if 'Zmax' in kwargs :
            Zmax = kwargs.get('Zmax')
            kwargs.pop('Zmax')
        else : Zmax = False

        if self.cbarON :
            if self.cbar :
                self.cbar.remove()
            surf = self.axes.plot_surface(X, Y, Z, **kwargs)
            self.cbar = self.fig.colorbar(surf, ax = self.axes, shrink=0.5, aspect=5)
        else :
            if self.cbar :
                self.fig.clf()
                self.axes = self.fig.add_subplot(111, projection = '3d')
                self.cbar = False
            surf = self.axes.plot_surface(X, Y, Z, **kwargs)

        if self.Spines :
            if Zmin and Zmax:
                self.axes.set_zlim(Zmin,Zmax)
        else :
            self.axes.axis("off")

        self.draw()

    def update_figure(self, Data, **kwargs):
        self.axes.cla()
        dtype = self.identifyDtype(Data)

        if dtype == 'multi' :
            for key in Data:
                Value = Data[key]
                sitem = Value[0]
                sdtype = Value[1]
                sdkwargs = Value[2]
                self.formatDatatype(sitem,sdtype,sdkwargs)
        else :
            self.formatDatatype(Data,dtype,**kwargs)


class TestApp(QtWidgets.QWidget):

    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        #self.menuBar().addMenu(self.file_menu)

        # self.help_menu = QtWidgets.QMenu('&Help', self)
        # self.menuBar().addSeparator()
        # self.menuBar().addMenu(self.help_menu)

        # self.help_menu.addAction('&About', self.about)

        self.canvas = DynamicCanvas(self)
        self.canvas.update_figure( np.random.random((50,50)) )
        #self.setCentralWidget(self.canvas)
        #self.addToolBar(NavigationToolbar(self.canvas, self))

        self.runButton1 = QtWidgets.QPushButton('End')
        self.process = QtCore.QProcess(self)
        self.process.readyRead.connect(self.dataReady)
        self.runButton1.clicked.connect(self.process.kill)

        l = QtWidgets.QGridLayout(self)

        self.SupSlider = SuperSlider( minimum = -100, maximum = 100, start = 0)

        l.addWidget(self.canvas,0,0,1,1)
        l.addWidget(self.SupSlider,1,0,1,1)

        l.setSpacing(2)
        l.setContentsMargins(2,2,2,2)

        self.setLayout(l)

        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About", "tg")

import threading


class LoadVideo(threading.Thread):

    #LoadIntermediateFrame = pyqtSignal()
    #LoadFullFile = pyqtSignal()

    def __init__(self):
        super(LoadVideo, self).__init__()

        self.qApp = QtWidgets.QApplication(sys.argv)
        self.aw = TestApp()
        self.data = None
        self.daemon = True
        self.start()

    def run(self):
        pass
        #self.aw.show()
        #self.qApp.exec()

        #self.qApp = QtWidgets.QApplication(sys.argv)

        #self.aw = TestApp()
        #self.aw.setWindowTitle("%s" % sys.argv[0])

        #sys.exit(self.qApp.exec())

        #self.LoadFullFile.emit()


class data_update_checker(QThread):
    pass


class interactive_plot():

    def __init__(data = None, **kwargs):

        self.data = data

        run = kwargs.get("run",True)

        self.thread = None
        self.appname = kwargs.get(appname,None)

        if run :
            self.run

    def run(self,**kwargs):

        try :
            if self.data is None :
                raise ValueError("Can't start GUI without setting data. Either specify data in arguments to interactive_plot or use add_data method before calling run")

                if self.thread is not None and kwargs.get(exit,False):
                    self.thread.stop()
                    self.thread.join()
                    #del self.thread
                    self.thread = None
                kwargs.pop("exit",None)
                if self.thread is None or not self.thread.is_alive() :
                    #del self.thread
                    self.thread = QappThread(self.data, appname = self.appname)

                else :
                    print("The application is still running. If you want to quit it, use kwarg exit = True when calling run")

        except Exception as e:
            print(e)

    def add_data(self,data,**kwargs):
        pass

    class QappThread(threading.Thread):

        def __init__(data, **kwargs ):

            appname = kwargs.get(appname,None)
            kwargs.pop("appname",None)
            if appname is None :
                self.application = "TestApp"
            else :
                self.application = appname
            self.kwargs = kwargs
            self.data = data
            self.returned = None

        def run(self):

            super(LoadVideo, self).__init__()

            #self.app = QtWidgets.QApplication(sys.argv)
            self.dialog = eval( self.application+"(self.data,**self.kwargs)" )
            self.daemon = True
            self.dialog.show()
            #self.dialog.exec()
            self.returned = dialog.Save()





def TestRun():
    global aw
    qApp = QtWidgets.QApplication(sys.argv)
    aw = TestApp()
    aw.show()
    sys.exit(qApp.exec_())

if __name__ == "__main__":

    #thrd = threading.Thread(target=TestRun)

    thrd = LoadVideo()
    #thrd.daemon = True
    #thrd.start()
    #global aw
    #aw.canvas.update_figure( np.random.random((100,100)) )
    # progname = os.path.basename(sys.argv[0])
    # qApp = QtWidgets.QApplication(sys.argv)

    # aw = TestApp()
    # aw.setWindowTitle("%s" % progname)
    # aw.show()
    # sys.exit(qApp.exec_())