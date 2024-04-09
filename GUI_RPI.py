# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# 希望实现的功能：
# 1. 用户名管理系统（用于登录系统，并拥有修改用户名及密码的功能）
# 2. 当前时间显示
# 3. 浏览以往数据（点击数据可plot到图上）
# 4. 用户登陆历史

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttkbs
from ttkbootstrap.tableview import Tableview
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import serial   
import pandas as pd
import RPi.GPIO as GPIO
import time
from datetime import datetime
import pathlib as Path
   
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
txtBoxHeight = 30
btnHeight = 22
stop_pressed = False
global segWid, segLen, segRadius
global strain,stress, data
strain = np.array([])
stress = np.array([])


# Create serial port
ser = serial.Serial('/dev/ttyAMA0', Uart_Baud, timeout=1) # used for RPi testing
if ser.is_open:
    print("port connected")

# PATH = Path(__file__).parent / 'dataset'
# print("dataset path is:", PATH)


class __Tensile_Tester_Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master


        master.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}+0+0")

#%%#########################  FRAME SETUP  ####################################
        inputFrame = ttk.Frame(
            master,
            width=INPUT_FRAME_WIDTH, 
            height = INPUT_FRAME_HEIGHT, 
            style="secondary.TFrame")        
        inputFrame.place(
            x=0,y=0,
            width=INPUT_FRAME_WIDTH,
            height=INPUT_FRAME_HEIGHT)

        outputFrame = ttk.Frame(
            master,
            width=OUTPUT_FRAME_WIDTH, 
            height = OUTPUT_FRAME_HEIGHT, 
            style="secondary.TFrame")
        outputFrame.place(
            x=0,
            y=INPUT_FRAME_HEIGHT)

        historyFrame = ttk.Frame(
            master,
            width=HISTORY_FRAME_WIDTH, 
            height=HISTORY_FRAME_HEIGHT, 
            style="secondary.TFrame")
        historyFrame.place(
            x=0,
            y=INPUT_FRAME_HEIGHT+OUTPUT_FRAME_HEIGHT)

        doneFrame = ttk.Frame(
            master,
            width=DONE_FRAME_WIDTH,
            height=DONE_FRAME_HEIGHT, 
            style="primary.TFrame")
        doneFrame.place(
            x=0,
            y=INPUT_FRAME_HEIGHT+OUTPUT_FRAME_HEIGHT+HISTORY_FRAME_HEIGHT)

        chartFrame = ttk.Frame(
            master,
            width=CHART_FRAME_WIDTH, 
            height=CHART_FRAME_HEIGHT, 
            style="secondary.TFrame")
        chartFrame.place(
            x=INPUT_FRAME_WIDTH,
            y=0)
                
