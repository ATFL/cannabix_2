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
timeVector = []#np.zeros((2500,))
global dataVector
dataVector = []
global livegraph
global app
global startTime
startTime = time.time()
global mos
global mos2
global x1
global x2
x1 = []
x2 = []


GPIO.setmode(GPIO.BCM)

class linearActuator():
    def __init__(self,pinNum,enPin):
        self.pinNum = pinNum
        self.enPin = enPin
        GPIO.setup(self.pinNum,GPIO.OUT)
        GPIO.setup(self.enPin,GPIO.OUT)
        GPIO.output(self.enPin,GPIO.HIGH)
        self.pwm = GPIO.PWM(self.pinNum,50)
        self.pwm.start(7.4)
        GPIO.output(self.enPin,GPIO.LOW)
        self.state = 'recovery'
        print(self.state)

    def recover(self):
        if self.state != 'recovery':
            print("Moving to Recovery")
            GPIO.output(self.enPin,GPIO.HIGH)
            self.pwm.ChangeDutyCycle(9)
            #time.sleep(2)
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
            self.pwm.ChangeDutyCycle(5.4)

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
        self.setRange(xRange=(0,200),yRange=(0,5),disableAutoRange=False)
        self.setTitle("Live Graph")
        self.setStyleSheet("pg.PlotWidget {border-style: outset; max-height: 50}")

def collect_data():
    global linearActuator
    global app
    global timeVector
    global totalTime
    #experimental values
    sensing_delay_time = 5
    sampling_time_index = 1
    sampling_time = 0.1
    exposure_time = 42
    duration_of_signal = 200
    #software testing values


    start_time = time.time()
    print('Starting Data Capture')
    while (time.time() < (start_time + duration_of_signal)):
        app.processEvents()
        if (time.time() > (start_time + (sampling_time * sampling_time_index))):
            global x1
            global x2
            x1.append(mos.read())
            x2.append(mos2.read())
            timeVector.append(time.time() - start_time)
            update_Graph()

        if (time.time() < (start_time + sensing_delay_time)):
            print("Pre Exposure Period")
            linAc.recover()
        if (time.time() > (start_time + sensing_delay_time) and time.time() < (start_time + sensing_delay_time + exposure_time)):
            print("Exposing System")
            linAc.expose()
        if(time.time() > (start_time + sensing_delay_time + exposure_time)):
            print("Done Exposing, recovering now")
            linAc.recover()


    combinedVector = np.column_stack((timeVector,x1,x2))
    filename = time.strftime("/home/pi/Desktop/ATFL/Projects/cannabix/tests/%a%d%b%Y%H%M%S.csv",time.localtime())
    np.savetxt(filename, combinedVector,fmt='%.10f',delimiter=',')
    print('File Saved')
    return



def update_Graph():
    global liveGraph
    global app
    global timeVector
    global x1
    global x2
    global startTime
    liveGraph.clear()
    liveGraph.plot(timeVector, x1, pen='r')
    liveGraph.plot(timeVector,x2, pen='b')
    app.processEvents()

class start_Button(QPushButton):
    def __init__(self,parent=None):
        super(start_Button,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Start")
        self.clicked.connect(lambda: self.start_Procedure())

    def start_Procedure(self):
        timeCheck = time.time()
        print("Starting Test")
        collect_data()

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


linAc = linearActuator(8,10)
mos = MOS(adc, 0)
mos2 = MOS(adc,1)
app = QApplication([])
app.setStyle('Fusion')

mainPage = QWidget()
mainPage.setWindowTitle("7 Sensor Adi")
mainPage.resize(800, 600)
liveGraph = live_Graph()
startB = start_Button()
linAc_exposeB = linAc_exposeButton(linAc)
linAc_recoverB = linAc_recoverButton(linAc)
pageLayout = QGridLayout()
pageLayout.addWidget(liveGraph)
pageLayout.addWidget(startB)
pageLayout.addWidget(linAc_exposeB)
pageLayout.addWidget(linAc_recoverB)
mainPage.setLayout(pageLayout)
mainPage.show()
app.exec()
