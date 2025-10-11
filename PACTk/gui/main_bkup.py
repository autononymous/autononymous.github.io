# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 10:28:10 2025

@author: rkiss
"""

import sys, cv2, time

import tkinter as tk
from tkinter import ttk
from cv2 import VideoCapture

from PIL import Image
from PIL import ImageTk

from ui import FrontEnd as FE

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, 
    NavigationToolbar2Tk)

COLORS = {
    "DIM":"#0C2138",
    "DARK":"#000000",
    "LIGHT":"#FFFFFF",
    "MAIN":"#005CB9",
    "MID":"#474657"    
}
FRAME = {
    "PRGM":
    [
         [800 ,600 ],
         [1920,1080]
    ],
    "TOOLS":
    [
         [200 ,550 ],
         [600 ,1000 ]
    ],
    "CAM":
    [
         [550 ,550 ],
         [1000,1000 ]
    ]
}
IMAGE = [512,512]
    
SCR = 0;
FRAMERATE = 1 / 60.0
MASKRATE  = 1 / 10.0 
PLOTRATE  = 1 / 1.0

KERNEL = 25

DBG = None;

class DEBUG:
    def __init__(self):
        self.text = "";
    def console(self, line, doFlush=True):
        self.text += "\n   >> " + str(line) if self.text != "" else str(line)
        if doFlush:
            print(self.text)
            self.text = ""
        
D = DEBUG()    
 
#width = root.winfo_screenwidth()
#height = root.winfo_screenheight()
    
class FSM_PACT:
    
    class Timer:
        def __init__(self, limit):
            self.tick = time.time() # "bookmark" of last overflow
            self.tock = 0.0         # relative time since last call
            self.limit = limit
        def tic(self,reset=True): # Get time elapsed
            now = time.time()
            self.tock = now - self.tick
            if reset: self.tick = now
            return self.tock            
        def toc(self,reset=True):
            if self.tic(False) > self.limit:
                if reset: self.tick = time.time()
                return True
            else:
                return False
    
    class CamCapture(VideoCapture):
        STATE = 0;
        
        LastRaw = []
        LastRead = []
        LastFrame = []
        Overlay = []
        LastProc = []
        
        isFrameReady = False
        isOverlayReady = False
        
        Norm = []      
        Ang = []
        Mag = []
        
        def __init__(self, ID, *args, **kwargs):
            super().__init__(*args, ID, **kwargs)
            if self.isOpened():
                self.isActive = True
                ok, frame = self.read()
                test = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.h, self.w = test.shape[:2]
            else:
                self.isActive = False
                print("No camera detected at ID = " + str(ID) + ".")
                
    class ConditionFlag():
        def __init__(self, Initial=False) -> None: self.State = Initial            
        def check(self) -> bool: return self.State            
        def shake(self):
            if self.State:
                self.State = False
                return True
            else:
                return False
        def setflag(self, NewState) -> None: self.State = NewState            
        def deactivate(self) -> None: self.State = False;            
        def activate(self) -> None: self.State = True;
   
    
    ## |====================================================================|
    ## |      [TASK 00]                         INITIALIZATION PROCESS      |
    ## |====================================================================|   
    def __init__(self, doTk=False) -> None: 
    ## Handshake Flags ====================================================
        self.f_DO_RESIZE    = self.ConditionFlag(False);
        self.f_IS_NEW_IMAGE = self.ConditionFlag(False);
    
        self.DBG1 = None
        self.DBG2 = None
        self.DBG3 = None
    
    ## Configuration parameters ===========================================
        
    # >> Pre-initialization variables: ====================================
        self.SPLIT      = 0.2        
        
        self.ZOOM = 1.0       
        self.ALPHA = 0.625
        self.SAMPLES = 4
        self.KERNEL = 25
        
        self.W_RES      = IMAGE[0]
        self.H_RES      = IMAGE[1]
        self.W_APP      = FRAME["PRGM"][SCR][0]
        self.H_APP      = FRAME["PRGM"][SCR][1]
        self.W_TOOL     = int(self.W_APP * self.SPLIT)          #FRAME["TOOLS"][SCR][0]
        self.H_TOOL     = self.H_APP                            #FRAME["TOOLS"][SCR][1]
        self.W_IMBAR    = int(self.W_APP * (1-self.SPLIT))  
        self.H_IMBAR    = self.H_APP             
        self.W_IMG      = min(self.W_IMBAR,self.W_RES)    
        self.H_IMG      = min(self.H_IMBAR,self.H_RES)       
        self.wCENTER    = int(self.W_IMG / 2)
        self.hCENTER    = int(self.H_IMG / 2)       
        
        self.T_LATENCY  = self.Timer(999)
        self.T_THROTTLE = self.Timer(FRAMERATE)  
        self.T_OVERLAY  = self.Timer(MASKRATE)
        self.T_DOPLOT   = self.Timer(PLOTRATE)
        
        self.FPS = 9999;
        
    # >> For TASK 00 | MASTERMIND:
        self.W_LAST = self.W_APP;
        self.H_LAST = self.H_APP;
        
    ## UI initialization ==================================================
        if doTk:
            self.root = tk.Tk() 
            self.root.title("Stolle PACT Inspection System")
            self.root.config(bg=COLORS["DIM"], width=self.W_APP, height=self.H_APP)
            
            self.tool_frame = tk.Frame(
                self.root)#, 
                #width=self.W_TOOL, 
                #height=self.H_TOOL)
            self.tool_frame.pack(
                padx=5,
                pady=5,
                side=tk.LEFT,
                fill=tk.BOTH)      
            self.info_title1 = tk.Label(self.tool_frame,text="---Statistics---") 
            self.info_title1.grid(row=0, column=0, columnspan=2)
            self.info_nFPS  = tk.Label(self.tool_frame,text="FPS: ")        
            self.info_nFPS.grid(row=1, column=0)
            self.info_FPS   = tk.Label(self.tool_frame,text="NaN")
            self.info_FPS.grid(row=1, column=1)
            self.info_DAT1  = tk.Label(self.tool_frame,text="xxx: ")
            self.info_DAT1.grid(row=2, column=0)
            
            self.cfg_title2 = tk.Label(self.tool_frame,text="\n---Configs---") 
            self.cfg_title2.grid(row=3, column=0, columnspan=2)
            self.cfg_slide = tk.Scale(self.tool_frame,from_=0,to=1000, orient=tk.HORIZONTAL)
            self.cfg_slide.grid(row=4, column=0, columnspan=2)
            self.cfg_slide.set(self.ALPHA*1000)
            
            self.plt_title3 = tk.Label(self.tool_frame, text="\n---Histogram---")
            self.plt_title3.grid(row=5, column=0, columnspan=2)
            self.plt_Hist  = tk.Label(self.tool_frame)
            self.plt_Hist.grid(row=6, column=0, columnspan = 2)
            
            self.HistFig = plt.Figure(figsize = (3,3), dpi = 100)
            self.HistPlt = self.HistFig.add_subplot(111)
            self.plt_canvas = FigureCanvasTkAgg(self.HistFig, master=self.plt_Hist)
            
            self.image_frame = tk.Frame(
                self.root, 
                width=self.W_IMBAR, 
                height=self.H_IMBAR)
            self.image_frame.pack(
                padx=5, 
                pady=5, 
                side=tk.RIGHT)#,fill=tk.Y)    
            
            self.TKpanel = tk.Canvas(
                self.image_frame, 
                width=self.W_IMG, 
                height=self.H_IMG)
            self.TKpanel.pack()#fill=tk.BOTH)
        
    ## CV2 camera initialization ==========================================
    # >> Establish camera object(s) and determine what is connected
        self.cap1 = self.CamCapture(1);
        self.cap2 = self.CamCapture(2);    
        
    ## Main program variables =============================================
        
    def ResizeWindow(self) -> None:
        self.W_APP      = self.root.winfo_width()
        self.H_APP      = self.root.winfo_height()
        self.W_TOOL     = int(self.W_APP * self.SPLIT)          
        self.H_TOOL     = self.H_APP       
        self.W_IMBAR    = int(self.W_APP * (1-self.SPLIT))  
        self.H_IMBAR    = self.H_APP             
        self.W_IMG      = min(self.W_IMBAR,self.W_RES)    
        self.H_IMG      = min(self.H_IMBAR,self.H_RES)
        self.wCENTER    = int(self.W_IMBAR / 2)
        self.hCENTER    = int(self.H_IMBAR / 2)
        self.tool_frame.configure(
            width=self.W_TOOL,
            height=self.H_TOOL
            )
        self.image_frame.configure(            
            width=self.W_IMBAR, 
            height=self.H_IMBAR
            )
        self.TKpanel.configure(
            width=self.W_IMBAR, 
            height=self.H_IMBAR
            )        
        self.W_APP      = self.root.winfo_width()
        self.H_APP      = self.root.winfo_height()
        self.W_LAST     = self.W_APP
        self.H_LAST     = self.H_APP
        
    def MakeSquare(self, img):
        h, w = img.shape[:2]
        if w > h:
            bound = int((w/2)-(h/2))
            self.IMG_WCROP = h
            self.IMG_HCROP = h
            return img[:,bound:bound+h]
        else:
            bound = int((h/2)-(w/2))
            self.IMG_WCROP = w
            self.IMG_HCROP = w
            return img[bound:bound+w,:]
        
    def Normalize(self, arr):
        h, w = arr.shape[:2]
        a_min = np.min(arr)
        a_max = np.max(arr)        
        a_rng = a_max - a_min
        if a_rng == 0:
            return (arr - a_min)
        else:
            return (arr - a_min) / a_rng
    def Gradient(self, arr, n_samples=8):
        GradX, GradY = np.gradient(arr,n_samples)
        self.DBG1 = GradX, GradY
        Mag = self.Normalize(np.sqrt( (GradX*GradX)+(GradY*GradY) ))
        Ang = np.arctan2(GradY,GradX)
        return Mag, Ang   
    def NormalMap(self, mag, ang):
        h, w = mag.shape[:2]
        Map = np.zeros([h,w,4],dtype='uint8')
        Map[:,:,0] = ( 255 - ( 128 * mag))                    # BLUE channel
        Map[:,:,1] = ( 127 + ( 128 * np.sin(ang) * mag ))     # GREEN channel
        Map[:,:,2] = ( 127 + ( 128 * np.cos(ang) * mag ))     # RED channel
        Map[:,:,3] = 255 * mag                                # ALPHA channel
        return Map
    def SquareMap(self, mag, ang):
        h, w = mag.shape[:2]
        Sqr = np.zeros([h,w,4],dtype='uint8')
        Sqr[:,:,0] = ( 255 - ( 128 * mag))                    # BLUE channel
        Sqr[:,:,1] = ( 127 + ( 128 * np.cos(ang * 4) * mag )) # GREEN channel
        Sqr[:,:,2] = ( 127 + ( 128 * np.sin(ang * 4) * mag )) # RED channel
        Sqr[:,:,3] = 255 * mag                                # ALPHA channel
        return Sqr
    def AlphaOver(self, over, under, thresh=0.150):
        h_o, w_o = over.shape[:2]
        h_u, w_u = under.shape[:2]
        if (h_o != h_u) and (w_o != w_u):
            under = cv2.resize(under, [h_o,w_o])
        alpha = (((over[:,:,3]/255.0) > thresh) * 1.0 )
        inv_a = 1.0 - alpha
        self.DBG2 = over,under
        result = np.zeros([h_o,w_o,3],dtype='uint8')
        for channel in range(3):
            result[:,:,channel] = (over[:,:,channel] * alpha) + (under * inv_a)
        return result
    
    def makeHistogram(self, mag, ang):
        h, w = mag.shape[:2]
        HistList = []
        for i in range(h):
            for j in range(w):
                if mag[i,j] > self.ALPHA:
                    x = ang[i,j] * 180 / 3.1416
                    while x <= -45: x += 90;
                    while x >=  45: x -= 90;
                    #HistList.append(np.abs(ang[i,j] * 180 / 3.1416))
                    HistList.append(np.abs(x))
                else: pass
        return HistList
        
        
    ## |====================================================================|
    ## |      [TASK 01]                     MASTERMIND (Control Logic)      |
    ## |====================================================================|   
    def TASK_MASTERMIND(self) -> None:
        ReadHeight = self.root.winfo_height()
        ReadWidth = self.root.winfo_width()
        if np.abs(ReadHeight - self.H_LAST) + np.abs(ReadWidth - self.W_LAST) > 50:
            self.f_DO_RESIZE.activate() #If window change, resize window
            
            
    ## |====================================================================|
    ## |      [TASK 02]                   POLL GUI (Check for changes)      |
    ## |====================================================================| 
    def TASK_POLL_GUI(self) -> None:
        self.ALPHA = self.cfg_slide.get() / 1000
    
    ## |====================================================================|
    ## |      [TASK 03]                GET IMAGE (Pull new image data)      |
    ## |====================================================================| 
    def TASK_GET_IMAGE(self, capN) -> None:
        if capN.isActive:
            if capN.STATE == 0: # SUBSTATE: Grabbing image
                grabbed = capN.grab()
                if grabbed:
                    capN.LastRaw = grabbed
                    capN.STATE = 1
            elif capN.STATE == 1: # SUBSTATE: Converting image
                retrieved = capN.retrieve(capN.LastRaw)
                if retrieved[0]:
                    capN.LastRead = retrieved[1]
                    capN.STATE = 2
            elif capN.STATE == 2: # SUBSTATE: Final Processing  
                NewSizing = min(self.W_IMG,self.H_IMG)
                capN.LastFrame = cv2.GaussianBlur(
                    cv2.resize(
                        self.MakeSquare(
                            cv2.cvtColor(
                                capN.LastRead,
                                cv2.COLOR_BGR2GRAY
                            )
                        ),
                        [NewSizing,NewSizing]
                    ),
                    (self.KERNEL,self.KERNEL),
                    0                    
                )
                capN.isFrameReady = True # First frame now exists.
                self.f_IS_NEW_IMAGE.activate()
                capN.STATE = 0
    
    
    ## |====================================================================|
    ## |      [TASK 04]            CREATE OVERLAY (Process image data)      |
    ## |====================================================================| 
    def TASK_CREATE_OVERLAY(self, cap) -> None:
        if cap.isActive and cap.isFrameReady:
            doOvr = self.T_OVERLAY.toc(True)
            if doOvr:
                #print(cap.LastFrame)
                cap.Mag, cap.Ang = self.Gradient(cap.LastFrame,self.SAMPLES)
                cap.Overlay = self.SquareMap(cap.Mag,cap.Ang)
                cap.isOverlayReady = True
    
    ## |====================================================================|
    ## |      [TASK 05]            GUI (Run GUI tasks, update, resize)      |
    ## |====================================================================| 
    def TASK_GUI(self) -> None:
        # Perform tkinter tasks instead of getting stuck in loop
        self.root.update_idletasks()
        self.root.update()
        if self.f_DO_RESIZE.shake():
            self.ResizeWindow()
        self.info_FPS.configure(text=str(np.round(1/self.FPS,0)))
        
    ## |====================================================================|
    ## |      [TASK 06]               UPDATE DISPLAY (Push image data)      |
    ## |====================================================================|     
    def TASK_UPDATE_DISPLAY(self) -> None:        
        if self.f_IS_NEW_IMAGE.check() and self.T_THROTTLE.toc(False):
            self.f_IS_NEW_IMAGE.shake()
            #print(self.T_THROTTLE.tock)
            self.T_THROTTLE.toc(True)
            self.FPS = self.T_LATENCY.tic(True)
            for cap in [self.cap1, self.cap2]:
                if cap.isActive and cap.isFrameReady:
                    if cap.isOverlayReady:                    
                        cap.LastProc = self.AlphaOver(cap.Overlay,cap.LastFrame,self.ALPHA)
                    else:
                        cap.LastProc = cap.LastFrame
                    square_size = min(self.W_IMBAR,self.H_IMBAR)
                    scaled = cv2.resize(cap.LastProc,[square_size,square_size])
                    PIL_img = Image.fromarray(scaled)
                    self.image = ImageTk.PhotoImage(
                        PIL_img,
                        master=self.TKpanel)                
                    self.TKpanel.create_image(
                        self.wCENTER, 
                        self.hCENTER, 
                        image=self.image,
                        anchor=tk.CENTER)
                    self.TKpanel.image = self.image
                    self.TKpanel.configure(height=self.H_IMBAR)                    
                    
                    if self.T_DOPLOT.toc(True):
                        self.HistPlt.cla()     
                        HistVals = self.makeHistogram(cap.Mag,cap.Ang)
                        #self.HistPlt.hist(HistVals,bins=40,range=(0,1))
                        self.HistPlt.hist(HistVals,bins=40,range=(0,45))
                        self.plt_canvas.draw()
                        self.plt_canvas.get_tk_widget().pack()
                   
        
    def COMMAND_LOOP(self) -> None:
        self.TASK_MASTERMIND()
        self.TASK_POLL_GUI()
        self.TASK_GET_IMAGE(self.cap1)
        self.TASK_GET_IMAGE(self.cap2)
        self.TASK_CREATE_OVERLAY(self.cap1)
        self.TASK_CREATE_OVERLAY(self.cap2)
        self.TASK_GUI()
        self.TASK_UPDATE_DISPLAY()


    def __del__(self) -> None:
        self.root.destroy()

if __name__ == "__main__":
    print('Initializing Stolle PACT...')
    PACT = FSM_PACT(True)    
    while True:
        PACT.COMMAND_LOOP()
        A = PACT.DBG1
        B = PACT.DBG2
        c = PACT.DBG3
        #MAG = PACT.cap2.Mag
        #ANG = PACT.cap2.Ang
        #ALP = PACT.cap2.Overlay
    
    
    
    
    
    
    
    
    
    