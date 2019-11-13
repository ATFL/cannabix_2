#Last edit: 21/05/2019
# -----> System Imports <-----
import os
import sys
import datetime
import time
# -----> Tkinter Imports <------
import tkinter as tk
from tkinter import ttk
# -----> Matplotlib Imports <------
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
# -----> Auxiliary Imports <------
import random

class LiveGraph(tk.Frame):
    def __init__(self, *args, ** kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.name = 'Live Graph'

        self.xList = []
        self.yList = []

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.subplot1 = self.fig.add_subplot(221)
        self.subplot2 = self.fig.add_subplot(222)
        self.subplot3 = self.fig.add_subplot(223)
        self.subplot4 = self.fig.add_subplot(224)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    def addData(self, xVal, yVal):
        self.xList.append(xVal)
        self.yList.append(yVal)
        self.fig.clear()
        self.fig.add_subplot(221).plot(self.xList, self.yList[:,1])
        self.fig.add_subplot(222).plot(self.xList, self.yList[:,2])
        self.fig.add_subplot(223).plot(self.xList, self.yList[:,3])
        self.fig.add_subplot(224).plot(self.xList, self.yList[:,4])
        self.canvas.draw()

    def clearData(self):
        self.xList = []
        self.yList = []
        self.fig.clear()
        self.fig.add_subplot(221).plot(self.xList, self.yList)
        self.fig.add_subplot(222).plot(self.xList, self.yList)
        self.fig.add_subplot(223).plot(self.xList, self.yList)
        self.fig.add_subplot(224).plot(self.xList, self.yList)
        self.canvas.draw()

    def returnData(self):
        return (self.xList, self.yList)

class SettingBar (tk.Frame):
    def __init__(self, master, setting, low, high, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.name = 'Setting Bar'
        self.var = tk.IntVar()
        self.var.set(0)
        self.range = [low, high]

        entry = tk.Entry(self, textvariable=self.var, bg='light blue')
        entry.place(relx=0.8, rely=0, relheight=0.6, relwidth=0.2)

        settingName = tk.Label(self, anchor='center', text=setting , bg='sky blue')
        settingName.place(relx=0, rely=0, relheight=0.6, relwidth=0.8)

        scale = tk.Scale(self,orient='horizontal', showvalue=0, width=30, from_=self.range[0], to=self.range[1], variable= self.var,  bg='light grey')
        scale.place(relx=0.1, rely=0.6, relheight=0.4, relwidth=0.8)

        Lbutton = tk.Button(self, text='<', command= lambda: self.LPress(),  bg='grey')
        Lbutton.place(relx=0, rely=0.6, relheight=0.4, relwidth=0.1)
        Rbutton = tk.Button(self, text='>', command= lambda: self.RPress(),  bg='grey')
        Rbutton.place(relx=0.9, rely=0.6, relheight=0.4, relwidth=0.1)

    def LPress(self):
        if self.var.get() > self.range[0]:
            self.var.set(self.var.get() - 1)

    def RPress(self):
        if self.var.get() < self.range[1]:
            self.var.set(self.var.get() + 1)

    def get(self):
        return self.var.get()

    def set(self, num):
        self.var.set(num)

class StdRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.config(state=tk.NORMAL)
        self.text_space.insert("end", string)
        self.text_space.see("end")
        self.text_space.config(state=tk.DISABLED)

class CoreGUI(object):
    def __init__(self, parent):
        scrollbar = tk.Scrollbar(parent)
        scrollbar.pack(side = tk.RIGHT, fill = 'y')
        text_box = tk.Text(parent, state=tk.DISABLED, yscrollcommand = scrollbar.set)
        scrollbar.config(command=text_box.yview)
        sys.stdout = StdRedirector(text_box)
        sys.stderr = StdRedirector(text_box)
        text_box.pack(expand = True, fill = "both")

class Timer(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.now = 0
        self.label = tk.Label(self, text=str(self.now)+' s')
        self.label.place(relx=0,rely=0,relheight=0.7,relwidth=1)
        self.label.after(1000, self.update)

        resetbtn = tk.Button(self, text='Reset', command=lambda:self.reset())
        resetbtn.place(relx=0,rely=0.7,relheight=0.3,relwidth=1)

    def update(self):
        self.now += 1
        self.label.configure(text=str(self.now)+' s')
        self.label.after(1000, self.update)

    def reset(self):
        self.now = 0
        self.label.configure(text=str(self.now)+' s')

    def get_time(self):
        return self.now

class AutoLiveGraph(tk.Frame):
    def __init__(self, parent, xList, yList):
        tk.Frame.__init__(self, parent)

        self.xList = xList
        self.yList = yList

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.subplot1 = self.fig.add_subplot(221)
        self.subplot2 = self.fig.add_subplot(222)
        self.subplot3 = self.fig.add_subplot(223)
        self.subplot4 = self.fig.add_subplot(224)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    def update(self, xList, yList):
        self.fig.clear()
        self.fig.add_subplot(221).plot(xList, yList[:,1])
        self.fig.add_subplot(222).plot(xList, yList[:,2])
        self.fig.add_subplot(223).plot(xList, yList[:,3])
        self.fig.add_subplot(224).plot(xList, yList[:,4])
        self.canvas.draw()

    def clear(self):
        self.fig.clear()
        self.fig.add_subplot(221).plot([], [])
        self.fig.add_subplot(222).plot([], [])
        self.fig.add_subplot(223).plot([], [])
        self.fig.add_subplot(224).plot([], [])

        self.canvas.draw()
