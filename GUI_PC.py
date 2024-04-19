# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# 希望实现的功能：
# 1. 用户名管理系统（用于登录系统，并拥有修改用户名及密码的功能）
# 2. 用户登陆历史
# 3. 当前时间显示
# 4. 浏览以往数据（点击数据可plot到图上） - 2024/04/09 完成
# 5. 滑块控制抓手位置                    - 2024/04/18 完成
# 6. 用户控制PWM（或通过快中慢模式)
# 7. 显示当前PWM，用meter widget

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
# from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttkbs
from ttkbootstrap.tableview import Tableview
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import serial
import pandas as pd
# import RPi.GPIO as GPIO
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

# choose BaudRate
# UART_BAUD = 9600
# UART_BAUD = 600
# UART_BAUD = 4800  
# UART_BAUD = 19200
UART_BAUD = 115200 
COM_PORT = "COM8"
 
txtBoxHeight = 30
btnHeight = 22
NUM_DATA_POINT =  12
TEST_WITH_TMS = False

if TEST_WITH_TMS:
    # Create serial ports
    try:
        ser = serial.Serial(
            port = COM_PORT, 
            baudrate = UART_BAUD, 
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1) # used for RPi testing
        if ser.is_open:
            print("port connected")
    except IOError:
        print("Failed at setting port\n")



class __Tensile_Tester_Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.test_flag = False

        self.__GUI_setup()
        master.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}+0+0")
        
        if TEST_WITH_TMS:
            ser.reset_input_buffer()

