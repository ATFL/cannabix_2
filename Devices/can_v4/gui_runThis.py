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
from os import *
import numpy as np
from numpy import genfromtxt
from math import *
from pandas import read_csv as rc
from statistics import mean

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
global curDir
curDir = getcwd()
global today
today = date.today()
global device_version
device_version = 3
global totalTime
global bsc
global exp
totalTime = 35
bsc = 5
exp = 15
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

##### COLORS ######
bgGrey = '#A9A9A9'

adc1 = 1
adc2 = 2

def refreshID():
    global idPath
    global idVal
    global curDir
    p1IDL.setText("ID: {:d}".format(idVal))
    p2IDL.setText("ID: {:d}".format(idVal))
    p3IDL.setText("ID: {:d}".format(idVal))
def refreshStatus():
    p1appStat.setText("Status: {}".format(appStatus))
    p2appStat.setText("Status: {}".format(appStatus))
    p3appStat.setText("Status: {}".format(appStatus))
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
def updateLog(message):
    global idVal
    global curDir
    global idPath
    global curTime
    logPath = "{}id{}.txt".format(idPath,idVal)
    bar = "-----------------------"
    f = open(logPath,'a+')
    if(message != ""):
        full_txt = "\n{}: {} \n{}".format(curTime,message,bar)
    else:
        full_txt = "\n{}: {} \n{}".format(curTime,"New Test Performed",bar)
    f.write(full_txt)
    close(f)
def saveFile(data):
    global idVal
    global curDir
    global today
    global appStatus
    global curTime
    appStatus = 'Saving'
    refreshStatus()


    curTime = time.strftime("%d-%m-%y_%H-%M-%S",time.localtime())
    msg,ok = QInputDialog.getText(None,"Add Log Info","Any Addition to ID Log?")
    updateLog(msg)
    np.savetxt("{}id{}_{}.csv".format(idPath,idVal,curTime),data,fmt='%.10f',delimiter=',')
    print('File Saved')
class MOS:
    def __init__(self, adc, channel):

        self.GAIN = 2 / 3
        self.adc = adc
        self.channel = channel
        #self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144

    def read(self):
        # self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144
        # return self.conversion_value
        global testTime
        return sin(time.time())*5

    def print(self):
        self.read()
        #print("\nReading from MOS: {}".format(self.conversion_value))
class graph(pg.PlotWidget):
    def __init(self,parent=None):
        super(graph,self).__init__()
        #self.setRange(xRange=(0,200),yRange=(0,5),disableAutoRange=True)
        self.setStyleSheet("pg.PlotWidget {border-style: outset; max-height: 50}")
class startTest(QPushButton):
    def __init__(self,parent=None):
        super(startTest,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Start Test")
        self.clicked.connect(lambda: self.startTest())

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


        ok1 = QMessageBox.information(self,"Test ID","Using ID {:d}. Press Ok if Correct".format(idVal),QMessageBox.Ok | QMessageBox.No)
        if(ok1 != QMessageBox.Ok):
            print("New ID set")
        # else:
        #     idb.setID()
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
        sens1plot = p1Graph.plot(testTime,sens1,pen='r',name='sens1')
        sens2plot = p1Graph.plot(testTime,sens2,pen='g',name='sens2')
        sens3plot = p1Graph.plot(testTime,sens3,pen='b',name='sens3')
        sens4plot = p1Graph.plot(testTime,sens4,pen='k',name='sens4')
        p1Graph.setYRange(0,5)
        p1Graph.setXRange(0,50)


        tgStatus = 1
        appStatus = "Testing"
        refreshStatus()

        while((time.time() - startTime) < totalTime and tgStatus == 1):
            app.processEvents()
            # if((time.time() - startTime) < bsc):
            #     if(linAc.state != 'r'):
            #         linAc.retract()
            # elif((time.time() - startTime) >= bsc and (time.time() - startTime) < exp):
            #     if(linAc.state != 'e'):
            #         linAc.extend()
            # elif((time.time() - startTime) >=exp):
            #     if(linAc.state != 'r'):
            #         linAc.retract()
            # else:
            #     if(linAc.state != 'r'):
            #         linAc.retract()
            testTime.append(time.time() - startTime)
            sens1.append(mos1.read())
            sens2.append(mos2.read())
            sens3.append(mos3.read())
            sens4.append(mos4.read())
            tempVal.append(mos5.read())
            humVal.append(mos6.read())
            pressVal.append(mos7.read())
            oxVal.append(mos8.read())
            tempVal_last = tempVal[-1]
            humVal_last = humVal[-1]
            pressVal_last = pressVal[-1]
            oxVal_last = oxVal[-1]
            updateGUI()
            app.processEvents()
        all_data = np.column_stack((testTime,sens1,sens2,sens3,sens4,tempVal,humVal,pressVal,oxVal))
        #ok2 = QMessageBox.information(self,"Save Data","Save the Data Now?",QMessageBox.Yes | QMessageBox.No)
        #if(ok2 == QMessageBox.Yes):
        saveFile(all_data)
        #else:
        #       print('File Not Saved')
        appStatus = 'Ready'
        refreshStatus()
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
        sens1plot = p1Graph.plot(testTime,sens1,pen='r',name='sens1')
        sens2plot = p1Graph.plot(testTime,sens2,pen='g',name='sens2')
        sens3plot = p1Graph.plot(testTime,sens3,pen='b',name='sens3')
        sens4plot = p1Graph.plot(testTime,sens4,pen='k',name='sens4')
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
class save(QPushButton):
    def __init__(self,parent=None):
        super(save,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Save")
        self.clicked.connect(lambda: self.savefcn())

    def savefcn(self):
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
        p3sens1plot = p3Graph.plot(p3Time,p3sens1,pen='r',name='sens1')
        p3sens2plot = p3Graph.plot(p3Time,p3sens2,pen='g',name='sens2')
        p3sens3plot = p3Graph.plot(p3Time,p3sens3,pen='b',name='sens3')
        p3sens4plot = p3Graph.plot(p3Time,p3sens4,pen='k',name='sens4')
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
p1L.addWidget(p1IDL,0,6,1,1)
p1L.addWidget(p1appStat,7,6,1,1)
p1L.addWidget(p1Graph,1,0,4,4)
p1L.addWidget(tgb,5,0,1,1)
p1L.addWidget(lgb,6,0,1,1)
p1L.addWidget(stpb,5,1,1,1)
p1L.addWidget(clb,6,1,1,1)
p1L.addWidget(vecLabel,1,6,2,1)
p1L.addWidget(p1testTime,3,6,2,1)
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

p2L.addWidget(p2IDL,0,6,1,1)
p2L.addWidget(p2appStat,7,6,1,1)

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
