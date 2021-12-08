# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 15:36:11 2020

@author: Timothe
"""

import sys, os#, time
import numpy as np
import cv2

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib

matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QSlider, QPushButton, QLineEdit, QLabel, QGroupBox, QGridLayout, QCheckBox, QComboBox, QMenu, QSpinBox, QApplication, QStyleFactory, QFrame , QMainWindow
from PyQt5 import QtWidgets as QrealWidgets
from PyQt5.QtCore import Qt , Signal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("__filename__"))))

from LibrairieVSDAna.ReadVSDfile import GetVSD_Data, GetVSD_FileList
from LibrairieVSDAna.masks import CreateEmptyMask, UpdateMask, MaskIN, MaskOUT, MaskCompatibility
from LibrairieVSDAna.VSDprocessing import ProcessDataExternal

from LibUtils import image, optimization, database_IO, plots

import sqlalchemy as sql
import scipy.ndimage as scp

import pyprind

from rasterio.fill import fillnodata

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


class PixelAreaTimeWidget(QMainWindow):

    def __init__(self, parent=None):

        QtWidgets.QMainWindow.__init__(self)

        self.main_widget = QtWidgets.QWidget(self)

        self.canvas = DynamicCanvas(self.main_widget, width=5, height=4, dpi=100)

        l = QtWidgets.QVBoxLayout(self.main_widget)

        l.addWidget(self.canvas)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def SetData():

        pass


class Plot1DWidget(QrealWidgets.QWidget):

    def __init__(self, parent=None):
        super(Plot1DWidget, self).__init__()

        l = QtWidgets.QVBoxLayout(self)

        self.canvas = DynamicCanvas(self, width=5, height=4, dpi=100)
        self.SupSlider = SuperSlider( minimum = -100, maximum = 100, start = 0)

        l.addWidget(self.canvas)
        l.addWidget(self.SupSlider)

        self.setLayout(l)

    def SetData():

        pass

class Plot2DWidget(QrealWidgets.QWidget):

    def __init__(self, parent=None):
        super(Plot2DWidget, self).__init__()

        l = QtWidgets.QVBoxLayout(self)

        self.canvas = DynamicCanvas(self, width=5, height=4, dpi=100)
        self.SupSlider = SuperSlider( minimum = -100, maximum = 100, start = 0)


        l.addWidget(self.canvas)
        l.addWidget(self.SupSlider)

        self.setLayout(l)

    def SetData(frame):

        pass

class Plot3DWidget(QrealWidgets.QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(Plot3DWidget, self).__init__()

        l = QtWidgets.QGridLayout(self)

        self.canvas = DynamicCanvas(self, **kwargs)
        self.SupSlider = SuperSlider( minimum = -100, maximum = 100, start = 0)
        self.BuildControlBox()
        self.BuildColorAdjustBox()

        l.addWidget(self.canvas,0,0,1,2)
        l.addWidget(self.ColorAdjustBox,1,0,2,1)
        l.addWidget(self.SupSlider,1,1,1,1)
        l.addWidget(self.ControlBox,2,1,1,1)

        l.setSpacing(2)
        l.setContentsMargins(2,2,2,2)

        self.rootPath = ""

        self.setLayout(l)

        self.LowCMode = True # lowComputation Mode, le

        self.MaskMode = False

        self.Spines = False
        self.canvas.Spines = self.Spines

        self.Enforce = False
        self.canvas.Enforce(self.Enforce)

        self.frame = 0

        self.SetData(np.repeat(image.Empty_img(500,500)[:,:,np.newaxis], 2, axis = 2))
        self.UpdateFrame(cmap='gray')

        self.ControlBox.setDisabled(True)

        self.ColorBar = True
        self.canvas.activateColorBar(self.ColorBar)


        self.SupSlider.ValueChange.connect(self.SetFrame)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

        self.RepairMask = None
        self.ExcludeMask = None
        self.BarrelMask = None
        self.Cropcoords = []

        self.TimePoint = []

        self.SupLines = None

    def showMenu(self,pos):
        menu = QMenu()

        if not self.LowCMode :
            if self.ControlBox.isVisible():
                VisibilityCtrlBox = menu.addAction("Hide Control Box")
                V = False
            else :
                VisibilityCtrlBox = menu.addAction("Show Control Box")
                V = True

        if self.ColorBar:
            VisibleColorBar = menu.addAction("Hide Color Scale")
            CB = False
        else :
            VisibleColorBar = menu.addAction("Show Color Scale")
            CB = True

        if self.Spines :
            ShowSpines = menu.addAction("Hide axes")
            SP = False
        else :
            ShowSpines = menu.addAction("Show axes")
            SP = True

        menu.addSeparator()####################################

        if self.Enforce :
            EnforceMode = menu.addAction("Display 2D plot")
            EN = False

        else :
            EnforceMode = menu.addAction("Display 3D plot")
            EN = '3D'

        if not self.LowCMode :
            if self.MaskMode:
                EnterMaskMode = menu.addAction("Quit Mask edit mode")
                M = False
            else :
                EnterMaskMode = menu.addAction("Enter Mask edit mode")
                M = True


        TimePointOption = menu.addAction("Show pixel time course")

        RAMdisp = menu.addAction("Print RAM usage")



        action = menu.exec_(self.mapToGlobal(pos))
        if not self.LowCMode :
            if action == VisibilityCtrlBox:
                self.ControlBox.setVisible(V)

        if action == VisibleColorBar:
            self.ColorBar = CB
            self.canvas.activateColorBar(self.ColorBar)
            self.UpdateFrame()

        if not self.LowCMode :
            if action == EnterMaskMode:
                self.SetMaskMode(M)

        if action == EnforceMode:
            self.Enforce = EN
            self.canvas.Enforce(self.Enforce)
            self.UpdateFrame()

        if action == ShowSpines:
            self.Spines = SP
            self.canvas.Spines = self.Spines
            self.UpdateFrame()

        if action == RAMdisp :
            self.PrintRAMUsage()

        if action == TimePointOption :
            self.TimePoint.append(PixelAreaTimeWidget(self))
            self.TimePoint[len(self.TimePoint)-1].show()

    def SetMaskMode(self,Bool):
        self.MaskMode = Bool

        if self.MaskMode :
            self.coords = []
            self.Drag = False
            self.cid = self.canvas.fig.canvas.mpl_connect('button_press_event', self.onclick)
            # self.canvas.setCursor(Qt.CrossCursor)
            #self.setCursor(QCursor(Qt.CrossCursor))
            QApplication.setOverrideCursor(Qt.CrossCursor)
            self.ProcessData()


        else :
            self.canvas.fig.canvas.mpl_disconnect(self.cid)
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            QApplication.restoreOverrideCursor()
            #self.setCursor(QCursor(Qt.ArrowCursor))
            # self.canvas.setCursor(Qt.ArrowCursor)
            MaskOUT(self.RepairMask,self.rootPath,r"DataProcessing\Expect_2\Mouse32\200722_VSD1")
            MaskOUT(self.BarrelMask,self.rootPath,r"MICAM\VSD\Mouse32\FunctionnalMapping","open_barrelmask.png")
            self.ProcessData()

    def onclick(self,event):
        ix, iy = event.xdata, event.ydata
        QApplication.setOverrideCursor(Qt.CrossCursor)
        if event.button == 1:
            print( 'x = {}, y = {}'.format(ix,iy))
            if ix is not None and iy is not None :
                self.ModifySelectedMask(int(round(ix)),int(round(iy)))


        if event.button == 2:
            if self.Drag :
                self.Drag.append([ix, iy])
                print('rectangle at : {}'.format(self.Drag))
                self.Drag = False
            else :
                self.Drag = [[ix, iy]]

    def MaskExists(self,mask):

        if type(mask) is not np.ndarray :
            mask = CreateEmptyMask(self.RawDATA)
        return mask

    def ModifySelectedMask(self,X,Y):

        crop = self.GetCropValues()

        chk = []
        if self.RepairMaskChkBox.isChecked():
            chk.append('repair')

        if self.ExcludeMaskChkBox.isChecked():
            chk.append('exclude')

        if self.BarrelsChkBox.isChecked():
            chk.append('barrel')

        if len(chk) == 1:

            if chk[0] == 'repair':
                self.RepairMask = self.MaskExists(self.RepairMask)
                self.RepairMask = UpdateMask(self.RepairMask,crop[0] + X, crop[2] + Y)

            elif chk[0] == 'exclude':
                self.ExcludeMask = self.MaskExists(self.ExcludeMask)
                self.ExcludeMask = UpdateMask(self.ExcludeMask,crop[0] + X, crop[2] + Y)

            elif chk[0] == 'barrel':
                self.BarrelMask = self.MaskExists(self.BarrelMask)
                self.BarrelMask = UpdateMask(self.BarrelMask,crop[0] + X, crop[2] + Y)

        self.ProcessData()


    def BuildColorAdjustBox(self):

        self.ColorAdjustBox = QGroupBox()
        self.ColorAdjustBox.setTitle('Color settings')

        self.IMax = QLineEdit("0.02")
        self.IMin = QLineEdit("-0.015")
        self.IAuto = QCheckBox("Auto")
        self.IAuto.setChecked(True)
        self.Cmap = QComboBox()

        self.Cmap.addItems(['gray','jet', 'geo' ,'plasma', 'inferno', 'magma','Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu','GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
            'binary', 'gist_yarg', 'gist_gray', 'bone', 'pink','spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper','PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu','RdYlBu', 'RdYlGn', 'Spectral',
            'coolwarm', 'bwr', 'seismic','Pastel1', 'Pastel2', 'Paired', 'Accent','Dark2', 'Set1', 'Set2', 'Set3','tab10', 'tab20',
            'tab20b', 'tab20c','flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern','gnuplot', 'gnuplot2', 'CMRmap',
            'cubehelix', 'brg', 'hsv','gist_rainbow', 'rainbow', 'viridis', 'nipy_spectral', 'gist_ncar', 'None'])

        self.Cmap.setMaxVisibleItems(6)

        self.IMax.setMaximumWidth(50)
        self.IMin.setMaximumWidth(50)
        self.Cmap.setMaximumWidth(80)


        self.IMax.returnPressed.connect(self.ProcessData)
        self.IMin.returnPressed.connect(self.ProcessData)
        self.IAuto.stateChanged.connect(self.ProcessData)
        self.Cmap.currentIndexChanged.connect(self.ProcessData)

        l = QGridLayout()

        l.addWidget(QLabel("Cmap"),0,0,1,1)
        l.addWidget(QLabel("Max"),1,0,1,1)
        l.addWidget(QLabel("Min"),2,0,1,1)
        l.addWidget(QLabel("Auto"),3,0,1,1)

        l.addWidget(self.Cmap,0,1,1,1)
        l.addWidget(self.IMax,1,1,1,1)
        l.addWidget(self.IMin,2,1,1,1)
        l.addWidget(self.IAuto,3,1,1,1)

        l.setSpacing(2)
        l.setContentsMargins(2,2,2,2)

        self.ColorAdjustBox.setLayout(l)
        self.ColorAdjustBox.setMaximumWidth(150)

    def BuildControlBox(self):

        self.ControlBox = QFrame()

        FilterBox = QGroupBox()
        FilterBox.setTitle('Filtering')

        self.Interp = QComboBox()
        self.Interp.addItems(['None','2D','3D'])
        self.InterpValue = QComboBox()
        self.InterpValue.addItems(['3','5','7','9'])

        self.Interp.setMaximumWidth(50)
        self.InterpValue.setMaximumWidth(50)

        self.Interp.currentIndexChanged.connect(self.ProcessData)
        self.InterpValue.currentIndexChanged.connect(self.ProcessData)

        l = QGridLayout()

        l.addWidget(self.Interp,1,1,1,1)
        l.addWidget(self.InterpValue,2,1,1,1)

        l.setSpacing(2)
        l.setContentsMargins(2,2,2,2)

        FilterBox.setLayout(l)

        #########################

        VSDCalculationsBox = QGroupBox()
        VSDCalculationsBox.setTitle('Calculations')

        self.Substract = QCheckBox("\u0394F/F") # \u0394 = delta character
        self.SubstractFrame = QSpinBox()
        self.SubstractFrame.setRange(0,500)
        self.SubstractFrame.setValue(25)
        self.Average = QSpinBox()
        self.Average.setRange(0,100)
        self.Average.setValue(50)

        self.SubstractFrame.setMaximumWidth(50)
        self.Average.setMaximumWidth(50)

        self.Substract.stateChanged.connect(self.ProcessData)
        self.SubstractFrame.valueChanged.connect(self.ProcessData)
        self.Average.valueChanged.connect(self.ProcessData)


        l = QGridLayout()


        l.addWidget(QLabel(""),0,0,1,1)
        l.addWidget(QLabel("Center frame"),1,0,1,1)
        l.addWidget(QLabel("+/- frames"),2,0,1,1)

        l.addWidget(self.Substract,0,1,1,1)
        l.addWidget(self.SubstractFrame,1,1,1,1)
        l.addWidget(self.Average,2,1,1,1)


        l.setSpacing(2)
        l.setContentsMargins(2,2,2,2)

        VSDCalculationsBox.setLayout(l)
        #########################

        MasksBox = QGroupBox()
        MasksBox.setTitle('Masking')

        self.RepairMaskChkBox = QCheckBox("Repair Mask")
        self.ExcludeMaskChkBox = QCheckBox("Exclude Mask")
        self.BarrelsChkBox = QCheckBox("Barrel Mask")

        self.RepairMaskChkBox.stateChanged.connect(self.ProcessData)
        self.ExcludeMaskChkBox.stateChanged.connect(self.ProcessData)
        self.BarrelsChkBox.stateChanged.connect(self.ProcessData)

        l = QGridLayout()

        l.addWidget(self.RepairMaskChkBox,0,0,1,1)
        l.addWidget(self.ExcludeMaskChkBox,1,0,1,1)
        l.addWidget(self.BarrelsChkBox,2,0,1,1)

        l.setSpacing(2)
        l.setContentsMargins(2,2,2,2)

        MasksBox.setLayout(l)
        #########################

        CropBox = QGroupBox()
        CropBox.setTitle('Cropping')

        self.Cropxmin = QSpinBox()
        self.Cropxmin.setRange(0,100)
        self.Cropxmin.setValue(0)

        self.Cropxmax = QSpinBox()
        self.Cropxmax.setRange(0,100)
        self.Cropxmax.setValue(100)

        self.Cropymin = QSpinBox()
        self.Cropymin.setRange(0,100)
        self.Cropymin.setValue(0)

        self.Cropymax = QSpinBox()
        self.Cropymax.setRange(0,100)
        self.Cropymax.setValue(100)

        self.Cropxmin.valueChanged.connect(self.ProcessData)
        self.Cropxmax.valueChanged.connect(self.ProcessData)
        self.Cropymin.valueChanged.connect(self.ProcessData)
        self.Cropymax.valueChanged.connect(self.ProcessData)

        l = QGridLayout()

        l.addWidget(QLabel("Crop values"),0,0,1,2)
        l.addWidget(self.Cropxmin,1,0,1,1)
        l.addWidget(self.Cropxmax,1,1,1,1)
        l.addWidget(self.Cropymin,2,0,1,1)
        l.addWidget(self.Cropymax,2,1,1,1)

        l.setSpacing(2)
        l.setContentsMargins(2,2,2,2)

        CropBox.setLayout(l)
        #########################

        l = QGridLayout()


        l.addWidget(FilterBox,0,0,1,1)
        l.addWidget(VSDCalculationsBox,0,1,1,1)
        l.addWidget(MasksBox,0,2,1,1)
        l.addWidget(CropBox,0,3,1,1)

        l.setSpacing(2)
        l.setContentsMargins(2,2,2,2)

        self.ControlBox.setLayout(l)

    def setColorFavorites(self):
        if self.LowCMode == True :
            self.IMax.setText("200")
            self.IMin.setText("20")
            self.IAuto.setChecked(False)
        else :
            if self.Substract.isChecked():
                pass
            #TODO

    def PrintRAMUsage(self):
        print("\nShowing Ram Usage :\nInside class:")
        for name, size in sorted(((name, sys.getsizeof(value)) for name, value in vars(self).items()),key= lambda x: -x[1])[:10]:
            print("{:>30}: {:>8}".format(name, optimization.sizeof_fmt(size)))
        print("\nOutsideClass :")
        for name, size in sorted(((name, sys.getsizeof(value)) for name, value in globals().items()),key= lambda x: -x[1])[:10]:
            print("{:>30}: {:>8}".format(name, optimization.sizeof_fmt(size)))

    def setlowCM(self,CM):

        if CM :
            self.ControlBox.setVisible(False)
            self.LowCMode = True
            self.ColorBar = False
            self.canvas.activateColorBar(self.ColorBar)
        else :
            self.ControlBox.setVisible(True)
            self.LowCMode = False
            self.ColorBar = True
            self.canvas.activateColorBar(self.ColorBar)

        self.setColorFavorites()

    def LoadData(self,path,dtype,**kwargs):

        print(f"Opening {path}")

        if "memoryusage" in kwargs :
            memorytype = kwargs.get('memoryusage')
        else :
            memorytype = 'RAM'

        if "rot" in kwargs:
            rotation = kwargs.get("rot")
        else :
            rotation = 0

        if memorytype == 'RAM' :
            if dtype == 'VSD':
                self.setlowCM(False)
                temp, self.signals, _ = GetVSD_Data(path)
                self.SetData(temp)

            elif dtype == 'BEH':
                videoHandle = cv2.VideoCapture(path,cv2.IMREAD_GRAYSCALE)
                #width  = int(videoHandle.get(cv2.CAP_PROP_FRAME_WIDTH))
                #height = int(videoHandle.get(cv2.CAP_PROP_FRAME_HEIGHT))
                length = int(videoHandle.get(cv2.CAP_PROP_FRAME_COUNT))



                bar = pyprind.ProgBar(length/10,bar_char='░', title=f'loading BEHAVIOR :{path}')

                for i in range(length):
                    _ , IMG = videoHandle.read()

                    if rotation != 0 :
                        IMG = np.rot90(IMG,rotation)

                    if i == 0:
                        FrameArray = np.empty((np.shape(IMG)[0],np.shape(IMG)[1],length),dtype=np.uint8)

                    FrameArray[:,:,i] = IMG[:,:,0]
                    if i % 10 == 0:
                        bar.update()
                del bar
                self.setlowCM(True)
                self.SetData(FrameArray)
            else :
                raise ValueError(f"Load data from path for type {dtype} not understood / available")

            self.ProcessData()

        elif memorytype == 'DISK':
            #TODO
            raise ValueError(f"memory usage type {memorytype} not yet implemented")
        elif memorytype == 'OPTIMIZED':
            #TODO
            raise ValueError(f"memory usage type {memorytype} not yet implemented")
        else:
            raise ValueError(f"memory usage type {memorytype} not understood")

    def SetFrame(self):
        self.frame = self.SupSlider.Slider.value()
        self.UpdateFrame()

    def SetData(self,DATA,**kwargs):

        self.RawDATA = DATA

        self.SupSlider.Slider.setMinimum(0)
        if len(np.shape(self.RawDATA)) > 2:
            self.SupSlider.Slider.setMaximum(np.shape(self.RawDATA)[2]-1)
        else :
            self.SupSlider.Slider.setMaximum(0)

        if not self.LowCMode :
            self.Cropxmax.setMaximum(np.shape(self.RawDATA)[0])
            #self.Cropxmax.setValue(np.shape(self.RawDATA)[0])
            self.Cropymax.setMaximum(np.shape(self.RawDATA)[1])
            #self.Cropymax.setValue(np.shape(self.RawDATA)[1])

            self.Proc_DATA = np.copy(self.RawDATA)

            #self.RepairMask = MaskIN(15,self.rootPath,r"DataProcessing\Expect_1\Mouse25\200303_VSD1")
            #self.BarrelMask = MaskIN(15,self.rootPath,r"MICAM\VSD\Mouse25\BarrelMap","BarrelMask.png")

            self.RepairMask = MaskIN(os.path.join(self.rootPath,r"DataProcessing\Expect_2\Mouse32\200722_VSD1","Repairmask.png"))
            self.BarrelMask = MaskIN(os.path.join(self.rootPath,r"MICAM\VSD\Mouse32\FunctionnalMapping","open_barrelmask.png"))

        self.ControlBox.setDisabled(False)

        self.SupLines = kwargs.get("supdata",None)

    def GetCropValues(self):

        cropxmin = int(self.Cropxmin.value())
        cropxmax = int(self.Cropxmax.value())
        cropymin = int(self.Cropymin.value())
        cropymax = int(self.Cropymax.value())

        return [cropxmin,cropxmax,cropymin,cropymax]


    def ProcessData(self):

        if not self.LowCMode and len(np.shape(self.RawDATA)) > 2:

            crop = self.GetCropValues()

            if self.RepairMaskChkBox.isChecked():
                RepairMa = self.MaskExists(self.RepairMask)
            else :
                RepairMa = None

            if self.BarrelsChkBox.isChecked():
                BarrelMa = self.MaskExists(self.BarrelMask)
            else :
                BarrelMa = None

            if not self.MaskMode :
                displayrep = False
            else :
                displayrep = True

            if self.Substract.isChecked() == True:
                substracttion = [self.SubstractFrame.value(),self.Average.value()]
            else :
                substracttion = None

            self.Proc_DATA = ProcessDataExternal(self.RawDATA, crops = crop, displayrepair = displayrep, repairMask = RepairMa, barrelmask = BarrelMa, substract = substracttion , substractmethod = "ratio", Interpmode = self.Interp.currentText(), Interpvalue = int(self.InterpValue.currentText())  )

        self.UpdateFrame()

    def ProcessDataOld(self):

        if not self.LowCMode and len(np.shape(self.RawDATA)) > 2:

            crops = self.GetCropValues()

            self.Proc_DATA = np.copy(self.RawDATA[crops[0] : crops[1] , crops[2] : crops[3] , :])

            ##################### repairing
            if self.RepairMaskChkBox.isChecked():
                self.RepairMask = self.MaskExists(self.RepairMask)
                notempty, derivedmask = MaskCompatibility(self.RepairMask,crops)

                if notempty:

                    if not self.MaskMode :
                        tempmask = np.invert(derivedmask).astype(int)
                        for F in range(np.shape(self.Proc_DATA)[2]):
                           self.Proc_DATA[:,:,F] = fillnodata(self.Proc_DATA[:,:,F] ,mask = tempmask , max_search_distance = 10, smoothing_iterations=0)
                    else :
                        tempmask = np.repeat(derivedmask[:,:,np.newaxis],np.shape(self.Proc_DATA)[2],axis = 2)
                        self.Proc_DATA = np.ma.masked_where(tempmask == True, self.Proc_DATA)

            #################### susbtracting
            if self.Substract.isChecked() == True:

                self.Proc_DATA = self.Proc_DATA.astype(np.float32)

                AvgMinframe = int(self.SubstractFrame.value()) - int((int(self.Average.value())-1)/2)
                AvgMaxframe = int(self.SubstractFrame.value()) + int((int(self.Average.value())-1)/2)
                if AvgMinframe < 0 :
                    AvgMinframe = 0
                    print("Error making average of {} frames around frame {} - Negaztive index".format(self.Average.text(),self.SubstractFrame.text()))
                if AvgMaxframe > np.shape(self.Proc_DATA)[2]-1 :
                    AvgMaxframe = np.shape(self.Proc_DATA)[2]-1
                    print("Error making average of {} frames around frame {} - Index greater than frame count".format(self.Average.text(),self.SubstractFrame.text()))

                AvgFrame = np.mean(self.Proc_DATA[:,:,AvgMinframe:AvgMaxframe], axis = 2)
                for Idx in range(np.shape(self.Proc_DATA)[2]):
                    self.Proc_DATA[:,:,Idx] = self.Proc_DATA[:,:,Idx] / AvgFrame

            ###################### filtering
            if not self.MaskMode :
                if self.Interp.currentText() == '2D':
                    size = int(self.InterpValue.currentText())
                    self.Proc_DATA = scp.uniform_filter(self.Proc_DATA,[size,size,0])
                if self.Interp.currentText() == '3D':
                    size = int(self.InterpValue.currentText())
                    self.Proc_DATA = scp.uniform_filter(self.Proc_DATA,[size,size,size])

            ####################### pixels exclusion
            if self.ExcludeMaskChkBox.isChecked():
                notempty, derivedmask = MaskCompatibility(self.ExcludeMask,crops)

            ###################### barrel assignation / visualization
            if self.BarrelsChkBox.isChecked():
                self.BarrelMask = self.MaskExists(self.BarrelMask)
                notempty, derivedmask = MaskCompatibility(self.BarrelMask,crops)
                if notempty:
                    tempmask = np.expand_dims(derivedmask, 2)
                    tempmask = np.repeat(tempmask, np.shape(self.Proc_DATA)[2], axis = 2)
                    self.Proc_DATA = np.ma.masked_where(tempmask == True, self.Proc_DATA)

        self.UpdateFrame()

    def MakeKWARGS(self, kwargs):

        if not kwargs :
            kwargs = {}

        if not self.Cmap.currentText() == 'None':
            kwargs.update( cmap = self.Cmap.currentText())

        if self.IAuto.isChecked() == False :
            kwargs.update( vmin = float(self.IMin.text()))
            kwargs.update( vmax = float(self.IMax.text()))

            if self.Enforce == '3D':
                kwargs.update( Zmin = float(self.IMin.text()))
                kwargs.update( Zmax = float(self.IMax.text()))

        return kwargs

    def UpdateFrame(self, **kwargs):

        kwargs = self.MakeKWARGS(kwargs)

        if self.SupLines is not None :
            if 'stop' in self.SupLines:
                #self.SupLines.drop(['Stop'], axis=1)
                self.SupLines['stop'] = self.frame
            else :
                self.SupLines.insert(0, 'stop', self.frame)
            kwargs.update({"Lines" : self.SupLines})


        if not self.LowCMode and len(np.shape(self.RawDATA)) > 2 :
            if len(self.Proc_DATA.shape) > 2 :
                self.canvas.update_figure(self.Proc_DATA[:,:,self.frame],**kwargs)
            elif len(self.Proc_DATA.shape) == 2 :
                self.canvas.update_figure(self.Proc_DATA,**kwargs)
            else :
                raise ValueError("processed Data shape is not 3d or 2d np.ndarray")
        else :
            if len(self.RawDATA.shape) > 2 :
                self.canvas.update_figure(self.RawDATA[:,:,self.frame],**kwargs)
            elif len(self.RawDATA.shape) == 2 :
                self.canvas.update_figure(self.RawDATA,**kwargs)
            else :
                raise ValueError("raw Data shape is not 3d or 2d np.ndarray")


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

class AppThree(QtWidgets.QMainWindow):


    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        # self.help_menu = QtWidgets.QMenu('&Help', self)
        # self.menuBar().addSeparator()
        # self.menuBar().addMenu(self.help_menu)

        # self.help_menu.addAction('&About', self.about)

        connect_string = 'mysql+mysqlconnector://Tim:Turion162!@127.0.0.1/maze?use_pure=True'
        self.sql_engine = sql.create_engine(connect_string)

        Qplotter = Plot3DWidget(parent=self)

        self.setCentralWidget(Qplotter)

        self.addToolBar(NavigationToolbar(Qplotter.canvas, self))

        root = r"D:"
        #Folder = os.path.join(root, database_IO.GetSessionFolder(1655, self.sql_engine, FOV = 'VSD'))

        VideoPath = os.path.join(root, database_IO.GetSessionFolder(1655, self.sql_engine, FOV='topView'))

        VideoFileList = []
        for root, dirs, files in os.walk(VideoPath, topdown=True):
            for name in files:
                if name[-4:] == '.avi':
                    VideoFileList.append(os.path.join(root, name))


        print(f"Found {len(VideoFileList)} behavioral videos")

        #List = GetVSD_FileList(Folder)
        #Qplotter.LoadData(List[5],'VSD')

        Qplotter.LoadData(VideoFileList[5],'BEH')

        #Qplotter.SetData(GetVSD_Data(List[5]))

        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About", "tg")





if __name__ == "__main__":
    progname = os.path.basename(sys.argv[0])
    qApp = QtWidgets.QApplication(sys.argv)

    aw = AppThree()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())