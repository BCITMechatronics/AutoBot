# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial


# control different testing host
feature_flag = {
    'ENABLE_UART_PCHOST' : False,   # set True if using PC to RPi
    'ENABLE_UART_TMS': False,       # set True if using TMS to RPi
    }
          
        
Uart_Baud = 19200    
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


# Create serial port
if feature_flag.get('ENABLE_UART_PCHOST', True):
    ser = serial.Serial('COM5', Uart_Baud)       # used for PC testing
if feature_flag.get('ENABLE_UART_TMS', True):
    ser = serial.Serial('/dev/ttyS0', Uart_Baud) # used for RPi testing



def __tensileTest():
    messagebox.showinfo("Information", "Starting tensile testing")
        
def __exportCSV():
    messagebox.showinfo("Information", "Export .CSV file")
    
def __exportPDF():
    messagebox.showinfo("Information", "Export .PDF file")
    
def __quit():
    root.quit()
    root.destroy()
    
def __update_plot():
    try:
        while True:            
            global data, strain, stress
            data_point = ser.readline().decode().strip()    # Obtain serial data from TMS
            
            # Decode the obtained data
            strain = (data_point | 0x00FF)
            stress = ((data_point>>8) | 0x00FF)
            
            # Append decoded data into array
            data[0].append(float(strain))
            data[1].append(float(stress))
            
            # Plot configuration
            axTens.set_xlim(0, 1.1*data[0].end)
            axTens.set_ylim(0, 1.1*data[1].end)
            
            # update plot
            line.set_data(strain, stress)
            testCanvas.draw()
            root.update()
            root.after(10)
            
    except KeyboardInterrupt:  # stop the drawing due to interrupt (design for limit switch as well user interrupt)
        ser.close()
        

# Figure data
data = [strain,stress]

# Tensile test figure
figTens, axTens = plt.subplots()
line, = axTens.plot(strain, stress, label='Data')
axTens.set_title("Stress vs Strain")
axTens.set_xlabel("Strain")
axTens.set_ylabel("Stress, MPa")


root = tk.Tk()
root.title("BCIT_AUTOBOT")
root.geometry("800x500+500+100")

############################ FRAME SETUP ######################################  
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
tk.Button(inputFrame, text="Tensile Test", command=__tensileTest, bg="white").place(relx=0.5,rely=0.8,relwidth=0.7,anchor="center")
        

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
tk.Button(exportFrame, text="Export .csv", command=__exportCSV, bg="white").place(relx=0.5, relwidth=0.5, anchor="e", rely=0.8)
tk.Button(exportFrame, text="Export .pdf", command=__exportPDF, bg="white").place(relx=0.5, relwidth=0.5, anchor="w", rely=0.8)

############################  QUIT FRAME ###################################### 
tk.Button(quitFrame, text="Exit Program", command=__quit, bg='white').place(relwidth=0.7, relx=0.5, rely=0.5, anchor="center")

############################  CHART FRAME ##################################### 
testCanvas = FigureCanvasTkAgg(figTens, chartFrame)
testCanvas.get_tk_widget().place(relx=0.5,rely=0.5,anchor='center',relwidth=0.95,relheight=0.95)
__update_plot()

root.mainloop()