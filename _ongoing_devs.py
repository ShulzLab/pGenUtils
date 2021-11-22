# -*- coding: utf-8 -*-
"""Boilerplate:
<EXCLUDE_MODULE_FROM_MKDOCSTRINGS>

<div id = "contributors">
Created on Tue Feb 16 19:25:15 2021
@author: Timothe
</div>
"""

import os, sys

uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
sys.path.append(uppath(__file__, 2))

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import (
    QSlider,
    QPushButton,
    QLineEdit,
    QLabel,
    QGroupBox,
    QGridLayout,
    QCheckBox,
    QComboBox,
    QMenu,
    QSpinBox,
    QApplication,
    QStyleFactory,
    QFrame,
    QMainWindow,
)
from PyQt5 import QtWidgets as QrealWidgets
from PyQt5.QtCore import Qt, Signal

import numpy as np


# -*- coding: utf-8 -*-

"""
Created on Tue Nov 24 22:19:51 2020

@author: Timothe
"""


import yaml

class DataEnvironment():

    def __init__(self,path):

        self.yaml_path = os.path.join(path,"data_environment.yaml")

        with open(self.yaml_path, 'r') as stream:
            try:
                print(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)



class SuperSlider(QrealWidgets.QWidget):

    ValueChange = Signal()
    MouseReleased = Signal()

    def __init__(self, parent=None, **kwargs):
        super(SuperSlider, self).__init__()

        l = QGridLayout(self)

        self.Slider = QSlider(Qt.Horizontal, self)
        self.Readout = QLabel("-")
        self.LeftButton = QPushButton("<")
        self.RightButton = QPushButton(">")

        self.Readout.setMaximumWidth(30)
        self.LeftButton.setMaximumWidth(20)
        self.RightButton.setMaximumWidth(20)

        if "minimum" in kwargs:
            minimum = kwargs.get("minimum")
            self.Slider.setMinimum(minimum)

        if "maximum" in kwargs:
            maximum = kwargs.get("maximum")
            if maximum < minimum:
                raise ValueError("Min slider value is higher than max slider value")
            else:
                self.Slider.setMaximum(maximum)

        if "start" in kwargs:
            start = kwargs.get("start")
            if start >= minimum and start <= maximum:
                self.Slider.setValue(start)
            else:
                self.Slider.setValue(self.Slider.minimum())
        else:
            self.Slider.setValue(self.Slider.minimum())
        self.Readout.setText(str(self.Slider.value()))

        self.Slider.sliderReleased.connect(self.MouseReleased_emiter)
        self.Slider.valueChanged.connect(self.ValueChanged_emiter)

        self.LeftButton.pressed.connect(self.MoveLeft)
        self.RightButton.pressed.connect(self.MoveRight)

        l.addWidget(self.Slider, 0, 0, 1, 8)
        l.addWidget(self.Readout, 0, 8, 1, 1)
        l.addWidget(self.LeftButton, 0, 9, 1, 1)
        l.addWidget(self.RightButton, 0, 10, 1, 1)

        self.setMaximumHeight(50)
        self.setLayout(l)

    @property
    def value(self):
        return self.Slider.value()

    def MoveLeft(self):
        if self.Slider.value() - 1 >= self.Slider.minimum():
            self.Slider.setValue(self.Slider.value() - 1)
            self.MouseReleased_emiter()

    def MoveRight(self):
        if self.Slider.value() + 1 <= self.Slider.maximum():
            self.Slider.setValue(self.Slider.value() + 1)
            self.MouseReleased_emiter()

    def MouseReleased_emiter(self):
        """Punch the bag"""
        self.MouseReleased.emit()

    def ValueChanged_emiter(self):
        self.Readout.setText(str(self.Slider.value()))
        """ Punch the bag """
        self.ValueChange.emit()

    def SetValueAndEmit(self, value):
        self.Slider.setValue(value)
        # self.ValueChange.emit()


