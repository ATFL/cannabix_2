import numpy as np
import os
import sys
import time
import csv
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime
from pandas import read_csv as rc
import pyqtgraph as pg
from statistics import mean
import RPi.GPIO as GPIO
import Adafruit_ADS1x15 as ads

GPIO.setmode(GPIO.BOARD)
adc1 = ads.ADS1115(0x48)
adc2 = ads.ADS1115(0x48)

# VARIABLE SETUP
global idVal
global directory
global filename
global appStatus
global window
global appStatGlobe
filename = ''
idVal = 0
directory = 'Data/byID/id{}'.format(idVal)
appStatus = 'Ready'
curDir = os.getcwd()

s1n = '2602'
s2n = '2603'
s3n = '2610'

prm_list = rc('parameters.csv', delimiter=',', header='infer')
sVersion = prm_list['Software Version'].values
dVersion = prm_list['Device Version'].values
dID = prm_list['Device ID'].values


app = QApplication(sys.argv)


class MOS:
    def __init__(self, adc, channel):
        self.GAIN = 2 / 3
        self.adc = adc
        self.channel = channel
        self.conversion_value = (self.adc.read_adc(self.channel, gain=self.GAIN) / pow(2, 15)) * 6.144

    def read(self):
        self.conversion_value = (self.adc.read_adc(self.channel, gain=self.GAIN) / pow(2, 15)) * 6.144
        return self.conversion_value
        # global testTime
        # return sin(time.time())*5

    def read_hum(self):
        self.conversion_value = (self.adc.read_adc(self.channel, gain=self.GAIN) / pow(2, 15)) * 6.144
        self.conversion_value2 = self.conversion_value / 5 * 125 - 12.5
        return self.conversion_value2

    # TODO: make functions to read temp pressure humidity and oxygen
    def read_temp(self):
        self.conversion_value = (self.adc.read_adc(self.channel, gain=self.GAIN) / pow(2, 15)) * 6.144
        self.conversion_value2 = self.conversion_value / 5 * 218.75 - 66.875
        return self.conversion_value2

    def print(self):
        self.read()
        # print("\nReading from MOS: {}".format(self.conversion_value))


