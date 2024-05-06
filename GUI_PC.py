# -*- coding: utf-8 -*-

# BCIT Mechatronics & Robotics Capstone - Tensile Tester
# Author: Mingqi Li
# Date: 2024/04/25
# Purpose: A GUI to control and obtain information from the tensile tester

# 希望实现的功能：
#  1. 用户名管理系统（用于登录系统，并拥有修改用户名及密码的功能） - 方案废弃
#  2. 用户登陆历史                        - 方案废弃
#  3. 当前时间显示                        - 方案废弃
#  4. 浏览以往数据（点击数据可plot到图上）  - 2024/04/09 完成
#  5. 滑块控制抓手位置                    - 2024/04/18 完成
#  6. 用户控制PWM（或通过快中慢模式)       - 2024/04/20 完成
#  7. 显示当前Force，用meter widget       - 2024/04/25 完成       
#  8. 启动校准模式                        - 2024/04/20 完成
#  9. 检查所需文件夹并创建                 - 2024/04/20 完成
# 10. 创建简易用户名登陆，用于backup data  - 2024/04/25 完成（NEW）

# conda install numpy
# pip install ttkbootstrap
# conda install matplotlib
# conda install pyserial
# conda install pandas


import tkinter as tk
from tkinter import messagebox, filedialog, ttk
# from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttkbs
from ttkbootstrap.tableview import Tableview 
from ttkbootstrap.toast import ToastNotification
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
TEST_WITH_TMS = True

## MECH PROPERTY
NM_PER_COUNT = 0.093612752          # lead screw moves per 1 encoder count
MM_PER_COUNT = 0.000331925          # lead screw moves per 1 encoder count
COUNT_PER_NM = 10.68230524          # count accumulation per 1 nm movement
MAX_COUNT = 6719170                 # default max count (not accurate, only used when user not want to calibrate)
ADC_BIT = 12                        # ADC Bit size for differential mode
ADC_N_MAX = 2**ADC_BIT              # number of steps for ADC

LOAD_CELL_CAP = 4900                # load cell capacity in kN
MOVING_AVG_NUM = 3                  # (desired) num of points to moving avg

if TEST_WITH_TMS:
    V_LSB_MV = 2820/ADC_N_MAX       # V_LSB in mV
    GRAVITY = 9.80665               # g in N/kg
    LDVT_CONST = 0.2                  # in kg/mV
    LVDT_NEWTON_PER_MV = GRAVITY * LDVT_CONST    # in N/mV
    CRITICAL_FORCE = 0.9*LOAD_CELL_CAP  # 90% of maximum capacity of load cell
    HIGH_FORCE = 0.6*LOAD_CELL_CAP    # 60% of maximum capacity of load cell
    READ_SIZE = 3
    NUM_DATA_POINT =  1
else:
    V_LSB_MV = 3300000/ADC_N_MAX    # V_LSB in mV
    LVDT_NEWTON_PER_MV = 0.01580558974    # LVDT output voltage per Newton
    CRITICAL_FORCE = 0.1*LOAD_CELL_CAP  # 90% of maximum capacity of load cell
    HIGH_FORCE = 0.05*LOAD_CELL_CAP    # 60% of maximum capacity of load cell
    READ_SIZE = 4
    NUM_DATA_POINT =  1
    

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
        self.login_userID = 'Jesus'
        self.test_flag = False
        self.xlim = 0
        self.ylim = 0
        self.csv_index = 0
        self.needed_file = ['asset','user','dataset']
        self.__check_or_create_folder()

        self.__GUI_setup()
        master.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}+0+0")
        
        if TEST_WITH_TMS:
            ser.reset_input_buffer()

        image_files = {
            'Ace_Ha':'Ace_Icon.png'
        }

        self.photoimages = []
        imgpath = pathlib.Path(__file__).parent / 'asset'
        for key, val in image_files.items():
            _path = imgpath / val
            self.photoimages.append(ttkbs.PhotoImage(name=key, file=_path))
        
