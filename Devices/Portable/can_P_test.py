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
from cannibix_components_P import *
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

sensor1 = MOS(adc2, 0) #
sensor2 = MOS(adc2, 1)
sensor3 = MOS(adc2, 2)
sensor4 = MOS(adc2, 3)

all_sensors = all_sensors(sensor1,sensor2,sensor3,sensor4)

# Temperature sensor
Temp_adc_channel = 1
temperatureSensor = TemperatureSensor(adc, Temp_adc_channel)
#Pressure Sensor
#Press_adc_channel = 0
#pressureSensor = PressureSensor(adc,Press_adc_channel)
# Valves
#pinInValve = 8
#inValve = Valve('Inlet Valve', pinInValve)
#pinOutValve = 10
#outValve = Valve('Outlet Valve', pinOutValve)
#pinValve1 = 24
#pinValve2 = 26


#v#alve1 = Valve('Valve 1', pinValve1)
#valve2 = Valve('Valve 2', pinValve2)
#valve3 = Valve('Valve 3', pinValve3)
# Pump
pinPump = 12
pump = Pump(pinPump)
#################### System Variables ####################
# Purging Variables
clean_chamber_purge_time = 1#15 # normally 30s
sensing_chamber_purge_time = 1#15 # normally 60s
# Filling Variables
chamber_fill_time = 1 # normally 45, fill the sensing chamber with the outlet valve open.
chamber_force_fill_time = 1 # normally 1, fill the sensing chamber without an outlet.

