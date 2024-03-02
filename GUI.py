# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import serial
import pandas as pd
import RPi.GPIO as GPIO
import time

# control different testing host
feature_flag = {
    'ENABLE_UART_TMS' : True,        # set True if using RPi to TMS
    'TESTING_WITH_PC_ONLY': False    # set True if only testing with PC
    }
          
A = 0x41
B = 0x42
C = 0x43
D = 0x44
E = 0x45
N = 0x4E        

# GPIO pin configuration
GPIO.setmode(GPIO.BCM)
pin_motor = 23
GPIO.setup(pin_motor,GPIO.OUT)
GPIO.output(pin_motor,GPIO.LOW)
GPIO.setwarnings(False)

Uart_Baud = 115200  
txtBoxWid = 22
stop_pressed = False

global strain,stress, data
strain = np.array([])
stress = np.array([])

# Create serial port
if feature_flag.get('ENABLE_UART_TMS', True):
    ser = serial.Serial('/dev/ttyAMA0', Uart_Baud, timeout=1) # used for RPi testing
    if ser.is_open:
        print("port connected")
elif feature_flag.get('TESTING_WITH_PC_ONLY', True):
    # Figure data (sample diagram)
    stress = np.concatenate( (np.linspace(0,50,50),np.linspace(50,70,50)))
    strain = np.arange(len(stress))
    data = [strain,stress]

def __fake_datainput():
    fakeData = b"ABCIT_MECHATRONICS&ROBOTICS_PROGRAMEND"
    ser.write(fakeData)
    time.sleep(0.1)

def __tensileTest():
    print("Tensile test initiated")
    GPIO.output(pin_motor,GPIO.HIGH)

    __update_plot()   # start the motor as the same time start plot real-time plotting
    # messagebox.showinfo("Information", "Starting tensile testing")
        
def __exportCSV():
    GPIO.output(pin_motor,GPIO.LOW)
    messagebox.showinfo("Information", "Export .CSV file")
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
    if file_path:
        df = pd.DataFrame(data)
        df = df.transpose()
        column_label = ["Strain","Stress, MPa"]
        df.columns = column_label
        df.to_csv(file_path, index=False)
      
def __exportPDF():
    GPIO.output(pin_motor,GPIO.LOW)
    messagebox.showinfo("Information", "Export .PDF file")
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        with PdfPages(file_path) as pdf:
            testCanvas.figure.savefig(pdf, format='pdf')
    
def __quit():
    GPIO.output(pin_motor,GPIO.LOW)
    root.quit()
    root.destroy()
    
def __update_plot():
    try:        
        __fake_datainput()
        print("entered update plot")
        Cmd_Byte = ser.read().decode()  # Obtain Cmd_Byte
        print('command: ',Cmd_Byte)
        # Decode the obtained data
        # Look Up Table for decoding
        #|----------------------------------------------------------------|
        #| Cmd_Byte |   Byte Size  |              Command                 |
        #|----------|--------------|--------------------------------------|
        #|    A     | 1+vary+E+N+D |  Encoder, LVDT data coming from TMS  |
        #|    B     |       1      |   Emergency Stop engaged, sys stops  |
        #|    C     |       1      |    Limit Switch engaged, sys stops   |
        #|  E+N+D   |       3      |   Ending Byte of data transmission   |
        #
        
        if Cmd_Byte == 'A':    # data transmission command

            print("entered Cmd_Byte == A")
            data_point = 0
            strainFlag = True   # To indicate incoming strain or stress data
            while True:          
                global data, stress, strain
                data_point = int.from_bytes(ser.read())    # Obtain serial data from TMS
                print("Reading byte: ", data_point)
                if data_point == E:
                    print("accepted byte E\n")
                    data_point = int.from_bytes(ser.read())
                    if data_point == N:
                        print("accepted byte N\n")
                        data_point = int.from_bytes(ser.read())                     
                        if data_point == D:
                            print("accepted byte D, breaking\n")
                            __data_concat()
                            break
                        if strainFlag == True:
                            strain = np.append(strain,np.array([E]))
                            stress = np.append(stress,np.array([E]))
                        else:
                            stress = np.append(stress,np.array([E]))
                            strain = np.append(strain,np.array([E]))                         
                    # Append decoded data into array
                    else:
                        if strainFlag == True:
                            strain = np.append(strain,np.array([E]))
                            strainFlag = False
                        else:
                            stress = np.append(stress,np.array([E]))
                            strainFlag = True          
                            
                # Append decoded data into array
                if strainFlag == True:
                    strainFlag = False
                    strain = np.append(strain,np.array([data_point]))
                    axTens.set_xlim(0, 2*data_point)
                else:
                    strainFlag = True
                    stress = np.append(stress,np.array([data_point]))
                    axTens.set_ylim(0, 2*data_point)
                    line.set_data(strain, stress)  
                    testCanvas.draw()
                    root.update()
                            
                print("strain: ",strain,"\nstress: ",stress)
                # update plot

                root.after(5)
                
                # stop updating diagram if user pressed stop button
                if stop_pressed:
                    __data_concat()
                    break
        
        elif Cmd_Byte == B:  # Emergency Stop engaged
            GPIO.output(pin_motor,GPIO.LOW) # stop the motor
            __data_concat()
            messagebox.showinfo("Warning","System stops due to e-stop engagement")
        elif Cmd_Byte == C:  # Limit Switch engaged
            GPIO.output(pin_motor,GPIO.LOW) # stop the motor
            __data_concat()
            messagebox.showinfo("Warning","System stops due to limit switch been triggered")
        print("enter nothing\n")
    except KeyboardInterrupt:  # stop the drawing due to interrupt (design for limit switch as well user interrupt)
        print("Interrupt from keyboard\n")
        ser.close()

