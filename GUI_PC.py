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
#import RPi.GPIO as GPIO
import time
from datetime import datetime
import pathlib
import os
   
A = 0x41
B = 0x42
C = 0x43
D = 0x44
E = 0x45
N = 0x4E        

# # GPIO pin configuration
# GPIO.setmode(GPIO.BCM)
# pin_motor = 23
# GPIO.setup(pin_motor,GPIO.OUT)
# GPIO.output(pin_motor,GPIO.LOW)
# GPIO.setwarnings(False)

Uart_Baud = 115200  
txtBoxHeight = 30
btnHeight = 22
stop_pressed = False
test_in_PC = True

# Create serial port
# ser = serial.Serial('/dev/ttyAMA0', Uart_Baud, timeout=1) # used for RPi testing
# if ser.is_open:
#     print("port connected")




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
        self.backup_path =  pathlib.Path(__file__).parent / 'dataset'
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

        self.file_names = []
        self.rowdata = []
        self.csv_count = 0
        for file in os.listdir(self.backup_path):
            if file.endswith(".csv"):
                self.csv_count += 1
                file = os.path.splitext(file)[0]
                print("found files: ",file)
                self.file_names.append(file)
                file_info = file.split("_")
                file_info[1] = datetime.fromtimestamp(int(file_info[1]))
                self.rowdata.append((file_info[0],file_info[1],file_info[2]))

        self.tableView = Tableview(
                            historyFrame,
                            autofit=True,
                            coldata=coldata,
                            rowdata=self.rowdata,
                            paginated=False,
                            searchable=True,
                            bootstyle='primary',
                            stripecolor=None,
                            delimiter=','
        )
        self.tableView.place(relwidth=1,relheight=1)

        self.tv = self.tableView.view
        self.tv.bind("<Double-1>", self.__plot_history)
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
        self.__fake_datainput()

        messagebox.showinfo("Information", "Starting tensile testing")  
        self.stop_pressed = False # reset software stop status 
        self.__clear_figure()
        print("Tensile test initiated")
        # GPIO.output(pin_motor,GPIO.HIGH)
        self.__xq_cmd()   # start the motor as the same time start plot real-time plotting
        
        self.__backup_data()
        messagebox.showinfo("Information", "Done tensile testing")

    def __clear_figure(self):
        self.figTens.legends = []
        self.axTens.cla()

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
        # self.fakeData = b"ABCIT_MECHATRONICS&ROBOTICS_PROGRAMEND"
        # ser.write(fakeData)
        self.fakeData = "A112223243536374849596876988995"

        time.sleep(0.1)
    
    def __xq_cmd(self):
        try:        
            
            print("entered update plot")
           
            count = 0
            # Cmd_Byte = ser.read().decode()  # Obtain Cmd_Byte
            Cmd_Byte = self.fakeData[count]  # use in PC debug

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
                self.__get_data()     
            elif Cmd_Byte == 'B':  # Emergency Stop engaged
                # GPIO.output(pin_motor,GPIO.LOW) # stop the motor
                self.__data_concat()
                messagebox.showinfo("Warning","System stops due to e-stop engagement")
            elif Cmd_Byte == 'C':  # Limit Switch engaged
                # GPIO.output(pin_motor,GPIO.LOW) # stop the motor
                self.__data_concat()
                messagebox.showinfo("Warning","System stops due to limit switch been triggered")
            else:
                print("enter nothing\n")
            
        except KeyboardInterrupt:  # stop the drawing due to interrupt (design for limit switch as well user interrupt)
            print("Interrupt from keyboard\n")
            # ser.close()
    
    def __get_data(self):

                self.strain=[]
                self.stress=[]
                self.line, = self.axTens.plot([], [], label='Current Test')
                self.figTens.legend()
                new_dataIn = 0
                count = 1
                data_point = 8
                data_size = data_point * 2
                print("entered Cmd_Byte == A")
                strainFlag = True   # To indicate incoming strain or stress data
                
                while (count<=data_size):          
                    new_dataIn = self.fakeData[count]    # Obtain serial data from TMS
                    print("Reading byte: ", new_dataIn)

                    new_dataIn = int(new_dataIn)
                    # Append decoded data into array
                    if strainFlag == True:
                        strainFlag = False
                        self.strain.append(new_dataIn)
                        self.axTens.set_xlim(0, 2*new_dataIn)
                    else:
                        strainFlag = True
                        self.stress.append(new_dataIn)
                        self.axTens.set_ylim(0, 2*new_dataIn)
                        self.line.set_data(self.strain, self.stress)
                        self.testCanvas.draw()
                        root.update()
                        
                    # stop updating diagram if user pressed stop button
                    if self.stop_pressed:
                        self.__data_concat()
                        break
                    count += 1 
                self.__data_concat()

                       
    def __stop_plot(self):
        self.stop_pressed = True
        # GPIO.output(pin_motor,GPIO.LOW)  # stop the motor
        messagebox.showinfo("Information","Process has been stopped")
        
    def __data_concat(self):
        # Organize data frame for exporting .csv
        self.stress = np.array(self.stress)
        self.strain = np.array(self.strain)
        self.data = np.concatenate(
            (self.strain.reshape(1,-1), self.stress.reshape(1,-1)), axis=0)

    def __backup_data(self):    
        print("dataset path is:", self.backup_path)
        dt_object = datetime.now()
        timestamp = int(datetime.timestamp(dt_object))
        backupDate = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        if (self.csv_count<10):
                csv_id = "A000{}".format(self.csv_count)
        elif (self.csv_count<100):
            csv_id = "A00{}".format(self.csv_count)
        elif (self.csv_count<1000):
            csv_id = "A0{}".format(self.csv_count)
        else:
            csv_id = "A{}".format(self.csv_count)
        
        ts = str(timestamp)
        userID = "Mingqi"
        
        self.csv_name = csv_id + "_" + ts + "_" + userID 
        backup_name = self.csv_name + ".csv"

        file_path = self.backup_path / backup_name
        # file_path = self.backup_path / 'A0005_20240407031050_Mingqi.csv'
        if file_path:
            self.df = pd.DataFrame(self.data)
            self.df = self.df.transpose()
            column_label = ["Strain","Stress, MPa"]
            self.df.columns = column_label
            self.df.to_csv(file_path, index=False)
            self.file_names.append(self.csv_name)
            self.csv_count += 1

            self.tableView.insert_row('end',[csv_id,backupDate,userID])
            self.tableView.load_table_data()     

    def __plot_history(self,event):
        messagebox.showinfo("Information","entered plot history function")
        selected_index = self.tv.index(self.tv.selection()[0])  # index from 0
        history_file = self.file_names[selected_index] + ".csv"
        history_path = pathlib.Path(__file__).parent / 'dataset' / history_file
        history_data = self.__read_csv_file(history_path)

        history_strain, history_stress = zip(*history_data)
        print("strain: \n",history_strain)
        print("stress: \n",history_stress)
        selectLabel = "ID: " + history_file.split('_')[0]
        self.axTens.plot(history_strain,history_stress, label=selectLabel)
        self.figTens.legend()
        self.testCanvas.draw()
        root.update()

        root.after(5)

    def __read_csv_file(self,filename):
    # Read the CSV file into a DataFrame
        df = pd.read_csv(filename)
        # Convert the DataFrame to a list of lists
        data = df.values.tolist()
        return data   
        
    def __exportCSV(self):
        # GPIO.output(pin_motor,GPIO.LOW)
        messagebox.showinfo("Information", "Export .CSV file")
        file_path = filedialog.asksaveasfilename(
                                            defaultextension=".csv", 
                                            filetypes=[("CSV files","*.csv")])
        if file_path:
            # df = pd.DataFrame(self.data)
            # df = df.transpose()
            # column_label = ["Strain","Stress, MPa"]
            # df.columns = column_label
            self.df.to_csv(file_path, index=False)
          
    def __exportPDF(self):
        # GPIO.output(pin_motor,GPIO.LOW)
        messagebox.showinfo("Information", "Export .PDF file")
        file_path = filedialog.asksaveasfilename(
                                            defaultextension=".pdf", 
                                            filetypes=[("PDF files", "*.pdf")])
        if file_path:
            with PdfPages(file_path) as pdf:
                self.testCanvas.figure.savefig(pdf, format='pdf')
        
    def __quit(self):
        # GPIO.output(pin_motor,GPIO.LOW)
        self.master.quit()
        self.master.destroy()
        

 
    
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
# ser.close()