class plot_cache:
    def __init__(self, **kwargs):
        """
        Stores the plot type (to use in python eval function later)
        Can be either :
            - "plt.plot"
            - "plt.imshow"
            - "plt.bar"
            - "plt.scatter"
            - "plt.hist"
            ... And other supported matplotlib functions.

        The compatibility between the type the user gives and the arguments or data structure
        it provides to this wrapper is not tested internally and the coherence is left up to
        the user to check or debug. Usual matplotlib errors will be raised and should help
        a python friendly user to find the issue. If needed, check the matplotlib pyplot website.

        Parameters
        ----------
        plt_type : str
            Matplotlib function name to use to plot a particular data type.

        Returns
        -------
        None.
        """

        # Necessary argument :
        self.set_data(kwargs.get("data", None))
        self.set_plt_type(kwargs.get("plt_type", None))
        # self.set_axid( kwargs.get("plt_axid" , None) )
        self.set_ax(kwargs.get("plt_ax", None))

        # Optional arguments :
        self.set_plt_params(kwargs.get("plt_params", None))
        self.set_sort_index(kwargs.get("sort_index", 2))

        self.set_plot_until_time(
            kwargs.get("plt_until", None)
        )  # list of indices to plot until, for a given time value returned by a slider in a GUI. This list must be of same size as slider min-max range and contain correspunding indices for data

        self.set_time(
            kwargs.get("time", None)
        )  # selected_index on last dimension to display different data over time when included in a GUI. Time dimension ( last ) must be the same as slider min-max range
        # Dev debug arguments :
        self.set_unwrap(kwargs.get("unwrap", None))
        self.set_name(kwargs.get("name", None))

    def set_realax(self, realaxlist: list):  # matplotlib.axes list
        self.realx = realax

    def set_data(self, data):
        if data is None:
            raise AttributeError("Data missing")
        self.data = np.array(data)

    def set_plt_type(self, plt_type: str):
        if plt_type is None:
            raise AttributeError("Plot type missing")
        self.plt_type = plt_type

    def set_ax(self, plt_ax):
        if plt_ax is None:
            raise AttributeError("Plt.Ax missing")
        self.plt_ax = plt_ax

    def set_name(self, name):
        self.name = name

    def set_sort_index(self, sort_index: int):
        self.sort_index = sort_index

    def set_time(self, time: int):
        self.time = time

    def set_plot_until_time(self, plt_until: list):
        self.plt_until = plt_until

    def set_plt_params(self, params: dict):
        self.plt_params = params

    def set_unwrap(self, unwrap: bool = True):
        if unwrap is not None:
            if unwrap:
                self.unwraper = "*"
            else:
                self.unwraper = ""
        else:
            self.__auto_set_unwrap()

    def __auto_set_unwrap(self):
        if self.plt_type == "plot":
            self.unwraper = "*"
        elif self.plt_type == "imshow":
            self.unwraper = ""
        elif self.plt_type == "scatter":
            self.unwraper = "*"
        else:
            self.unwraper = ""

    def draw(self):
        if self.time is None:
            drawsentence = f"self.plt_ax.{self.plt_type}({self.unwraper}self.data"
        else:
            if self.plt_until is not None:
                drawsentence = f"self.plt_ax.{self.plt_type}({self.unwraper}self.data[...,:{self.plt_until[self.time]}]"
            else:
                drawsentence = f"self.plt_ax.{self.plt_type}({self.unwraper}self.data[...,{self.time}]"
        if self.plt_params is None:
            drawsentence = drawsentence + ")"
        else:
            drawsentence = drawsentence + f",**self.plt_params)"

        eval(f"{drawsentence}")

    def __str__(self):
        return f"Plot item:\n\ttype: {self.plt_type}\n\tname: {self.name}\n\tsort_index: {self.sort_index}"


class ax_cache_list(list):
    def __init__(self, first_item=None, **kwargs):
        super(ax_cache_list, self).__init__()
        if first_item is not None:
            self.append(first_item)
        elif kwargs:
            self.add_cache(**kwargs)

    def sort(self):
        import operator

        super().sort(key=operator.attrgetter("sort_index"))

    def add_cache(self, **kwargs):
        self.append(plot_cache(**kwargs))

    def append(self, item):
        if len(self) > 0:
            if item.plt_ax != self[0].plt_ax:
                raise TypeError(
                    "Cannot store values of different axes inside one ax_cache_list. Use fig_cache_list to store multiple axes"
                )
            for list_item in self:
                if list_item == item:
                    return
        else:
            self.__set_ax(item.plt_ax)

        super().append(item)
        if self[len(self) - 1].name is None:
            self[len(self) - 1].set_name(
                f"item_{self[len(self)-1].plt_type}_n{len(self)-1}"
            )
        self.sort()

    def shift(self, start_index, shift_amount=1):
        for idx, item in enumerate(self):
            if idx >= start_index:
                self[idx].set_sort_index(self[idx].sort_index + shift_amount)

    def draw(self):
        for item in self:
            item.draw()

    def __set_ax(self, ax):
        self.plt_ax = ax

    def __str__(self):
        printstr = "ax_cache_list:\n\t["
        for idx, item in enumerate(self):
            if idx > 0:
                printstr = printstr + ",\n\t "
            printstr = printstr + item.__str__().replace("\t", "\t\t")
        return printstr + "\n\t]"

    def set_time(self, time):
        for item in self:
            if item.time is not None:
                item.set_time(time)