#%%#########################  FRAME SETUP  ####################################
    def __GUI_setup(self):
        inputFrame = ttk.Frame(
            self.master,
            width=INPUT_FRAME_WIDTH, 
            height = INPUT_FRAME_HEIGHT, 
            style="secondary.TFrame"
            )        
        inputFrame.place(
            x=0,y=0,
            width=INPUT_FRAME_WIDTH,
            height=INPUT_FRAME_HEIGHT)

        outputFrame = ttk.Frame(
            self.master,
            width=OUTPUT_FRAME_WIDTH, 
            height = OUTPUT_FRAME_HEIGHT, 
            style="secondary.TFrame")
        outputFrame.place(
            x=0,
            y=INPUT_FRAME_HEIGHT)

        historyFrame = ttk.Frame(
            self.master,
            width=HISTORY_FRAME_WIDTH, 
            height=HISTORY_FRAME_HEIGHT, 
            style="secondary.TFrame")
        historyFrame.place(
            x=0,
            y=INPUT_FRAME_HEIGHT+OUTPUT_FRAME_HEIGHT)

        doneFrame = ttk.Frame(
            self.master,
            width=DONE_FRAME_WIDTH,
            height=DONE_FRAME_HEIGHT, 
            style="secondary.TFrame")
        doneFrame.place(
            x=0,
            y=INPUT_FRAME_HEIGHT+OUTPUT_FRAME_HEIGHT+HISTORY_FRAME_HEIGHT)

        chartFrame = ttk.Frame(
            self.master,
            width=CHART_FRAME_WIDTH, 
            height=CHART_FRAME_HEIGHT, 
            style="secondary.TFrame")
        chartFrame.place(
            x=INPUT_FRAME_WIDTH+TUNE_FRAME_WIDTH,
            y=0)
                
        tuneFrame = ttk.Frame(
            self.master,
            width=TUNE_FRAME_WIDTH, 
            height=TUNE_FRAME_HEIGHT, 
            style="dark.TFrame")
        tuneFrame.place(
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
                                relwidth=ITEM_RELWID,
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
                relwidth=ITEM_RELWID,
                anchor="center")
                
        ttk.Button(
            inputFrame, 
            text="Confirm dimension",
            command=self.__confirm_dim,
            style='success.TButton').place(
                relx=0.5,
                rely=INPUT_BTN_TEST,
                y=INPUT_BTN_CNFM,
                relwidth=ITEM_RELWID,
                anchor="center")
                
        stopBtn = ttk.Button(
            inputFrame, 
            text="Stop", 
            command=self.__stop_plot,
            style="danger.TButton")
        stopBtn.place(
            relx=0.5, 
            rely=INPUT_BTN_TEST, 
            y=INPUT_BTN_STOP,
            relwidth=ITEM_RELWID, 
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
            relwidth=ITEM_RELWID,
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
            relwidth=ITEM_RELWID/2,
            anchor="e")
        
        self.dim3 = tk.DoubleVar()
        self.dim3.set(0.0)
        self.nty_dim3 = ttk.Entry(
                        inputFrame, 
                        textvariable=self.dim3,
                        justify='center',
                        style="danger.TEntry")
        self.nty_dim3.place(
            relx=0.5,
            rely=INPUT_LABEL_CBBOX,
            y=INPUT_ENTRY_DIM3,
            relwidth=ITEM_RELWID/2,
            anchor="w")  
             
        # Label in input frame        
        ttkbs.Label(
            inputFrame,
            text="select segment shape",
            style='inverse-secondary',
            justify='center').place(
                                    relx=0.5,
                                    rely=INPUT_LABEL_CBBOX,
                                    relwidth=ITEM_RELWID,
                                    anchor="center")
        
        self.labl_dim1 = ttk.Label(
                        inputFrame, 
                        textvariable="dimension1",
                        style='inverse-secondary')
        self.labl_dim1.place(
            relx=0.5,
            rely=INPUT_LABEL_CBBOX,
            y=INPUT_LABEL_DIM1,
            relwidth=ITEM_RELWID,
            anchor="center")
        
        self.labl_dim2 = ttk.Label(
                        inputFrame, 
                        textvariable="dimension2",
                        style='inverse-secondary')
        self.labl_dim2.place(
            relx=0.5,
            rely=INPUT_LABEL_CBBOX,
            y=INPUT_LABEL_DIM2,
            relwidth=ITEM_RELWID/2,
            anchor="e")

        self.labl_dim3 = ttk.Label(
                        inputFrame, 
                        textvariable="dimension3",
                        style='inverse-secondary')
        self.labl_dim3.place(
            relx=0.5,
            rely=INPUT_LABEL_CBBOX,
            y=INPUT_LABEL_DIM3,
            relwidth=ITEM_RELWID/2,
            anchor="w")


        self.setvar("dimension1","segment length, mm:")
        self.setvar("dimension2","segment width, mm:")
        self.setvar("dimension3","segment thickness, mm:")
        
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
        #     ('A0004', '2024/04/06 22:54:43', 'Mingqi'),
        #     ('A0005', '2024/04/06 22:54:43', 'Ace')
        # ]

        self.file_names = []
        self.rowdata = []
        csv_count = 0
        for file in os.listdir(self.backup_path):
            if file.endswith(".csv"):
                csv_count += 1
                file = os.path.splitext(file)[0]
                print("found files: ",file)
                self.file_names.append(file)
                file_info = file.split("_")
                file_info[1] = datetime.fromtimestamp(int(file_info[1]))
                self.rowdata.append((file_info[0],file_info[1],file_info[2]))
                self.csv_index = int(file_info[0].split("A")[1])
                # print("csv index is", self.csv_index)
        print("Total {} csv files found!".format(csv_count))
        self.csv_index += 1     # add one for next file saved

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
            command=self.__quit,
            style='danger').place(
                                    relwidth=0.7, 
                                    relx=0.5, 
                                    rely=0.8, 
                                    anchor="s")
       
        # Bottom frame buttons
        ttk.Button(
            doneFrame, 
            text="Export .csv", 
            command=self.__exportCSV,
            style='success').place(
                                        relx=0.5, 
                                        relwidth=0.5, 
                                        anchor="ne")
        ttk.Button(
            doneFrame, 
            text="Export .pdf", 
            command=self.__exportPDF,
            style='success').place(
                                        relx=0.5, 
                                        relwidth=0.5, 
                                        anchor="nw")


