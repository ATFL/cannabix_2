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
global mos1
mos1_data = []
global mos2
mos2_data = []
global mos3
mos3_data = []
global mos4
mos4_data = []
global dataVector
dataVector = []
global liveGraph
global liveGraph2
global app
global startTime
startTime = time.time()
global mos
global recording_status
recording_status = False

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
        #self.setRange(xRange=(0,200),yRange=(0.5,3),disableAutoRange=True)
        #self.setXRange(0,200)
        self.setYRange(0,5)
        #self.autoRange()
        #self.setAutoPan()
        self.setTitle("Live Graph")

        self.setStyleSheet("pg.PlotWidget {border-style: outset; max-height: 50}")
def update_Graph():
    global liveGraph
    global liveGraph2
    global app
    global timeVector
    global dataVector
    global startTime
    global mos1_data
    global mos2_data
    global mos3_data
    global mos4_data
    global mos
    liveGraph.clear()
    #liveGraph2.clear()
    timeVector.append(time.time() - startTime)
    mos1_data_new = mos1.read()
    mos2_data_new = mos2.read()
    mos3_data_new = mos3.read()
    mos4_data_new = mos4.read()
    mos1_data.append(mos1_data_new)
    mos2_data.append(mos2_data_new)
    mos3_data.append(mos3_data_new)
    mos4_data.append(mos4_data_new)
    #os = [mos1,mos2]

    liveGraph.plot(timeVector, mos1_data,pen='r')
    liveGraph.plot(timeVector, mos2_data,pen='b')
    liveGraph.plot(timeVector, mos3_data,pen='g')
    liveGraph.plot(timeVector, mos4_data)

    app.processEvents()
    return mos1_data_new,mos2_data_new,mos3_data_new,mos4_data_new

class start_recording_button(QPushButton):
    def __init__(self,parent=None):
        super(start_recording_button,parent=None).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Start Recording")
        self.clicked.connect(lambda: self.start_recording())

    def start_recording(self):
        global recording_status
        recording_status = True
        while recording_status == True:
            m1,m2,m3,m4 = update_Graph()



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
            if time.time() - timeCheck > 0.05:
                update_Graph()
                timeCheck = time.time()
            else:
                pass


mos1 = MOS(adc, 0)
mos2 = MOS(adc,1)
mos3 = MOS(adc,2)
mos4 = MOS(adc,3)
app = QApplication([])
app.setStyle('Fusion')

mainPage = QWidget()
mainPage.setWindowTitle("Mahan's Program")
mainPage.resize(1200, 700)
liveGraph = live_Graph()
#liveGraph2 = live_Graph()
startB = start_Button()
pageLayout = QGridLayout()
pageLayout.addWidget(liveGraph)
#pageLayout.addWidget(liveGraph2)
pageLayout.addWidget(startB)
mainPage.setLayout(pageLayout)
mainPage.show()
app.exec()