#%%#########################  INPUT FRAME  ####################################

        # ComboBox in input frame
        croxSectionType = ["Rectangular","Circular"]
        self.cbBox_typeSel = ttk.Combobox(
                                    inputFrame, 
                                    values=croxSectionType,
                                    justify="center",
                                    state='readonly')
        self.cbBox_typeSel.place(
                                relx=0.5, 
                                rely=INPUT_LABEL_CBBOX,
                                y=INPUT_CBBOX,
                                relwidth=0.7,
                                anchor='center')
        self.cbBox_typeSel.current(0)
        self.cbBox_typeSel.bind("<<ComboboxSelected>>", self.__get_shape)
        
        # Button in input frame
        ttk.Button(
            inputFrame, 
            text="Tensile Test",
            command=self.__tensileTest,
            style='primary.TButton').place(
                relx=0.5,
                rely=INPUT_BTN_TEST,
                relwidth=0.7,
                anchor="center")
                
        ttk.Button(
            inputFrame, 
            text="Confirm dimension",
            command=self.__confirm_dim,
            style='danger.TButton').place(
                relx=0.5,
                rely=INPUT_BTN_TEST,
                y=INPUT_BTN_CNFM,
                relwidth=0.7,
                anchor="center")
                
        stopBtn = ttk.Button(
            inputFrame, 
            text="Stop", 
            command=self.__stop_plot,
            style="primary.TButton")
        stopBtn.place(
            relx=0.5, 
            rely=INPUT_BTN_TEST, 
            y=INPUT_BTN_STOP,
            relwidth=0.7, 
            anchor='center')
        
        # Entry in input frame
        self.dim1 = tk.DoubleVar()
        self.dim1.set(0.0)
        self.nty_dim1 = ttk.Entry(
                        inputFrame, 
                        textvariable=self.dim1,
                        justify='center',
                        style="danger.TEntry")
        self.nty_dim1.place(
            relx=0.5,
            rely=INPUT_LABEL_CBBOX,
            y=INPUT_ENTRY_DIM1,
            relwidth=0.7,
            anchor="center")
        
        self.dim2 = tk.DoubleVar()
        self.dim2.set(0.0)
        self.nty_dim2 = ttk.Entry(
                        inputFrame, 
                        textvariable=self.dim2,
                        justify='center')
        self.nty_dim2.place(
            relx=0.5,
            rely=INPUT_LABEL_CBBOX,            
            y=INPUT_ENTRY_DIM2,
            relwidth=0.7,
            anchor="center")
        
        # Label in input frame        
        ttk.Label(
            inputFrame,
            text="select segment shape",
            ).place(
                                    relx=0.5,
                                    rely=INPUT_LABEL_CBBOX,
                                    relwidth=0.7,
                                    anchor="center")
        
        self.labl_dim1 = ttk.Label(
                        inputFrame, 
                        textvariable="dimension1",
                        )
        self.labl_dim1.place(
            relx=0.5,
            rely=INPUT_LABEL_CBBOX,
            y=INPUT_LABEL_DIM1,
            relwidth=0.7,
            anchor="center")
        self.setvar("dimension1","segment length, mm:")
        self.setvar("dimension2","segment width, mm:")
        
        self.labl_dim2 = ttk.Label(
                        inputFrame, 
                        textvariable="dimension2")
        self.labl_dim2.place(
            relx=0.5,
            rely=INPUT_LABEL_CBBOX,
            y=INPUT_LABEL_DIM2,
            relwidth=0.7,
            anchor="center")
        
        
#%%#########################  OUTPUT FRAME ####################################

        tk.Label(
            outputFrame, 
            text="Segment Area, mm^2",
            justify='center').place(
                                            relx=0.5, 
                                            relwidth=1, 
                                            anchor="n")
                
        self.segArea = tk.DoubleVar()
        entry_Area = tk.Label(
                            outputFrame, 
                            textvariable=self.segArea,
                            justify='center')
        entry_Area.place(
                    relx=0.5, 
                    relwidth=1, 
                    anchor="n", 
                    y=btnHeight)

        tk.Label(
            outputFrame, 
            text="Ultimate Stress, MPa").place(
                                            relx=0.5, 
                                            relwidth=1, 
                                            anchor="n", 
                                            y=btnHeight*2)
                
        self.segUltSt = tk.DoubleVar()
        entry_segUlt = tk.Label(
                        outputFrame, 
                        textvariable=self.segUltSt)
        entry_segUlt.place(
                        relx=0.5, 
                        relwidth=1, 
                        anchor="n", 
                        y=btnHeight*3)
        
        tk.Label(
            outputFrame, 
            text="Young's Modulus, GPa").place(
                                            relx=0.5, 
                                            relwidth=1, 
                                            anchor="n",
                                            y=btnHeight*4)
                
        self.segYoung = tk.DoubleVar()
        entry_segYoung = tk.Label(
                            outputFrame, 
                            textvariable=self.segYoung)
        entry_segYoung.place(
                            relx=0.5, 
                            relwidth=1, 
                            anchor="n", 
                            y=btnHeight*5)



#%%#########################  HISTORYFRAME ####################################
        coldata = [
            {"text": "TEST_ID", "stretch": True},
            {"text": "DATE", "stretch": True},
            {"text": "TESTER", "stretch": True}
        ]

        # rowdata = [
        #     ('A0001', '2024/04/06 22:52:43', 'Isaiah'),
        #     ('A0002', '2024/04/06 22:54:43', 'Andrew'),
        #     ('A0003', '2024/04/06 22:57:43', 'Edwin')
        # ]



        self.tableView = Tableview(
                            historyFrame,
                            autofit=True,
                            coldata=coldata,
                            paginated=False,
                            searchable=True,
                            bootstyle='primary',
                            stripecolor=None,
                            delimiter=','
        )
        self.tableView.place(relwidth=1,relheight=1)