# Testing Variables
sampling_time = 0.1 # time between samples taken, determines sampling frequency
sensing_delay_time = 1#5 # normall 10, time delay after beginning data acquisition till when the sensor is exposed to sample
sensing_retract_time = 1#50 # normally 60, time allowed before sensor is retracted, no longer exposed to sample
duration_of_signal = 1#200 # normally 150, time allowed for data acquisition per test run
#################### Data Array ####################
# DO NOT TOUCH # -teehee touched
dataVector = []
timeVector = []
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

        intro = '''Microfluidic-based THC- Breathalyzer. Developed by ATF Lab
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

        stat_pump_lbl = tk.Label(statusFrame, text='PUMP: ', anchor='w')
        stat_pump_lbl.place(relx=0,rely=0,relheight=0.1,relwidth=(1-0.4))
        # stat_Valve1_lbl = tk.Label(statusFrame, text= 'Valve 1: ', anchor='w')
        # stat_Valve1_lbl.place(relx=0,rely=0.1,relheight=0.1,relwidth=(1-0.4))
        # stat_Valve2_lbl = tk.Label(statusFrame, text='Valve 2: ', anchor='w')
        # stat_Valve2_lbl.place(relx=0,rely=0.2,relheight=0.1,relwidth=(1-0.4))
        stat_LA_lbl = tk.Label(statusFrame, text='LA: ', anchor='w')
        stat_LA_lbl.place(relx=0,rely=0.1,relheight=0.1,relwidth=(1-0.4))

        stat_pump = tk.Label(statusFrame, text=pump.state, anchor='w')
        stat_pump.place(relx=.4,rely=0,relheight=0.1,relwidth=(1-0.4))
        # stat_Valve1 = tk.Label(statusFrame, text=inValve.state, anchor='w')
        # stat_Valve1.place(relx=.4,rely=0.1,relheight=0.1,relwidth=(1-0.4))
        # stat_Valve2 = tk.Label(statusFrame, text=outValve.state, anchor='w')
        # stat_Valve2.place(relx=.4,rely=0.2,relheight=0.1,relwidth=(1-0.4))
        stat_LA = tk.Label(statusFrame, text=linearActuator.state, anchor='w')
        stat_LA.place(relx=.2,rely=0.1,relheight=0.1,relwidth=(1-0.4))



        responseFrame = tk.Frame(self)
        responseFrame.place(relx=0.8,rely=0,relheight=0.3,relwidth=0.2)
        self.naturalGasLabel = tk.Label(responseFrame, text = 'THC\n Detected', relief='groove', borderwidth=2, anchor='center')
        self.naturalGasLabel.place(relx=0,rely=0,relheight=0.7,relwidth=1)
        self.orig_color = self.naturalGasLabel.cget("background") # Store the original color of the label.

        # ppmDisplay = tk.Frame(responseFrame, relief='groove', borderwidth=2)
        # ppmDisplay.place(relx=0,rely=0.7,relheight=0.3,relwidth=1)
        # ppmLabel = tk.Label(ppmDisplay, text = 'PPM:')
        # ppmLabel.place(relx=0,rely=0,relheight=1,relwidth=0.3)
        # self.ppmVar = tk.IntVar()
        # self.ppmVar.set(0)
        # ppmDisplay = tk.Label(ppmDisplay, textvariable = self.ppmVar, anchor='w')
        # ppmDisplay.place(relx=0.3,rely=0,relheight=1,relwidth=0.7)

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
        # self.btn_3 = tk.Button(controlFrame, text='Default Linear Actuator', command=lambda:linearActuator.default())#,app.frames[DataPage].stat_LA.set(linearActuator.state)])
        # self.btn_3.place(relx=0,rely=0.2,relheight=0.1,relwidth=buttonWidth)
        self.btn_4 = tk.Button(controlFrame, text='Read Sensors', command=lambda:all_sensors.print())
        self.btn_4.place(relx=0,rely=0.3,relheight=0.1,relwidth=buttonWidth)
        self.btn_5 = tk.Button(controlFrame, text='Read Temperature Sensor', command=lambda:temperatureSensor.print())
        self.btn_5.place(relx=0,rely=0.4,relheight=0.1,relwidth=buttonWidth)
        # self.btn_6 = tk.Button(controlFrame, text='Switch Valve 1', command=lambda:valve1.switch())#,app.frames[DataPage].stat_valve1.set(inValve.state)])
        # self.btn_6.place(relx=0,rely=0.5,relheight=0.1,relwidth=buttonWidth)
        # self.btn_7 = tk.Button(controlFrame, text='Switch Valve 2', command=lambda:valve2.switch())#,app.frames[DataPage].stat_valve2.set(outValve.state)])
        # self.btn_7.place(relx=0,rely=0.6,relheight=0.1,relwidth=buttonWidth)
        self.btn_8 = tk.Button(controlFrame, text='Switch Pump', command=lambda:pump.switch())#,app.frames[DataPage].stat_pump.set(pump.state)])
        self.btn_8.place(relx=0,rely=0.5,relheight=0.1,relwidth=buttonWidth)
        # self.btn_9 = tk.Button(controlFrame, text='Read Pressure', command=lambda:pressureSensor.print())
        # self.btn_9.place(relx=0,rely=0.8,relheight=0.1,relwidth=buttonWidth)

        lbl_1 = tk.Label(controlFrame, text='  Extend the linear actuator to the sensing chamber.', anchor='w')
        lbl_1.place(relx=buttonWidth,rely=0,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_2 = tk.Label(controlFrame, text='  Retract the linear actuator to the clean chamber.', anchor='w')
        lbl_2.place(relx=buttonWidth,rely=0.1,relheight=0.1,relwidth=(1-buttonWidth))
        # lbl_3 = tk.Label(controlFrame, text='  Reset the linear to the default (center) position.', anchor='w')
        # lbl_3.place(relx=buttonWidth,rely=0.2,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_4 = tk.Label(controlFrame, text='  Read the current value of the MOS (gas) sensors.', anchor='w')
        lbl_4.place(relx=buttonWidth,rely=0.3,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_5 = tk.Label(controlFrame, text='  Read the current internal temperature of the device.', anchor='w')
        lbl_5.place(relx=buttonWidth,rely=0.4,relheight=0.1,relwidth=(1-buttonWidth))
        # lbl_6 = tk.Label(controlFrame, text='   Toggle the inlet valve.', anchor='w')
        # lbl_6.place(relx=buttonWidth,rely=0.5,relheight=0.1,relwidth=(1-buttonWidth))
        # lbl_7 = tk.Label(controlFrame, text='   Toggle the outlet valve.', anchor='w')
        # lbl_7.place(relx=buttonWidth,rely=0.6,relheight=0.1,relwidth=(1-buttonWidth))
        lbl_8 = tk.Label(controlFrame, text='  Toggle the pump.', anchor='w')
        lbl_8.place(relx=buttonWidth,rely=0.5,relheight=0.1,relwidth=(1-buttonWidth))
        # lbl_9 = tk.Label(controlFrame, text='  Read the current Pressure.', anchor='w')
        # lbl_9.place(relx=buttonWidth,rely=0.8,relheight=0.1,relwidth=(1-buttonWidth))

def suppress_buttons():
    app.frames[ManualControlPage].btn_1.config(state='disabled')
    app.frames[ManualControlPage].btn_2.config(state='disabled')
    #app.frames[ManualControlPage].btn_3.config(state='disabled')
    app.frames[ManualControlPage].btn_4.config(state='disabled')
    app.frames[ManualControlPage].btn_5.config(state='disabled')
    # app.frames[ManualControlPage].btn_6.config(state='disabled')
    # app.frames[ManualControlPage].btn_7.config(state='disabled')
    app.frames[ManualControlPage].btn_8.config(state='disabled')
    # app.frames[ManualControlPage].btn_9.config(state='disabled')
    app.frames[HomePage].exitBtn.config(state='disabled')
    app.frames[HomePage].shutdownBtn.config(state='disabled') #random

def release_buttons():
    app.frames[ManualControlPage].btn_1.config(state='normal')
    app.frames[ManualControlPage].btn_2.config(state='normal')
    #app.frames[ManualControlPage].btn_3.config(state='normal')
    app.frames[ManualControlPage].btn_4.config(state='normal')
    app.frames[ManualControlPage].btn_5.config(state='normal')
    # app.frames[ManualControlPage].btn_6.config(state='normal')
    # app.frames[ManualControlPage].btn_7.config(state='normal')
    app.frames[ManualControlPage].btn_8.config(state='normal')
    # app.frames[ManualControlPage].btn_9.config(state='normal')
    app.frames[HomePage].exitBtn.config(state='normal')
    app.frames[HomePage].shutdownBtn.config(state='normal')


def purge_system():

    if linearActuator.state != 'retracted':
        linearActuator.retract()
        #app.frames[DataPage].stat_LA.set(linearActuator.state)
    messagebox.showinfo("PUMP ON","Please Connect the Pump and turn on. Press Okay once ready.")
    # Purge the clean chamber.
    start_time = time.time() # Time at which the purging starts.

    while time.time() < (start_time + sensing_chamber_purge_time) and continueTest == True:
        # if pump.state != True:
        #     pump.enable()
        if linearActuator.state != 'retracted':
            linearActuator.retract()

            #app.frames[DataPage].stat_pump.set(pump.state)
        # if inValve.state != True:
        #     inValve.enable()
        #     #app.frames[DataPage].stat_valve1.set(inValve.state)
        # if outValve.state != True:
        #     outValve.enable()
            #app.frames[DataPage].stat_valve2.set(outValve.state)

    # Purge the sensing chamber.
    start_time = time.time() #Reset the time at which purging starts.
    while time.time() < (start_time + clean_chamber_purge_time) and continueTest == True:
        # if pump.state != True:
        #     pump.enable()
        if linearActuator.state != 'extended':
            linearActuator.extend()
            #app.frames[DataPage].stat_pump.set(pump.state)
        # if inValve.state != False:
        #     inValve.disable()
        #     #app.frames[DataPage].stat_valve2.set(inValve.state)
        # if outValve.state != False:
        #     outValve.disable()
        #     #app.frames[DataPage].stat_valve2.set(outValve.state)

    pump.disable() # Turn off the pump after purging.
    #app.frames[DataPage].stat_pump.set(pump.state)
    if linearActuator.state != 'retracted':
        linearActuator.retract()
    pass

def fill_chamber():

    if linearActuator.state != 'retracted':
        linearActuator.retract()
    #Put an alert box

def collect_data(xVector,yVector):
    start_time = time.time()  # Local value. Capture the time at which the test began. All time values can use start_time as a reference
    dataVector = yVector
    timeVector = xVector
    dataVector.clear()
    timeVector.clear()
    sampling_time_index = 1

    # Initial state checks
    if linearActuator.state != 'retracted':
        linearActuator.retract()
    #if inValve.state != False:
        #inValve.disable()
    #if outValve.state != False:
        #outValve.disable()

    print('Starting data capture.')
    while (time.time() < (start_time + duration_of_signal)) and (continueTest == True):  # While time is less than duration of logged file
        if (time.time() > (start_time + (sampling_time * sampling_time_index)) and (continueTest == True)):  # if time since last sample is more than the sampling time, take another sample
            dataVector.append(all_sensors.read())  # Perform analog to digital function, reading voltage from first sensor channel
            timeVector.append(time.time() - start_time)
            sampling_time_index += 1

        # If time is between 10-50 seconds and the Linear Actuator position sensor signal from the ADC indicates a retracted state, extend the sensor
        elif (time.time() >= (start_time + sensing_delay_time) and time.time() <= (
                sensing_retract_time + start_time) and (continueTest == True)):
            if linearActuator.state != 'extended':
                linearActuator.extend()

        # If time is less than 10 seconds or greater than 50 seconds and linear actuator position sensor signal from the ADC indicates an extended state, retract the sensor
        elif (((time.time() < (sensing_delay_time + start_time)) or (
                time.time() > (sensing_retract_time + start_time)))) and (continueTest == True):
            if linearActuator.state != 'retracted':
                linearActuator.retract()

        # Otherwise, keep outputs off
        else:
            if linearActuator.state != 'retracted':
                linearActuator.retract()
    print('Data Capture Complete')
    combinedVector = np.column_stack((timeVector, dataVector))

    filename = strftime("testsP/%a%-d%b%Y%H%M%S.csv",gmtime())
    np.savetxt(filename,combinedVector, fmt='%.10f', delimiter=',')


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
            app.frames[DataPage].contFill.tkraise()

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
    data_thread = threading.Thread(target=collect_data,args=(timeVector,dataVector))
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
        #release_buttons()
        app.frames[DataPage].runBtn.tkraise()
        app.frames[DataPage].status.set('  System ready.')
try:
    app = CannibixHHGUI()
    app.mainloop()
except keyboardinterrupt:
    GPIO.cleanup()
finally:
    GPIO.cleanup()
