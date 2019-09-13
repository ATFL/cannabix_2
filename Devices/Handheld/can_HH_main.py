#!/usr/bin/python3

# -----> System Imports <-----
import os
import sys
from time import *
import datetime
import shutil
import threading
# -----> Tkinter Imports <------
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import *
# -----> Matplotlib Imports <------
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
# -----> Auxiliary Imports <------
from gui_widgets import *
from cannibix_components_HH import *
# -----> RPi Imports <------
import RPi.GPIO as GPIO
import time
import os
import Adafruit_ADS1x15 as ADS
import serial
from pathlib import Path
#----> Machine learning Imports <----
# import pickle
# import sklearn

#################### Object Declaration ####################
GPIO.setmode(GPIO.BOARD)
# Linear Actuator
pinLA = 8
pinEnable = 10
linearActuator = LinearActuator(pinLA, pinEnable)
# Analog-Digital Converter
adc = ADS.ADS1115(0x48)
adc2 = ADS.ADS1115(0x49)
# MOS Sensor

#ADC2
sensor1 = MOS(adc2, 0)
sensor2 = MOS(adc2, 1)
sensor3 = MOS(adc2, 2)
sensor4 = MOS(adc2, 3)

#ADC1
sensor5 = MOS(adc, 0)
sensor6 = MOS(adc, 1)
sensor7 = MOS(adc, 2)
sensor8 = MOS(adc, 3)

#MOS SENSORS
all_sensors = all_sensors(sensor1,sensor2,sensor3,sensor4)
# all_sensors2 = all_sensors(sensor5,sensor6,sensor7,sensor8)
# Temperature sensor
Temp_adc_channel = 1
temperatureSensor = TemperatureSensor(adc, Temp_adc_channel)
#Pressure Sensor
Press_adc_channel = 0
pressureSensor = PressureSensor(adc,Press_adc_channel)
# Valves
pinInValve = 8
inValve = Valve('Inlet Valve', pinInValve)
pinOutValve = 10
outValve = Valve('Outlet Valve', pinOutValve)
pinValve1 = 24
pinValve2 = 26


valve1 = Valve('Valve 1', pinValve1)
valve2 = Valve('Valve 2', pinValve2)
#valve3 = Valve('Valve 3', pinValve3)
# Pump
pinPump = 11
pump = Pump(pinPump)
#################### System Variables ####################
# Purging Variables
clean_chamber_purge_time = 15 # normally 30s
sensing_chamber_purge_time = 15 # normally 60s
# Filling Variables
chamber_fill_time = 1 # normally 45, fill the sensing chamber with the outlet valve open.
chamber_force_fill_time = 1 # normally 1, fill the sensing chamber without an outlet.

# Testing Variables
sampling_time = 0.1 # time between samples taken, determines sampling frequency
sensing_delay_time = 5 # normall 10, time delay after beginning data acquisition till when the sensor is exposed to sample
sensing_retract_time =50# 50 # normally 60, time allowed before sensor is retracted, no longer exposed to sample
duration_of_signal = 200#200 # normally 150, time allowed for data acquisition per test run

##############TESTING TIMING###################################
# clean_chamber_purge_time = 1 # normally 30s
# sensing_chamber_purge_time = 1 # normally 60s
# # Filling Variables
# chamber_fill_time = 1 # normally 45, fill the sensing chamber with the outlet valve open.
# chamber_force_fill_time = 1 # normally 1, fill the sensing chamber without an outlet.
#
# # Testing Variables
# sampling_time = 0.1 # time between samples taken, determines sampling frequency
# sensing_delay_time = 1 # normall 10, time delay after beginning data acquisition till when the sensor is exposed to sample
# sensing_retract_time =2# 50 # normally 60, time allowed before sensor is retracted, no longer exposed to sample
# duration_of_signal = 5
##################################################
#################### Data Array ####################
# DO NOT TOUCH # -teehee touched
dataVector = []
timeVector = []
test_type_Vector = []
#################### Color Settings ####################
warning_color = '#FFC300'
tabBar_color = '#85929E'
tabBarActive_color = '#AEB6BF'
runBtn_color = '#9DE55F'
stopBtn_color = '#FF4E4E'

