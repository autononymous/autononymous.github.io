# -*- coding: utf-8 -*-
##|=========================================================================|##
##|                                                                         |##
##|                            ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                              |##
##|                           ▒▒             ▒▒                             |##
##|                        ▒▒   █████████████   ▒▒                          |##
##|                      ▒▒▒  █████████████████  ▒▒▒                        |##
##|                     ▒▒▒▒ ████████   ████████ ▒▒▒▒                       |##
##|                     ▒▒▒  ████████             ▒▒▒                       |##
##|                     ▒▒▒  ███████████████████  ▒▒▒                       |##
##|                     ▒▒▒             ████████  ▒▒▒                       |##
##|                     ▒▒▒▒ ████████   ████████ ▒▒▒▒                       |##
##|                      ▒▒▒  █████████████████  ▒▒▒                        |##
##|                        ▒▒   █████████████   ▒▒                          |##
##|                           ▒▒             ▒▒                             |##
##|                            ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                              |##
##|                                                                         |##
##|=========================================================================|##
##|                          ░█░█░▀█▀░░░░█▀█░█░█                            |##
##|                          ░█░█░░█░░░░░█▀▀░░█░                            |##
##|                          ░▀▀▀░▀▀▀░▀░░▀░░░░▀░                            |##
##|=========================================================================|##
##|            :                                                            |##
##|   PROJECT <|> Project "PACT" -- Plate Alignment Calibration Tool        |##
##|            :  AKA the "Pre-Registration Fixture"                        |##
##|            :                                                            |##
##|   COMPANY <|> STOLLE MACHINERY COMPANY, LLC                             |##
##|            :  6949 S. POTOMAC STREET                                    |##
##|            :  CENTENNIAL, COLORADO, 80112                               |##
##|            :                                                            |##
##|      FILE <|> pact_ui.py                                                |##
##|            :                                                            |##
##|    AUTHOR <|> Ryan Kissinger                                            |##
##|            :                                                            |##
##|   VERSION <|> '-' - 09/29/25                                            |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|   PURPOSE <|> Generating User Interface for the system.                 |##
##|           <|> Receiving and deploying new camera image updates.         |##
##|           <|> Displaying calculated data.                               |##
##|           <|> Allowing user to change calculation parameters and        |##
##|            :  control image acquisition process.                        |##
##|            :                                                            |##
##|   LICENSE <|> Copyright (C) Stolle Machinery Company                    |##
##|            :  All Rights Reserved                                       |##
##|            :                                                            |##
##|           <|> This source code is protected under international         |##
##|            :  copyright law. All rights reserved and protected by the   |##
##|            :  copyright holders. This file is confidential and only     |##
##|            :  available to authorized individuals with the permission   |##
##|            :  of the copyright holders.  If you encounter this file     |##
##|            :  and do not have permission, please contact the copyright  |##
##|            :  holders and delete this file.                             |##
##|            :                                                            |##
##|=========================================================================|##

# Standard functions
import tkinter as tk
from tkinter import (ttk, font)
from PIL import (Image, ImageTk)
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Custom Functions
from pact_mastermind import ConditionFlag