#%%#########################  FUNCTION DEF  ####################################
    # Purpose: to set up all widgets of the GUI
    # 
    # | Component | InputFrame | OutputFrame | HistoryFrame | DoneFrame | TuneFrame | ChartFrame | 
    # |  Button   |      
    def __GUI_setup(self):
        
        #### Input Frame ###
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

        #### Output Frame ###
        outputFrame = ttk.Frame(
            self.master,
            width=OUTPUT_FRAME_WIDTH, 
            height = OUTPUT_FRAME_HEIGHT, 
            style="secondary.TFrame")
        outputFrame.place(
            x=0,
            y=INPUT_FRAME_HEIGHT)
        
        #### History Frame ###
        historyFrame = ttk.Frame(
            self.master,
            width=HISTORY_FRAME_WIDTH, 
            height=HISTORY_FRAME_HEIGHT, 
            style="secondary.TFrame")
        historyFrame.place(
            x=0,
            y=INPUT_FRAME_HEIGHT+OUTPUT_FRAME_HEIGHT)
        
        #### Output Frame ###
        doneFrame = ttk.Frame(
            self.master,
            width=DONE_FRAME_WIDTH,
            height=DONE_FRAME_HEIGHT, 
            style="secondary.TFrame")
        doneFrame.place(
            x=0,
            y=INPUT_FRAME_HEIGHT+OUTPUT_FRAME_HEIGHT+HISTORY_FRAME_HEIGHT)
        
        #### Chart Frame ###
        chartFrame = ttk.Frame(
            self.master,
            width=CHART_FRAME_WIDTH, 
            height=CHART_FRAME_HEIGHT, 
            style="secondary.TFrame")
        chartFrame.place(
            x=INPUT_FRAME_WIDTH+TUNE_FRAME_WIDTH,
            y=0)
               
        #### Tune Frame ###         
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
        
        ttk.Button(     # calibration button
            inputFrame, 
            text="Calibration",
            command=self.__calibration_info,
            style='warning.TButton').place(
                relx=0.5,
                rely=INPUT_BTN_TEST,
                y=INPUT_BTN_CALI,
                relwidth=ITEM_RELWID,
                anchor="center")
        
        self.testbtn = ttk.Button(     # tensile test button
            inputFrame, 
            text="Tensile Test",
            command=self.__tensileTest,
            style='primary.TButton',
            state='disable')
        self.testbtn.place(
                relx=0.5,
                rely=INPUT_BTN_TEST,
                relwidth=ITEM_RELWID,
                anchor="center")
                
        self.dimbtn = ttk.Button(     # confirm dimension button
            inputFrame, 
            text="Confirm dimension",
            command=self.__confirm_dim,
            style='success.TButton',
            state='disable')
        self.dimbtn.place(
                relx=0.5,
                rely=INPUT_BTN_TEST,
                y=INPUT_BTN_CNFM,
                relwidth=ITEM_RELWID,
                anchor="center")
                
        ttk.Button(     # stop button
            inputFrame, 
            text="Stop", 
            command=self.__stop_plot,
            style="danger.TButton").place(
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
        ttkbs.Label(        # selet segment shape label
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

        tk.Label(       # "Segment Area, mm^2" label
            outputFrame, 
            text="Segment Area, mm^2",
            justify='center').place(
                                    relx=0.5, 
                                    relwidth=1, 
                                    anchor="n")
                
        self.segArea = tk.DoubleVar()
        tk.Label(       # segment area label
                outputFrame, 
                textvariable=self.segArea,
                justify='center').place(
                    relx=0.5, 
                    relwidth=1, 
                    anchor="n", 
                    y=btnHeight)

        tk.Label(       # "Ultimate Stress, MPa" label
            outputFrame, 
            text="Ultimate Stress, MPa").place(
                                            relx=0.5, 
                                            relwidth=1, 
                                            anchor="n", 
                                            y=btnHeight*2)
                
        self.segUltSt = tk.DoubleVar()
        tk.Label(       # Ultimate Stress value label
                outputFrame, 
                textvariable=self.segUltSt).place(
                relx=0.5, 
                relwidth=1, 
                anchor="n", 
                y=btnHeight*3)
        
        # tk.Label(       # "Young's Modulus, GPa" label
        #     outputFrame, 
        #     text="Young's Modulus, GPa").place(
        #                                     relx=0.5, 
        #                                     relwidth=1, 
        #                                     anchor="n",
        #                                     y=btnHeight*4)
                
        # self.segYoung = tk.DoubleVar()
        # tk.Label(       # Young's Modulus value label
        #         outputFrame, 
        #         textvariable=self.segYoung).place(
        #         relx=0.5, 
        #         relwidth=1, 
        #         anchor="n", 
        #         y=btnHeight*5)

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
                            autoalign=True,
                            coldata=coldata,
                            rowdata=self.rowdata,
                            paginated=True,
                            searchable=True,
                            bootstyle='primary',
                            stripecolor=None,
                            delimiter=','
        )
        self.tableView.place(relwidth=1,relheight=1)

        self.tv = self.tableView.view
        self.tv.bind("<Double-1>", self.__plot_history)
#%%#########################  Done FRAME   ####################################
        ttk.Button(     # Exit button
            doneFrame, 
            text="Exit Program", 
            command=self.__quit,
            style='danger').place(
                                    relwidth=0.7, 
                                    relx=0.5, 
                                    rely=0.8, 
                                    anchor="s")
       
        # Bottom frame buttons
        ttk.Button(     # Export CSV button
            doneFrame, 
            text="Export .csv", 
            command=self.__exportCSV,
            style='success').place(
                                        relx=0.5, 
                                        rely=0.1,
                                        relwidth=0.5, 
                                        anchor="ne")
        ttk.Button(     # Export PDF button
            doneFrame, 
            text="Export .pdf", 
            command=self.__exportPDF,
            style='success').place(
                                        relx=0.5, 
                                        rely=0.1,
                                        relwidth=0.5, 
                                        anchor="nw")


#%%#########################  TUNE FRAME  ####################################
        for val in [SEPERATOR_TOP_RELY,
                    SEPERATOR_FORCE_TOP_RELY,
                    SEPERATOR_FORCE_BOT_RELY,
                    SEPERATOR_MID_RELY,
                    SEPERATOR_BOT_RELY]:
            ttkbs.Separator(
                master=tuneFrame,
                orient='horizontal'
                ).place(relx=0.5,
                        rely=val,
                        relwidth=1,
                        anchor='center')
        
        label_dir = {'  force indicator  ':SEPERATOR_TOP_RELY,
                     '  AutoBot  ':SEPERATOR_MID_RELY,
                     '  move gripper  ':SEPERATOR_BOT_RELY}
        for key,val in label_dir.items():
            ttkbs.Label(
                master=tuneFrame,
                text=key,
                style='inverse-dark',
                justify='center'
            ).place(
                relx=0.5,
                rely=val,
                anchor='center')

        self.meter = ttkbs.Meter(
                    master=tuneFrame,
                    metersize=230,
                    amountused=0,
                    amounttotal=4900,
                    stripethickness = 3,
                    textright="N",
                    metertype="semi",
                    subtext="max: 4900N",
                    interactive=False,
                    padding=20,
                    bootstyle='dark'
                )
        
        self.meter.place(relx=0.5,
                         rely=0.25,
                         anchor='center')
        
        # self.panedwindow = ttk.Panedwindow(
        #                             master=tuneFrame, 
        #                             orient=tk.VERTICAL,
        #                             style='danger')
        # self.panedwindow.place(relx=0.5,
        #                   rely=PANWINDOW_RELY,
        #                   relheight=PANWINDOW_RELHEIGHT,
        #                   relwidth=0.5,
        #                   anchor='center'
        #                   )
        
        # panTop = ttk.Frame(self.panedwindow,style='dark.TFrame')
        # panBot = ttk.Frame(self.panedwindow,style='dark.TFrame')

        # self.panedwindow.add(panTop)
        # self.panedwindow.add(panBot)
        
        # self.panedwindow.bind("<ButtonRelease-1>", self.__send_pos)
        # panBot.bind("<Configure>",self.__label_travel)

        # self.tunePos = tk.IntVar()
        # self.tuneLable = tk.DoubleVar()
        # self.tuneLable = ttk.Label(
        #     tuneFrame,
        #     textvariable=self.tunePos,
        #     style='inverse-dark')        
        # self.tuneLable.place(relx=0.5,
        #                      rely=0.05,
        #                      anchor='center')
        
        # Radio buttons in tune frame
        radioBtnFrame_PWM = ttk.Frame(tuneFrame)
        radioBtnFrame_PWM.place(relwidth=1,relheight=0.1,rely=1,anchor='sw')
        radioBtnFrame_DIR = ttk.Frame(tuneFrame,style='dark')
        radioBtnFrame_DIR.place(relwidth=1,relheight=0.05,rely=0.9,anchor='sw')

        self.dirVar = tk.IntVar()
        self.radVar = tk.IntVar()

        ttk.Radiobutton(        # moveup radiobutton
                        radioBtnFrame_DIR,
                        text='Move Up',
                        variable=self.dirVar,
                        value=1,
                        command=self.__update_dir,
                        ).pack(
                            side = 'left', 
                            expand = True, 
                            fill = 'both')       
        ttk.Radiobutton(        # movedown radiobutton
                        radioBtnFrame_DIR,
                        text='Move Down',
                        variable=self.dirVar,
                        value=2,
                        command=self.__update_dir).pack(
                            side = 'left', 
                            expand = True, 
                            fill = 'both')
        
        ttk.Radiobutton(        # slow radiobutton
                        radioBtnFrame_PWM,
                        style='success-toolbutton',
                        text='Slow',
                        variable=self.radVar,
                        value=1,
                        command=self.__update_PWM).pack(
                            side = 'left', 
                            expand = True, 
                            fill = 'both')
        ttk.Radiobutton(        # medium radiobutton
                        radioBtnFrame_PWM,
                        style='warning-toolbutton',
                        text='Medium',
                        variable=self.radVar,
                        value=2,
                        command=self.__update_PWM).pack(
                            side = 'left', 
                            expand = True, 
                            fill = 'both')     
        ttk.Radiobutton(        # fast radiobutton
                        radioBtnFrame_PWM,
                        style='danger-toolbutton',
                        text='Fast',
                        variable=self.radVar,
                        value=3,
                        command=self.__update_PWM).pack(
                            side = 'left', 
                            expand = True, 
                            fill = 'both')
        
        # self.checkVar = tk.IntVar()
        # ttk.Checkbutton(
        #     master=tuneFrame,
        #     text='Move Up',
        #     variable=self.checkVar,
        #     command=self.__get_dir
        # ).place(relx)
        

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
        
        ttk.Button(
            master=chartFrame,
            text='reset chart',
            command=self.__clear_figure,
            style='outline-secondary').place(
                relx=0,
                rely=0,
                relwidth=0.1,
                anchor='nw'
            )
        
#%%#####################  Start-up Toplevel  ##################################
        self.loginTop = ttkbs.Toplevel(self,topmost=True)
        self.loginTop.geometry("400x200+500+300")
        self.loginTop.title("User login")
        
        ttk.Label(
            master=self.loginTop,
            text='Please enter your name\n (for back up data purpose)',
            justify='center'
        ).pack(
            side='top',
            pady=20
        )

        self.userVar = tk.StringVar()
        entry_login = ttk.Entry(
                master=self.loginTop,
                textvariable=self.userVar,
                
            )
        entry_login.pack(side='top',
                pady=5)
        entry_login.bind("<Return>",self.__get_user)
        
        
        ttk.Button(
            master=self.loginTop,
            text='Confirm',
            command=self.__get_user,
            style='info'
        ).pack(
            side='top',
            pady=5
            
        )

        self.loginTop.grab_set()

#%%#########################  Func Defn    ####################################

    # Purpose : to start the tensile testing, is the core function of the device
    # Function: 1. switch to test mode (set test_flag)
    #           2. clear the current plotting figure (ie. the canvas)
    #           3. enter command executing function (__xq_cmd) to read data from TMS
    #           4. after data reading, concate the data frame (__data_concat) in shape
    #           5. back up the testing data (__backup_data)
    #           6. inform user the testing is done and switch to free-run mode (reset test_flag)
    def __tensileTest(self):
        # messagebox.showinfo("Information", "Starting tensile testing") 
        self.rawStrain = []
        self.rawStress = []
        self.strain=[]
        self.stress=[]
        self.ultimateSt = 0
        self.data_count = 0
        self.test_flag = True
        self.xlim = 0
        self.ylim = 0
        self.filter_count = 0

        print("Tensile test initiated")
        self.stop_pressed = False # reset software stop status 

        self.__clear_figure()
        self.line, = self.axTens.plot([], [], label='Current Test')        
        self.figTens.legend()

        if TEST_WITH_TMS:
            ser.reset_input_buffer()
            # ser.reset_output_buffer()
            ser.write("MOVE,UP\r".encode())
            ser.write("START\r".encode())
            time.sleep(0.5)
            # messagebox.showinfo("Information","Starting Test")
            while(ser.in_waiting):
                # time.sleep(0.01)
                if not self.__xq_cmd():
                    print("xq_cmd return 0")
                    print("send STOP")
                    break    
            ser.write(("STOP\r").encode())
        else:
            self.__fake_datainput() 
            while(True): 
                self.filter_count += 1
                if not self.__xq_cmd():
                    break               

        self.__data_concat()
        if len(self.data) != 0:    
            self.__backup_data()

        else:
            messagebox.showinfo("Information","Empty dataset")
        messagebox.showinfo("Information", "Done tensile testing")
        self.test_flag = False


    def __update_dir(self):
        dirVal = self.dirVar.get()
        if (dirVal == 1):
            messagebox.showinfo("Information", "Moving up")
            if TEST_WITH_TMS:
                ser.write(("MOVE,UP\r").encode())
        elif (dirVal == 2):
            messagebox.showinfo("Information", "Moving down")
            if TEST_WITH_TMS:
                ser.write(("MOVE,DOWN\r").encode())

    # Purpose : to inform the TMS and update the PWM based on user selected speed
    # Function: get the selection value, and send command to TMS through UART
    # command : "PWM,(%DutyCycle)", ie. "PWM,50" indicating 50% duty cycle PWM
    def __update_PWM(self):
        if self.radVar.get() == 1:
            if TEST_WITH_TMS:
                ser.write(("PWM,10\r").encode())
            messagebox.showinfo("Information","device is set to slow mode (PWM = 10% Duty Cycle)")
        elif self.radVar.get() == 2:
            if TEST_WITH_TMS:
                ser.write(("PWM,50\r").encode())            
            messagebox.showinfo("Information","device is set to medium mode (PWM = 50% Duty Cycle)")
        elif self.radVar.get() == 3:
            if TEST_WITH_TMS:
                ser.write(("PWM,100\r").encode())    
            messagebox.showinfo("Information","device is set to fast mode (PWM = 100% Duty Cycle)")



    # Purpose : to request the user for a calibration
    # Function: pop up a calibration window to inform user briefly the calibration process, and wait
    #           for user pressing "start calibration" button. Main window can not be interacted 
    #           while this window is shown
    def __calibration_info(self):        
        self.caliTop = ttkbs.Toplevel(self,topmost=True)
        self.caliTop.geometry("400x200+500+300")
        self.caliTop.title("Initialization Calibration")
        ttk.Label(
            self.caliTop, 
            text="Calibration Process is ready...").pack(
                pady=20, 
                side='top' )
        ttk.Label(
            self.caliTop, 
            text="Please stay away from the device").pack(
                side='top')
        ttk.Label(
            self.caliTop, 
            text="Estimated completion time = 2 minutes").pack(
                side='top')
        ttk.Button(
            self.caliTop,
            text="Start calibration",
            command=self.__calibration_initialzation).pack(
                pady=20)
        if TEST_WITH_TMS:
            ser.reset_input_buffer()
        self.caliTop.grab_set()  # prevent user interact with main window
    


    # Purpose : to initialize the calibration after receiving user pressing "start initialization" button
    # Function: will toast a info at right-bottom corner to notifying user the calibration starting
    # command : "CALIBRATE" --> TMS
    def __calibration_initialzation(self):
        toast = ToastNotification(
        title="Calibration initializing.....",
        message="Calibration is initializing, please DO NOT block the device or engage your body in the device... ",
        duration=30000,
        alert=True,
        bootstyle='dark'
        )
        toast.show_toast()

        if TEST_WITH_TMS:
            ser.write(("CALIBRATE\r").encode())
            time.sleep(0.05)
            while(not ser.in_waiting):      # polling to get calibration result from TMS
                time.sleep(0.1)
            # cmd = ser.read().decode()
            cmd = ser.read(1).decode().strip()
            print("received " + cmd)
            messagebox.showinfo("Information","Done calibration")
            self.max_range = ser.read(3)
            print("max range is:", self.max_range)
            self.max_range = int.from_bytes(self.max_range,byteorder='little')
            print("max range is:", self.max_range)
            self.caliTop.destroy()

        self.dimbtn.configure(state='enable')



    # Purpose : to visually inform user what % of position of the tensile tester currently position at,
    #           %POS will travell along with the slide bar and change to the corresponding integer
    # Function: at free-run mode, user can drag the slide bar to manually control the device position
    def __label_travel(self,event):
        self.posSash = self.panedwindow.sashpos(0)
        # print("Lable posSash is:",self.posSash)
        self.panFullRange = SCREEN_HEIGHT * PANWINDOW_RELHEIGHT
        posTensile = 100 - (self.posSash * 100 / self.panFullRange)
        # print("Position at:", posTensile)
        self.int_tunePos = int(posTensile)
        # print(self.int_tunePos)
        self.tunePos.set(self.int_tunePos)
        posPercent = self.posSash / SCREEN_HEIGHT
        self.tuneLable.place(y=self.panFullRange*2*(PANWINDOW_RELY*1.28),
                             relx=0.5,
                             rely=posPercent,
                             anchor='center')
    


    # Purpose : to update TMS or the host the position information
    # Function: if at testing mode (test_flag set), slide bar and label value will update by encoder data read from TMS
    #           if at free-run mode (test_flag reset), dragging user controlled slide bar will inform TMS to move the 
    #           gripper to the user set-position
    # Command : "POS,%POS" to TMS, ie. "POS,50" for 50% position away from max pos
    def __send_pos(self,event):
        if not self.test_flag:
            if TEST_WITH_TMS:
                print("Send position at: ", self.int_tunePos)
                ser.write(("POS,{}\r".format(self.int_tunePos)).encode())

    def __update_pos(self, posData):
        if self.test_flag:
            if TEST_WITH_TMS:
                pass
            else:
                self.max_range = 10
            barPos = (self.max_range - posData) / self.max_range * self.panFullRange
            # print("barPos is: ",barPos)
            barPos = int(barPos)
            self.posSash = self.panedwindow.sashpos(0,barPos)

    def __update_force(self, fData):
        self.meter.amountusedvar.set(fData)
        # print("force is: ", fData)
        # print("Critical Force is: ", CRITICAL_FORCE)
        # print("Middle Force is: ", HIGH_FORCE)
        if (fData>CRITICAL_FORCE):
            self.meter.configure(bootstyle='danger')
        elif (fData>HIGH_FORCE):
            self.meter.configure(bootstyle='warning')
        else:
            self.meter.configure(bootstyle='dark')





    # Purpose : to clear the figure
    # Function: clear the figure and legend
    def __clear_figure(self):
        self.figTens.legends = []
        self.axTens.cla()
        self.axTens.set_title("Stress vs Strain")
        self.axTens.set_xlabel("Strain")
        self.axTens.set_ylabel("Stress, MPa")
        self.testCanvas.draw()
        self.master.update()

    def __get_user(self,*event):
        self.login_userID = self.userVar.get()
        print("user ID is: " + self.login_userID)
        if self.login_userID == 'Ace Ha':
            self.haha = ttkbs.Toplevel(topmost=True)
            self.haha.geometry("+500+300")
            ttk.Label(self.haha,image='Ace_Ha').pack(side='left',expand=True,fill='both')
            self.haha.protocol("WM_DELETE_WINDOW", self.__on_closing)
            self.haha.bind("<Unmap>", self.__on_minimize)
            # self.haha.bind("<Configure>", self.__on_resize)
        self.loginTop.destroy()
        messagebox.showinfo("Welcome","Welcome {}".format(self.login_userID))
    
    # def __on_resize(self,event):
    #     ttk.Label(self.haha,image='Ace_Ha').pack(side='left',expand=True,fill='both')

    def __on_minimize(self,event):
        self.haha.attributes("-topmost", True)
        self.haha.deiconify()

    def __on_closing(self):
        answer = messagebox.askyesno("Haha","Really??")
        if answer:
            while messagebox.askokcancel("Haha","Try again"):
                messagebox.askokcancel("Haha","Try again")
            messagebox.showinfo("Haha","Okay")
        else:
            messagebox.showinfo("Haha","Okay")
            


    # Purpose : to obtain the test segment cross sectional shape, in order to calculate stress later
    # Function: depend on user selected item from the combo-box, re-configure the displaying widgets,
    #           for rectangle, display length entry, width entry, and thickness entry;
    #           for circular, only display diameter entry and thickness entry, other widgets are disable
    #           also inform user the selected shape is updated
    def __get_shape(self,event):
        self.segShape = self.cbBox_typeSel.current()
        self.testbtn.configure(state='disable')

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



    # Purpose : to calculate and display the segment cross-sectional area to user
    # Function: get dimension data from user input after user pressed "Confirm Dimension" button, and 
    #           calculate the segment area, update on the area display entry, and inform user by messagebox        
    def __confirm_dim(self):
        self.segShape = self.cbBox_typeSel.current()
                
        if (self.segShape == 0): # rectangle shape        
            area = self.dim2.get() * self.dim3.get()

        elif (self.segShape == 1): # circular shape            
            area = np.pi * (0.5*self.dim2.get())**2

        if area == 0 or self.dim1.get() == 0:
            messagebox.showwarning("Warning","Invalid Inputs!")
        else:
            rounded_area = round(area,4)
            self.segArea.set(rounded_area)        
            messagebox.showinfo("Information", "Dimension updated!")
            self.testbtn.configure(state='enable')

            self.inv_length = 1 / self.dim1.get()
            self.inv_area = 1/area



    # Purpose : to generate fake data package and feed in the program, used for testing real-time plotting 
    #           functionality and debug; not used when in real application
    # Function: Uart write the fake data to the program/ or by assigning a fake data string     
    def __fake_datainput(self):
        # if TEST_WITH_TMS:
        #     self.fakeData = b"ABCIT_MECHATRONICS&ROBOTICS_PROGRAMEND"
        #     ser.write(self.fakeData)
        # else:
        #     self.fakeData = "A112223243536374849596876988995END"

        # self.fakeData = "A001122334455667788998877665544332211C"
        # self.fakeData = "A00112233A44556566A66766767A66554433A22112233A44556677A44556566A66766767A66554433A22112233A44556677A44556566A66766767A66554433A22112233A44556677A07080809A09080807A07080809D"
        self.fakeData = "A00A11A22A33A44A55A65A66A66A76A67A67A66A55A44A33A22A11A22A33A44A55A66A77A44A55A65A66A66A76A67A67A66A55A44A33A22A11A22A33A44A55A66A77A44A55A65A66A66A76A67A67A66A55A44A33A22A11A22A33A44A55A66A77A07A08A08A09A09A08A08A07A07A08A08A09D"
        time.sleep(0.1)
    
    def __xq_cmd(self):  
        try:         
            # print("entered __xq_cmd")   

            if TEST_WITH_TMS: 
                Cmd_Byte = (ser.read().decode().strip()) # Obtain Cmd_Byte
                print('\ncommand: ' + Cmd_Byte + ' type:', type(Cmd_Byte))
                # Cmd_Byte = (ser.read()) # Obtain Cmd_Byte
                # print('\ncommand: ', Cmd_Byte, ' type:', type(Cmd_Byte))
                # print("decoded string:", Cmd_Byte.decode())
                # Cmd_Byte = int.from_bytes(Cmd_Byte, byteorder='little')
                # print("int from byte: ", Cmd_Byte)
            
            else:
                Cmd_Byte = self.fakeData[self.data_count]  # use in PC debug                
                print("int from byte: ", Cmd_Byte)
                self.data_count += 1 

            # Decode the obtained data
            # Look Up Table for decoding
            #|----------------------------------------------------------------|
            #| Cmd_Str  |   Byte Size  |              Command                 |
            #|----------|--------------|--------------------------------------|
            #|    A     |    1+vary    |  Encoder, LVDT data coming from TMS  |
            #|    B     |       1      |   Emergency Stop engaged, sys stops  |
            #|    C     |       1      |    Limit Switch engaged, sys stops   |
            #|    D     |       1      |      Segment breaks, test done       |
            
            # if TEST_WITH_TMS:      # testing with TMS
            #     if Cmd_Byte == A:    # data transmission command 
            #         self.__get_data()
            #         return 1   
            #     elif Cmd_Byte == B:  # Emergency Stop engaged
            #         messagebox.showwarning("Warning","System stops due to e-stop engagement")
            #         return 0
                    
            #     elif Cmd_Byte == C:  # Limit Switch engaged
            #         messagebox.showwarning("Warning","System stops due to limit switch been triggered")
            #         return 0
            #     elif Cmd_Byte == D:  # Segment breaks, test done
            #         messagebox.showinfo("Information","System detected segment failure, testing done")
            #         return 0
            #     else:
            #         print("enter nothing\n")
            # else:           # testing without TMS
            if Cmd_Byte == 'A':    
                if not self.__get_data():
                    return 0
                return 1   
            elif Cmd_Byte == 'B':  # Emergency Stop engaged
                messagebox.showwarning("Warning","System stops due to e-stop engagement")
                return 0
                
            elif Cmd_Byte == 'C':  # Limit Switch engaged
                messagebox.showwarning("Warning","System stops due to limit switch been triggered")
                return 0
            elif Cmd_Byte == 'D':  # Segment breaks, test done
                messagebox.showinfo("Information","System detected segment failure, testing done")
                return 0
            else:
                print("enter nothing\n")
                return 1
        except KeyboardInterrupt:
            print("Interrupt from keyboard\n")
            ser.close()
    
    def __get_data(self):
        new_dataIn = 0
        data_size = NUM_DATA_POINT * 2
        count = 0
        sumStrain = 0
        sumStress = 0
        # print("entered Cmd_Byte == A")
        strainFlag = False   # To indicate incoming strain or stress data
        # self.axTens.set_xlim(0, 1)

        
        while count<data_size:    
            if TEST_WITH_TMS:    
                new_dataIn = (ser.read(READ_SIZE))    # Obtain serial data from TMS
                # print("Reading byte: ", new_dataIn)
                new_dataIn = int.from_bytes(new_dataIn,byteorder='little')
                # print("Converting int: ", new_dataIn)
            else:
                new_dataIn = int(self.fakeData[self.data_count])
                # print("Converting int: ", new_dataIn)
                self.data_count += 1
            count += 1

            print("filter count:" , self.filter_count)
            if self.filter_count < MOVING_AVG_NUM:
                # print("waiting for enough data to be averaged")
                if strainFlag == False:
                    strainFlag = True
                    self.rawStress.append(new_dataIn)   # raw stress data
                    # print("pre append rawStress:",self.rawStress)
                elif strainFlag == True:               
                    strainFlag = False
                    self.rawStrain.append(new_dataIn)
                    # print("pre append rawStrain:",self.rawStrain)
                    self.filter_count += 1
            else:
                # Append decoded data into array
                ########  FILTER STRESS ##########    
                if strainFlag == False:
                    strainFlag = True
                    self.rawStress.append(new_dataIn)   # raw stress data
                    # print("rawStress:",self.rawStress)     
                    for k in range(MOVING_AVG_NUM):
                        sumStress += self.rawStress[self.filter_count-k]
                    avgStress = sumStress/MOVING_AVG_NUM      
                    fine_force = avgStress*V_LSB_MV*LVDT_NEWTON_PER_MV     # force 
                    self.__update_force(round(fine_force,2))
                    fine_stress = fine_force * self.inv_area     # stress
                    print("fine stress is:", fine_stress,"ult stress is:", self.ultimateSt)
                    if fine_stress > self.ultimateSt:
                        self.ultimateSt = fine_stress
                        # print("update Ultimate Strength is: ", self.ultimateSt)
                    elif fine_stress < (self.ultimateSt * 0.1):     # 5% of ultimate Strength to determine breaks
                        print("Ultimate Strength is: ", self.ultimateSt)
                        print("fine stress: ", self.stress)
                        print("fine strain: ",self.strain)
                        self.segUltSt.set(self.ultimateSt)
                        return 0

                    self.stress.append(fine_stress)
                    if fine_stress>self.ylim:
                        self.ylim = fine_stress
                        self.axTens.set_ylim(0, 1.2*self.ylim)


                ########  FILTER STRAIN ########## 
                elif strainFlag == True:               
                    strainFlag = False
                    self.rawStrain.append(new_dataIn)
                    # print("rawStrain:", self.rawStrain)
                    for j in range(MOVING_AVG_NUM):
                        sumStrain += self.rawStrain[self.filter_count-j]
                    avgStrain = sumStrain/MOVING_AVG_NUM 
                    # self.__update_pos(new_dataIn)
                    # print("inv_length: ",self.inv_length)
                    fine_strain = avgStrain * MM_PER_COUNT * self.inv_length
                    # print("delL: ",new_dataIn * MM_PER_COUNT)
                    self.strain.append(fine_strain)
                    # new_dataIn = round(new_dataIn,2)
                    if fine_strain>self.xlim:      
                        # print("set x axis during get data, xlim={}, new_dataIn={}".format(self.xlim,new_dataIn))              
                        self.xlim = fine_strain
                        self.axTens.set_xlim(0, 1.2*self.xlim)
                    
                    self.filter_count += 1
                    self.line.set_data(self.strain, self.stress)
                    self.testCanvas.draw()
                    self.master.update()           
                    
                     # stop updating diagram if user pressed stop button
                    if self.stop_pressed:
                        self.__data_concat()
                        if TEST_WITH_TMS:
                            print("stop pressed")
                            return 0


                

        return 1
          
    def __stop_plot(self):
        self.stop_pressed = True
        if TEST_WITH_TMS:
            ser.write("STOP\r".encode())
            ser.reset_output_buffer()
            ser.reset_input_buffer()
            ser.write("MOVE,UP\r".encode())
        self.radVar.set(0)
        self.dirVar.set(1)
        messagebox.showinfo("Information","Process has been stopped")
        
        
    def __data_concat(self):
        self.df_stress = np.array(self.stress)
        self.df_strain = np.array(self.strain)

        # Organize data frame for exporting .csv
        self.data = np.concatenate(
            (self.df_strain.reshape(1,-1), self.df_stress.reshape(1,-1)), axis=0)

    def __backup_data(self):    
        print("back up dataset path is:", self.backup_path)
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
        # userID = "Mingqi"
        userID = self.login_userID
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
        page_index = self.tableView._pageindex.get()
        row_limit = len(self.tableView.tablerows_visible)
        plot_index = (page_index-1) * row_limit + selected_index
        print("page index", page_index)
        print("page limit", row_limit)
        print("plot index", plot_index)
        history_file = self.file_names[plot_index] + ".csv"
        # print(selected_index)
        history_path = pathlib.Path(__file__).parent / 'dataset' / history_file
        history_data = self.__read_csv_file(history_path)

        history_strain, history_stress = zip(*history_data)
        # print("strain: \n",history_strain)
        # print("stress: \n",history_stress)
        max_xlim = max(history_strain)
        max_ylim = max(history_stress)
        print("max strain, ",max_xlim, "max stress: ",max_ylim)

        selectLabel = "ID: " + history_file.split('_')[0]
        self.axTens.plot(history_strain,history_stress, label=selectLabel)

        if max_xlim > self.xlim:
            self.axTens.set_xlim(0, 1.2*max_xlim)
            self.xlim = max_xlim
        if max_ylim > self.ylim:
            self.axTens.set_ylim(0, 1.2*max_ylim)
            self.ylim = max_ylim

        self.figTens.legend()
        self.testCanvas.draw()
        self.master.update()

    def __check_or_create_folder(self):
        for val in self.needed_file:
            # print(val)
            if not os.path.exists(val):
                os.makedirs(val)

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
root = ttkbs.Window(themename='sandstone')
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
INPUT_BTN_TEST = 0.8
INPUT_BTN_CALI = -3*btnHeight
INPUT_BTN_CNFM = -1.5*btnHeight
INPUT_BTN_STOP = 1.5*btnHeight
ITEM_RELWID = 0.7

# Other
PANWINDOW_RELHEIGHT = 0.3
PANWINDOW_RELY = 0.65
SEPERATOR_TOP_RELY = 0.05
SEPERATOR_FORCE_TOP_RELY = 0.15
SEPERATOR_FORCE_BOT_RELY = 0.35
SEPERATOR_MID_RELY = 0.45
SEPERATOR_BOT_RELY = 0.83
#%%#########################  GUI Init  #######################################   
app = __Tensile_Tester_Application(master = root)
# root.withdraw()
root.mainloop()
if TEST_WITH_TMS:
    ser.close()