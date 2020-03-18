import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
import random
import sys
import time
from datetime import date
import csv
import os
import numpy as np
from numpy import genfromtxt
from math import *

global curDir
curDir = os.getcwd()

class loadDataButton(QPushButton):
    def __init__(self,parent=None):
        super(loadDataButton,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Load Data")
        global curDir
        self.clicked.connect(lambda: self.loadData())

    def loadData(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file','{}'.format(curDir),"CSV Files (*.csv)")

        print("Under Construction")
app = QApplication([])
app.setStyle('Fusion')

mainPage = QWidget()
mainPage.resize(800,600)
mpl = QGridLayout()

loadButton = loadDataButton()
mpl.addWidget(loadButton)
mainPage.setLayout(mpl)
mainPage.show()
app.exec_()
