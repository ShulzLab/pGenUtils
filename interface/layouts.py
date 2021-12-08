# -*- coding: utf-8 -*-

"""Boilerplate:
A one line summary of the module or program, terminated by a period.

Rest of the description. Multiliner

<div id = "exclude_from_mkds">
Excluded doc
</div>

<div id = "content_index">

<div id = "contributors">
Created on Fri Aug 27 17:25:06 2021
@author: Timothe
</div>
"""

from PyQt5.QtWidgets import QWidget, QPushButton,QHBoxLayout, QGridLayout, QApplication, QFrame, QVBoxLayout

class QDynamicGenericLayout():
    def __init__(self):
        super().__init__()
        self._mapping = {}
        self._map_index = 0

    @property
    def _lower_index(self):
        try :
            max_index =  max(list(self._mapping.values()))
        except ValueError : #if mapping values has no item because we have selfdeleted the layout
            return
        if self._map_index - 1 > max_index :
            self._map_index = max_index + 1

    def __getitem__(self, key):
        try :
            return self.itemAt(self._mapping[key]).widget()
        except Exception as e:
            print(e,self._mapping)
            return None

    def delete(self,key):
        if self[key] is not None :
            self[key].deleteLater()
            self._mapping.pop(key)
        self._lower_index

    def selfdelete(self):
        for key in list(self._mapping.keys()):
            self.delete(key)

class QDynamicGridLayout(QGridLayout, QDynamicGenericLayout):
    def __init__(self,parent = None):
        super().__init__()

    def addWidget(self, widgetname, widget , coordx, coordy):
        if widgetname in self._mapping.keys():
            raise ValueError("Two widgets with the same name, not allowed")

        self._mapping.update({widgetname:self._map_index})
        self._map_index += 1
        super().addWidget(widget, coordx, coordy)

class QDynamicHLayout(QHBoxLayout, QDynamicGenericLayout):
    def __init__(self,parent = None):
        super().__init__()

    def addWidget(self, widgetname, widget ):
        if widgetname in self._mapping.keys():
            raise ValueError("Two widgets with the same name, not allowed")

        self._mapping.update({widgetname:self._map_index})
        self._map_index += 1
        super().addWidget(widget)

class QDynamicVLayout(QVBoxLayout, QDynamicGenericLayout):
    def __init__(self,parent = None):
        super().__init__()

    def addWidget(self, widgetname, widget ):
        if widgetname in self._mapping.keys():
            raise ValueError("Two widgets with the same name, not allowed")

        self._mapping.update({widgetname:self._map_index})
        self._map_index += 1
        super().addWidget(widget)