def __stop_plot():
    global stop_pressed
    stop_pressed = True
    GPIO.output(pin_motor,GPIO.LOW)  # stop the motor
    messagebox.showinfo("Information","Process has been stopped")
    
def __data_concat():
    global data
    # Organize data frame for exporting .csv
    data = np.concatenate((strain.reshape(1,-1), stress.reshape(1,-1)), axis=0)
    
    

root = tk.Tk()
root.title("BCIT_AUTOBOT")

SCREEN_WIDTH = root.winfo_screenwidth() - 200
INPUT_FRAME_WIDTH = SCREEN_WIDTH * 250 / 800
OUTPUT_FRAME_WIDTH = SCREEN_WIDTH * 250 / 800
EXPORT_FRAME_WIDTH = SCREEN_WIDTH * 250 / 800
QUIT_FRAME_WIDTH = SCREEN_WIDTH * 250 / 800
CHART_FRAME_WIDTH = SCREEN_WIDTH * 550 / 800

SCREEN_HEIGHT = root.winfo_screenheight() - 800
INPUT_FRAME_HEIGHT = SCREEN_HEIGHT * 150 / 500
OUTPUT_FRAME_HEIGHT = SCREEN_HEIGHT * 150 / 500
EXPORT_FRAME_HEIGHT = SCREEN_HEIGHT * 150 / 500
QUIT_FRAME_HEIGHT = SCREEN_HEIGHT * 50 / 500
CHART_FRAME_HEIGHT = SCREEN_HEIGHT

root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}+0+0")

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

stopBtn = tk.Button(outputFrame, text="Stop", bg='white', command=__stop_plot)
stopBtn.place(relx=0.5, rely=0.8, relwidth=0.7, anchor='center')

############################  EXPORT FRAME #################################### 
tk.Button(exportFrame, text="Export .csv", command=__exportCSV, bg="white").place(relx=0.5, relwidth=0.5, anchor="e", rely=0.8)
tk.Button(exportFrame, text="Export .pdf", command=__exportPDF, bg="white").place(relx=0.5, relwidth=0.5, anchor="w", rely=0.8)

############################  QUIT FRAME ###################################### 
tk.Button(quitFrame, text="Exit Program", command=__quit, bg='white').place(relwidth=0.7, relx=0.5, rely=0.5, anchor="center")

############################  CHART FRAME ##################################### 
# Tensile test figure
figTens, axTens = plt.subplots()
line, = axTens.plot([], [], label='Data')
axTens.set_title("Stress vs Strain")
axTens.set_xlabel("Strain")
axTens.set_ylabel("Stress, MPa")

testCanvas = FigureCanvasTkAgg(figTens, chartFrame)
testCanvas.get_tk_widget().place(relx=0.5,rely=0.5,anchor='center',relwidth=0.95,relheight=0.95)

root.mainloop()
ser.close()