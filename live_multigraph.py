from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg
import numpy as np
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

global timeVector
timeVector = []
global dataVector
dataVector = []
global livegraph
global app
global startTime
startTime = time.time()

class live_Graph(pg.PlotWidget):
    def __init__(self,parent=None):
        super(live_Graph,self).__init__()
        #self.setAutoFillBackground(True)
        self.setRange(xRange=(0,200),yRange=(0,5),disableAutoRange=False)
        self.setTitle("Live Graph")
        self.setStyleSheet("pg.PlotWidget {border-style: outset; max-height: 50}") 
