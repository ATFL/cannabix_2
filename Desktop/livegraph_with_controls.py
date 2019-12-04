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
global dataVector
dataVector = []
global liveGraph
global liveGraph2
global app
global startTime
startTime = time.time()
global mos

GPIO.setmode(GPIO.BCM)

class linearActuator():
    def __init__(self,pinNum,enPin):
        self.pinNum = pinNum
        self.enPin = enPin
        GPIO.setup(self.pinNum,GPIO.OUT)
        GPIO.setup(self.enPin,GPIO.OUT)
        GPIO.output(self.enPin,GPIO.HIGH)
        self.pwm = GPIO.PWM(self.pinNum,50)
        self.pwm.start(7.6)
        time.sleep(2)
        GPIO.output(self.enPin,GPIO.LOW)
        self.state = 'recovery'
        print(self.state)

    def recover(self):
        if self.state != 'recovery':
            print("Moving to Recovery")
            GPIO.output(self.enPin,GPIO.HIGH)
            self.pwm.ChangeDutyCycle(7.6)
            time.sleep(2)
            GPIO.output(self.enPin,GPIO.LOW)
            print("At Recovery")
            self.state = 'recovery'

        else:
            print("LA at Recovery")
            pass
    def expose(self):
        if self.state != 'exposure':
            print("Moving to Exposure")
            GPIO.output(self.enPin,GPIO.HIGH)
            self.pwm.ChangeDutyCycle(5.0)
            time.sleep(2)
            GPIO.output(self.enPin,GPIO.LOW)
            #time.sleep(2)
            print("At Exposure")
            self.state = 'exposure'

        else:
            print("LA at Exposure")
            pass


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
    global mos
    liveGraph.clear()
    #liveGraph2.clear()
    timeVector.append(time.time() - startTime)
    mos1_data.append(mos1.read())
    mos2_data.append(mos2.read())
    #os = [mos1,mos2]

    liveGraph.plot(timeVector, mos1_data,pen='r')
    liveGraph.plot(timeVector, mos2_data,pen='b')

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
            if time.time() - timeCheck > 0.05:
                update_Graph()
                timeCheck = time.time()
            else:
                pass
class linAc_exposeButton(QPushButton):
    def __init__(self,linAc, parent=None):
        super(linAc_exposeButton,self).__init__()
        self.linearActuator = linAc
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Expose")
        self.state = "recovery"
        self.clicked.connect(lambda: self.expose())

    def expose(self):
        if self.linearActuator.state == 'recovery':
            self.linearActuator.expose()
            #self.setText("Click to Recover")
            #self.setIcon(self.green)
            self.linearActuator.state = 'exposure'

class linAc_recoverButton(QPushButton):
    def __init__(self,linAc, parent=None):
        super(linAc_recoverButton,self).__init__()
        self.linearActuator = linAc
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Recover")
        self.state = "expose"
        self.clicked.connect(lambda: self.recover())

    def recover(self):
        if self.linearActuator.state == 'exposure':
            self.linearActuator.recover()
            self.setText("Click to Expose")
            #self.setIcon(self.red)
            self.linearActuator.state = 'recovery'


linAc = linearActuator(14,15)
mos1 = MOS(adc, 2)
mos2 = MOS(adc,3)
app = QApplication([])
app.setStyle('Fusion')

mainPage = QWidget()
mainPage.setWindowTitle("Mahan's Program")
mainPage.resize(1200, 700)
liveGraph = live_Graph()
#liveGraph2 = live_Graph()
startB = start_Button()
linAc_exposeB = linAc_exposeButton(linAc)
linAc_recoverB = linAc_recoverButton(linAc)
pageLayout = QGridLayout()
pageLayout.addWidget(liveGraph)

pageLayout.addWidget(startB)
mainPage.setLayout(pageLayout)
mainPage.show()
app.exec()