#%%#########################  TUNE FRAME  ####################################

        self.panedwindow = ttk.Panedwindow(tuneFrame, 
                                      orient=tk.VERTICAL,
                                      style='danger')
        self.panedwindow.place(relx=0.5,
                          rely=PANWINDOW_RELY,
                          relheight=PANWINDOW_RELHEIGHT,
                          relwidth=0.5,
                          anchor='center'
                          )
        
        panTop = ttk.Frame(self.panedwindow,style='dark.TFrame')
        panBot = ttk.Frame(self.panedwindow,style='dark.TFrame')

        self.panedwindow.add(panTop)
        self.panedwindow.add(panBot)
        
        self.panedwindow.bind("<ButtonRelease-1>", self.__update_pos)
        panTop.bind("<Configure>",self.__label_travel)

        self.tunePos = tk.IntVar()
        self.tuneLable = tk.DoubleVar()
        self.tuneLable = ttk.Label(
            tuneFrame,
            textvariable=self.tunePos,
            style='inverse-dark')        
        self.tuneLable.place(relx=0.5,
                             rely=0.05,
                             anchor='center')
        
        # Radio buttons in tune frame
        ttk.Radiobutton(tuneFrame,
                        style='success-toolbutton',
                        text='Slow').place(relwidth=0.33,
                                           rely=1,
                                           relx=0,
                                           anchor='sw')
        
        ttk.Radiobutton(tuneFrame,
                        style='warning-toolbutton',
                        text='Medium').place(relwidth=0.33,
                                           rely=1,
                                           relx=0.33,
                                           anchor='sw')
        
        ttk.Radiobutton(tuneFrame,
                        style='danger-toolbutton',
                        text='Fast').place(relwidth=0.33,
                                           rely=1,
                                           relx=0.66,
                                           anchor='sw')
        

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
    def __label_travel(self,event):
        self.posSash = self.panedwindow.sashpos(0)
        # print(self.posSash)
        self.panFullRange = SCREEN_HEIGHT * PANWINDOW_RELHEIGHT
        posTensile = 100 - (self.posSash * 100 / self.panFullRange)
        # print(posTensile)
        self.int_tunePos = int(posTensile)
        self.tunePos.set(self.int_tunePos)
        posPercent = self.posSash / SCREEN_HEIGHT
        self.tuneLable.place(y=self.panFullRange*2*(PANWINDOW_RELY+0.15),
                             relx=0.5,
                             rely=posPercent,
                             anchor='center')
    
    def __update_pos(self,event):
        if not self.test_flag:
            if TEST_WITH_TMS:
                ser.write(self.int_tunePos)
        else:
            self.posSash = self.panedwindow.sashpos(0,200)
        
        


    def __tensileTest(self):
        # messagebox.showinfo("Information", "Starting tensile testing") 
        self.strain=[]
        self.stress=[]

        self.test_flag = True

        if not TEST_WITH_TMS:
            self.__fake_datainput() 
        print("Tensile test initiated")
        self.stop_pressed = False # reset software stop status 

        self.__clear_figure()

        if TEST_WITH_TMS:
            while(ser.in_waiting):
                self.__xq_cmd() 
        else:
            self.__xq_cmd()

        self.__data_concat()
        if len(self.data) != 0:    
            self.__backup_data()
        else:
            messagebox.showinfo("Information","Empty dataset")
        messagebox.showinfo("Information", "Done tensile testing")
        self.test_flag = False

    def __clear_figure(self):
        self.figTens.legends = []
        self.axTens.cla()

    def __get_shape(self,event):
        self.segShape = self.cbBox_typeSel.current()
        if (self.segShape == 0): # rectangle shape
            self.setvar("dimension2","segment width, mm:")
            self.setvar("dimension3","segment thickness, mm:")
            self.nty_dim2.configure(state='enable')
            self.nty_dim3.configure(state='enable')
            self.labl_dim2.place(
                relx=0.5,
                rely=INPUT_LABEL_CBBOX,
                y=INPUT_LABEL_DIM2,
                relwidth=ITEM_RELWID/2,
                anchor="e")
            self.nty_dim2.place(
                relx=0.5,
                rely=INPUT_LABEL_CBBOX,            
                y=INPUT_ENTRY_DIM2,
                relwidth=ITEM_RELWID/2,
                anchor="e")
            self.labl_dim3.place(
                relx=0.5,
                rely=INPUT_LABEL_CBBOX,
                y=INPUT_LABEL_DIM3,
                relwidth=ITEM_RELWID/2,
                anchor="w")
            self.nty_dim3.place(
                relx=0.5,
                rely=INPUT_LABEL_CBBOX,            
                y=INPUT_ENTRY_DIM3,
                relwidth=ITEM_RELWID/2,
                anchor="w")
            

        elif (self.segShape == 1): # circular shape
            self.setvar("dimension2","segment diamter, mm")            
            self.labl_dim2.place(
                relx=0.5,
                rely=INPUT_LABEL_CBBOX,
                y=INPUT_LABEL_DIM2,
                relwidth=ITEM_RELWID,
                anchor="center")
            self.nty_dim2.place(
                relx=0.5,
                rely=INPUT_LABEL_CBBOX,            
                y=INPUT_ENTRY_DIM2,
                relwidth=ITEM_RELWID,
                anchor="center")
            self.nty_dim3.configure(state='disable')
            self.labl_dim3.place_forget()
            self.nty_dim3.place_forget()
            
        self.dim1.set(0.0)
        self.dim2.set(0.0)

        messagebox.showinfo("Information", "Shape updated!")
        
    def __confirm_dim(self):
        self.segShape = self.cbBox_typeSel.current()
                
        if (self.segShape == 0): # rectangle shape        
            area = self.dim2.get() * self.dim3.get()

        elif (self.segShape == 1): # circular shape            
            area = np.pi * (0.5*self.dim2.get())**2

        rounded_area = round(area,4)
        self.segArea.set(rounded_area)        
        messagebox.showinfo("Information", "Dimension updated!")
     
    def __fake_datainput(self):
        # if TEST_WITH_TMS:
        #     self.fakeData = b"ABCIT_MECHATRONICS&ROBOTICS_PROGRAMEND"
        #     ser.write(self.fakeData)
        # else:
        #     self.fakeData = "A112223243536374849596876988995END"

        self.fakeData = "A112223243536374849596876988995END"
        time.sleep(0.1)
    
    def __xq_cmd(self):  
        try:         
            print("entered __xq_cmd")   
            if TEST_WITH_TMS: 
                Cmd_Byte = (ser.read()) # Obtain Cmd_Byte
                print('\ncommand: ', Cmd_Byte, ' type:', type(Cmd_Byte))
                # print("decoded string:", Cmd_Byte.decode())
                Cmd_Byte = int.from_bytes(Cmd_Byte, byteorder='little')
                print("int from byte: ", Cmd_Byte)
            
            else:
                count = 0
                Cmd_Byte = self.fakeData[count]  # use in PC debug                
                print("int from byte: ", Cmd_Byte)

            # Decode the obtained data
            # Look Up Table for decoding
            #|----------------------------------------------------------------|
            #| Cmd_Byte |   Byte Size  |              Command                 |
            #|----------|--------------|--------------------------------------|
            #|    A     |    1+vary    |  Encoder, LVDT data coming from TMS  |
            #|    B     |       1      |   Emergency Stop engaged, sys stops  |
            #|    C     |       1      |    Limit Switch engaged, sys stops   |
            #
            
            if TEST_WITH_TMS:      # testing with TMS
                if Cmd_Byte == A:    # data transmission command 
                    self.__get_data()
                    return 1   
                elif Cmd_Byte == B:  # Emergency Stop engaged
                    messagebox.showinfo("Warning","System stops due to e-stop engagement")
                    return 0
                    
                elif Cmd_Byte == C:  # Limit Switch engaged
                    messagebox.showinfo("Warning","System stops due to limit switch been triggered")
                    return 0
                else:
                    print("enter nothing\n")
            else:           # testing without TMS
                if Cmd_Byte == 'A':    
                    self.__get_data()
                    return 1   
                elif Cmd_Byte == 'B':  # Emergency Stop engaged
                    messagebox.showinfo("Warning","System stops due to e-stop engagement")
                    return 0
                    
                elif Cmd_Byte == 'C':  # Limit Switch engaged
                    messagebox.showinfo("Warning","System stops due to limit switch been triggered")
                    return 0
                else:
                    print("enter nothing\n")
        except KeyboardInterrupt:
            print("Interrupt from keyboard\n")
            ser.close()
    
    def __get_data(self):

        self.line, = self.axTens.plot([], [], label='Current Test')
        self.figTens.legend()
        new_dataIn = 0
        count = 0
        data_size = NUM_DATA_POINT * 2
        xlim = 0
        ylim = 0
        print("entered Cmd_Byte == A")
        strainFlag = True   # To indicate incoming strain or stress data

        
        while count<data_size:    
            if TEST_WITH_TMS:    
                new_dataIn = (ser.read(4))    # Obtain serial data from TMS
                print("Reading byte: ", new_dataIn)
                new_dataIn = int.from_bytes(new_dataIn,byteorder='little')
                print("Converting int: ", new_dataIn)
            else:
                count += 1
                new_dataIn = int(self.fakeData[count])
                print("Converting int: ", new_dataIn)

            # Append decoded data into array
            if strainFlag == True:
                strainFlag = False
                self.strain.append(new_dataIn)
                if new_dataIn>xlim:
                    self.axTens.set_xlim(0, 2*new_dataIn)
            else:
                strainFlag = True
                self.stress.append(new_dataIn)
                if new_dataIn>ylim:
                    self.axTens.set_ylim(0, 2*new_dataIn)
                self.line.set_data(self.strain, self.stress)
                self.testCanvas.draw()
                root.update()

            # stop updating diagram if user pressed stop button
            if self.stop_pressed:
                self.__data_concat()
                break
          
    def __stop_plot(self):
        self.stop_pressed = True
        messagebox.showinfo("Information","Process has been stopped")
        
    def __data_concat(self):
        self.stress = np.array(self.stress)
        self.strain = np.array(self.strain)

        # Organize data frame for exporting .csv
        self.data = np.concatenate(
            (self.strain.reshape(1,-1), self.stress.reshape(1,-1)), axis=0)

    def __backup_data(self):    
        print("dataset path is:", self.backup_path)
        dt_object = datetime.now()
        timestamp = int(datetime.timestamp(dt_object))
        backupDate = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        
        if (self.csv_index<10):
                csv_id = "A000{}".format(self.csv_index)
        elif (self.csv_index<100):
            csv_id = "A00{}".format(self.csv_index)
        elif (self.csv_index<1000):
            csv_id = "A0{}".format(self.csv_index)
        else:
            csv_id = "A{}".format(self.csv_index)
        
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
            self.csv_index += 1

            self.tableView.insert_row('end',[csv_id,backupDate,userID])
            self.tableView.load_table_data()     

    def __plot_history(self,event):
        messagebox.showinfo("Information","entered plot history function")
        selected_index = self.tv.index(self.tv.selection()[0])  # index from 0
        history_file = self.file_names[selected_index] + ".csv"
        print(selected_index)
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
        self.master.quit()
        self.master.destroy()
        

 