#%%#########################  Done FRAME   ####################################
        ttk.Button(
            doneFrame, 
            text="Exit Program", 
            command=self.__quit).place(
                                    relwidth=0.7, 
                                    relx=0.5, 
                                    rely=0.8, 
                                    anchor="s")
       
        # Bottom frame buttons
        ttk.Button(
            doneFrame, 
            text="Export .csv", 
            command=self.__exportCSV).place(
                                        relx=0.5, 
                                        relwidth=0.5, 
                                        anchor="ne")
        ttk.Button(
            doneFrame, 
            text="Export .pdf", 
            command=self.__exportPDF).place(
                                        relx=0.5, 
                                        relwidth=0.5, 
                                        anchor="nw")

#%%#########################  CHART FRAME  ####################################
        # Tensile test figure
        self.figTens, self.axTens = plt.subplots()
        self.line, = self.axTens.plot([], [], label='Data')
        self.axTens.set_title("Stress vs Strain")
        self.axTens.set_xlabel("Strain")
        self.axTens.set_ylabel("Stress, MPa")

        self.testCanvas = FigureCanvasTkAgg(self.figTens, chartFrame)
        self.testCanvas.get_tk_widget().place(
                                    relx=0.5,
                                    rely=0.5,
                                    anchor='center',
                                    relwidth=1,
                                    relheight=1)
#%%#########################  Func Defn    ####################################
    def __tensileTest(self):

        print("Tensile test initiated")
        GPIO.output(pin_motor,GPIO.HIGH)
        self.__update_plot()   # start the motor as the same time start plot real-time plotting
        messagebox.showinfo("Information", "Starting tensile testing")    
        
 
    def __get_shape(self,event):
        self.segShape = self.cbBox_typeSel.current()
        if (self.segShape == 0): # rectangle shape
            self.setvar("dimension1","segment length, mm:")
            self.setvar("dimension2","segment width, mm:")
            self.nty_dim2.configure(state='enable')
            self.labl_dim2.place(
                relx=0.5,
                rely=INPUT_LABEL_CBBOX,
                y=INPUT_LABEL_DIM2,
                relwidth=0.7,
                anchor="center")
            self.nty_dim2.place(
                relx=0.5,
                rely=INPUT_LABEL_CBBOX,            
                y=INPUT_ENTRY_DIM2,
                relwidth=0.7,
                anchor="center")

        elif (self.segShape == 1): # circular shape
            self.setvar("dimension1","segment radius, mm")
            self.nty_dim2.configure(state='disable')
            self.labl_dim2.place_forget()
            self.nty_dim2.place_forget()
            
        self.dim1.set(0.0)
        self.dim2.set(0.0)

        messagebox.showinfo("Information", "Shape updated!")
        
    def __confirm_dim(self):
        self.segShape = self.cbBox_typeSel.current()
                
        if (self.segShape == 0): # rectangle shape        
            area = self.dim1.get() * self.dim2.get()

        elif (self.segShape == 1): # circular shape            
            area = np.pi * self.dim1.get()**2

        rounded_area = round(area,4)
        self.segArea.set(rounded_area)        
        messagebox.showinfo("Information", "Dimension updated!")

        
    def __fake_datainput(self):
        fakeData = b"ABCIT_MECHATRONICS&ROBOTICS_PROGRAMEND"
        ser.write(fakeData)
        time.sleep(0.1)

    
        
    def __exportCSV(self):
        GPIO.output(pin_motor,GPIO.LOW)
        messagebox.showinfo("Information", "Export .CSV file")
        file_path = filedialog.asksaveasfilename(
                                            defaultextension=".csv", 
                                            filetypes=[("CSV files","*.csv")])
        if file_path:
            df = pd.DataFrame(data)
            df = df.transpose()
            column_label = ["Strain","Stress, MPa"]
            df.columns = column_label
            df.to_csv(file_path, index=False)
          
    def __exportPDF(self):
        GPIO.output(pin_motor,GPIO.LOW)
        messagebox.showinfo("Information", "Export .PDF file")
        file_path = filedialog.asksaveasfilename(
                                            defaultextension=".pdf", 
                                            filetypes=[("PDF files", "*.pdf")])
        if file_path:
            with PdfPages(file_path) as pdf:
                self.testCanvas.figure.savefig(pdf, format='pdf')
        
    def __quit(self):
        GPIO.output(pin_motor,GPIO.LOW)
        self.master.quit()
        self.master.destroy()
        
    def __update_plot(self):
        try:        
            self.__fake_datainput()
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
                                self.__data_concat()
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
                        self.axTens.set_xlim(0, 2*data_point)
                    else:
                        strainFlag = True
                        stress = np.append(stress,np.array([data_point]))
                        self.axTens.set_ylim(0, 2*data_point)
                        self.line.set_data(strain, stress)  
                        self.testCanvas.draw()
                        self.update()
                                
                    print("strain: ",strain,"\nstress: ",stress)
                    # update plot
    
                    self.after(5)
                    
                    # stop updating diagram if user pressed stop button
                    if stop_pressed:
                        self.__data_concat()
                        break
            
            elif Cmd_Byte == B:  # Emergency Stop engaged
                # GPIO.output(pin_motor,GPIO.LOW) # stop the motor
                self.__data_concat()
                messagebox.showinfo("Warning","System stops due to e-stop engagement")
            elif Cmd_Byte == C:  # Limit Switch engaged
                # GPIO.output(pin_motor,GPIO.LOW) # stop the motor
                self.__data_concat()
                messagebox.showinfo("Warning","System stops due to limit switch been triggered")
            print("enter nothing\n")
        except KeyboardInterrupt:  # stop the drawing due to interrupt (design for limit switch as well user interrupt)
            print("Interrupt from keyboard\n")
            ser.close()
    
    def __stop_plot(self):
        global stop_pressed
        stop_pressed = True
        # GPIO.output(pin_motor,GPIO.LOW)  # stop the motor
        messagebox.showinfo("Information","Process has been stopped")
        
    def __data_concat(self):
        global data
        # Organize data frame for exporting .csv
        data = np.concatenate(
            (strain.reshape(1,-1), stress.reshape(1,-1)), axis=0)
    
    