#################### GUI ####################
projectName = 'Cannibix HH GUI'
class CannibixHHGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs) #Passes all aguments to the parent class.

        self.title(projectName + ' GUI') #Title of the master window.
        self.geometry('640x480') #Initial size of the master window.
        # self.resizable(0,0) #The allowance for the master window to be adjusted by.

        canvas = tk.Frame(self) #Creates the area for which pages will be displayed.
        canvas.place(relx=0, rely=0, relheight=0.9, relwidth=1) #Defines the area which each page will be displayed.
        canvas.grid_rowconfigure(0, weight=1) #DO NOT ADJUST. Forces each frame to overlap.
        canvas.grid_columnconfigure(0, weight=1) #DO NOT ADJUST. Forces each frame to overlap.

        self.tabBar = tk.Frame(self, bg=tabBar_color) #Creates the area for which control buttons will be placed.
        self.tabBar.place(relx=0, rely=0.9, relheight=0.1, relwidth=1) #Defines the area for which control buttons will be placed.

        self.frames = {} #Dictonary to store each frame after creation.

        for f in (HomePage, DataPage, ManualControlPage): #For pages to be added, do the following:
            frame = f(canvas,self) #Creates a frame of the above classes.
            self.frames[f] = frame #Add the created frame to the 'frames' dictionary.
            frame.grid(row=0, column=0, sticky="nsew") #Overlaps the frame in the same grid space.
        self.show_frame(HomePage) #Sets the default page.

        #Setup controls for fullscreen
        self.attributes("-fullscreen", True)
        self.fullscreen = True
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.end_fullscreen)

        print('System ready.')

    def show_frame(self, cont): #Control buttons will run this command for their corresponding pages.
        frame = self.frames[cont] #Obtain frame object from the dictionary.
        frame.tkraise()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen  # Just toggling the boolean.
        self.attributes("-fullscreen", self.fullscreen) #Pass the fullcreen boolean to tkinter.
        return "break"

    def end_fullscreen(self, event=None):
        self.fullscreen = False
        self.attributes("-fullscreen", False)
        return "break"

    def shutdown(self):
        os.system("sudo shutdown -h now")

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        control_btn = tk.Button(controller.tabBar, text='Home', bg=tabBar_color, activebackground=tabBarActive_color, bd=0, command=lambda: controller.show_frame(HomePage)) #Creates a control button in the tabs bar.
        control_btn.pack(side='left', expand= True, fill = 'both')

        title = tk.Label(self, text=projectName, font=14, relief='solid')
        title.place(relx=0.2,rely=0.3,relwidth=0.6,relheight=0.15)

        intro = '''Microfluidic-based natural gas detector. Developed by ATF Lab
        [F11: Toggle Fullscreen]
        [Esc: Exit Fullscreen]'''

        introduction = tk.Label(self, text=intro, anchor='n')
        introduction.place(relx=0.1,rely=0.55,relheight=0.35,relwidth=0.8)

        #Hash this out if no such functionallity is required. Or if there are bugs.
        self.exitBtn = tk.Button(self, text='Exit Fullscreen', command=lambda:controller.end_fullscreen())
        self.exitBtn.place(relx=0.1,rely=0.8,relheight=0.2,relwidth=0.3)
        self.shutdownBtn = tk.Button(self, text='Shutdown', command=lambda:controller.shutdown())
        self.shutdownBtn.place(relx=0.6,rely=0.8,relheight=0.2,relwidth=0.3)

class DataPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        control_btn = tk.Button(controller.tabBar, text='Data', bg=tabBar_color, activebackground=tabBarActive_color, bd=0, command=lambda: controller.show_frame(DataPage))
        control_btn.pack(side='left', expand= True, fill = 'both')
        #    while(pressureSensor.read() < b_threshold_val):
