# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tkinter as tk
from tkinter import messagebox

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.config(height=800,width=1000)
        self.master = master
        self.place(x=0,y=0)
        self.createWidget()
        
    def createWidget(self):
        tk.Label(self, text="Enter Segment Length in mm").place(relx=0,rely=0,x=10)
        
        segLen = tk.DoubleVar()
        self.entry_SegLen = tk.Entry(self, textvariable=segLen)
        self.entry_SegLen.place(relx=0, y=25,x=15)
        
        
        tk.Label(self, text="Enter Segment Width in mm").place(relx=0,y=50,x=10)
        
        segWid = tk.DoubleVar()
        self.entry_SegWid = tk.Entry(self, textvariable=segWid)
        self.entry_SegWid.place(relx=0, y=75,x=15)
        
root = tk.Tk()
root.title("BCIT_AUTOBOT")
root.geometry("500x300+700+300")
app = Application(master=root)

root.mainloop()