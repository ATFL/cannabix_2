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

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
import Adafruit_ADS1x15 as ads
adc1 = ads.ADS1115(0x48)
# adc2 = ads.ADS1115(0x49)

########## GLOBAL VARIABLES ###############################
global subID
subID = 0
global tempVal
tempVal = []
global humVal
humVal = []
global pressVal
pressVal = []
global tempVala
tempVala = 25 #comment when running
global humVala
humVala = 26#comment when running
global pressVala
pressVala = 27#comment when running
global testTime
testTime = []
global sens1
sens1 = []
global sens2
sens2 = []
global sens3
sens3 = []
global sens4
sens4 = []
global mos1
global mos2
global mos3
global mos4
global runStatus
runStatus = 0
global lgStatus
lgStatus = 0
global tempLabel
global humLabel
global pressLabel
global idVal
global curDir
global today
global device_version

idVal = ''
curDir = os.getcwd()
today = date.today()
device_version = 2.5
###########################################################
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
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'r'

    def extend(self):
        print('Extending linear actuator.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        extending = 5.55 #5.3
        self.pwm.ChangeDutyCycle(extending) #5.3
        print('Extended at',extending)
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'e'

    def retract(self):
        print('Retracting linear actuator.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(8.5)
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'r'
def updateGraph():
    global testTime
    global sens1
    global sens2
    global sens3
    global sens4
    global sens1plot
    global sens2plot
    global sens3plot
    global sens4plot
    global tempVal
    global humVal
    global pressVal
    global tempVala
    global humVala
    global pressVala
    global tempLabel
    global humLabel
    global pressLabel
    sens1plot.setData(testTime,sens1)
    sens2plot.setData(testTime,sens2)
    sens3plot.setData(testTime,sens3)
    sens4plot.setData(testTime,sens4)
    tempLabel.setNum(tempVala)
    humLabel.setNum(humVala)
    pressLabel.setNum(pressVala)
    app.processEvents()


#### Page 1 Buttons ####
class startTest(QPushButton):
    def __init__(self,parent=None):
        super(startTest,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Start Test")
        self.clicked.connect(lambda: self.startTestfcn())

    def startTestfcn(self):
        #starting full breath test
        #gpGraph.clear()
        cl_b.clearGraphfcn()
        QMessageBox.information(self,"Breath Input","Press Okay After Breath Input",QMessageBox.Ok)
        print("Starting Recording Data")
        global runStatus
        global testTime
        global mos1
        global mos2
        global mos3
        global mos4
        global sens1
        global sens2
        global sens3
        global sens4
        global tempVal
        global humVal
        global pressVal
        global tempVala
        global humVala
        global pressVala
        startTime = time.time()
        global sens1plot
        global sens2plot
        global sens3plot
        global sens4plot
        global subID
        # gpGraph.addLegend(offset=(0,10))
        sens1plot = gpGraph.plot(testTime,sens1,pen='r',name='sens1')
        sens2plot = gpGraph.plot(testTime,sens2,pen='g',name='sens2')
        sens3plot = gpGraph.plot(testTime,sens3,pen='b',name='sens3')
        sens4plot = gpGraph.plot(testTime,sens4,pen='k',name='sens4')
        gpGraph.setYRange(0,5)
        gpGraph.setXRange(0,35)

        runStatus = 1
        totalTime = 35

        while((time.time() - startTime) < totalTime and runStatus ==1):
            app.processEvents()
            if((time.time() - startTime) < 10):
                if(linAc.state != 'r'):
                    linAc.retract()
            elif((time.time() - startTime) >= 10 and (time.time() - startTime) < 30):
                if(linAc.state != 'e'):
                    linAc.extend()
            elif((time.time() - startTime) >=30):
                if(linAc.state != 'r'):
                    linAc.retract()
            else:
                if(linAc.state != 'r'):
                    linAc.retract()
            # if(runStatus == 0): #maybe comment this out
            #     break
            testTime.append(time.time() - startTime)
            sens1.append(mos1.read())
            sens2.append(mos2.read())
            sens3.append(mos3.read())
            sens4.append(mos4.read())
            tempVal.append(tempVala)
            humVal.append(humVala)
            pressVal.append(pressVala)
            updateGraph()
            app.processEvents()
        # TODO: save data
        final_file = np.column_stack((testTime,sens1,sens2,sens3,sens4,tempVal,humVal,pressVal))

class stop(QPushButton):
    def __init__(self,parent=None):
        super(stop,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Stop")
        self.clicked.connect(lambda: self.stopfcn())

    def stopfcn(self):
        global runStatus
        global lgStatus
        runStatus = 0
        lgStatus = 0
        app.processEvents()
        print("Stop Everything")
class liveReading(QPushButton):
    def __init__(self,parent=None):
        super(liveReading,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Live Graph")
        self.clicked.connect(lambda: self.liveReadingfcn())

    def liveReadingfcn(self):
        #gpGraph.clear()
        cl_b.clearGraphfcn()
        global runStatus
        global lgStatus
        lgStatus = 1
        global testTime
        testTime = list(range(100))
        global mos1
        global mos2
        global mos3
        global mos4
        global sens1
        sens1 = [0 for _ in range(100)]
        global sens2
        sens2 = [0 for _ in range(100)]
        global sens3
        sens3 = [0 for _ in range(100)]
        global sens4
        sens4 = [0 for _ in range(100)]
        global tempVal
        global humVal
        global pressVal
        global tempVala
        global humVala
        global pressVala
        startTime = time.time()
        global sens1plot
        global sens2plot
        global sens3plot
        global sens4plot
        # gpGraph.addLegend(offset=(300,0))
        sens1plot = gpGraph.plot(testTime,sens1,pen='r',name='sens1')
        sens2plot = gpGraph.plot(testTime,sens2,pen='g',name='sens2')
        sens3plot = gpGraph.plot(testTime,sens3,pen='b',name='sens3')
        sens4plot = gpGraph.plot(testTime,sens4,pen='k',name='sens4')
        gpGraph.setYRange(0,5)
        gpGraph.setXRange(0,35)
        while(lgStatus == 1):
            app.processEvents()
            # if(lgStatus == 0):
            #     break
            sens1 = sens1[1:]
            sens2 = sens2[1:]
            sens3 = sens3[1:]
            sens4 = sens4[1:]
            sens1.append(mos1.read())
            sens2.append(mos2.read())
            sens3.append(mos3.read())
            sens4.append(mos4.read())
            updateGraph()
            app.processEvents()

class clearGraph(QPushButton):
    def __init__(self,parent=None):
        super(clearGraph,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Clear Graph")
        self.clicked.connect(lambda: self.clearGraphfcn())

    def clearGraphfcn(self):
        clearmsg = QMessageBox.warning(self,"Clear Warning","Are you sure you want to clear?",QMessageBox.Yes | QMessageBox.No)
        if(clearmsg == QMessageBox.Yes):
            global testTime
            global sens1
            global sens2
            global sens3
            global sens4
            global tempVal
            global humVal
            global pressVal
            global tempLabel
            global humLabel
            global pressLabel
            testTime = []
            sens1 = []
            sens2 = []
            sens3 = []
            sens4 = []
            tempVal = []
            humVal = []
            pressVal = []
            gpGraph.clear()
            tempLabel.clear()
            humLabel.clear()
            pressLabel.clear()

        print("Clear All Data")
class analyze(QPushButton):
    def __init__(self,parent=None):
        super(analyze,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Analyze Data")
        self.clicked.connect(lambda: self.analyzefcn())

    def analyzefcn(self):
        print("Under Construction")
class linAC_extend(QPushButton):
    def __init__(self,parent=None):
        super(linAC_extend,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("linAC Extend")
        self.clicked.connect(lambda: linAc.extend())
        print("Extend Linear Actuator")
class linAC_retract(QPushButton):
    def __init__(self,parent=None):
        super(linAC_retract,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("linAC Retract")
        self.clicked.connect(lambda: linAc.retract())
        print("Retract Linear Actuator")

#### Page 2 Buttons ####
class nsButton(QPushButton):
   ### This Function Generates a Button to create new subjects
    def __init__(self,parent=None):
        super(nsButton,self).__init__()
        self.setStyleSheet("QPushButton {font:13px}")
        self.setText("Add New Subject")
        self.clicked.connect(lambda:self.add_new_s())

    def add_new_s(self):
        app.processEvents()
        subNumber = self.genSubNumber()
        message = 'Add Subject ' + str(subNumber)
        newSubjectReply = QMessageBox.question(self, 'Add Subject',message,QMessageBox.Yes | QMessageBox.No)
        if newSubjectReply == QMessageBox.Yes:
            #self.getSubInfo(subNumber)
            self.genSubject(subNumber)
            print('New Subject Added')

        else:
            print('No Actions Done')
    def genSubNumber(self):
        ###This function generates a random number for a test participant
        myArray = genfromtxt('idDatabase.csv',delimiter=',',skip_header=1)
        col1 = myArray[:,0]
        numFound = False
        myRand = 0
        while(numFound == False):
            myRand = np.random.randint(1,10,1)
            check = np.isin(myRand,col1,assume_unique=True)
            if(check == True):
                pass
            else:
                numFound = True
        return myRand

    #def getSubInfo(self,subNumber):


    def genSubject(self,subNumber):
        ## This function generates the files and folders required for each subject also updates the database
        subN = str(subNumber)[1:-1]
        filename = 'id' + str(subN)
        directory = 'Data/byID/' + filename
        if not os.path.exists(directory):
            os.makedirs(directory)

        global today
        global curDir
        global device_version
        creationDate = today.strftime("%d-%m-%Y")
        f = open(directory + '/' + filename + '.txt',"w+")
        init_message = "ID Number: "+ subN+ "\nCreated on: " + str(creationDate) + "\nDevice Version: " + str(device_version) + "\n-----------------------"
        f.write(init_message)

        #Update database
        #Information I need: ID, Date Created, Data file Location, device Version
        with open('idDatabase.csv','a') as f:
            writer = csv.writer(f)
            writer.writerow([subN,creationDate,"",directory,device_version])

        print("Subject Folder Created, Database Updated")
class lsButton(QPushButton):
    ### This Function Generates a Button to load old subjects
    def __init__(self,parent=None):
        super(lsButton,self).__init__()
        self.setStyleSheet("QPushButton {font:13px}")
        self.setText("Load Existing Subject")
        self.clicked.connect(lambda:self.load_s())

    def load_s(self):
        app.processEvents()
        global curDir
        #show a box to input number in
        subNum,okpressed = QInputDialog.getInt(self,"Which Subject?", "Subject: ",0,1,100,1)
        #print(subNum)
        #need to access file directory
        filename = 'id' + str(subNum)
        directory = 'Data/byID/' + filename
        ## Testing loading directory
#         with open(directory + "/" + filename +".txt",'r') as f:
#             fR = csv.reader(f)
#             for row in fR:
#                 print(row)

        print('Old Subject Loaded')

#### Page 3 Buttons ####
class loadDataButton(QPushButton):
    def __init__(self,parent=None):
        super(loadDataButton,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Load Data")
        self.clicked.connect(lambda: self.loadData())

    def loadData(self):
        print("Under Construction")
class generateFile(QPushButton):
    def __init__(self,parent=None):
        super(generateFile,self).__init__()
        self.setStyleSheet("QPushButton {font: 13px}")
        self.setText("Generate File")
        self.clicked.connect(lambda: self.genFile())

    def genFile(self):
        print("Under Construction")
# class loadDataButton(QPushButton):
#     def __init__(self,parent=None):
#         super(loadDataButton,self).__init__()
#         self.setStyleSheet("QPushButton {font: 13px}")
#         self.setText("Load Data")
#         self.clicked.connect(lambda: self.loadData())
#
#     def loadData(self):
#         print("Under Construction")
# class loadDataButton(QPushButton):
#     def __init__(self,parent=None):
#         super(loadDataButton,self).__init__()
#         self.setStyleSheet("QPushButton {font: 13px}")
#         self.setText("Load Data")
#         self.clicked.connect(lambda: self.loadData())
#
#     def loadData(self):
#         print("Under Construction")
# class loadDataButton(QPushButton):
#     def __init__(self,parent=None):
#         super(loadDataButton,self).__init__()
#         self.setStyleSheet("QPushButton {font: 13px}")
#         self.setText("Load Data")
#         self.clicked.connect(lambda: self.loadData())
#
#     def loadData(self):
#         print("Under Construction")

linAc = LinearActuator(8,10)
mos1 = MOS(adc1,0)
mos2 = MOS(adc1,1)
mos3 = MOS(adc1,2)
mos4 = MOS(adc1,3)
app = QApplication([])
app.setStyle('Fusion')

mainPage = QTabWidget()
mainPage.setWindowTitle("CANNABIX THC DETECTOR")
mainPage.resize(800,600)

################ PAGE 1 ###############################
#graphical testing page
gpage = QWidget()
gpLayout = QGridLayout()
gpage.setStyleSheet("background-color: grey;")
gpGraph = graph()
gpGraph.addLegend(offset=(0,10))
st1_b = startTest()
stop_b = stop()
lg_b = liveReading()
cl_b = clearGraph()
at_b = analyze()
linac_eb = linAC_extend()
linac_rb = linAC_retract()
gp_subIDL = QLabel()
gp_subIDL.setText("ID: ")
gp_subID = QLabel()
gp_subID.setNum(subID)
gp_subID.setFrameShape(QFrame.Box)
tempL = QLabel()
tempL.setText("Temperature: ")
global tempLabel
tempLabel = QLabel()
tempLabel.setNum(tempVala)
tempLabel.setFrameShape(QFrame.Box)
global humLabel
humL = QLabel()
humL.setText("Humidity: ")
humLabel = QLabel()
humLabel.setNum(humVala)
humLabel.setFrameShape(QFrame.Box)
pressL = QLabel()
pressL.setText("Pressure: ")
global pressLabel
pressLabel = QLabel()
pressLabel.setNum(pressVala)
pressLabel.setFrameShape(QFrame.Box)

gpLayout.addWidget(gpGraph,1,0,4,4)
gpLayout.addWidget(st1_b,5,0,1,1)
gpLayout.addWidget(stop_b,5,2,2,1)
gpLayout.addWidget(lg_b,5,1,1,1)
gpLayout.addWidget(cl_b,6,0,1,1)
gpLayout.addWidget(at_b,6,1,1,1)
gpLayout.addWidget(linac_eb,5,3,1,1)
gpLayout.addWidget(linac_rb,6,3,1,1)
gpLayout.addWidget(gp_subIDL,0,5,1,1)
gpLayout.addWidget(gp_subID,0,6,1,1)

gpLayout.addWidget(tempL,1,5,1,1)
gpLayout.addWidget(humL,2,5,1,1)
gpLayout.addWidget(pressL,3,5,1,1)
gpLayout.addWidget(tempLabel,1,6,1,1)
gpLayout.addWidget(humLabel,2,6,1,1)
gpLayout.addWidget(pressLabel,3,6,1,1)

gpage.setLayout(gpLayout)
mainPage.addTab(gpage,"Graphical")

#######################################################

################ PAGE 2 ###############################
#subject control page
sPage = QWidget()
spLayout = QGridLayout()
sPage.setStyleSheet("background-color: grey;")

sp_subIDL = QLabel()
sp_subIDL.setText("ID: ")
sp_subID = QLabel()
sp_subID.setNum(subID)
sp_subID.setFrameShape(QFrame.Box)

newSub_b = nsButton()
loadSub_b = lsButton()

spLayout.addWidget(sp_subIDL,0,5,1,1)
spLayout.addWidget(sp_subID,0,6,1,1)
spLayout.addWidget(newSub_b,2,2,2,3)
spLayout.addWidget(loadSub_b,4,2,2,3)

sPage.setLayout(spLayout)
mainPage.addTab(sPage,"Subject")

#######################################################

################ PAGE 3 ###############################

dPage = QWidget()
dpLayout = QGridLayout()
dPage.setStyleSheet("background-color: grey;")

dp_subIDL = QLabel()
dp_subIDL.setText("ID: ")
dp_subID = QLabel()
dp_subID.setNum(subID)
dp_subID.setFrameShape(QFrame.Box)
dpGraph = graph()
load_b = loadDataButton()
genDoc_b = generateFile()
dpLayout.addWidget(dp_subIDL,0,5,1,1)
dpLayout.addWidget(dp_subID,0,6,1,1)
dpLayout.addWidget(dpGraph,1,0,4,4)
dpLayout.addWidget(load_b,5,0,1,2)
dpLayout.addWidget(genDoc_b,5,2,1,2)
dPage.setLayout(dpLayout)
mainPage.addTab(dPage,"Load Data")
#######################################################


######## NO CODE BELOW THIS ##########
mainPage.show()
app.exec_()