class LinearActuator:
    def __init__(self, pinLA, pinEnable):
        self.pinLA = pinLA
        self.pinEnable = pinEnable
        GPIO.setup(self.pinLA, GPIO.OUT)
        GPIO.setup(self.pinEnable, GPIO.OUT)
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm = GPIO.PWM(pinLA, 50)
        self.pwm.start(8.5)
        QTimer.singleShot(1.5*1000, lambda: GPIO.output(self.pinEnable, GPIO.LOW))
        self.state = 'r'

    def extend(self):
        # print('Extending linear actuator.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        extending = 5.3  # 5.3
        self.pwm.ChangeDutyCycle(extending)
        print("Extending")
        QTimer.singleShot(1.5*1000, lambda: GPIO.output(self.pinEnable, GPIO.LOW))
        self.state = 'e'

    def retract(self):
        # print('Retracting linear actuator.')
        print("Retracting") 
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(8.5)
        QTimer.singleShot(1.5*1000, lambda: GPIO.output(self.pinEnable, GPIO.LOW))
        self.state = 'r'

    def default(self):
        # print('Moving linear actuator to default (center) position.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(6)
        QTimer.singleShot(1.5*1000, lambda: GPIO.output(self.pinEnable, GPIO.LOW))
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
        # print("GPIO.LOW")

    def disable(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False
        print(self.name + ' disabled.')


valve1 = Valve("main", 18)
valve1.disable()
valve2 = Valve("main2", 15)
valve2.disable()
valve3 = Valve("main3", 16)
valve3.disable()

mos1 = MOS(adc1, 0)
mos2 = MOS(adc1, 1)
mos3 = MOS(adc1, 2)
mos4 = MOS(adc1, 3)
mos5 = MOS(adc2, 0)
mos6 = MOS(adc2, 1)
mos7 = MOS(adc2, 2)
mos8 = MOS(adc2, 3)

la = LinearActuator(8, 10)
la.retract()


class Frontpage(QWidget):
    class Graph(pg.PlotWidget):
        def __init__(self, parent=None):
            super(Frontpage.Graph, self).__init__()
            self.setStyleSheet("pg.PlotWidget {border-style: outset; max-height: 50}")

    class startTest(QPushButton):
        def __init__(self, parent=None):
            super(Frontpage.startTest, self).__init__()
            self.setText('Start Test')

    class stop(QPushButton):
        def __init__(self, parent=None):
            super(Frontpage.stop, self).__init__()
            self.setText('Stop')

    class liveReading(QPushButton):
        def __init__(self, parent=None):
            super(Frontpage.liveReading, self).__init__()
            self.setText('Live Reading')

    class clear(QPushButton):
        def __init__(self, parent=None):
            super(Frontpage.clear, self).__init__()
            self.setText('Clear All')

    class linac_eb(QPushButton):
        def __init__(self, parent=None):
            super(Frontpage.linac_eb, self).__init__()
            self.setText('Extend LA')
            self.clicked.connect(lambda: la.extend())

    class linac_rb(QPushButton):
        def __init__(self, parent=None):
            super(Frontpage.linac_rb, self).__init__()
            self.setText('Retract LA')
            self.clicked.connect(lambda: la.retract())

    class valve_op(QPushButton):
        def __init__(self, parent=None):
            super(Frontpage.valve_op, self).__init__()
            self.setText('Open Valves')
            self.clicked.connect(lambda: valve1.enable())
            self.clicked.connect(lambda: valve2.enable())
            self.clicked.connect(lambda: valve3.enable())

    class valve_cl(QPushButton):
        def __init__(self, parent=None):
            super(Frontpage.valve_cl, self).__init__()
            self.setText('Close Valves')
            self.clicked.connect(lambda: valve1.disable())
            self.clicked.connect(lambda: valve2.disable())
            self.clicked.connect(lambda: valve3.disable())

    def __init__(self, *args, **kwargs):
        super(Frontpage, self).__init__(*args, **kwargs)
        self.pTime1 = 2  # Pre-purge: this will normally run for 60 seconds
        self.pTime2 = 2  # Pre-purge: this will normally run for 30 seconds
        self.pTime3 = 2  # Pre-purge: this is commented out
        self.pTime4 = 2  # Post-purge: this will normally run for 40 seconds

        self.totTime = 20  # This is the total time: normally 300 seconds
        self.tTime1 = 5  # This is the time when the sensor is extended: Normally 10
        self.tTime2 = 10  # This is the time when the sensor is retracted: Normally 60

        self.runTime = []  # All Time Values

        self.sens1 = []  # All MOS 1 Values
        self.sens2 = []  # All MOS 2 Values
        self.sens3 = []  # All MOS 3 Values
        # self.sens4 = [] # All MOS 4 Values : GENERALLY COMMENTED OUT

        self.tempVal = [] # Full List of temp values over test
        self.pressVal = [] # Full List of pressure values over test
        self.humVal = [] # Full List of humidity values over test
        self.oxVal = [] # Full List of oxygen values over test

        self.tempVal_last = 0 # Last value for the UI
        self.pressVal_last = 0 # Last value for the UI
        self.humVal_last = 0 # Last value for the UI
        self.oxVal_last = 0 # Last value for the UI

        self.UI()

    def UI(self):
        self.layout = QGridLayout()
        global idVal
        self.idL = QLabel('ID: {:d}'.format(idVal))
        self.idL.setFrameShape(QFrame.Box)
        global appStatus
        self.appStat = QLabel('Status: {}'.format(appStatus))
        self.appStat.setFrameShape(QFrame.Box)
        self.testTime = QLabel('Baseline Check Time: {}s \n\n'
                               'Exposure Time: {}s \n\nRecovery Time: {}s \n\nTotal Time: {}s'.format(self.tTime1,
                                                                                            self.tTime2 - self.tTime1,
                                                                                            self.totTime - self.tTime2,
                                                                                            self.totTime))

        self.testTime.setFrameShape(QFrame.Box)
        self.vecL = QLabel(
            'Temp: {:d}℃ \n\nHumidity: {:d}% \n\nPressure: {:d}kPa \n\nOxygen: {:d}%'.format(int(self.tempVal_last),
                                                                                             int(self.humVal_last),
                                                                                             int(self.pressVal_last),
                                                                                             int(self.oxVal_last)))
        self.vecL.setFrameShape(QFrame.Box)
        self.graph = self.Graph()
        # Buttons
        self.stb = self.startTest()
        self.lirb = self.liveReading()
        self.stpb = self.stop()
        self.clb = self.clear()
        self.leb = self.linac_eb()
        self.lrb = self.linac_rb()
        self.vob = self.valve_op()
        self.vcb = self.valve_cl()
        # Button Actions
        self.stb.clicked.connect(lambda: self.runTest())
        self.lirb.clicked.connect(lambda: self.lgTest())
        self.clb.clicked.connect(lambda: self.clrfcn())
        self.stpb.clicked.connect(lambda: self.stopTest())
        # SET LAYOUT #
        self.layout.addWidget(self.idL, 0, 6, 1, 1)
        self.layout.addWidget(self.appStat, 7, 6, 1, 1)
        self.layout.addWidget(self.vecL, 1, 6, 2, 1)
        self.layout.addWidget(self.testTime, 3, 6, 2, 1)
        self.layout.addWidget(self.graph, 1, 0, 4, 4)
        self.layout.addWidget(self.stb, 5, 0, 1, 1)
        self.layout.addWidget(self.lirb, 6, 0, 1, 1)
        self.layout.addWidget(self.stpb, 5, 1, 1, 1)
        self.layout.addWidget(self.clb, 6, 1, 1, 1)
        self.layout.addWidget(self.leb, 5, 2, 1, 1)
        self.layout.addWidget(self.lrb, 6, 2, 1, 1)
        self.layout.addWidget(self.vob, 5, 3, 1, 1)
        self.layout.addWidget(self.vcb, 6, 3, 1, 1)

        self.setLayout(self.layout)

    def clrfcn(self):
        self.runTime = []  # All time values

        self.sens1 = []  # All MOS 1 Values
        self.sens2 = []  # All MOS 2 Values
        self.sens3 = []  # All MOS 3 Values
        # self.sens4 = [] # All MOS 4 Values : GENERALLY COMMENTED OUT

        self.tempVal = []  # Full List of temp values over test
        self.pressVal = []  # Full List of pressure values over test
        self.humVal = []  # Full List of humidity values over test
        self.oxVal = []  # Full List of oxygen values over test

        self.tempVal_last = 0  # Last value for the UI
        self.pressVal_last = 0  # Last value for the UI
        self.humVal_last = 0  # Last value for the UI
        self.oxVal_last = 0  # Last value for the UI

        self.graph.clear()
        
        global appStatus
        appStatus = "Status: Ready"
        self.appStat.setText(appStatus)
        global window
        window.subject.appStat.setText(appStatus)
        window.data.appStat.setText(appStatus) 

    def stopTest(self):
        global appStatus
        appStatus = "Status: Test Aborted"
        self.appStat.setText(appStatus)
        window.front.appStat.setText(appStatus)
        window.subject.appStat.setText(appStatus)
        window.data.appStat.setText(appStatus)
        self.appStat.setText(appStatus)
        app.processEvents()
        if self.runStatus == 1:
            
            if 'dataTimer' in globals():
                global dataTimer
                dataTimer.stop()
            # dataTimer.setInterval(0)
                global uiTimer
                uiTimer.stop()
            # uiTimer.setInterval(0)
            la.retract()
            valve1.disable()
            valve2.disable()
            valve3.disable()
            print('Accessories Reset')
            
        elif self.runStatus == 2:
            global lgTimer
            lgTimer.stop()
           
        else:
            pass

    def lgTest(self):
        self.runStatus = 2
        self.clrfcn()
        print('Live Graph')
        global appStatus
        appStatus = "Live Graph"
        self.appStat.setText('Live Graph')
        self.lgTime = list(range(100))
        self.lgsens1 = [0 for _ in range(100)]
        self.lgsens2 = [0 for _ in range(100)]
        self.lgsens3 = [0 for _ in range(100)]
        # sens4 = [0 for _ in range(100)] # Normally Commented Out
        self.lgplot1 = self.graph.plot(self.lgTime, self.lgsens1, pen='r', name='{}'.format(s1n))
        self.lgplot2 = self.graph.plot(self.lgTime, self.lgsens2, pen='g', name='{}'.format(s2n))
        self.lgplot3 = self.graph.plot(self.lgTime, self.lgsens3, pen='b', name='{}'.format(s3n))
        # self.lgplot4 = self.graph.plot(self.lgTime, self.lgsens4, pen='k', name='{}'.format(s1n))

        def endTest():
            lgTimer.stop()
        def updateUI():
            self.lgsens1 = self.lgsens1[1:]
            self.lgsens2 = self.lgsens2[1:]
            self.lgsens3 = self.lgsens3[1:]
            # self.lgsens4 = self.lgsens4[1:]

            self.lgsens1.append(mos1.read())
            self.lgsens2.append(mos2.read())
            self.lgsens3.append(mos3.read())
            # self.lgsens4.append(mos4.read())

            self.lgplot1.setData(self.lgTime, self.lgsens1)
            self.lgplot2.setData(self.lgTime, self.lgsens2)
            self.lgplot3.setData(self.lgTime, self.lgsens3)
            # self.lgplot4.setData(self.lgTime, self.lgsens4)
            
            global appStatus
            global window
            window.subject.appStat.setText(appStatus)
            window.data.appStat.setText(appStatus)
        global lgTimer
        lgTimer = QTimer()
        lgTimer.timeout.connect(lambda: updateUI())
        lgTimer.start(100)

    def purge(self):
        global appStatus
        appStatus = 'purging'

        self.appStat.setText(appStatus)
        window.subject.appStat.setText(appStatus)
        window.data.appStat.setText(appStatus)
        app.processEvents()

        valve1.disable()
        valve2.disable()
        valve3.disable()
        la.retract()

        def p1():
            valve1.enable()
            print('Purge Sequence 1')

        def p2():
            valve1.disable()
            la.extend()
            valve2.enable()
            valve3.enable()
            print('Purging Sequence 2')

        def p3():
            valve1.enable()
            valve2.enable()
            valve3.enable()
            la.default()
            print('Purging Sequence 3')

        p1()
        QTimer.singleshot(self.pTime2 * 1000, lambda: p2())
        QTimer.singleshot(self.pTime3 * 1000, lambda: p3())

    def runTest(self):
        self.runStatus = 1
        self.clrfcn()
        self.purge()
        print('Testing')
        global appStatus
        appStatus = "Testing"
        self.appStat.setText('Testing')
        
        ## end of purge phase 
        la.retract()
        valve1.disable()
        valve2.disable()
        valve3.disable()
        startTime = time.time()
        self.p1 = self.graph.plot(self.runTime, self.sens1, pen='r', name='{}'.format(s1n))
        self.p2 = self.graph.plot(self.runTime, self.sens2, pen='g', name='{}'.format(s2n))
        self.p3 = self.graph.plot(self.runTime, self.sens3, pen='b', name='{}'.format(s3n))
        # self.p1 = self.graph.plot(self.runTime, self.sens1, pen - 'r', name='{}'.format(s1n)) # Normally Commented Out
        
        def updateData():
            app.processEvents()
            self.runTime.append(time.time() - startTime)
            self.sens1.append(mos1.read())
            self.sens2.append(mos2.read())
            self.sens3.append(mos3.read())
            # self.sens4.append(mos4.read()) # Normally commented out
            self.tempVal.append(mos5.read())
            self.pressVal.append(mos6.read())
            self.humVal.append(mos7.read())
            self.oxVal.append(mos8.read())

        def updateUI():
            app.processEvents()
            self.p1.setData(self.runTime, self.sens1)
            self.p2.setData(self.runTime, self.sens2)
            self.p3.setData(self.runTime, self.sens3)
            # self.p4.setData(self.runTime, self.sens4) # Normally Commented out
            self.vecL.setText(
                'Temp: {:d}℃ \n\nHumidity: {:d}% \n\nPressure: {:d}kPa \n\nOxygen: {:d}%'.format(int(self.tempVal[-1]),
                                                                                                 int(self.humVal[-1]),
                                                                                                 int(
                                                                                                     self.pressVal[-1]),
                                                                                                 int(self.oxVal[-1])))

        def endTest():
            dataTimer.stop()
            uiTimer.stop()
            all_data = np.column_stack((self.runTime, self.sens1, self.sens2, self.sens3, self.tempVal, self.pressVal, self.humVal, self.oxVal))
            global directory
            global idVal
            np.savetxt('{}/{}_id{}.csv'.format(directory, datetime.now().strftime('%Y_%m_%d_%H%M%S'), idVal), all_data,fmt='%.10f', delimiter=',')
            print('File Saved')
            la.retract()
            valve1.disable()
            valve2.disable()
            valve3.disable()
            self.purge()
            global appStatus
            appStatus = "Test Complete"
            print('Accessories Reset')
            self.appStat.setText(appStatus)
            window.subject.appStat.setText(appStatus)
            window.data.appStat.setText(appStatus)
            
        QTimer.singleShot(self.tTime1 * 1000, lambda: la.extend())
        QTimer.singleShot(self.tTime2 * 1000, lambda: la.retract())
        QTimer.singleShot(self.totTime * 1000, lambda: endTest())
        global dataTimer
        dataTimer = QTimer()
        dataTimer.timeout.connect(lambda: updateData())
        global uiTimer
        uiTimer = QTimer()
        uiTimer.timeout.connect(lambda: updateUI())
        dataTimer.start(100)
        uiTimer.start(1000)


class Subjectpage(QWidget):
    class load_subject(QPushButton):
        def __init__(self, parent=None):
            super(Subjectpage.load_subject, self).__init__()
            self.setText('Load Subject')
            self.clicked.connect(lambda: self.load_s())

        def load_s(self):
            subNum, okpressed = QInputDialog.getInt(self, 'Subject ID', 'Subject: ', 0, 1, 100, 1)
            idCheck = subNum
            myArray = np.genfromtxt('idDatabase.csv', delimiter=',', skip_header=1)
            col1 = myArray[:, 0]
            check = np.isin(idCheck, col1, assume_unique=True)
            if check:
                global idVal
                global directory
                idVal = idCheck
                directory = 'Data/byID/id{}'.format(idVal)
                print('ID {} Found'.format(idVal))
                window.front.idL.setText("ID: " + str(idVal))
                window.subject.idL.setText("ID: " + str(idVal))
                window.data.idL.setText("ID: " + str(idVal))

    class new_subject(QPushButton):
        def __init__(self, parent=None):
            super(Subjectpage.new_subject, self).__init__()
            self.setText('New Subject')
            self.clicked.connect(lambda: self.gen_ns())

        def genSubNumber(self):
            myArray = np.genfromtxt('idDatabase.csv', delimiter=',', skip_header=1)
            col1 = myArray[:, 0]
            numFound = False
            myRand = 0
            while not numFound:
                myRand = np.random.randint(1, 100, 1)
                check = np.isin(myRand, col1, assume_unique=True)
                if not check:
                    numFound = True

            return int(myRand)

        def genSubject(self):
            global filename
            global directory
            global idVal
            filename = 'id{}'.format(str(idVal))
            directory = 'Data/byID/{}'.format(filename)

            if not os.path.exists(directory):
                os.mkdir(directory)

            today = datetime.now().strftime('%d-%m-%Y')
            f = open('{}/{}.txt'.format(directory, filename), 'w+')
            init_message = 'ID Number: {}\nCreated On: ' \
                           '{}\nDevice Version: {}\nSoftware Version: ' \
                           '{}\nDevice ID: {}\n--------------------'.format(str(idVal),
                                                                            datetime.now().strftime('%d-%m-%Y'),
                                                                            dVersion, sVersion, dID)
            f.write(init_message)

            with open('idDatabase.csv', 'a') as g:
                writer = csv.writer(g)
                writer.writerow([])
                writer.writerow([idVal, today, directory, dVersion, dID])

            print('subject {} created'.format(idVal))

        def gen_ns(self):
            global idVal
            idVal = self.genSubNumber()
            print('Subject {} generated.'.format(idVal))
            self.genSubject()
            global window
            window.front.idL.setText("ID: " + str(idVal))
            window.subject.idL.setText("ID: " + str(idVal))
            window.data.idL.setText("ID: " + str(idVal))

    class addLog(QPushButton):
        def __init__(self, parent=None):
            super(Subjectpage.addLog, self).__init__()
            self.setText('Add Log')
            self.clicked.connect(lambda: self.addLogFunc())
            
        def addLogFunc(self):
            global idVal
            global curDir
            global idPath
            global curTime
            idPath = "{}/Data/byID/id{}/".format(curDir,idVal)
            logPath = "{}id{}.txt".format(idPath,idVal)
            curTime = time.strftime("%d-%m-%y_%H-%M-%S",time.localtime())
            bar = "-----------------------"
            f = open(logPath, "a+")
            message,ok1 = QInputDialog.getText(None, "Custom Log", "Add text if you want a custom message")
            print(message)
            if(message !=""):
                full_txt = "\n{}: {} \n{}".format(curTime,message,bar)
            else:full_txt = "\n{}: {} \n{}".format(curTime, "New Test Performed", bar)
            f.write(full_txt)
                    
    def __init__(self, *args, **kwargs):
        super(Subjectpage, self).__init__(*args, **kwargs)
        self.UI()

    def UI(self):
        self.layout = QGridLayout()
        self.idL = QLabel('ID: {:d}'.format(idVal))
        self.idL.setFrameShape(QFrame.Box)
        global appStatus
        self.appStat = QLabel('Status: {}'.format(appStatus))
        self.appStat.setFrameShape(QFrame.Box)

        self.layout.addWidget(self.idL, 0, 6, 1, 1)
        self.layout.addWidget(self.appStat, 7, 6, 1, 1)
        self.layout.addWidget(self.new_subject(), 2, 1, 1, 3)
        self.layout.addWidget(self.load_subject(), 4, 1, 1, 3)
        self.layout.addWidget(self.addLog(), 3, 1, 1, 3)
        self.setLayout(self.layout)


class Datapage(QWidget):
    class Graph(pg.PlotWidget):
        def __init__(self, parent=None):
            super(Datapage.Graph, self).__init__()
            self.setStyleSheet("pg.PlotWidget {border-style: outset; max-height: 50}")

    class clear(QPushButton):
        def __init__(self, parent=None):
            super(Datapage.clear, self).__init__()
            self.setText('Clear')

    class loadData(QPushButton):
        def __init__(self, parent=None):
            super(Datapage.loadData, self).__init__()
            self.setText('Load Data')

    class genReport(QPushButton):
        def __init__(self, parent=None):
            super(Datapage.genReport, self).__init__()
            self.setText('Generate Report')

    def __init__(self, *args, **kwargs):
        super(Datapage, self).__init__(*args, **kwargs)

        self.pTime1 = 2  # Pre-purge: this will normally run for 60 seconds
        self.pTime2 = 2  # Pre-purge: this will normally run for 30 seconds
        self.pTime3 = 2  # Pre-purge: this is commented out
        self.pTime4 = 2  # Post-purge: this will normally run for 40 seconds

        self.totTime = 20  # This is the total time: normally 300 seconds
        self.tTime1 = 5  # This is the time when the sensor is extended: Normally 10
        self.tTime2 = 10  # This is the time when the sensor is retracted: Normally 60

        self.runTime = [] # All Time Values

        self.sens1 = [] # All MOS 1 Values
        self.sens2 = [] # All MOS 2 Values
        self.sens3 = [] # All MOS 3 Values
        # self.sens4 = [] # All MOS 4 Values : GENERALLY COMMENTED OUT

        self.tempVal = []  # Full List of temp values over test
        self.pressVal = []  # Full List of pressure values over test
        self.humVal = []  # Full List of humidity values over test
        self.oxVal = []  # Full List of oxygen values over test

        self.tempVal_last = 0  # Last value for the UI
        self.pressVal_last = 0  # Last value for the UI
        self.humVal_last = 0  # Last value for the UI
        self.oxVal_last = 0  # Last value for the UI

        self.UI()

    def UI(self):

        self.layout = QGridLayout()
        self.idL = QLabel('ID: {:d}'.format(idVal))
        self.idL.setFrameShape(QFrame.Box)
        global appStatus
        self.appStat = QLabel('Status: {}'.format(appStatus))
        self.appStat.setFrameShape(QFrame.Box)
        global appStatGlobe
        appStatGlobe = self.appStat
        self.testTime = QLabel('Baseline Check Time: {}s \n\n'
                               'Exposure Time: {}s \n\nRecovery Time: {}s \n\nTotal Time: {}s'.format(self.tTime1,
                                                                                                      self.tTime2 - self.tTime1,
                                                                                                      self.totTime - self.tTime2,
                                                                                                      self.totTime))

        self.testTime.setFrameShape(QFrame.Box)
        self.vecL = QLabel(
            'Temp: {:d}℃ \n\nHumidity: {:d}% \n\nPressure: {:d}kPa \n\nOxygen: {:d}%'.format(int(self.tempVal_last),
                                                                                             int(self.humVal_last),
                                                                                             int(self.pressVal_last),
                                                                                             int(self.oxVal_last)))
        self.vecL.setFrameShape(QFrame.Box)

        self.graph = self.Graph()
        self.graph.addLegend(offset = (0,10))
        self.clb = self.clear()
        self.clb.clicked.connect(lambda: self.clearFcn())
        self.ldb = self.loadData()
        self.ldb.clicked.connect(lambda: self.loadDataFcn())
        self.grb = self.genReport()
        self.grb.clicked.connect(lambda: self.genReportFcn())

        self.layout.addWidget(self.idL, 0, 6, 1, 1)
        self.layout.addWidget(self.appStat, 7, 6, 1, 1)
        self.layout.addWidget(self.vecL, 1, 6, 2, 1)
        self.layout.addWidget(self.testTime, 3, 6, 2, 1)
        self.layout.addWidget(self.graph, 1, 0, 4, 4)
        self.layout.addWidget(self.clb, 6, 1, 1, 1)
        self.layout.addWidget(self.ldb, 6, 0, 1, 1)
        self.layout.addWidget(self.grb, 6, 2, 1, 1)

        self.setLayout(self.layout)

    def clearFcn(self):
        self.runTime = [] # All time values

        self.sens1 = []  # All MOS 1 Values
        self.sens2 = []  # All MOS 2 Values
        self.sens3 = []  # All MOS 3 Values
        # self.sens4 = [] # All MOS 4 Values : GENERALLY COMMENTED OUT

        self.tempVal = []  # Full List of temp values over test
        self.pressVal = []  # Full List of pressure values over test
        self.humVal = []  # Full List of humidity values over test
        self.oxVal = []  # Full List of oxygen values over test

        self.tempVal_last = 0  # Last value for the UI
        self.pressVal_last = 0  # Last value for the UI
        self.humVal_last = 0  # Last value for the UI
        self.oxVal_last = 0  # Last value for the UI

        self.graph.clear()
        self.graph.plotItem.legend.removeItem(self.p1.name())
        self.graph.plotItem.legend.removeItem(self.p2.name())
        self.graph.plotItem.legend.removeItem(self.p3.name())
        
        
        
    def loadDataFcn(self):
        self.fname, self.__var__ = QFileDialog.getOpenFileName(self, 'Open file', '{}'.format(curDir), "CSV Files (*.csv)")
        self.f = rc(self.fname, delimiter = ',')

        self.runTime = self.f.iloc[:, 0].values
        self.sens1 = self.f.iloc[:, 1].values
        self.sens2 = self.f.iloc[:, 2].values
        self.sens3 = self.f.iloc[:, 3].values
        # self.sens4 = self.f.iloc[:, 0].values
        self.tempVal = self.f.iloc[:, 4].values
        self.pressVal = self.f.iloc[:, 5].values
        self.humVal = self.f.iloc[:, 6].values
        self.oxVal = self.f.iloc[:, 7].values

        self.p1 = self.graph.plot(self.runTime, self.sens1, pen='r', name='{}'.format(s1n))
        self.p2 = self.graph.plot(self.runTime, self.sens2, pen='g', name='{}'.format(s2n))
        self.p3 = self.graph.plot(self.runTime, self.sens3, pen='b', name='{}'.format(s3n))
        # self.graph.plot(self.runTime, self.sens4, pen='k', name='{}'.format(s4n))
        self.graph.setYRange(0, 5)
        self.graph.setXRange(0, self.totTime)

        self.tempVal_last = mean(self.tempVal)
        self.pressVal_last = mean(self.pressVal)
        self.humVal_last = mean(self.humVal)
        self.oxVal_last = mean(self.oxVal)
        self.vecL.setText('Temp: {:d}℃ \n\nHumidity: {:d}% \n\nPressure: {:d}kPa \n\nOxygen: {:d}%'.format(int(self.tempVal_last), int(self.humVal_last), int(self.pressVal_last), int(self.oxVal_last)))

    def genReportFcn(self):
        print('Under Construction')


class mainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(mainWindow, self).__init__(*args, **kwargs)
        self.UI()

    def UI(self):
        self.layout = QGridLayout()
        tab = QTabWidget()
        self.front = Frontpage()
        tab.addTab(self.front, 'Main')
        self.subject = Subjectpage()
        tab.addTab(self.subject, 'Subject')
        self.data = Datapage()
        tab.addTab(self.data, 'Data Loading')
        self.layout.addWidget(tab)
        self.setLayout(self.layout)


def main():
    global window
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
