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
from pandas import read_csv as rc
from statistics import mean


import RPi.GPIO as GPIO
import Adafruit_ADS1x15 as ads

GPIO.setmode(GPIO.BOARD)

global curDir
curDir = os.getcwd()
global today
today = date.today()

#### CONFIGUREABLES ####
global device_version
global totalTime
global bsc
global exp
global pur0Time
global pur1Time
global pur2Time
device_version = 3 # This is the device version just to ensure that we have some sort of idea what we are using
totalTime = 35 # This will be the total runtime
bsc = 10 # This will be the base line check time
exp = 15 # This will be the exposure time
pur0Time= 10
pur1Time= 10
pur2Time=10


#######################
global appStatus
appStatus = "Ready"
global idVal
idVal = 0
global tgStatus
tgStatus = 0
global lgStatus
lgStatus = 0
global tempVal_last
tempVal_last = 0
global humVal_last
humVal_last = 0
global pressVal_last
pressVal_last = 0
global oxVal_last
oxVal_last = 0
global p3temp
global p3hum
global p3press
global p3ox
p3temp = 0
p3hum = 0
p3press = 0
p3ox = 0
global p3Time
global p3sens1
global p3sens2
global p3sens3
global p3sens4

global idPath
idPath = "{}/Data/byID/id{}/".format(curDir,idVal)

### SENSOR NAME DEFINITION ###
sensor1name = '2601'
sensor2name = '2603'
sensor3name = '2620'
sensor4name = '822'
##### COLORS ######
bgGrey = '#A9A9A9'

adc1 = ads.ADS1115(0x48)
adc2 = ads.ADS1115(0x49)

def refreshID():
    global idPath
    global idVal
    global curDir
    p1IDL.setText("ID: {:d}".format(idVal))
    p2IDL.setText("ID: {:d}".format(idVal))
    p3IDL.setText("ID: {:d}".format(idVal))
    app.processEvents()
def refreshStatus():
    p1appStat.setText("Status: {}".format(appStatus))
    p2appStat.setText("Status: {}".format(appStatus))
    p3appStat.setText("Status: {}".format(appStatus))
    app.processEvents()
def clear_all():
    global tgStatus
    global lgStatus
    global appStatus
    global idVal
    global sens1
    global sens2
    global sens3
    global sens4
    global mos1
    global mos2
    global mos3
    global mos4
    global mos5
    global mos6
    global mos7
    global mos8
    global sens1plot
    global sens2plot
    global sens3plot
    global sens4plot
    tgStatus = 0
    lgStatus = 0
    appStatus = 'Ready'
    refreshStatus()
    testTime = []
    sens1 = []
    sens2 = []
    sens3 = []
    sens4 = []
    tempVal = []
    humVal = []
    pressVal = []
    oxVal = []
    p1Graph.clear()
    vecLabel.setText("Temp: {}℃ \n\nHumidity: {}% \n\nPressure: {}kPa \n\nOxygen: {}%".format('','','',''))
    app.processEvents()
def something():
    print("I dont know")
def updateGUI():
    global testTime
    global sens1
    global sens2
    global sens3
    global sens4
    global tempVal_last
    global humVal_last
    global pressVal_last
    global oxVal_last
    global sens1plot
    global sens2plot
    global sens3plot
    global sens4plot

    sens1plot.setData(testTime,sens1)
    sens2plot.setData(testTime,sens2)
    sens3plot.setData(testTime,sens3)
    sens4plot.setData(testTime,sens4)
    vecLabel.setText("Temp: {}℃ \n\nHumidity: {}% \n\nPressure: {}kPa \n\nOxygen: {}%".format(int(tempVal_last),int(humVal_last),int(pressVal_last),int(oxVal_last)))
    app.processEvents()
def updateLog():
    global idVal
    global curDir
    global idPath
    global curTime
    idPath = "{}/Data/byID/id{}/".format(curDir,idVal)
    logPath = "{}id{}.txt".format(idPath,idVal)
    curTime = time.strftime("%d-%m-%y_%H-%M-%S",time.localtime())

    bar = "-----------------------"
    f = open(logPath,'a+')
    message,ok1 = QInputDialog.getText(None,"Custom Log","Add text if you want a custom message")
    print(message)
    if(message != ""):
        full_txt = "\n{}: {} \n{}".format(curTime,message,bar)
    else:
        full_txt = "\n{}: {} \n{}".format(curTime,"New Test Performed",bar)
    f.write(full_txt)