##|=========================================================================|##
##|            :                                                            |##
##|    CLASS  <:> PACT_UI                                                   |##
##|            :     Controls for the user interface of the program.        |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
##|                         << GENERAL FUNCTIONS >>                         |##
##|      def  -:-    window_exit : Safely close window on [X] press.        |##
##|-------------------------------------------------------------------------|##
##|                    << GETTER AND SETTER FUNCTIONS >>                    |##
##|      def  -:-    loadConfig : Load configuration & deploy theme.        |##
##|      def  -:-    loadImage : Load image into tk.Canvas on screen.       |##
##|      def  -:-    UpdateData : Update information in the right sidebar.  |##
##|      def  -:-    GetAlpha : Return alpha from slider.                   |##
##|      def  -:-    SetAlpha : Set alpha value on slider.                  |##
##|      def  -:-    GetFreezeAlpha : Return alpha freeze from slider.      |##
##|      def  -:-    SetFreezeAlpha : Set alpha freeze value on slider.     |##
##|-------------------------------------------------------------------------|##
class PACT_UI:    
    isInit = False
    
    def window_exit(self):
    #     close = tk.messagebox.askyesno("Exit?", "Are you sure you want to exit?")
    #     if close:
        self.ROOT.destroy()  
    
    ## |----------------------------------------------------------------------|
    ## |                         SETTER FUNCTIONS    
    ## |----------------------------------------------------------------------|
    def loadConfig(self,cfg=None) -> None:
        # PURPOSE  <|> Set current theme of program. If elements are
        #           |  initialized, then deploy changes.
        #    ARGS  <|> cfg -> Loaded JSON object
        # RETURNS  <|> None  
        if cfg is not None: self.CONFIG = cfg;                                  # If no config arg, use existing config
        self.S = self.CONFIG.style                                              # STY for STYLE
        self.P = self.CONFIG.param                                              # PRM for PARAMETER
        self.F = self.CONFIG.fonts        
        if self.isInit: self.deployTheme();
        
    def loadImage(self, mst,src): 
        return ImageTk.PhotoImage( master=mst, image=Image.open(src),size=(250,150))
    
    def UpdateData(self, cam, datum, value, color=None):
        if datum < 0 or datum > self.DATUMENTRIES-1:
            print("[WARN] Entry index out of range for UpdateData()."); return
        if cam < 0 or cam > self.N_CAMERAS:
            print("[WARN] Camera index out of range for UpdateData()."); return
        self.CAMDATUM[cam][datum][1].configure(text=str(value))
        if color is not None:
            self.CAMDATUM[cam][datum][1].configure(fg=color)
        
    def GetAlpha(self) -> int:
        return int( (1.0 - self.WIDGETS[self.WI['guides']][0].get()) * 255 )
    
    def SetAlpha(self,value) -> None:
        if value < 0: value = 0;
        if value > 255: value = 255;
        self.WIDGETS[self.WI['guides']][0].set(1-(value/255.0))
        
    def GetFreezeAlpha(self) -> float:
        return self.WIDGETS[self.WI['freeze']][0].get()
    
    def SetFreezeAlpha(self,value) -> None:
        if value < 0: value = 0.0;
        if value > 1: value = 1.0
        self.WIDGETS[self.WI['freeze']][0].set(value)
     
    ##|---------------------------------------------------------------------|##
    ##|                 >> EXPORTING IMAGE TO TK FORMAT <<                  |##
    ##|---------------------------------------------------------------------|##
    def deployImage(self, img, master_elem) -> int: #array     
        h, w = img.shape[:2]
        PIL_img = Image.fromarray(img)
        TkImage = ImageTk.PhotoImage(PIL_img, master=master_elem)  
        master_elem.create_image(int(w/2),int(h/2),image=TkImage,anchor=tk.CENTER)
        master_elem.image = TkImage
        master_elem.configure(width=w,height=h)
        
        
    ## |----------------------------------------------------------------------|
    ## |                         COMMON FUNCTIONS    
    ## |----------------------------------------------------------------------|    
    def runUpdate(self) -> None:
        if not self.isInit: print("[ERROR] Cannot update uninitialized GUI."); return 
        self.ROOT.update_idletasks()
        self.ROOT.update()
        return
    
    def deployTheme(self) -> None: #TODO
        # PURPOSE  <|> Deploy styles to tkinter windows and objects.
        #    ARGS  <|> None
        # RETURNS  <|> None  
        pass
    
    def Freeze(self) -> None:
        self.isFreezeActive = True
        print('Freezing image.')
    
    def Unfreeze(self) -> None: 
        self.isFreezeActive = False
        print('Unfreezing image.')   
    
    def buildProgram(self) -> None:
        # PURPOSE  <|> Build program in initialization state.
        #    ARGS  <|> None
        # RETURNS  <|> None 
        if self.isInit: print("[WARN] Program already built."); return           # Check if program was already built
        self.ROOT = tk.Tk()                                                     # Initialize tkinter
        self.ROOT.title(f"Stolle PACT Interface [Version {self.P.version}]")    # Give the window a name
        self.ROOT.geometry(f"{self.P.window_x}x{self.P.window_y}")              # Set initial window size
       
        self.winit = tk.Label(   master  = self.ROOT, 
                            text    = "Initializing...", 
                            bg      = self.S.L2, 
                            fg      = self.S.h1,
                            font    = self.F.h2() )
        self.winit.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
       
        self.ROOT.update_idletasks()
        self.ROOT.update()
       
        self.winit.destroy()
       
        
        # |>> MAIN PROGRAM STRUCTURE
        # |------------------------------------------------------------
        self.ROOT.columnconfigure( 0, weight=0, uniform=350 )
        self.ROOT.columnconfigure( 1, weight=1, minsize=500 )  
        self.ROOT.rowconfigure(0, weight=1)
        
        self.ROOT.protocol("WM_DELETE_WINDOW", self.window_exit)
        
        parent = self.ROOT
        self.PANEL = [
           tk.Frame(    master  = parent, 
                        bg      = self.S.L1, 
                        borderwidth=1 ),
           tk.Frame(    master  = parent, 
                        bg      = self.S.L0, 
                        borderwidth=1,
                        pady    = 10,
                        padx    = 10)]; elem = self.PANEL        
        for i in range(len(elem)): elem[i].grid( row=0, column=i, sticky="nsew")
        
        # |>> CONTROL / SIDEBAR OF PROGRAM
        # |------------------------------------------------------------
        parent = self.PANEL[0]
        self.SIDEBAR = [
            tk.Frame(   master  = parent, 
                        bg      = self.S.L2, 
                        padx    = 10,
                        pady    = 10)]; elem = self.SIDEBAR       
        for i in range(len(elem)): elem[i].pack( fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        # Building sidebar elements ------------------------------------------|
        self.logo = self.loadImage(self.SIDEBAR[0],self.S.logoURL)
        parent = self.SIDEBAR[0]
        self.WIDGETS = [
        # >> Stolle Logo...
            [tk.Label(   master  = parent, 
                        image   = self.logo, 
                        bg      = self.S.L2),0,0,3,1,"nsew",None],
        # >> Program Identifier (Subtitle)...
            [tk.Label(   master  = parent, 
                        text    = "PACT Alignment Tool", 
                        bg      = self.S.L2, 
                        fg      = self.S.h1,
                        font    = self.F.h1() ),1,0,3,1,"nsew",None],
        # >> ALPHA LEVEL control...
            [tk.Label(   master  = parent, 
                        text    = "Guide Controls", 
                        bg      = self.S.L3, 
                        fg      = self.S.h1,
                        font    = self.F.h2() ),2,0,3,1,"nsew",None],
            [tk.Label(   master  = parent,
                        text    = "Guide Visibility  ",
                        font    = self.F.h2(),
                        bg      = self.S.L2,
                        fg      = self.S.h2),3,0,1,1,"e",None],
            [tk.Scale(   master  = parent,
                        sliderlength = 20,
                        from_   = 0,
                        to      = 1,
                        length  = 150,
                        resolution=.01,
                        tickinterval=0.25,
                        orient  = tk.HORIZONTAL,
                        bg      = self.S.L2,
                        fg      = self.S.p,),3,1,2,1,"nsew",'guides'],
            [tk.Label(   master  = parent, 
                        text    = "Image Control", 
                        bg      = self.S.L3, 
                        fg      = self.S.h1,
                        font    = self.F.h2() ),4,0,3,1,"nsew",None],            
            [tk.Label(   master  = parent,
                        text    = "Freeze Capture",
                        font    = self.F.h2(),
                        bg      = self.S.L2,
                        fg      = self.S.h2),5,0,1,1,"w",None],
            [tk.Button(  master  = parent,
                        text    = " Freeze ",
                        command = self.Freeze),5,1,1,1,"ns",None],
            [tk.Button(  master  = parent,
                        text    = "  Thaw  ",
                        command = self.Unfreeze),5,2,1,1,"ns",None],
            [tk.Label(   master  = parent,
                        text    = "Freeze Opacity  ",
                        font    = self.F.h2(),
                        bg      = self.S.L2,
                        fg      = self.S.h2),6,0,1,1,"w",None],
            [tk.Scale(   master  = parent,
                        sliderlength = 20,
                        from_   = 0,
                        to      = 1,
                        length  = 150,
                        resolution=.01,
                        tickinterval=0.25,
                        orient  = tk.HORIZONTAL,
                        bg      = self.S.L2,
                        fg      = self.S.p,),6,1,2,1,"nsew",'freeze']
            ]; elem = self.WIDGETS   
        
        self.WI = {}
        indx = 0;
        for w, row_, col_, cspan_, rspan_, stick_, alias in self.WIDGETS:            
            w.grid( row=row_, column=col_, columnspan=cspan_, rowspan=rspan_, sticky=stick_, pady=10)
            if alias is not None:
                self.WI.update({alias:indx})
            indx += 1;
        
        
        # |>> CAMERA ELEMENTS
        # |------------------------------------------------------------
        parent = self.PANEL[1]
        # >> Drawing each camera window as a row item...
        self.CAMWINDOWS = []
        for i in range(self.N_CAMERAS): 
            self.CAMWINDOWS.append(
                tk.Frame(   master = parent,
                            bg      = self.S.L3, 
                            padx    = 25,
                            pady    = 25));  
            self.PANEL[1].rowconfigure(i, weight=1, minsize=200)        
        self.PANEL[1].columnconfigure( 0, weight=1, minsize=200 ) 
        elem = self.CAMWINDOWS       
        for i in range(len(elem)): elem[i].grid( row=i, column=0, sticky="nsew")
        
        # >> Establishing space for camera inside each camera window row
        self.CAMFEED = []
        for i in range(self.N_CAMERAS):
            parent = self.CAMWINDOWS[i]
            self.CAMFEED.append(
                tk.Canvas(  master = parent,
                            bg      = self.S.L1, 
                            width   = 350,
                            height  = 350));  
        elem = self.CAMFEED
        for i in range(len(elem)): elem[i].grid( row=0, column=0, sticky="n")         
        self.CAMFEED[i].columnconfigure( 0, weight=0, minsize=350 )

        # >> Placing data window...
        self.CAMDATA = []
        for i in range(self.N_CAMERAS):
            parent = self.CAMWINDOWS[i]
            self.CAMDATA.append(
                tk.Frame(   master = parent,
                            bg      = self.S.L2, 
                            padx    = 10,
                            pady    = 10));  
        elem = self.CAMDATA
        for i in range(len(elem)): 
            elem[i].grid( row=0, column=1, sticky="nsew")
            elem[i].columnconfigure( 0, weight=1, minsize=100 )
            elem[i].columnconfigure( 1, weight=1, minsize=100 )
        
        for i in range(self.N_CAMERAS):                 
            self.CAMWINDOWS[i].columnconfigure( 0, weight=1, minsize=350 ) 
            self.CAMWINDOWS[i].columnconfigure( 1, weight=0, uniform=400 )    
          
        self.CAMDATUM = [[]]
        for i in range(self.N_CAMERAS):  
            parent = self.CAMDATA[i]
            self.CAMDATUM.append([])
            for j in range(len(self.DATUMNAMES)):
                self.CAMDATUM[i].append([
                    # >> These are couplets of DATUM, VALUE as labels
                    tk.Label(   master  = parent, 
                                text    = self.DATUMNAMES[j], 
                                bg      = self.S.L2, 
                                fg      = self.S.h1,
                                font    = self.F.h2() ),
                    tk.Label(   master  = parent, 
                                text    = self.DATUMVALUES[j],
                                bg      = self.S.L2, 
                                fg      = self.S.h1,
                                font    = self.F.p() ),
                ]);
                
                
                #print(self.CAMDATUM)
            n_entries = len(self.CAMDATUM[i])
            n_pairs = len(self.CAMDATUM[i][0])
            #print("entries: "+str(n_entries) + "\npairs: "+ str(n_pairs))
            for j in range(n_entries):
                # for k in range(n_pairs):
                #     self.CAMDATUM[i][j][k].grid( row=j, column=k, sticky="nsew")
                self.CAMDATUM[i][j][0].grid( row=j, column=0, sticky="e")
                self.CAMDATUM[i][j][1].grid( row=j, column=1, sticky="w")
                    
        
        
        return
    ## |----------------------------------------------------------------------|
    ## |                        CLASS INITIALIZATION   
    ## |----------------------------------------------------------------------|
    def __init__(self,CONFIG,cameras=2,data_names=None) -> None:  
        if data_names is None:
            self.DATUMNAMES     = [ 'Status',    "FPS", "Center",  "Angle" ] 
            self.DATUMVALUES    = [     '--',     "--",     "--",     "--" ]
        else:
            self.DATUMNAMES = []
            self.DATUMVALUES = []
            for name in data_names:
                self.DATUMNAMES.append(name)
                self.DATUMVALUES.append("--")
                
        self.DATUMENTRIES   = len(self.DATUMNAMES)        
        self.N_CAMERAS      = cameras
        
        self.isFreezeActive = False
        
        self.CONFIG = CONFIG
        self.loadConfig()                                            # Load theme into STYLE.
        
        self.buildProgram()           
        
        #> Initialization is complete.
        self.isInit = True
            
    # Set program style from configuration
    
    

##|=========================================================================|##
##|              S T A N D A L O N E      E X E C U T I O N                 |##
##|=========================================================================|##
    
if __name__ == "__main__":
    from config import CONFIG
    UI_test = PACT_UI(CONFIG())