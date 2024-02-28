# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
       

def tensileTest():
    messagebox.showinfo("Information", "Starting tensile testing")
        
def exportCSV():
    messagebox.showinfo("Information", "Export .CSV file")
    
def exportPDF():
    messagebox.showinfo("Information", "Export .PDF file")
    
def __quit():
    root.quit()
    root.destroy()

        
txtBoxWid = 22

INPUT_FRAME_WIDTH = 250
OUTPUT_FRAME_WIDTH = 250
EXPORT_FRAME_WIDTH = 250
QUIT_FRAME_WIDTH = 250
CHART_FRAME_WIDTH = 550

INPUT_FRAME_HEIGHT = 150
OUTPUT_FRAME_HEIGHT = 150
EXPORT_FRAME_HEIGHT = 150
QUIT_FRAME_HEIGHT = 50
CHART_FRAME_HEIGHT = 500

# Figure data
strain = np.arange(0,10,0.1)
stress = np.concatenate((np.arange(0,50,1), np.arange(50,70,0.4)))

# Tensile test figure
figTens, axTens = plt.subplots()
axTens.plot(strain,stress)
axTens.set_title("Stress vs Strain")
axTens.set_xlabel("Strain")
axTens.set_ylabel("Stress")

#plt.show()


root = tk.Tk()
root.title("BCIT_AUTOBOT")
root.geometry("800x500+500+100")


inputFrame = tk.Frame(root,width=INPUT_FRAME_WIDTH, height=INPUT_FRAME_HEIGHT, bg="blue")
inputFrame.place(x=0,y=0)

outputFrame = tk.Frame(root,width=OUTPUT_FRAME_WIDTH, height = OUTPUT_FRAME_HEIGHT, bg="red")
outputFrame.place(x=0,y=INPUT_FRAME_HEIGHT)

exportFrame = tk.Frame(root,width=EXPORT_FRAME_WIDTH, height=EXPORT_FRAME_HEIGHT, bg="green")
exportFrame.place(x=0,y=INPUT_FRAME_HEIGHT+OUTPUT_FRAME_HEIGHT)

quitFrame = tk.Frame(root,width=QUIT_FRAME_WIDTH,height=QUIT_FRAME_HEIGHT, bg="yellow")
quitFrame.place(x=0,y=INPUT_FRAME_HEIGHT+OUTPUT_FRAME_HEIGHT+EXPORT_FRAME_HEIGHT)

chartFrame = tk.Frame(root,width=CHART_FRAME_WIDTH, height=CHART_FRAME_HEIGHT, bg="brown")
chartFrame.place(x=INPUT_FRAME_WIDTH,y=0)
        
############################  INPUT FRAME #####################################        
# Labels in input frame
tk.Label(inputFrame, text="Enter Segment Length in mm", bg="white").place(relx=0.5, relwidth=1,anchor="n")
tk.Label(inputFrame, text="Enter Segment Width in mm", bg="white").place(relx=0.5,relwidth=1,anchor="n", y=txtBoxWid*2)

# Entry in input frame 
segLen = tk.DoubleVar()
entry_SegLen = tk.Entry(inputFrame, textvariable=segLen ,justify='center')
entry_SegLen.place(relx=0.5, relwidth=1, y=txtBoxWid+1, anchor='n')

segWid = tk.DoubleVar()
entry_SegWid = tk.Entry(inputFrame, textvariable=segWid ,justify='center')
entry_SegWid.place(relx=0.5, relwidth=1, y=txtBoxWid*3+1, anchor='n')

# Button in input frame
tk.Button(inputFrame, text="Tensile Test", command=tensileTest, bg="white").place(relx=0.5,rely=0.8,relwidth=0.7,anchor="center")
        

############################  OUTPUT FRAME #################################### 
tk.Label(outputFrame, text="Ultimate Stress, MPa", bg="white").place(relx=0.5, relwidth=1, anchor="n")
        
segUltSt = tk.DoubleVar()
entry_SegWid = tk.Label(outputFrame, textvariable=segUltSt,bg='white')
entry_SegWid.place(relx=0.5, relwidth=1, anchor="n", y=txtBoxWid)

tk.Label(outputFrame, text="Young's Modulus, GPa", bg="white").place(relx=0.5, relwidth=1, anchor="n", y=txtBoxWid*2)
        
segYoung = tk.DoubleVar()
entry_SegWid = tk.Label(outputFrame, textvariable=segYoung, bg="white")
entry_SegWid.place(relx=0.5, relwidth=1, anchor="n", y=txtBoxWid*3)

############################  EXPORT FRAME #################################### 
tk.Button(exportFrame, text="Export .csv", command=exportCSV, bg="white").place(relx=0.5, relwidth=0.5, anchor="e", rely=0.8)
tk.Button(exportFrame, text="Export .pdf", command=exportPDF, bg="white").place(relx=0.5, relwidth=0.5, anchor="w", rely=0.8)

############################  QUIT FRAME ###################################### 
tk.Button(quitFrame, text="Exit Program", command=__quit, bg='white').place(relwidth=0.7, relx=0.5, rely=0.5, anchor="center")

############################  CHART FRAME ##################################### 
testCanvas = FigureCanvasTkAgg(figTens, chartFrame)
testCanvas.draw()
testCanvas.get_tk_widget().place(relx=0.5,rely=0.5,anchor='center',relwidth=0.95,relheight=0.95)


root.mainloop()