def saveFile(data):
    global idVal
    global curDir
    global today
    global appStatus
    global curTime
    appStatus = 'Saving'
    refreshStatus()

    updateLog()
    np.savetxt("{}id{}_{}.csv".format(idPath,idVal,curTime),data,fmt='%.10f',delimiter=',')
    print('File Saved')


class MOS:
    def __init__(self, adc, channel):

        self.GAIN = 2 / 3
        self.adc = adc
        self.channel = channel
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144

    def read(self):
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144
        return self.conversion_value
        # global testTime
        # return sin(time.time())*5
    def read_hum(self):
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144
        self.conversion_value2 = self.conversion_value/5*125-12.5
        return self.conversion_value2
    # TODO: make functions to read temp pressure humidity and oxygen
    def read_temp(self):
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144
        self.conversion_value2 = self.conversion_value/5*218.75-66.875
        return self.conversion_value2
    def print(self):
        self.read()
        #print("\nReading from MOS: {}".format(self.conversion_value))
class graph(pg.PlotWidget):
    def __init(self,parent=None):
        super(graph,self).__init__()
        #self.setRange(xRange=(0,200),yRange=(0,5),disableAutoRange=True)
        self.setStyleSheet("pg.PlotWidget {border-style: outset; max-height: 50}")
class LinearActuator:
    def __init__(self, pinLA , pinEnable):
        self.pinLA = pinLA
        self.pinEnable = pinEnable
        GPIO.setup(self.pinLA, GPIO.OUT)
        GPIO.setup(self.pinEnable, GPIO.OUT)
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm = GPIO.PWM(pinLA, 50)
        self.pwm.start(8.5)
        timestart = time.time()
        while((time.time() - timestart) < 1.5):
            # time.sleep(0.1)
            #app.processEvents()
            pass
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'r'

    def extend(self):
        #print('Extending linear actuator.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        extending = 5.3 #5.3
        self.pwm.ChangeDutyCycle(extending)
        timestart = time.time()
        while((time.time() - timestart) < 1.5):
            # time.sleep(0.1)
            #app.processEvents() #5.3
            pass
        #print('Extended at',extending)
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'e'

    def retract(self):
        #print('Retracting linear actuator.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(8.5)
        timestart = time.time()
        while((time.time() - timestart) < 1.5):
            # time.sleep(0.1)
            #app.processEvents()
            pass
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'r'

    def default(self):
        #print('Moving linear actuator to default (center) position.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(6)
        time.sleep(1.5)
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'd'
class Valve:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False

    def switch(self):
        if self.state == False:
            self.enable()
        elif self.state == True:
            self.disable()

    def enable(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = True
        print(self.name + ' enabled.')
        #print("GPIO.LOW")

    def disable(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False
        print(self.name + ' disabled.')
class startTest(QPushButton):
    def __init__(self,parent=None):
        super(startTest,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Start Test")
        self.clicked.connect(lambda: self.startTest())


    def pre_purge(self):
        valve1.disable()
        valve2.disable()
        valve3.disable()
        if(linAc.state != 'r'):
            linAc.retract()
        print("Starting Purge - 0")
        global appStatus
        appStatus = "Purge - 0"
        refreshStatus()
        global pur0Time
        global pur1Time
        pur0Start = time.time()
        while((time.time() - pur0Start) < pur0Time and tgStatus == 1):
            if(valve1.state != True):
                valve1.enable()
            app.processEvents()
        valve1.disable()
        if(linAc.state != 'e'):
            linAc.extend()
        print("Starting Purge - 1")
        appStatus = "Purge - 1"
        refreshStatus()
        pur1Start = time.time()
        while((time.time() - pur1Start) < pur1Time and tgStatus == 1):
            if(linAc.state != 'e'):
                linAc.extend()
            if(valve2.state != True):
                valve2.enable()
            if(valve3.state != True):
                valve3.enable()
            app.processEvents()
        if(linAc.state != 'r'):
            linAc.retract()
        if(valve1.state != False):
            valve1.disable()
        if(valve2.state != False):
            valve2.disable()
        if(valve3.state != False):
            valve3.disable()
        app.processEvents()
    def post_purge(self):
        global pur2Time
        app.processEvents()
        purgestart = time.time()
        global appStatus
        appStatus = "Purge - 2"
        refreshStatus()
        valve1.enable()
        valve2.enable()
        valve3.enable()
        if(linAc.state != 'd'):
            linAc.default()
        while((time.time() - purgestart) < pur2Time and tgStatus == 1):
            app.processEvents()
            if(linAc.state != 'd'):
                linAc.default()
            if(valve1.state != True):
                valve1.enable()
            if(valve2.state != True):
                valve2.enable()
            if(valve3.state != True):
                valve3.enable()
        valve1.disable()
        valve2.disable()
        valve3.disable()
        if(linAc.state != 'r'):
            linAc.retract()

    def startTest(self):
        clear_all()
        print("Starting Data Collection Procedure")
        global tgStatus
        global lgStatus
        global appStatus
        global idVal
        global testTime
        global sens1
        global sens2
        global sens3
        global sens4
        global tempVal
        global humVal
        global pressVal
        global oxVal
        global tempVal_last
        global humVal_last
        global pressVal_last
        global oxVal_last
        global mos1
        global mos2
        global mos3
        global mos4
        global mos5
        global mos6
        global mos7
        global mos8
        global sens1plot
        global sens2plot
        global sens3plot
        global sens4plot

        global totalTime
        global bsc
        global exp

        #### START UP CHECKS ####
        valve1.disable()
        valve2.disable()
        valve3.disable()
        tgStatus = 1
        if(linAc.state != 'r'):
            linAc.retract()
        QMessageBox.information(self,"Pre Test Purge","Press okay to initiate Pre-Test Purge",QMessageBox.Ok)
        self.pre_purge()

        ok1 = QMessageBox.information(self,"Test ID","Using ID {:d}. Press Ok if Correct".format(idVal),QMessageBox.Ok | QMessageBox.No)
        if(ok1 == QMessageBox.Ok):
            print("Using ID {}".format(idVal))
            testTime = []
            sens1 = []
            sens2 = []
            sens3 = []
            sens4 = []
            tempVal = []
            humVal = []
            pressVal = []
            oxVal = []

            QMessageBox.information(self,"Breath Input","Press Okay After Breath Input",QMessageBox.Ok)
            app.processEvents()
            startTime = time.time()
            p1Graph.addLegend(offset=(0,10))
            sens1plot = p1Graph.plot(testTime,sens1,pen='r',name='{}'.format(sensor1name))
            sens2plot = p1Graph.plot(testTime,sens2,pen='g',name='{}'.format(sensor2name))
            sens3plot = p1Graph.plot(testTime,sens3,pen='b',name='{}'.format(sensor3name))
            sens4plot = p1Graph.plot(testTime,sens4,pen='k',name='{}'.format(sensor4name))
            p1Graph.setYRange(0,5)
            p1Graph.setXRange(0,50)


            tgStatus = 1
            appStatus = "Testing"
            refreshStatus()

            while((time.time() - startTime) < totalTime and tgStatus == 1):
                app.processEvents()
                if((time.time() - startTime) < bsc):
                    if(linAc.state != 'r'):
                        linAc.retract()
                elif((time.time() - startTime) >= bsc and (time.time() - startTime) < exp):
                    if(linAc.state != 'e'):
                        linAc.extend()
                elif((time.time() - startTime) >=exp):
                    if(linAc.state != 'r'):
                        linAc.retract()
                else:
                    if(linAc.state != 'r'):
                        linAc.retract()
                testTime.append(time.time() - startTime)
                sens1.append(mos1.read())
                sens2.append(mos2.read())
                sens3.append(mos3.read())
                sens4.append(mos4.read())
                tempVal.append(mos5.read_temp())
                humVal.append(mos6.read_hum())
                pressVal.append(mos7.read())
                oxVal.append(mos8.read())
                tempVal_last = tempVal[-1]
                humVal_last = humVal[-1]
                pressVal_last = pressVal[-1]
                oxVal_last = oxVal[-1]
                updateGUI()
                app.processEvents()
            all_data = np.column_stack((testTime,sens1,sens2,sens3,sens4,tempVal,humVal,pressVal,oxVal))
            ok2 = QMessageBox.information(self,"Save Data","Save the Data Now?",QMessageBox.Yes | QMessageBox.No)
            if(ok2 == QMessageBox.Yes):
                saveFile(all_data)
            else:
                print('File Not Saved')

            ok3 = QMessageBox.information(self,"Purge","Connect Pump and click yes to purge",QMessageBox.Yes| QMessageBox.No)
            if(ok3 == QMessageBox.Yes):
                print("starting purge")
                self.post_purge()
            else:
                pass
            appStatus = 'Ready'
            refreshStatus()
        else:
            QMessageBox.information(self,"Test Cancelled","Select Proper ID and Try again.",QMessageBox.Ok)

class liveReading(QPushButton):
    def __init__(self,parent=None):
        super(liveReading,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Live Graph")
        self.clicked.connect(lambda: self.liveReading())


    def liveReading(self):
        clear_all()

        global tgStatus
        global lgStatus
        global appStatus
        global testTime
        global idVal
        global sens1
        global sens2
        global sens3
        global sens4
        global tempVal_last
        global humVal_last
        global pressVal_last
        global oxVal_last
        global mos1
        global mos2
        global mos3
        global mos4
        global mos5
        global mos6
        global mos7
        global mos8
        global sens1plot
        global sens2plot
        global sens3plot
        global sens4plot

        appStatus = "Live"
        refreshStatus()
        testTime = list(range(100))
        sens1 = [0 for _ in range(100)]
        sens2 = [0 for _ in range(100)]
        sens3 = [0 for _ in range(100)]
        sens4 = [0 for _ in range(100)]

        p1Graph.addLegend(offset=(0,10))
        sens1plot = p1Graph.plot(testTime,sens1,pen='r',name='{}'.format(sensor1name))
        sens2plot = p1Graph.plot(testTime,sens2,pen='g',name='{}'.format(sensor2name))
        sens3plot = p1Graph.plot(testTime,sens3,pen='b',name='{}'.format(sensor3name))
        sens4plot = p1Graph.plot(testTime,sens4,pen='k',name='{}'.format(sensor4name))
        p1Graph.setYRange(0,5)
        p1Graph.setXRange(0,50)

        lgStatus = 1
        while(lgStatus == 1):
            app.processEvents()
            sens1 = sens1[1:]
            sens2 = sens2[1:]
            sens3 = sens3[1:]
            sens4 = sens4[1:]
            sens1.append(mos1.read())
            sens2.append(mos2.read())
            sens3.append(mos3.read())
            sens4.append(mos4.read())
            tempVal_last = mos5.read()
            humVal_last = mos6.read()
            pressVal_last = mos7.read()
            oxVal_last = mos8.read()
            updateGUI()
            app.processEvents()
class stop(QPushButton):
    def __init__(self,parent=None):
        super(stop,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Stop")
        self.clicked.connect(lambda: self.stopfcn())

    def stopfcn(self):
        app.processEvents()
        global lgStatus
        global tgStatus
        global appStatus
        lgStatus = 0
        tgStatus = 0
        appStatus = "Stopped"
        refreshStatus()
        app.processEvents()
        print("Stop Everything")
class clear(QPushButton):
    def __init__(self,parent=None):
        super(clear,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Clear Graph")
        self.clicked.connect(lambda: self.clearfcn())

    def clearfcn(self):
        q1 = QMessageBox.information(self,"Clear All","Do you Want to clear all Data?",QMessageBox.Yes | QMessageBox.No)
        if(q1 == QMessageBox.Yes):
            clear_all()
class clear2(QPushButton):
    def __init__(self,parent=None):
        super(clear2,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Clear Graph")
        self.clicked.connect(lambda: self.clearfcn())

    def clearfcn(self):
        q1 = QMessageBox.information(self,"Clear All","Do you Want to clear all Data?",QMessageBox.Yes | QMessageBox.No)
        if(q1 == QMessageBox.Yes):
            global p3gStatus
            global p3Time
            global p3sens1
            global p3sens2
            global p3sens3
            global p3sens4
            global p3temp
            global p3hum
            global p3press
            global p3ox

            appStatus = 'Ready'
            refreshStatus()
            p3Time = []
            p3sens1 = []
            p3sens2 = []
            p3sens3 = []
            p3sens4 = []
            p3temp = []
            p3hum = []
            p3press = []
            p3ox = []
            p3Graph.clear()
            p3vecLabel.setText("Temp: {}℃ \n\nHumidity: {}% \n\nPressure: {}kPa \n\nOxygen: {}%".format('','','',''))
class loadDataButton(QPushButton):
    def __init__(self,parent=None):
        super(loadDataButton,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Load Data")
        self.clicked.connect(lambda: self.loadData())

    def loadData(self):
        fname,something = QFileDialog.getOpenFileName(self, 'Open file','{}'.format(curDir),"CSV Files (*.csv)")
        print(fname)
        f = rc(fname,delimiter=',',)
        global p3Time
        global p3sens1
        global p3sens2
        global p3sens3
        global p3sens4
        global p3temp
        global p3hum
        global p3press
        global p3ox
        p3Time = f.iloc[:,0].values
        p3sens1 = f.iloc[:,1].values
        p3sens2 = f.iloc[:,2].values
        p3sens3 = f.iloc[:,3].values
        p3sens4 = f.iloc[:,4].values
        p3temp = f.iloc[:,5].values
        p3hum = f.iloc[:,6].values
        p3press = f.iloc[:,7].values
        p3ox = f.iloc[:,8].values

        p3Graph.addLegend(offset=(0,10))
        p3sens1plot = p3Graph.plot(p3Time,p3sens1,pen='r',name='{}'.format(sensor1name))
        p3sens2plot = p3Graph.plot(p3Time,p3sens2,pen='g',name='{}'.format(sensor2name))
        p3sens3plot = p3Graph.plot(p3Time,p3sens3,pen='b',name='{}'.format(sensor3name))
        p3sens4plot = p3Graph.plot(p3Time,p3sens4,pen='k',name='{}'.format(sensor4name))
        p3temp = mean(p3temp)
        p3hum = mean(p3hum)
        p3press = mean(p3press)
        p3ox = mean(p3ox)
        p3vecLabel.setText("Temp: {}℃ \n\nHumidity: {}% \n\nPressure: {}kPa \n\nOxygen: {}%".format(int(p3temp),int(p3hum),int(p3press),int(p3ox)))
        p3Graph.setYRange(0,5)
        p3Graph.setXRange(0,50)
class generateFile(QPushButton):
    def __init__(self,parent=None):
        super(generateFile,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Generate File")
        self.clicked.connect(lambda: self.genFile())

    def genFile(self):
        print("Under Construction")
class nsButton(QPushButton):
   ### This Function Generates a Button to create new subjects
    def __init__(self,parent=None):
        super(nsButton,self).__init__()
        self.setStyleSheet("QPushButton {font:20px}")
        self.setText("Add New Subject")
        self.clicked.connect(lambda:self.add_new_s())

    def add_new_s(self):
        app.processEvents()
        subNumber = self.genSubNumber()
        global idVal
        idVal = subNumber
        message = "Add Subject :" + str(subNumber)
        newSubjectReply = QMessageBox.question(self, 'Add Subject',message,QMessageBox.Yes | QMessageBox.No)
        if newSubjectReply == QMessageBox.Yes:
            #self.getSubInfo(subNumber)

            self.genSubject(subNumber)
            print('Subject Added')

        else:
            print('No Actions Done')

        refreshID()
    def genSubNumber(self):
        ###This function generates a random number for a test participant
        myArray = genfromtxt('idDatabase.csv',delimiter=',',skip_header=1)
        col1 = myArray[:,0]
        numFound = False
        myRand = 0
        while(numFound == False):
            myRand = np.random.randint(1,20,1)
            check = np.isin(myRand,col1,assume_unique=True)
            if(check == True):
                pass
            else:
                numFound = True
        return int(myRand)

    #def getSubInfo(self,subNumber):


    def genSubject(self,subNumber):
        ## This function generates the files and folders required for each subject also updates the database
        global curDir
        print(subNumber)
        subN = str(subNumber)
        print(subN)

        filename = 'id{}'.format(subN)
        print(filename)

        directory = 'Data/byID/{}'.format(filename)
        print(directory)

        if not os.path.exists(directory):
            os.makedirs(directory)

        global today
        global device_version
        creationDate = today.strftime("%d-%m-%Y")
        f = open('{}/{}.txt'.format(directory,filename),'w+')
        init_message = "ID Number: "+ subN+ "\nCreated on: " + str(creationDate) + "\nDevice Version: " + str(device_version) + "\n-----------------------"
        #init_message = 'ID Number: {}\nCreated On: {}\nDevice Version: {} \n-----------------------'.format(subN,creationDate,device_version)
        f.write(init_message)

        #Update database
        #Information I need: ID, Date Created, Data file Location, device Version
        with open('idDatabase.csv','a') as f:
            writer = csv.writer(f)
            writer.writerow([subN,creationDate,"",directory,device_version])

        idVal = subNumber
        refreshID()
        print("Subject Folder Created, Database Updated, label changed")
class lsButton(QPushButton):
    ### This Function Generates a Button to load old subjects
    def __init__(self,parent=None):
        super(lsButton,self).__init__()
        self.setStyleSheet("QPushButton {font:20px}")
        self.setText("Load Existing Subject")
        self.clicked.connect(lambda:self.load_s())

    def checkSubNumber(self,input):
        ###This function checks to see if a Subject Exits to load
        myArray = genfromtxt('idDatabase.csv',delimiter=',',skip_header=1)
        col1 = myArray[:,0]
        check = np.isin(input,col1,assume_unique=True)
        if(check == True):
            aval = 1
        else:
            aval = 0
        return aval

    def load_s(self):
        app.processEvents()
        subNum,okpressed = QInputDialog.getInt(self,"Which Subject?", "Subject: ",0,1,100,1)
        #idCheck = checkSubNumber(subNum)
        idCheck = 1
        if(idCheck == 1):
            global idVal
            idVal = subNum
            refreshID()
            print('Old Subject Loaded')
        else:
            print('ID Not Found')

class addLogButton(QPushButton):
    ### This Function Generates a Button to load old subjects
    def __init__(self,parent=None):
        super(addLogButton,self).__init__()
        self.setStyleSheet("QPushButton {font:20px}")
        self.setText("Add to Log")
        self.clicked.connect(lambda:self.addLog())

    def addLog(self):
        app.processEvents()
        updateLog()
class analyze(QPushButton):
    def __init__(self,parent=None):
        super(analyze,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Analyze Data")
        self.clicked.connect(lambda: self.analyzefcn())

    def analyzefcn(self):
        print("Under Construction")
class linAC_extend(QPushButton):
    def __init__(self,parent=None):
        super(linAC_extend,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("linAC Extend")
        global linAc
        self.clicked.connect(lambda: linAc.extend())
        print("Extend Linear Actuator")
class linAC_retract(QPushButton):
    def __init__(self,parent=None):
        super(linAC_retract,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("linAC Retract")
        global linAc
        self.clicked.connect(lambda: linAc.retract())
        print("Retract Linear Actuator")
class valve_opb(QPushButton):
    def __init__(self,parent=None):
        super(valve_opb,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Valve Open")
        global valve1
        global valve2
        global valve3
        self.clicked.connect(lambda: valve1.enable())
        self.clicked.connect(lambda: valve2.enable())
        self.clicked.connect(lambda: valve3.enable())
        print("Valve Open")
class valve_clb(QPushButton):
    def __init__(self,parent=None):
        super(valve_clb,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Valve Closed")
        global valve1
        global valve2
        global valve3
        self.clicked.connect(lambda: valve1.disable())
        self.clicked.connect(lambda: valve2.disable())
        self.clicked.connect(lambda: valve3.disable())
        print("Valve Closed")

#### EXTERNAL COMPONENT SELECTION ####
global linAc
linAc = LinearActuator(8,10)
global valve1
global valve2
global valve3
valve1 = Valve("main",18)
valve2 = Valve("main2",15)
valve3 = Valve("main3",16)
mos1 = MOS(adc1,0)
mos2 = MOS(adc1,1)
mos3 = MOS(adc1,2)
mos4 = MOS(adc1,3)
mos5 = MOS(adc2,0)
mos6 = MOS(adc2,1)
mos7 = MOS(adc2,2)
mos8 = MOS(adc2,3)

app = QApplication([])
app.setStyle('Fusion')
mp = QTabWidget()
mp.setWindowTitle("Cannabix GUI v4")
mp.resize(800,600)


#####################################
p1 = QWidget()
p1.setStyleSheet("background-color: {}".format(bgGrey))
p1L = QGridLayout()

p1IDL = QLabel()
p1IDL.setText("ID: {:d}".format(idVal))
p1IDL.setFrameShape(QFrame.Box)
p1appStat = QLabel()
p1appStat.setText("Status: {}".format(appStatus))
p1appStat.setFrameShape(QFrame.Box)
p1testTime = QLabel()
p1testTime.setText("Delay Time: {}s \n\nExposure Time: {}s \n\nRecovery Time: {}s \n\nTotal Time: {}s".format(bsc,exp,(totalTime - (bsc+exp)),totalTime))
p1testTime.setFrameShape(QFrame.Box)
p1Graph = graph()
tgb = startTest()
lgb = liveReading()
stpb = stop()
clb = clear()
vecLabel = QLabel()
vecLabel.setText("Temp: {:d}℃ \n\nHumidity: {:d}% \n\nPressure: {:d}kPa \n\nOxygen: {:d}%".format(int(tempVal_last),int(humVal_last),int(pressVal_last),int(oxVal_last)))
vecLabel.setFrameShape(QFrame.Box)
linac_eb = linAC_extend()
linac_rb = linAC_retract()
valve_op = valve_opb()
valve_cl = valve_clb()

p1L.addWidget(p1IDL,0,6,1,1)
p1L.addWidget(p1appStat,7,6,1,1)
p1L.addWidget(p1Graph,1,0,4,4)
p1L.addWidget(tgb,5,0,1,1)
p1L.addWidget(lgb,6,0,1,1)
p1L.addWidget(stpb,5,1,1,1)
p1L.addWidget(clb,6,1,1,1)
p1L.addWidget(vecLabel,1,6,2,1)
p1L.addWidget(p1testTime,3,6,2,1)
p1L.addWidget(linac_eb,5,2,1,1)
p1L.addWidget(linac_rb,6,2,1,1)
p1L.addWidget(valve_op,5,3,1,1)
p1L.addWidget(valve_cl,6,3,1,1)

p1.setLayout(p1L)
mp.addTab(p1,"Page 1")
#####################################
p2 = QWidget()
p2.setStyleSheet("background-color: {}".format(bgGrey))
p2L = QGridLayout()

p2IDL = QLabel()
p2IDL.setText("ID: {:d}".format(idVal))
p2IDL.setFrameShape(QFrame.Box)
p2appStat = QLabel()
p2appStat.setText("Status: {}".format(appStatus))
p2appStat.setFrameShape(QFrame.Box)
newsub_b = nsButton()
loadsub_b = lsButton()
addLog = addLogButton()


p2L.addWidget(p2IDL,0,6,1,1)
p2L.addWidget(p2appStat,7,6,1,1)
p2L.addWidget(newsub_b,2,1,1,3)
p2L.addWidget(loadsub_b,4,1,1,3)
p2L.addWidget(addLog,3,5,1,2)

p2.setLayout(p2L)
mp.addTab(p2,"Page 2")
#####################################
p3 = QWidget()
p3.setStyleSheet("background-color: {}".format(bgGrey))
p3L = QGridLayout()

p3IDL = QLabel()
p3IDL.setText("ID: {:d}".format(idVal))
p3IDL.setFrameShape(QFrame.Box)
p3appStat = QLabel()
p3appStat.setText("Status: {}".format(appStatus))
p3appStat.setFrameShape(QFrame.Box)
p3vecLabel = QLabel()
p3vecLabel.setText("Temp: {:d}℃ \n\nHumidity: {:d}% \n\nPressure: {:d}kPa \n\nOxygen: {:d}%".format(int(p3temp),int(p3hum),int(p3press),int(p3ox)))
p3vecLabel.setFrameShape(QFrame.Box)
p3Graph = graph()
p3clear = clear2()
loadData = loadDataButton()
genFButton = generateFile()
p3L.addWidget(p3IDL,0,6,1,1)
p3L.addWidget(p3appStat,7,6,1,1)
p3L.addWidget(p3Graph,1,0,4,4)
p3L.addWidget(p3vecLabel,1,6,2,1)
p3L.addWidget(p3clear,6,1,1,1)
p3L.addWidget(loadData,6,0,1,1)
p3L.addWidget(genFButton,6,2,1,1)
p3.setLayout(p3L)
mp.addTab(p3,"Page 3")
#####################################
mp.show()
app.exec_()
GPIO.cleanup()