#%%#########################  Main Loop  ######################################
root = ttkbs.Window('flatly')
#%%#########################  Frame GEO    ####################################
SCREEN_WIDTH = root.winfo_screenwidth()
INPUT_FRAME_WIDTH = SCREEN_WIDTH * 250 / 800
OUTPUT_FRAME_WIDTH = SCREEN_WIDTH * 250 / 800
HISTORY_FRAME_WIDTH = SCREEN_WIDTH * 250 / 800
DONE_FRAME_WIDTH = SCREEN_WIDTH * 250 / 800
CHART_FRAME_WIDTH = SCREEN_WIDTH * 550 / 800

SCREEN_HEIGHT = root.winfo_screenheight() - 100
INPUT_FRAME_HEIGHT = SCREEN_HEIGHT * 180 / 500
OUTPUT_FRAME_HEIGHT = SCREEN_HEIGHT * 90 / 500
HISTORY_FRAME_HEIGHT = SCREEN_HEIGHT * 170 / 500
DONE_FRAME_HEIGHT = SCREEN_HEIGHT - (HISTORY_FRAME_HEIGHT
                                     +OUTPUT_FRAME_HEIGHT
                                     +INPUT_FRAME_HEIGHT)
CHART_FRAME_HEIGHT = SCREEN_HEIGHT

# Input frame widget geometry
INPUT_LABEL_CBBOX = 0.1
INPUT_CBBOX =  txtBoxHeight
INPUT_LABEL_DIM1 = 2*txtBoxHeight
INPUT_ENTRY_DIM1 = 3*txtBoxHeight
INPUT_LABEL_DIM2 = 4*txtBoxHeight
INPUT_ENTRY_DIM2 = 5*txtBoxHeight
INPUT_BTN_TEST = 0.75
INPUT_BTN_CNFM = -1.5*btnHeight
INPUT_BTN_STOP = 1.5*btnHeight
#%%#########################  GUI Init  #######################################   
app = __Tensile_Tester_Application(master = root)

root.title("BCIT_AUTOBOT")

root.mainloop()
ser.close()