class fig_cache_list(list):
    def __init__(self, first_item=None, **kwargs):
        super(fig_cache_list, self).__init__()
        if first_item is not None:
            self.append(first_item)
        elif kwargs:
            self.add_cache(**kwargs)

    def add_cache(self, **kwargs):
        self.append(plot_cache(**kwargs))

    def __search_ax_index(self, ax_handle):
        if len(self) > 0:
            for idx, item in enumerate(self):
                if item.plt_ax == ax_handle:
                    return idx
            return None
        else:
            return None

    def append(self, item):
        if type(item) == ax_cache_list:
            super_index = self.__search_ax_index(item.plt_ax)
            if super_index is None:
                super().append(item)
            else:
                for item_list in item:
                    super().__getitem__(super_index).append(item_list)
        elif type(item) == plot_cache:
            super_index = self.__search_ax_index(item.plt_ax)
            if super_index is None:
                newlist = ax_cache_list(item)
                super().append(newlist)
            else:
                super().__getitem__(super_index).append(item)

    def draw(self):
        for item in self:
            item.draw()

    def __getitem__(self, index):
        super_index = self.__search_ax_index(index)
        return super().__getitem__(super_index)

    def set_time(self, time):
        for item in self:
            item.set_time(time)

    def show(self):

        app = QApplication.instance()
        if not app:  # sinon on crée une instance de QApplication
            app = QApplication(sys.argv)

        progname = os.path.basename(sys.argv[0])
        qApp = QtWidgets.QApplication(sys.argv)

        aw = CacheList_Figure_App(self)
        aw.setWindowTitle("%s" % progname)
        aw.show()
        sys.exit(qApp.exec_())


class QFigure(FigureCanvas):
    """Qwidget containing a matplotlib updateable figure"""

    def __init__(self, parent=None, **kwargs):

        # self.set_subplots(1,1,figsize=(width, height), dpi=dpi)

        # self.fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes = self.fig.add_subplot(111)

        self.set_subplots()  # ,figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.size_update()
        # self.setParent(parent)
        self.set_fig_cache(kwargs.get("fig_cache_list", None))

    def set_subplots(self, **kwargs):
        self.fig = Figure(figsize=(5, 5), dpi=70)
        self.axes = []
        self.axes.append(self.fig.add_subplot(211))
        self.axes.append(self.fig.add_subplot(212))

        self.fig.subplots_adjust(
            left=0.03, right=0.97, bottom=0.03, top=0.97, hspace=0.2, wspace=0.2
        )

    def size_update(self):
        super().setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        super().updateGeometry()

    def set_fig_cache(self, fig_cache):
        self.fig_cache = fig_cache

    def draw(self):
        for ax in self.axes:
            ax.cla()
        # self.fig.clf()
        self.fig_cache.draw()
        super().draw()

    def set_time(self, time):
        self.fig_cache.set_time(time)
        self.draw()

    def Test(self):
        self.test_fig_cache()
        self.set_time(2)
        self.draw()

    def test_fig_cache(self):
        import LibUtils

        fig_cache = fig_cache_list(
            data=LibUtils.utimg.RandVideo(20, 20, 5),
            plt_type="imshow",
            plt_ax=self.axes[0],
            sort_index=2,
            time=0,
        )
        fig_cache.add_cache(
            data=[
                [
                    1,
                    2,
                    5,
                    7,
                    8,
                ],
                [14, 1, 4, 8, 5],
            ],
            plt_type="plot",
            plt_ax=self.axes[0],
            sort_index=1,
            plt_params={"color": "red", "linewidth": "10"},
        )
        fig_cache.add_cache(
            data=[
                [
                    1,
                    2,
                    5,
                    7,
                    8,
                ],
                [14, 1, 4, 8, 5],
            ],
            plt_type="plot",
            plt_ax=self.axes[1],
            sort_index=0,
            plt_params={"color": "green", "linewidth": "2"},
        )
        fig_cache.add_cache(
            data=[
                [
                    1,
                    2,
                    5,
                    7,
                    8,
                ],
                [14, 1, 4, 8, 5],
            ],
            plt_type="scatter",
            plt_ax=self.axes[1],
            sort_index=2,
            plt_params={"color": "cyan", "s": 50},
            time=0,
            plt_until=[1, 2, 3, 4, 5],
        )
        self.fig_cache = fig_cache


