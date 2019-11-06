## Code for Mahan

import numpy as np
import RPi.GPIO as GPIO
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
import datetime
import Adafruit_ADS1x15 as ads

adc = ads.ADS1115(0x48)
global timeVector
timeVector = []
global dataVector
dataVector = []
global livegraph
global app
global startTime
startTime = time.time()
global mos

class MOS:
    def __init__(self, adc, channel):
        # Choose a gain of 1 for reading voltages from 0 to 4.09V.
        # Or pick a different gain to change the range of voltages that are read:
        #  - 2/3 = +/-6.144V
        #  -   1 = +/-4.096V
        #  -   2 = +/-2.048V
        #  -   4 = +/-1.024V
        #  -   8 = +/-0.512V
        #  -  16 = +/-0.256V
        # See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
        self.GAIN = 2 / 3
        self.adc = adc
        self.channel = channel
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144

    def read(self):
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144
        return self.conversion_value

    def print(self):
        self.read()
        print("\nReading from MOS: {}".format(self.conversion_value))

class live_Graph(pg.PlotWidget):
    def __init__(self,parent=None):
        super(live_Graph,self).__init__()
        #self.setAutoFillBackground(True)
        self.setRange(xRange=(0,200),yRange=(0,5),disableAutoRange=False)
        self.setTitle("Live Graph")
        self.setStyleSheet("pg.PlotWidget {border-style: outset; max-height: 50}")
def update_Graph():
    global liveGraph
    global app
    global timeVector
    global dataVector
    global startTime
    liveGraph.clear()
    timeVector.append(time.time() - startTime)
    dataVector1.append(mos2.read())
    dataVector
    liveGraph.plot(timeVector, dataVector[0])
    app.processEvents()

class start_Button(QPushButton):
    def __init__(self,parent=None):
        super(start_Button,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Start")
        self.clicked.connect(lambda: self.start_Procedure())

    def start_Procedure(self):
        timeCheck = time.time()
        runForever = True
        while runForever:
            if time.time() - timeCheck > 0.1:
                update_Graph()
                timeCheck = time.time()
            else:
                pass


mos1 = MOS(adc, 0)
mos2 = MOS(adc, 1)
mos3 = MOS(adc, 2)
mos4 = MOS(adc, 3)
app = QApplication([])
app.setStyle('Fusion')

mainPage = QWidget()
mainPage.setWindowTitle("Mahan's Program")
mainPage.resize(750, 550)
liveGraph = live_Graph()
startB = start_Button()
pageLayout = QGridLayout()
pageLayout.addWidget(liveGraph)
pageLayout.addWidget(startB)
mainPage.setLayout(pageLayout)
mainPage.show()
app.exec()
