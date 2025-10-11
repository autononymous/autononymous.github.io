# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 10:28:10 2025

@author: rkiss
"""

import sys, cv2, time
from cv2 import VideoCapture

from PIL import Image
from PIL import ImageTk

from ui import FrontEnd

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


class FSM_PACT:
    
    class CamCapture(VideoCapture):
        STATE = 0;
        
        LastRaw = []
        LastRead = []
        LastFrame = []
        Overlay = []
        LastProc = []
        
        HistPlot = []
        HistVals = None
        EstimatedAngle = 0
        
        Cx = 0; Cy = 0
        Skewness = 0
        
        isFrameReady = False
        isOverlayReady = False     
        
        Norm = []      
        Ang = []
        Mag = []
        dX = []
        dY = []
        
        def __init__(self, ID, *args, **kwargs):
            super().__init__(*args, ID, **kwargs)            
            self.T_OVERLAY  = Timer(MASKRATE)
            self.T_LATENCY  = Timer(999)
            self.ID = ID
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
    def __init__(self, Interface, StartIndex=0) -> None: 
    ## Handshake Flags ====================================================
        self.f_DO_RESIZE    = self.ConditionFlag(False);
        self.f_IS_NEW_IMAGE = self.ConditionFlag(False);
    
    ## Configuration parameters ===========================================
        self.Interface = Interface
        
    # >> Pre-initialization variables: ====================================
        self.SPLIT      = 0.2        
        
        self.ZOOM = 1.0       
        self.ALPHA = 0.625
        self.SAMPLES = 4
        self.KERNEL = 5
        self.SOLVER_RES = 256
        self.ANGTHRESH = 20
        
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
        
        self.T_THROTTLE = Timer(FRAMERATE)  
        self.T_DOPLOT   = Timer(PLOTRATE)
        
        self.FPS = 9999;
        
    # >> For TASK 00 | MASTERMIND:
        self.W_LAST = self.W_APP;
        self.H_LAST = self.H_APP;      

        
    ## CV2 camera initialization ==========================================
    # >> Establish camera object(s) and determine what is connected
        self.caps = [ self.CamCapture(StartIndex),self.CamCapture(StartIndex+1) ]
          
        
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
        
    def FindCentroid(self, mag, image,res=128) -> float:  
        centroid = np.zeros(2)
        weight = 0
        h, w = mag.shape[:2]
        mag = cv2.resize(mag,dsize=[res,res])
        for i in range(res):
            for j in range(res):
                if mag[i,j] > self.ALPHA:
                    centroid[0] += i * mag[i,j]
                    centroid[1] += j * mag[i,j]
                    weight += mag[i,j]
        if weight == 0: # Prevent dividing by zero when there are no samples
            xp = int(h/2)
            yp = int(w/2)
        else:
            xp = int(centroid[0] * (1 / weight) / res * h)
            yp = int(centroid[1] * (1 / weight) / res * w)        
        return xp,yp
    
    def EstimateAngle(self,values):
        valsum = 0
        count = 0
        for value in values:
            absval = np.abs(value)
            if absval <= self.ANGTHRESH:
                valsum += value
                count += 1
        if count == 0:
            return 0
        else:
            return valsum / count
        
                
                
    def DrawLines(self,image,Cx,Cy,ang_d):
        ang_r = ang_d * 3.1416 / 180
        h, w = image.shape[:2]        
        pt1x =  0
        pt1y =  int(Cy + (Cx*np.sin(ang_r)))
        
        pt2x =  (w-1)
        pt2y =  int(Cy - ((h-Cx-1)*np.sin(ang_r)))
        
        cv2.line(image, [pt1x,pt1y], [pt2x,pt2y], [255,255,255],thickness=2)
        
        pt1x =  int(Cx - (Cy*np.sin(ang_r)))
        pt1y =  0
                
        pt2x =  int(Cx + ((h-Cy-1)*np.sin(ang_r)))
        pt2y =  (w-1)
        
        cv2.line(image, [pt1x,pt1y], [pt2x,pt2y], [255,255,255],thickness=2)
        
        cv2.circle(image,(Cx,Cy),10,(255,255,255))
        
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
        dX, dY = np.gradient(arr,n_samples)
        Mag = self.Normalize(np.sqrt( (dX*dX)+(dY*dY) ))
        Ang = np.arctan2(dY,dX)
        return Mag, Ang, dX, dY
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
                    HistList.append(x)
                else: pass
        return HistList
        
        
    ## |====================================================================|
    ## |      [TASK 01]                     MASTERMIND (Control Logic)      |
    ## |====================================================================|   
    def TASK_MASTERMIND(self) -> None:
        ReadHeight = self.Interface.ROOT.winfo_height()
        ReadWidth = self.Interface.ROOT.winfo_width()
        if np.abs(ReadHeight - self.H_LAST) + np.abs(ReadWidth - self.W_LAST) > 50:
            self.f_DO_RESIZE.activate() #If window change, resize window
            
            
    ## |====================================================================|
    ## |      [TASK 02]                   POLL GUI (Check for changes)      |
    ## |====================================================================| 
    def TASK_POLL_GUI(self) -> None:
        self.ALPHA = self.Interface.GetAlpha()
        self.KERNEL = self.Interface.GetKernel()
        self.SAMPLES = self.Interface.GetSamples()
    
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
            elif capN.STATE == 2: # SUBSTATE: Final  Processing  
                NewSizing = min(self.W_IMG,self.H_IMG)
                capN.LastFrame = cv2.blur(
                    cv2.resize(
                        self.MakeSquare(
                            cv2.cvtColor(
                                capN.LastRead,
                                cv2.COLOR_BGR2GRAY
                            )
                        ),
                        [NewSizing,NewSizing]
                    ),
                    (self.KERNEL,self.KERNEL)               
                )
                capN.isFrameReady = True # First frame now exists.
                self.f_IS_NEW_IMAGE.activate()
                capN.STATE = 0
    
    
    ## |====================================================================|
    ## |      [TASK 04]            CREATE OVERLAY (Process image data)      |
    ## |====================================================================| 
    def TASK_CREATE_OVERLAY(self, cap) -> None:
        if cap.isActive and cap.isFrameReady:
            doOvr = cap.T_OVERLAY.toc(True)
            if doOvr:
                #print(cap.LastFrame)
                cap.Mag, cap.Ang, cap.dX, cap.dY = self.Gradient(cap.LastFrame,self.SAMPLES)
                cap.Overlay = self.SquareMap(cap.Mag,cap.Ang)
                [cap.Cy,cap.Cx] = self.FindCentroid(cap.Mag,cap.Overlay,self.SOLVER_RES) 
                #cap.Skewness = self.FindAngle(cap.Mag,cap.Ang)#,self.SOLVER_RES)
                #print(cap.ID, cap.Skewness)
                cap.isOverlayReady = True
    
    ## |====================================================================|
    ## |      [TASK 05]            GUI (Run GUI tasks, update, resize)      |
    ## |====================================================================| 
    def TASK_GUI(self) -> None:
        # Perform tkinter tasks instead of getting stuck in loop
        self.Interface.RunUpdate()
        if self.f_DO_RESIZE.shake():
            pass#self.ResizeWindow()
        #self.info_FPS.configure(text=str(np.round(1/self.FPS,0)))
        
    ## |====================================================================|
    ## |      [TASK 06]               UPDATE DISPLAY (Push image data)      |
    ## |====================================================================|     
    def TASK_UPDATE_DISPLAY(self) -> None:        
        if self.f_IS_NEW_IMAGE.check() and self.T_THROTTLE.toc(False):
            self.f_IS_NEW_IMAGE.shake()
            #print(self.T_THROTTLE.tock)
            self.T_THROTTLE.toc(True)
            for i in range(len(self.caps)):
                cap = self.caps[i]
                SPF = cap.T_LATENCY.tic(True)
                self.Interface.SetFPS(i, 1 / (1 if SPF == 0 else SPF) )
                if cap.isActive and cap.isFrameReady:
                    if cap.isOverlayReady:                    
                        cap.LastProc = self.AlphaOver(cap.Overlay,cap.LastFrame,self.ALPHA)
                        self.Interface.SetOffset(i,cap.Cx,cap.Cy)
                        self.DrawLines(cap.LastProc,cap.Cx,cap.Cy,cap.EstimatedAngle)
                    else:
                        self.cap.LastProc = cap.LastFrame
                    #square_size = min(self.W_IMBAR,self.H_IMBAR)
                    w,h = self.Interface.getWindowSize()
                    scaled = cv2.resize(self.caps[i].LastProc,[h,w])#[square_size,square_size])
                    self.Interface.DeployFrame(scaled,i,int(w/2),int(h/2))
                    
        if self.T_DOPLOT.toc(True):
            for i in range(len(self.caps)):
                cap = self.caps[i]
                if cap.isActive and cap.isFrameReady:
                    cap.HistVals = self.makeHistogram(cap.Mag,cap.Ang)
                    self.Interface.DrawHistogram(i,cap.HistVals)
                    cap.EstimatedAngle = self.EstimateAngle(cap.HistVals)
                    self.Interface.SetAngle(i,cap.EstimatedAngle)
                   
        
    def COMMAND_LOOP(self) -> None:
        self.TASK_MASTERMIND()
        self.TASK_POLL_GUI()
        self.TASK_GET_IMAGE(self.caps[0])
        self.TASK_GET_IMAGE(self.caps[1])
        self.TASK_CREATE_OVERLAY(self.caps[0])
        self.TASK_CREATE_OVERLAY(self.caps[1])
        self.TASK_GUI()
        self.TASK_UPDATE_DISPLAY()


    def __del__(self) -> None:
        self.root.destroy()

if __name__ == "__main__":
    print('Initializing Stolle PACT...')
    FE = FrontEnd()    
    PACT = FSM_PACT(FE,1)    
    while True:
        PACT.COMMAND_LOOP()
        Q = PACT.caps[0].Skewness
        H = FE.debugitem
    
# https://patorjk.com/software/taag/#p=about&f=Pagga&t=&x=none&v=4&h=4&w=80&we=false