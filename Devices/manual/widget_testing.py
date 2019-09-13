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


print("doing things")
#warning_box = messagebox.showwarning("This warning", "press enter")
warning_box = messagebox.showinfo("something","else")
print("done warning")
yesno = messagebox.askyesno("Yes no","Press yes or no")
print(yesno)
