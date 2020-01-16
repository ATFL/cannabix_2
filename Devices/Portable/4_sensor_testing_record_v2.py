## Code for KLN Testing

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
import os

adc = ads.ADS1115(0x48) #0x49 pressure/temp/humidity sensor, 04xA triple sensor, 0x48 quad sensor
global timeVector
timeVector = []
global x1
global x2
global x3
global x4
x1 = []
x2 = []
x3 = []
x4 = []
global livegraph
global app
global startTime
startTime = time.time()
global sens1
global sens2
global sens3
global sens4
global run_test
run_test = False
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
    global x1
    global x2
    global x3
    global x4
    global startTime 
    liveGraph.clear()
    timeVector.append(time.time() - startTime)
    x1.append(sens1.read())
    x2.append(sens2.read())
    x3.append(sens3.read())
    x4.append(sens4.read())
    liveGraph.plot(timeVector, x1,pen='r')
    liveGraph.plot(timeVector, x2,pen='g')
    liveGraph.plot(timeVector, x3,pen='b')
    #liveGraph.plot(timeVector, x4)
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
        run_test = True
        while run_test:
            if time.time() - timeCheck > 0.1:
                update_Graph()
                timeCheck = time.time()
            else:
                pass

class save_Button(QPushButton):
    def __init__(self,parent=None):
        super(save_Button,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Save")
        self.clicked.connect(lambda: self.save())

    def save(self):
        run_test = False
        global timeVector
        global x1
        global x2
        global x3
        global x4
        combinedVector = np.column_stack((timeVector,x1,x2,x3,x4))
        filename = time.strftime('quad_sens_%a%d%b%Y%H%M.csv',time.localtime())
        if os.path.isfile(filename):
            print('Filename ',filename, ' already exists.')
            filename = time.strftime('quad_sens_%a%d%b%Y%H%M%S.csv',time.localtime())
        np.savetxt(filename,combinedVector,fmt='%.10f',delimiter=',')
        print("file saved as " + filename)
        timeVector = []
        x1 = []
        x2 = []
        x3 = []
        x4 = []
        combinedVector = []

sens1 = MOS(adc, 0)
sens2 = MOS(adc, 1)
sens3 = MOS(adc, 2)
sens4 = MOS(adc, 3)
app = QApplication([])
app.setStyle('Fusion')

mainPage = QWidget()
mainPage.setWindowTitle("4 Sensor")
mainPage.resize(800, 600)
liveGraph = live_Graph()
startB = start_Button()
saveB = save_Button()
pageLayout = QGridLayout()
pageLayout.addWidget(liveGraph)
pageLayout.addWidget(startB)
pageLayout.addWidget(saveB)
mainPage.setLayout(pageLayout)
mainPage.show()
app.exec()