#%%#########################  Main Loop  ######################################
root = ttkbs.Window('flatly')
root.title("BCIT_AUTOBOT")

#%%#########################  Frame GEO    ####################################
SCREEN_WIDTH = root.winfo_screenwidth()
INPUT_FRAME_WIDTH = SCREEN_WIDTH * 200 / 800
OUTPUT_FRAME_WIDTH = INPUT_FRAME_WIDTH
HISTORY_FRAME_WIDTH = INPUT_FRAME_WIDTH
DONE_FRAME_WIDTH = INPUT_FRAME_WIDTH
TUNE_FRAME_WIDTH = SCREEN_WIDTH * 150 / 800
CHART_FRAME_WIDTH = SCREEN_WIDTH - (INPUT_FRAME_WIDTH
                                    +TUNE_FRAME_WIDTH)

SCREEN_HEIGHT = root.winfo_screenheight() - 100
INPUT_FRAME_HEIGHT = SCREEN_HEIGHT * 200 / 500
OUTPUT_FRAME_HEIGHT = SCREEN_HEIGHT * 70 / 500
HISTORY_FRAME_HEIGHT = SCREEN_HEIGHT * 170 / 500
DONE_FRAME_HEIGHT = SCREEN_HEIGHT - (HISTORY_FRAME_HEIGHT
                                     +OUTPUT_FRAME_HEIGHT
                                     +INPUT_FRAME_HEIGHT)
CHART_FRAME_HEIGHT = SCREEN_HEIGHT
TUNE_FRAME_HEIGHT = SCREEN_HEIGHT

# Input frame widget geometry
INPUT_LABEL_CBBOX = 0.1
INPUT_CBBOX =  txtBoxHeight
INPUT_LABEL_DIM1 = 2*txtBoxHeight
INPUT_ENTRY_DIM1 = 3*txtBoxHeight
INPUT_LABEL_DIM2 = 4*txtBoxHeight
INPUT_ENTRY_DIM2 = 5*txtBoxHeight
INPUT_LABEL_DIM3 = 4*txtBoxHeight
INPUT_ENTRY_DIM3 = 5*txtBoxHeight
INPUT_BTN_TEST = 0.75
INPUT_BTN_CNFM = -1.5*btnHeight
INPUT_BTN_STOP = 1.5*btnHeight
ITEM_RELWID = 0.7

# Other
PANWINDOW_RELHEIGHT = 0.3
PANWINDOW_RELY = 0.6
#%%#########################  GUI Init  #######################################   
app = __Tensile_Tester_Application(master = root)
winds = ttkbs.Toplevel(root)
winds.mainloop()


root.mainloop()
if TEST_WITH_TMS:
    ser.close()