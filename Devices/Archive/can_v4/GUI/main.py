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

class graph(pg.PlotWidget):
    def __init(self,parent=None):
        super(graph,self).__init__()
        #self.setRange(xRange=(0,200),yRange=(0,5),disableAutoRange=True)
        self.setStyleSheet("pg.PlotWidget {border-style: outset; max-height: 50}")
##### BUTTONS #####
### Page 1 Buttons ###
#start test, stop, live graph, clear graph, linear actuator (extend, retract), valves (open close)
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
        else:
            idb.setID()
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
        ok2 = QMessageBox.information(self,"Save Data","Save the Data Now?",QMessageBox.Yes | QMessageBox.No)
        if(ok2 == QMessageBox.Yes):
            saveFile(all_data)
        else:
            print('File Not Saved')
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
class linAC_extend(QPushButton):
    def __init__(self,parent=None):
        super(linAC_extend,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("linAC Extend")
        self.clicked.connect(lambda: linAc.extend())
        print("Extend Linear Actuator")
class linAC_retract(QPushButton):
    def __init__(self,parent=None):
        super(linAC_retract,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("linAC Retract")
        self.clicked.connect(lambda: linAc.retract())
        print("Retract Linear Actuator")
class valve_open(QPushButton):
    def __init__(self,parent=None):
        super(valve_open,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Valve Open")
        self.clicked.connect(lambda: linAc.extend())
        print("Extend Linear Actuator")
class valve_close(QPushButton):
    def __init__(self,parent=None):
        super(valve_close,self).__init__()
        self.setStyleSheet("QPushButton {font: 20px}")
        self.setText("Valve Close")
        self.clicked.connect(lambda: linAc.retract())
        print("Retract Linear Actuator")
######################

### Page 2 Buttons ###
# New Subject, Load Subject, Add to log
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
class addtoLog(QPushButton):
    def __init__(self,parent=None):
        super(lsButton,self).__init__()
        self.setStyleSheet("QPushButton {font:13px}")
        self.setText("Add to Log")
        self.clicked.connect(lambda:self.addtoLog())

    def addtoLog(self):
        print(doing stuff)
