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
# from cannibix_components_HH import *
# # -----> RPi Imports <------
# import RPi.GPIO as GPIO
# import time
# import os
# import Adafruit_ADS1x15 as ADS
# import serial
# from pathlib import Path

# GPIO.setmode(GPIO.BOARD)
# adc = ADS.ADS1115(0x48)
# adc2 = ADS.ADS1115(0x49)
#
# #ADC2
# sensor1 = MOS(adc2, 0)
# sensor2 = MOS(adc2, 1)
# sensor3 = MOS(adc2, 2)
# sensor4 = MOS(adc2, 3)
#
# #ADC1
# sensor5 = MOS(adc, 0)
# sensor6 = MOS(adc, 1)
# sensor7 = MOS(adc, 2)
# sensor8 = MOS(adc, 3)
#
# all_sensors = all_sensors(sensor1,sensor2,sensor3,sensor4)
# # all_sensors2 = all_sensors(sensor5,sensor6,sensor7,sensor8)
# # Temperature sensor
# Temp_adc_channel = 1
# temperatureSensor = TemperatureSensor(adc, Temp_adc_channel)
# #Pressure Sensor
# Press_adc_channel = 0
# pressureSensor = PressureSensor(adc,Press_adc_channel)

##################################################
#################### Data Array ####################
# DO NOT TOUCH # -teehee touched
dataVector = []
timeVector = []
test_type_Vector = []
param_vector = []
#################### Color Settings ####################
warning_color = '#FFC300'
tabBar_color = '#85929E'
tabBarActive_color = '#AEB6BF'
runBtn_color = '#9DE55F'
stopBtn_color = '#FF4E4E'
default_bg_color = '#22487d'
#################### GUI ####################

projectName = 'Cannibix Manual GUI'
class CannibixManGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs) #Passes all aguments to the parent class.

        self.title(projectName + ' GUI') #Title of the master window.
        self.geometry('640x480') #Initial size of the master window.
        # self.resizable(0,0) #The allowance for the master window to be adjusted by.

        canvas = tk.Frame(self, bg = default_bg_color) #Creates the area for which pages will be displayed.
        canvas.place(relx=0, rely=0, relheight=0.9, relwidth=1) #Defines the area which each page will be displayed.
        canvas.grid_rowconfigure(0, weight=1) #DO NOT ADJUST. Forces each frame to overlap.
        canvas.grid_columnconfigure(0, weight=1) #DO NOT ADJUST. Forces each frame to overlap.

        self.tabBar = tk.Frame(self, bg=tabBar_color) #Creates the area for which control buttons will be placed.
        self.tabBar.place(relx=0, rely=0.9, relheight=0.1, relwidth=1) #Defines the area for which control buttons will be placed.

        self.frames = {} #Dictonary to store each frame after creation.

        for f in (HomePage, DataPage):#, ManualControlPage): #For pages to be added, do the following:
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
        tk.Frame.__init__(self, parent, bg = default_bg_color)
        control_btn = tk.Button(controller.tabBar, text='Home', bg=tabBar_color, activebackground=tabBarActive_color, bd=0, command=lambda: controller.show_frame(HomePage)) #Creates a control button in the tabs bar.
        control_btn.pack(side='left', expand= True, fill = 'both')

        title = tk.Label(self, text=projectName, font=14, relief='solid')
        title.place(relx=0.2,rely=0.3,relwidth=0.6,relheight=0.15)

        intro = '''Microfluidic-based THC detector. Developed by ATF Lab
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
        tk.Frame.__init__(self, parent, bg = default_bg_color)
        control_btn = tk.Button(controller.tabBar, text='Data', bg=tabBar_color, activebackground=tabBarActive_color, bd=0, command=lambda: controller.show_frame(DataPage))
        control_btn.pack(side='left', expand= True, fill = 'both')

        seq1Frame = tk.Frame(self,borderwidth = 5,relief = GROOVE)
        seq1Frame.place(relx = .05,rely = 0, relheight = 0.2, relwidth = .9)
        self.seq1Label = tk.Label(seq1Frame, text='This is step 1',font=20)
        self.seq1Label.place(relx = 0, rely = .5, relheight = .4, relwidth = .5)
        self.seq1button = tk.Button(seq1Frame, )
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



# self.timer = Timer(self)
# self.timer.place(relx = .5, rely = .5, relheight = .5, relwidth = 0.5)
# self.status = tk.StringVar()
# self.status.set('Ready for Sample Sequence')
#
# self.progressTitle = tk.Label(self, textvariable = self.status, anchor='w')
# self.progressTitle.place(relx=0,rely=0.9,relheight=0.07,relwidth=0.8)
#
# self.progressbar = ttk.Progressbar(self, orient='horizontal', mode='determinate', maximum=100)
# self.progressbar.place(relx=0,rely=0.97,relheight=0.03,relwidth=0.8)

# def fill_cup():
#     messagebox.showwarning("Sample Gas Testing","Insert Sample Gas line into Cup and Press OK")
#     app.frames[DataPage].timer.reset()
#     responseFrame = tk.Frame(self)
#     responseFrame.place(relx=0.8,rely=0,relheight=0.3,relwidth=0.2)
#
#     self.filenamelbl = tk.Label(responseFrame,text='Filename (Optional)',anchor='w')
#     self.filenamelbl.place(relx=0,rely=0.7,relheight = 0.5,relwidth = 1)
#     #self.filename_add = tk.StringVar()
#     self.filenamefiller = tk.Entry(responseFrame)
#     self.filenamefiller.place(relx=0,rely=.8,relwidth=1)

try:
    app = CannibixManGUI()
    app.mainloop()
except KeyboardInterrupt:
    #GPIO.cleanup()
    pass
finally:
    #GPIO.cleanup()
    pass