class QTimeFigure(QrealWidgets.QWidget):
    """Qwidget containing a matplotlib updateable figure and a timeslider connected to it"""

    def __init__(self, parent=None, **kwargs):
        super().__init__()
        # QFigure.__init__(self, parent = self, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.Figure = QFigure(parent, **kwargs)
        self.SupSlider = SuperSlider(minimum=0, maximum=4, start=0)

        l = QtWidgets.QVBoxLayout(self)
        l.addWidget(self.Figure)
        l.addWidget(self.SupSlider)
        # self.addToolBar(NavigationToolbar(self.Figure.canvas, self))
        self.setLayout(l)
        self.SupSlider.ValueChange.connect(
            lambda: self.Figure.set_time(self.SupSlider.value)
        )


def test_fig_cache(fig):
    import LibUtils

    ax = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    fig_cache = fig_cache_list(
        data=LibUtils.utimg.RandVideo(20, 20, 5),
        plt_type="imshow",
        plt_ax=ax,
        sort_index=2,
        time=0,
    )
    fig_cache.add_cache(
        data=[
            [
                1,
                2,
                5,
                7,
                8,
            ],
            [14, 1, 4, 8, 5],
        ],
        plt_type="plot",
        plt_ax=ax,
        sort_index=1,
        plt_params={"color": "red", "linewidth": "10"},
    )
    fig_cache.add_cache(
        data=[
            [
                1,
                2,
                5,
                7,
                8,
            ],
            [14, 1, 4, 8, 5],
        ],
        plt_type="plot",
        plt_ax=ax2,
        sort_index=0,
        plt_params={"color": "green", "linewidth": "2"},
    )
    fig_cache.add_cache(
        data=[
            [
                1,
                2,
                5,
                7,
                8,
            ],
            [14, 1, 4, 8, 5],
        ],
        plt_type="scatter",
        plt_ax=ax2,
        sort_index=2,
        plt_params={"color": "cyan", "s": 50},
        time=0,
        plt_until=[1, 2, 3, 4, 5],
    )
    return fig_cache


def dependancies_test_caller():
    import _dependancies
    _dependancies.dep_miss_raising(_dependancies.dependancy_placeholder("sqlalchemy"))
    
if __name__ is "__main__":
    import networks
    dependancies_test_caller()

    sys.exit()

if __name__ == "__main__":

    # import LibUtils
    # import matplotlib.pyplot as plt
    # #%matplotlib inline
    # fig = plt.figure()
    # ax = fig.add_subplot(211)
    # ax2 = fig.add_subplot(212)

    # fig_cache = fig_cache_list(data = LibUtils.image.RandImage(20, 20), plt_type = "imshow", plt_ax = ax, sort_index = 2)
    # fig_cache.add_cache(data = [[1,2,5,7,8,],[14,1,4,8,5]], plt_type = "plot", plt_ax = ax, sort_index = 1, plt_params = {"color":'red',"linewidth":"10"})
    # fig_cache.add_cache(data = [[1,2,5,7,8,],[14,1,4,8,5]], plt_type = "plot", plt_ax = ax2, sort_index = 2, plt_params = {"color":'green',"linewidth":"2"})
    # fig_cache.add_cache(data = [[1,2,5,7,8,],[14,1,4,8,5]], plt_type = "scatter", plt_ax = ax2, sort_index = 2, plt_params = {"color":'cyan'}, time = 4, plt_until = [1,2,3,4,5])
    # fig_cache.draw()
    # print(fig_cache[ax])
    # fig.show()

    ######################################################################

    class CacheList_Figure_App(QtWidgets.QMainWindow):
        def __init__(self, CachelistFigure_object):
            QtWidgets.QMainWindow.__init__(self)

            QApplication.setStyle(QStyleFactory.create("Fusion"))
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

            self.Fig = QTimeFigure(fig_cache_list=CachelistFigure_object)
            self.setCentralWidget(self.Fig)

            self.addToolBar(NavigationToolbar(self.Fig.Figure, self))

        def fileQuit(self):
            self.close()

    app = QApplication.instance()
    if not app:  # sinon on crée une instance de QApplication
        app = QApplication(sys.argv)

    progname = os.path.basename(sys.argv[0])
    qApp = QtWidgets.QApplication(sys.argv)

    # aw = TestApp()
    import matplotlib.pyplot as plt

    fig = plt.figure()

    aw = CacheList_Figure_App(test_fig_cache(fig))
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
    # sys.exit(qApp.exec_())

    Figure()
    