#        print("BLOW HARDER: %d", pressureSensor.read())
#    while(pressureSensor.read() > b_threshold_val):
#        print("Collecting sample")
#        # if inValve.state != True:
#        #     inValve.enable()

        self.graph = AutoLiveGraph(self, timeVector, dataVector)
        self.graph.place(relx=0,rely=0,relheight=0.9,relwidth=0.8)

        self.status = tk.StringVar()
        self.status.set('Ready for Breath Sample')

        self.progressTitle = tk.Label(self, textvariable = self.status, anchor='w')
        self.progressTitle.place(relx=0,rely=0.9,relheight=0.07,relwidth=0.8)

        self.progressbar = ttk.Progressbar(self, orient='horizontal', mode='determinate', maximum=100)
        self.progressbar.place(relx=0,rely=0.97,relheight=0.03,relwidth=0.8)

        self.run_and_stop = tk.Frame(self)
        self.run_and_stop.place(relx=0.8,rely=0.9,relheight=0.1,relwidth=0.2)
        self.run_and_stop.grid_rowconfigure(0, weight=1) #DO NOT ADJUST. Forces buttons to overlap.
        self.run_and_stop.grid_columnconfigure(0, weight=1) #DO NOT ADJUST.

        self.stopBtn = tk.Button(self.run_and_stop, text='STOP', bg=stopBtn_color, activebackground=stopBtn_color, command=lambda:end_testing())
        self.stopBtn.grid(row=0, column=0, sticky="nsew")

        self.contFill = tk.Button(self.run_and_stop, text='CONTINUE', bg=runBtn_color, activebackground=runBtn_color, command=lambda:start_fill_thread())
        self.contFill.grid(row=0, column=0, sticky="nsew")

        self.runBtn = tk.Button(self.run_and_stop, text='RUN', bg=runBtn_color, activebackground=runBtn_color, command=lambda:start_purge_thread())
        self.runBtn.grid(row=0, column=0, sticky="nsew")


        statusFrame = tk.LabelFrame(self, text ='Status')
        statusFrame.place(relx=0.8,rely=0.3,relheight=0.6,relwidth=0.2)

        def callback1(*args):
            print("Test_Type was read, value is ",test_type.get())
        def callback2(*args):
            print("Test_type was changed to ", test_type.get())
        global test_type
        test_type = IntVar()
        test_type.set(0)
        test_type.trace('r',callback1)
        test_type.trace('w',callback2)

        self.neg_resp = Radiobutton(statusFrame,text='Negative',variable = test_type,value=0)
        self.neg_resp.place(relx = 0, rely = 0.1, relwidth = 1,relheight = .1)
        self.pos_resp = Radiobutton(statusFrame,text='Positive',variable = test_type,value=1)
        self.pos_resp.place(relx = 0, rely = 0.2,relwidth = 1, relheight = .1)
        self.other_resp = Radiobutton(statusFrame,text='Other',variable = test_type,value = 2)
        self.other_resp.place(relx = 0, rely = 0.3, relwidth = 1, relheight = .1)

        responseFrame = tk.Frame(self)
        responseFrame.place(relx=0.8,rely=0,relheight=0.3,relwidth=0.2)
        self.naturalGasLabel = tk.Label(responseFrame, text = 'THC\n Detected', relief='groove', borderwidth=2, anchor='center')
        self.naturalGasLabel.place(relx=0,rely=0,relheight=0.7,relwidth=1)
        self.orig_color = self.naturalGasLabel.cget("background") # Store the original color of the label.

        self.filenamelbl = tk.Label(responseFrame,text='Filename (Optional)',anchor='w')
        self.filenamelbl.place(relx=0,rely=0.7,relheight = 0.5,relwidth = 1)
        #self.filename_add = tk.StringVar()
        self.filenamefiller = tk.Entry(responseFrame)
        self.filenamefiller.place(relx=0,rely=.8,relwidth=1)
        #self.filenamefiller.set('')
class ManualControlPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        control_btn = tk.Button(controller.tabBar, text='Manual Controls', bg=tabBar_color, activebackground=tabBarActive_color, bd=0, command=lambda: controller.show_frame(ManualControlPage))
        control_btn.pack(side='left', expand= True, fill = 'both')

        #Create a termial within a parent frame.
        terminal = tk.Frame(self)
        CoreGUI(terminal)
        terminal.place(relx=0.7,rely=0,relheight=1,relwidth=0.3)

        controlFrame = tk.LabelFrame(self, text='System')
        controlFrame.place(relx=0,rely=0,relheight=1,relwidth=0.7)
        leftControlFrame = tk.Frame(controlFrame)
        leftControlFrame.place(relx=0,rely=0,relheight=1,relwidth=0.5)
        rightControlFrame = tk.Frame(controlFrame)
        rightControlFrame.place(relx=0.5,rely=0,relheight=1,relwidth=0.5)

        buttonWidth = 0.4 #Relative width of buttons within the frame
        self.btn_1 = tk.Button(controlFrame, text='Extend Linear Actuator', command=lambda:linearActuator.extend())#,app.frames[DataPage].stat_LA.set(linearActuator.state)])
        self.btn_1.place(relx=0,rely=0,relheight=0.1,relwidth=buttonWidth)
        self.btn_2 = tk.Button(controlFrame, text='Retract Linear Actuator', command=lambda:linearActuator.retract())#,app.frames[DataPage].stat_LA.set(linearActuator.state)])
        self.btn_2.place(relx=0,rely=0.1,relheight=0.1,relwidth=buttonWidth)
        self.btn_3 = tk.Button(controlFrame, text='Default Linear Actuator', command=lambda:linearActuator.default())#,app.frames[DataPage].stat_LA.set(linearActuator.state)])
        self.btn_3.place(relx=0,rely=0.2,relheight=0.1,relwidth=buttonWidth)
        self.btn_4 = tk.Button(controlFrame, text='Read Sensors', command=lambda:all_sensors.print())
        self.btn_4.place(relx=0,rely=0.3,relheight=0.1,relwidth=buttonWidth)
        self.btn_5 = tk.Button(controlFrame, text='Read Temperature Sensor', command=lambda:temperatureSensor.print())
        self.btn_5.place(relx=0,rely=0.4,relheight=0.1,relwidth=buttonWidth)
        self.btn_6 = tk.Button(controlFrame, text='Switch Valve 1', command=lambda:valve1.switch())#,app.frames[DataPage].stat_valve1.set(inValve.state)])
        self.btn_6.place(relx=0,rely=0.5,relheight=0.1,relwidth=buttonWidth)
        self.btn_7 = tk.Button(controlFrame, text='Switch Valve 2', command=lambda:valve2.switch())#,app.frames[DataPage].stat_valve2.set(outValve.state)])
        self.btn_7.place(relx=0,rely=0.6,relheight=0.1,relwidth=buttonWidth)
        self.btn_8 = tk.Button(controlFrame, text='Switch Pump', command=lambda:pump.switch())#,app.frames[DataPage].stat_pump.set(pump.state)])
        self.btn_8.place(relx=0,rely=0.7,relheight=0.1,relwidth=buttonWidth)
        self.btn_9 = tk.Button(controlFrame, text='Read Pressure', command=lambda:pressureSensor.print())
        self.btn_9.place(relx=0,rely=0.8,relheight=0.1,relwidth=buttonWidth)

        lbl_1 = tk.Label(controlFrame, text='  Extend the linear actuator to the sensing chamber.', anchor='w')
        lbl_1.place(relx=buttonWidth,rely=0,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_2 = tk.Label(controlFrame, text='  Retract the linear actuator to the clean chamber.', anchor='w')
        lbl_2.place(relx=buttonWidth,rely=0.1,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_3 = tk.Label(controlFrame, text='  Reset the linear to the default (center) position.', anchor='w')
        lbl_3.place(relx=buttonWidth,rely=0.2,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_4 = tk.Label(controlFrame, text='  Read the current value of the MOS (gas) sensor.', anchor='w')
        lbl_4.place(relx=buttonWidth,rely=0.3,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_5 = tk.Label(controlFrame, text='  Read the current internal temperature of the device.', anchor='w')
        lbl_5.place(relx=buttonWidth,rely=0.4,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_6 = tk.Label(controlFrame, text='   Toggle the inlet valve.', anchor='w')
        lbl_6.place(relx=buttonWidth,rely=0.5,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_7 = tk.Label(controlFrame, text='   Toggle the outlet valve.', anchor='w')
        lbl_7.place(relx=buttonWidth,rely=0.6,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_8 = tk.Label(controlFrame, text='  Toggle the pump.', anchor='w')
        lbl_8.place(relx=buttonWidth,rely=0.7,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_9 = tk.Label(controlFrame, text='  Read the current Pressure.', anchor='w')
        lbl_9.place(relx=buttonWidth,rely=0.8,relheight=0.1,relwidth=(1-buttonWidth))

def suppress_buttons():
    app.frames[ManualControlPage].btn_1.config(state='disabled')
    app.frames[ManualControlPage].btn_2.config(state='disabled')
    app.frames[ManualControlPage].btn_3.config(state='disabled')
    app.frames[ManualControlPage].btn_4.config(state='disabled')
    app.frames[ManualControlPage].btn_5.config(state='disabled')
    app.frames[ManualControlPage].btn_6.config(state='disabled')
    app.frames[ManualControlPage].btn_7.config(state='disabled')
    app.frames[ManualControlPage].btn_8.config(state='disabled')
    app.frames[ManualControlPage].btn_9.config(state='disabled')
    app.frames[HomePage].exitBtn.config(state='disabled')
    app.frames[HomePage].shutdownBtn.config(state='disabled') #random

def release_buttons():
    app.frames[ManualControlPage].btn_1.config(state='normal')
    app.frames[ManualControlPage].btn_2.config(state='normal')
    app.frames[ManualControlPage].btn_3.config(state='normal')
    app.frames[ManualControlPage].btn_4.config(state='normal')
    app.frames[ManualControlPage].btn_5.config(state='normal')
    app.frames[ManualControlPage].btn_6.config(state='normal')
    app.frames[ManualControlPage].btn_7.config(state='normal')
    app.frames[ManualControlPage].btn_8.config(state='normal')
    app.frames[ManualControlPage].btn_9.config(state='normal')
    app.frames[HomePage].exitBtn.config(state='normal')
    app.frames[HomePage].shutdownBtn.config(state='normal')

def purge_system():

    if linearActuator.state != 'default':
        linearActuator.default()


    # Purge the sensing chamber.
    messagebox.showinfo("Connect Pump", "Connect Pump into pump input and then press OK")
    start_time = time.time() # Time at which the purging starts.

    while time.time() < (start_time + sensing_chamber_purge_time) and continueTest == True:
        if pump.state != True:
            pass
        if inValve.state != True:
            inValve.enable()
        if outValve.state != True:
            outValve.enable()

    # Purge the clean chamber.
    start_time = time.time() #Reset the time at which purging starts.
    while time.time() < (start_time + clean_chamber_purge_time) and continueTest == True:
        if pump.state != True:
            pass
        if inValve.state != False:
            inValve.disable()
        if outValve.state != False:
            outValve.disable()
    pass

def fill_chamber():

    if linearActuator.state != 'extended':
        linearActuator.extend()
    if inValve.state != True:
        inValve.enable()
    if pump.state != False:
        pump.disable()
    print('Ready for Breath')
    b_threshold_val = 5200
    if inValve.state != False:
        inValve.disable()
    messagebox.showinfo("External Valve","Please Close Exeternal Valve, then click Okay.")

def collect_data(xVector,yVector,zVector):
    start_time = time.time()  # Local value. Capture the time at which the test began. All time values can use start_time as a reference
    dataVector = yVector
    timeVector = xVector
    test_type_Vector = zVector
    dataVector.clear()
    timeVector.clear()
    test_type_Vector.clear()
    sampling_time_index = 1

    # Initial state checks
    if linearActuator.state != 'extended':
        linearActuator.extend()
    if inValve.state != False:
        inValve.disable()
    if outValve.state != False:
        outValve.disable()

    print('Starting data capture.')
    while (time.time() < (start_time + duration_of_signal)) and (continueTest == True):  # While time is less than duration of logged file
        if (time.time() > (start_time + (sampling_time * sampling_time_index)) and (continueTest == True)):  # if time since last sample is more than the sampling time, take another sample
            dataVector.append(all_sensors.read())  # Perform analog to digital function, reading voltage from first sensor channel
            timeVector.append(time.time() - start_time)
            sampling_time_index += 1

        # If time is between 10-50 seconds and the Linear Actuator position sensor signal from the ADC indicates a retracted state, extend the sensor
        elif (time.time() >= (start_time + sensing_delay_time) and time.time() <= (
                sensing_retract_time + start_time) and (continueTest == True)):
            if linearActuator.state != 'retracted':
                linearActuator.retract()

        # If time is less than 10 seconds or greater than 50 seconds and linear actuator position sensor signal from the ADC indicates an extended state, retract the sensor
        elif (((time.time() < (sensing_delay_time + start_time)) or (
                time.time() > (sensing_retract_time + start_time)))) and (continueTest == True):
            if linearActuator.state != 'extended':
                linearActuator.extend()

        # Otherwise, keep outputs off
        else:
            if linearActuator.state != 'extended':
                linearActuator.extend()
    print('Data Capture Complete')
    global test_type
    arr_shape = len(timeVector)
    test_type_Val = test_type.get()
    test_type_Vector = np.full(arr_shape,test_type_Val)
    combinedVector = np.column_stack((timeVector, dataVector,test_type_Vector))

    #########NAMING THE SAVED FILE##########
    fpath = "testsH/" #this is where files are saved
    #fpath = "testing_site/" #this is a testing area
    f1 = app.frames[DataPage].filenamefiller.get()
    f2 = strftime("%a%-d%b%Y%H%M%S",localtime())
    fsuffix = ".csv"

    ### OPTION 1: STRING IS ADDITION TO FILENAME BELOW
    #filename = fpath+f2+f1+fsuffix
    ### OPTION 2: STRING IS REPLACEMENT FOR FILENAME
    if f1 != '':
        filename = fpath+f1+fsuffix
    else:
        filename = fpath+f2+fsuffix

    np.savetxt(filename,combinedVector, fmt='%.10f', delimiter=',')
    # app.frames[DataPage].filenamefiller.delete(0, END)
    # app.frames[DataPage].filenamefiller.insert(0,'')
    print("Data Saved")
    pass

def start_purge_thread():
    suppress_buttons()
    app.frames[DataPage].stopBtn.tkraise()
    app.frames[DataPage].naturalGasLabel.config(bg=app.frames[DataPage].orig_color)
    global purge_thread
    global continueTest
    continueTest = True
    purge_thread = threading.Thread(target=purge_system)
    purge_thread.daemon = True
    app.frames[DataPage].status.set('  Purging chambers...')
    app.frames[DataPage].progressbar.start((clean_chamber_purge_time+sensing_chamber_purge_time)*10)
    purge_thread.start()
    app.after(20, check_purge_thread)

def check_purge_thread():
    if purge_thread.is_alive():
        app.after(20, check_purge_thread)
    else:
        app.frames[DataPage].progressbar.stop()
        if continueTest ==True:
            start_fill_thread()
            #app.frames[DataPage].contFill.tkraise()

def start_fill_thread():
    suppress_buttons()
    app.frames[DataPage].stopBtn.tkraise()
    global fill_thread
    global continueTest
    continueTest = True
    fill_thread = threading.Thread(target=fill_chamber)
    fill_thread.daemon = True
    app.frames[DataPage].status.set(' Collecting Breath Sample')
    #app.frames[DataPage].progressbar.start((chamber_fill_time+chamber_force_fill_time)*10)
    fill_thread.start()
    app.after(20, check_fill_thread)

def check_fill_thread():
    if fill_thread.is_alive():
        app.after(20, check_fill_thread)
    else:
        app.frames[DataPage].progressbar.stop()
        if continueTest == True:
            start_data_thread()

def start_data_thread():
    suppress_buttons()
    global data_thread
    global continueTest
    continueTest = True
    data_thread = threading.Thread(target=collect_data,args=(timeVector,dataVector,test_type_Vector))
    data_thread.daemon = True
    app.frames[DataPage].status.set('  Capturing data...')
    app.frames[DataPage].progressbar.start(duration_of_signal*10)
    data_thread.start()
    app.after(20, check_data_thread)

def check_data_thread():
    if data_thread.is_alive():
        app.after(20, check_data_thread)
    else:
        app.frames[DataPage].progressbar.stop()
        app.frames[DataPage].graph.update(timeVector,dataVector)
        #app.frames[DataPage].naturalGasLabel.config(bg=warning_color)
        release_buttons()
        app.frames[DataPage].runBtn.tkraise()
        app.frames[DataPage].status.set('  System ready.')

def end_testing():
    if purge_thread.is_alive() or fill_thread.is_alive() or data_thread.is_alive():
        global continueTest
        continueTest = False #Set the test flag to false, stops testing.
        release_buttons()
        app.frames[DataPage].runBtn.tkraise()
        app.frames[DataPage].status.set('  System ready.')
try:
    app = CannibixHHGUI()
    app.mainloop()
except KeyboardInterrupt:
    GPIO.cleanup()
finally:
    GPIO.cleanup()
