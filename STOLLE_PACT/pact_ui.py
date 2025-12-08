 # -*- coding: utf-8 -*-
"""
@file pact_ui.py
@author Ryan Kissinger

@brief Handles user interface deployment, updates, and user interactions.
"""
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
    BOOLTHRESH = 32
    
    def window_exit(self):
        close = tk.messagebox.askyesno("Exit?", "Are you sure you want to exit?")
        if close:
            self.RUNNING = False
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
        
    def GetBlur(self) -> int:
        return self.WIDGETS[self.WI['blur']][0].get()
    
    def SetBlur(self,value) -> None:
        if value < 0: value = 0;
        if value > 12: value = 12
        self.WIDGETS[self.WI['blur']][0].set(value)    
        
    def IsBoolMode(self) -> bool:           
        return 'selected' in self.WIDGETS[self.WI['doBool']][0].state()
    
    
    def SetBoolMode(self,value) -> None:
        self.WIDGETS[self.WI['blur']][0].set(value and True)
        
    def GetBoolThresh(self) -> int:
        value = self.WIDGETS[self.WI['bool']][0].get()   
        return 1 if value < 1 else (254 if value > 254 else value)
        
    def SetBoolThresh(self,value) -> None:
        if value < self.BOOLTHRESH: value = self.BOOLTHRESH;
        if value > 255-self.BOOLTHRESH: value = 255-self.BOOLTHRESH;
        self.WIDGETS[self.WI['bool']][0].set(value) 
        
    def BoundBoolSpan(self):
        # limit to bounds of 0 to 255 with respect to current bool thresh value        
        BOOL_THRESH = self.WIDGETS[self.WI['bool']][0].get() 
        limiter = int(min(254-BOOL_THRESH, BOOL_THRESH+1))
        
    def GetBoolSpan(self) -> int:
        return self.WIDGETS[self.WI['boolSpan']][0].get()
        
    def SetBoolSpan(self,value) -> None:        
        self.WIDGETS[self.WI['boolSpan']][0].set(1 if value < 1 else (self.BOOLTHRESH if value > self.BOOLTHRESH else value))
        
        
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
                        fg      = self.S.p,),6,1,2,1,"nsew",'freeze'],
            [tk.Label(   master  = parent,
                        text    = "Image Blurring ",
                        font    = self.F.h2(),
                        bg      = self.S.L2,
                        fg      = self.S.h2),7,0,1,1,"w",None],
            [tk.Scale(   master  = parent,
                        sliderlength = 20,
                        from_   = 1,
                        to      = 12,
                        length  = 150,
                        resolution=1,
                        tickinterval=1,
                        orient  = tk.HORIZONTAL,
                        bg      = self.S.L2,
                        fg      = self.S.p,),7,1,2,1,"nsew",'blur'],
            [tk.Label(   master  = parent, 
                        text    = "Image Control", 
                        bg      = self.S.L3, 
                        fg      = self.S.h1,
                        font    = self.F.h2() ),8,0,3,1,"nsew",None],
            [tk.Label(   master  = parent,
                        text    = "Boolean Mode?  ",
                        font    = self.F.h2(),
                        bg      = self.S.L2,
                        fg      = self.S.h2),9,0,1,1,"w",None],
            [ttk.Checkbutton( master = parent),9,1,2,1,"w","doBool"],
            [tk.Label(   master  = parent,
                        text    = "Boolean Level ",
                        font    = self.F.h2(),
                        bg      = self.S.L2,
                        fg      = self.S.h2),10,0,1,1,"w",None],
            [tk.Scale(   master  = parent,
                        sliderlength = 20,
                        from_   = self.BOOLTHRESH,
                        to      = 255-self.BOOLTHRESH,
                        length  = 150,
                        resolution=1,
                        orient  = tk.HORIZONTAL,
                        bg      = self.S.L2,
                        fg      = self.S.p,),10,1,2,1,"nsew",'bool'],
            [tk.Label(   master  = parent,
                        text    = "Boolean Span   ",
                        font    = self.F.h2(),
                        bg      = self.S.L2,
                        fg      = self.S.h2),11,0,1,1,"w",None],
            [tk.Scale(   master  = parent,
                        sliderlength = 20,
                        from_   = 1,
                        to      = self.BOOLTHRESH,
                        length  = 150,
                        resolution=1,
                        orient  = tk.HORIZONTAL,
                        bg      = self.S.L2,
                        fg      = self.S.p,),11,1,2,1,"nsew",'boolSpan']
            
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
        
        self.RUNNING = True
        
        self.buildProgram()           
        
        #> Initialization is complete.
        self.isInit = True
            
    # Set program style from configuration
    
##|=========================================================================|##
##|            :                                                            |##
##|    CLASS  <:> PACT_UI_V2                                                |##
##|           <:>    Controls for the user interface of the program. Second |##
##|            :     iteration of the award-winning program interface that  |##
##|            :     has captured millions of hearts around the world.      |##      
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
##|                         << GENERAL FUNCTIONS >>                         |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
##|                    << GETTER AND SETTER FUNCTIONS >>                    |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
class PACT_UI2:    
    '''! Class that contains all necessary functions for updating the UI.
         As the system is a Finite State Machine, this handles little of the logic:
         it is intended to carry out the will of the "Mastermind" main.py.'''
    # Not initialized yet at instance deployment.
    isInit = False      
    # For later handshake with Mastermind that does the logic. These signify
    # that a button has been pressed, denoting request from the user.    
    doCapture = ConditionFlag();    # Capture button
    doRelease = ConditionFlag();    # Release button
    doItemDelete = ConditionFlag(); # Delete Entry button
    doItemLoad = ConditionFlag();   # Load Entry button
    
    def window_exit(self):
        '''! Closing confirmation [Y/N].'''
        close = tk.messagebox.askyesno("Exit?", "Are you sure you want to exit?")
        # If close, stop running and destroy instance of Tk.
        if close:
            self.RUNNING = False
            self.ROOT.destroy() 
    
    class WidgetItem:
        '''! Subclass that organizes widgets better than Tk does.'''
        class IndexedEntry:
            '''Subsubclass containing widgets' information.'''
            def __init__(self,index,widget):
                self.index = index
                self.widget = widget
            def updateIndex(self,index):
                self.index = index
            def updateWidget(self,widget):
                self.widget = widget
        
        # When unspecified, defaults padx and pady to these parameters.
        DefaultPadding = [10,10]
        # Initialized values before definition in __init__().
        parent  = None
        child   = []
        weight  = 0
        
        def __init__(self,widget,indices,parent=None,spans=None,sticky=None,padding=None,alias=None,configdata=None,ipadding=None):
            '''! Initializing function for WidgetItem. Sets up the standard 
                 parameters of a widget to avoid extraneous code.
                 @param widget      The actual TK widget as an argument to be stored.
                 @param indices     Index of this widget's position as [row,column].
                 @param parent      The parent widget, otherwise None if top level.
                 @param spans       The span of a widget in grid space: [rowspan,colspan].
                 @param sticky      The behavior of the widget containing what cardinal direction it sticks to.
                 @param padding     External padding/spacing from other elements: [x,y].
                 @param alias       An optional name for the widget.
                 @param configdata  Deprecated.
                 @param ipadding    Internal padding/spacing from other elements: [x,y].'''
            self.parent = parent;
            self.widget = widget;
            if self.parent is not None: 
                self.parent.child.append(self);  
                self.hindex = self.parent.hindex + 1            
            else:
                self.hindex = 0   
            # Aggregate entry into a master indexed deployment list.
            # I set it up this way if I wanted to hold off deployment until
            # after creating all widgets.
            self.entry = self.IndexedEntry(self.hindex,self.widget)
            # Turning arguments into lasting data like any conversation with my fiancee.
            self.row = indices[0]
            self.col = indices[1]
            self.rspan = 1 if spans is None else spans[0]
            self.cspan = 1 if spans is None else spans[1]
            self.stick = 'nsew' if sticky is None else sticky
            self.xpad = self.DefaultPadding[0] if padding is None else padding[0]
            self.ypad = self.DefaultPadding[1] if padding is None else padding[1]
            self.xipad = 0 if ipadding is None else ipadding[0]
            self.yipad = 0 if ipadding is None else ipadding[1]
            self.alias = alias  
            # @TODO @DEPRECATE
            if configdata is None:
                self.config = [[1],[1]]
            else: self.config = configdata;
        
        def SetInGrid(self,rparams=None,cparams=None):
            '''! When called, place the widget into the grid with the 
                 initialized parameters.
                 @param rparams  2D array of row parameters [[rowindex,weight,minsize,uniform],[...]]
                 @param rparams  2D array of column parameters [[colindex,weight,minsize,uniform],[...]]'''
                 
            self.widget.grid( 
                row        = self.row,
                column     = self.col,
                rowspan    = self.rspan,
                columnspan = self.cspan,
                sticky     = self.stick,
                padx       = self.xpad,
                pady       = self.ypad,
                ipadx      = self.xipad,
                ipady      = self.yipad) 
            if rparams is not None:
                for paramset in rparams:               
                    if   len(paramset) > 3: self.widget.rowconfigure(paramset[0],weight=paramset[1],minsize=paramset[2],uniform=paramset[3]); 
                    elif len(paramset) > 2: self.widget.rowconfigure(paramset[0],weight=paramset[1],minsize=paramset[2]);
                    elif len(paramset) > 1: self.widget.rowconfigure(paramset[0],weight=paramset[1]);
                    else:                   self.widget.rowconfigure(paramset[0],weight=1);
            if cparams is not None:
                for paramset in cparams:
                    if   len(paramset) > 3: self.widget.columnconfigure(paramset[0],weight=paramset[1],minsize=paramset[2],uniform=paramset[3]);
                    elif len(paramset) > 2: self.widget.columnconfigure(paramset[0],weight=paramset[1],minsize=paramset[2]);
                    elif len(paramset) > 1: self.widget.columnconfigure(paramset[0],weight=paramset[1]);
                    else:                   self.widget.columnconfigure(paramset[0],weight=1);
                    
        def ReturnToGrid(self):
            '''! Bring back into the grid if hidden.'''
            self.widget.grid()
            
        def HideFromGrid(self):
            '''! Hide from view in the grid.'''
            self.widget.grid_remove()
    
    def loadConfig(self,cfg=None) -> None:
        '''! Load configurations from config.json for styles.
             @param cfg  Option for custom config from text.'''
        if cfg is not None: self.CONFIG = cfg;
        self.S = self.CONFIG.style
        self.P = self.CONFIG.param
        self.F = self.CONFIG.fonts        
        # If already initalized and loading newer config, deploy it.
        if self.isInit: self.deployTheme()
    
    def loadImage(self, mst,src,w=None,h=None): 
        '''! Load image into Tk.
             @param mst  Master widget.
             @param src  Source of image as a /path/.
             @param w    Width forcing resize of image.
             @param h    Height forcing resize of image.
             @return  Image object as PhotoImage.'''
        # Both w and h must be present to resize image.
        if (w is None) or (h is None):            
            return ImageTk.PhotoImage( master=mst, image=Image.open(src))
        else:
            return ImageTk.PhotoImage( master=mst, image=Image.open(src).resize((w,h)))
      
    def deployImage(self, img, master_elem) -> None:   
        '''! Deploys image inside given element.
             @param img  The image, in array form.
             @param master_elem  The element to modify/append image.'''
        h, w = img.shape[:2]
        PIL_img = Image.fromarray(img)
        TkImage = ImageTk.PhotoImage(PIL_img, master=master_elem)  
        master_elem.create_image(int(w/2),int(h/2),image=TkImage,anchor=tk.CENTER)
        master_elem.image = TkImage
        master_elem.configure(width=w,height=h)
        
    def runUpdate(self) -> None:
        '''! Perform TK's requisite update stuff.'''
        if not self.isInit: print("[ERROR] Cannot update uninitialized GUI."); return 
        self.ROOT.update_idletasks()
        self.ROOT.update()
        return
        
    # FUNCTIONS FOR DISPLAYING SHEETS IN SIDEBAR
    def setSheet1(self, event):
        '''! Show the first sheet: INDEX. Hide the others.'''
        self.W1222.HideFromGrid(); self.W1212.widget.config(bg=self.S.Inactive);
        self.W1223.HideFromGrid(); self.W1213.widget.config(bg=self.S.Inactive);
        self.W1224.HideFromGrid(); self.W1214.widget.config(bg=self.S.Inactive);
        self.W1221.SetInGrid([[0,1]],[[0,1]])
        self.W1211.widget.config(bg=self.S.Active)
    def setSheet2(self, event):
        '''! Show the second sheet: VISION. Hide the others.'''
        self.W1221.HideFromGrid(); self.W1211.widget.config(bg=self.S.Inactive);
        self.W1223.HideFromGrid(); self.W1213.widget.config(bg=self.S.Inactive);
        self.W1224.HideFromGrid(); self.W1214.widget.config(bg=self.S.Inactive);
        self.W1222.SetInGrid([[0,1]],[[0,1]])
        self.W1212.widget.config(bg=self.S.Active)
    def setSheet3(self, event):   
        '''! Show the third sheet: GUIDES. Hide the others.'''   
        self.W1221.HideFromGrid(); self.W1211.widget.config(bg=self.S.Inactive);
        self.W1222.HideFromGrid(); self.W1212.widget.config(bg=self.S.Inactive);
        self.W1224.HideFromGrid(); self.W1214.widget.config(bg=self.S.Inactive);
        self.W1223.SetInGrid([[0,1]],[[0,1]])
        self.W1213.widget.config(bg=self.S.Active)
    def setSheet4(self, event):
        '''! Show the fourth sheet: OTHER. Hide the others.'''
        self.W1221.HideFromGrid(); self.W1212.widget.config(bg=self.S.Inactive);
        self.W1222.HideFromGrid(); self.W1212.widget.config(bg=self.S.Inactive);
        self.W1223.HideFromGrid(); self.W1213.widget.config(bg=self.S.Inactive);
        self.W1224.SetInGrid([[0,1]],[[0,1]])
        self.W1214.widget.config(bg=self.S.Active)
        
    # FUNCTIONS FOR HIGHER-LEVEL INTELLIGENCE OPERATIONS
    def handleCapture(self) -> None:
        '''! Handshake flag for button press.'''
        self.doCapture.activate()
        print("Capture")
        return
    def handleRelease(self) -> None:
        '''! Handshake flag for button press.'''
        self.doRelease.activate()
        print("Release")
        return
    
    def handleDelete(self) -> None:
        '''! Handshake flag for button press.'''
        self.doItemDelete.activate()
        print("Delete")
        return
    def handleLoad(self) -> None:
        '''! Handshake flag for button press.'''
        self.doItemLoad.activate()
        print("Load")
        return
    
    # @TODO switch controls for image adjustments.
    

    class ClickData:    
        '''! Organizes information on where window was clicked, and whether
             it was a right or left click.'''
        # What no information looks like for a click descriptor.
        empty = [None,None]     
        def reset(self):      
            '''! Reset all data to None couplets.
                 @var datum   First click setting cross point.
                 @var orient  Second click setting angle from datum.
                 @var data    Array organizing data into indexable form.'''
            self.datum = self.empty
            self.orient = self.empty
            self.data = [self.datum,self.orient]
        def __init__(self,res=3):
            '''! Initializing function for ClickData.
                 @param res  Resolution to display data.'''
            self.reset()    
            # Make sure exponent makes sense.
            res = 4 if res > 4 else 0 if res < 0 else res
            self.resolution = np.power(10,res)
        def getPositions(self):
            '''! Retrieve both DATUM and ORIENT coordinates.'''
            if self.datum[0] is None or self.datum[1] is None: 
                print("WARN: No left click values exist.")            
            if self.orient[0] is None or self.orient[1] is None:
                print("WARN: No right click values exist.")                   
            return [self.datum,self.orient]
        def setDatum(self,x,y):
            '''! Set the value of DATUM and truncate to desired resolution.'''
            self.datum = [int(x*self.resolution)/self.resolution,int(y*self.resolution)/self.resolution]
            self.data = [self.datum,self.orient]
        def setOrient(self,x,y):
            '''! Set the value of ORIENT and truncate to desired resolution.'''
            self.orient = [int(x*self.resolution)/self.resolution,int(y*self.resolution)/self.resolution]
            self.data = [self.datum,self.orient]
        #@TODO check if return is None to ensure all data is accounted for.
    
    # Organizing instances of ClickData class to [left,right] camera windows.        
    SelectData = [ClickData(),ClickData()]
        
    def getxy(self, event, clickType, windowType, widget):
        '''! Get the x- and y- coordinates of a mouse click, and set the
             new data accordingly.
             @param event  Tied to callback function.
             @param clickType  0=left, 1=right click.
             @param windowType  0=left, 1=right camera window.
             @param widget  The widget to query for width and height.'''
        w = event.x/widget.winfo_width()
        h = event.y/widget.winfo_height()
        #name = ["left","right"]
        if clickType == 0:
            self.SelectData[windowType].setDatum(w,h)
        elif clickType == 1:
            self.SelectData[windowType].setOrient(w,h)
        else:
            #print('ClickData not set.')
            return
        ##uncomment for debug
        #print(f"Mouse {name[clickType]} click on {name[windowType]} window. ")
        #print(f"New data input is {self.SelectData[windowType].getPositions()[clickType]} for ")
        
        
            
        
    def buildProgram(self,window_dims=None) -> None:
        '''! Builds out the program in order of parented level.'''
    #|-----------------------------------------------------------------------|#
    #|                        MASTER TK BUILD OUTLINE                        |#
    #|-----------------------------------------------------------------------|#
    #|            : Program will follow the build order in the tree          |#
    #|            :   shown below. Element ID established by level.          |#
    #|-----------------------------------------------------------------------|#
    #|                                                                       |#
    #|       L00 L01 L02 L03 L04 ...                                         |#
    #|                                                                       |#
    #|       [1] Program Canvas                                              |#
    #|        ┣━━[1] Controls Canvas                                         |#
    #|        ┃   ┃                                                          |#
    #|        ┃   ┣━━[1] Controls Header                                     |#
    #|        ┃   ┃   ┣━━[1] Logo Container                                  |#
    #|        ┃   ┃   ┃   ┣━━[1] Logo Object (e.g. ID 11111)                 |#
    #|        ┃   ┃   ┗━━[2] Program Info Container                          |#
    #|        ┃   ┃       ┣━━[1] Program Title                               |#
    #|        ┃   ┃       ┗━━[2] Program Subtitle (e.g. ID 11122)            |#
    #|        ┃   ┃                                                          |#
    #|        ┃   ┗━━[2] Controls Box                                        |#
    #|        ┃       ┣━━[1] Tab Container                                   |#
    #|        ┃       ┃   ┣━━[1] First Tab                                   |#
    #|        ┃       ┃   ┣━━[2] Second Tab                                  |#
    #|        ┃       ┃   ┣━━[3] Third Tab                                   |#
    #|        ┃       ┃   ┗━━[4] Fourth Tab                                  |#
    #|        ┃       ┃                                                      |#
    #|        ┃       ┗━━[2] Controls Sheets                                 |#
    #|        ┃           ┣━━[1] First Sheet (ACTIVE)                        |#
    #|        ┃           ┊   ┗[+] {Contents TBD}                            |#
    #|        ┃           ┣━━[2] Second Sheet (INACTIVE)                     |#
    #|        ┃           ┊   ┗[+] {Contents TBD}                            |#
    #|        ┃           ┣━━[3] Third Sheet (INACTIVE)                      |#
    #|        ┃           ┊   ┗[+] {Contents TBD}                            |#
    #|        ┃           ┗━━[4] Fourth Sheet (INACTIVE)                     |#
    #|        ┃               ┗[+] {Contents TBD}                            |#
    #|        ┃                                                              |#
    #|        ┗━━[2]>Scopes/Cameras Canvas                                   |#
    #|            ┣━━[1] Left Scope Canvas                                   |#
    #|            ┃   ┣━━[1] Left Camera Window                              |#
    #|            ┃   ┗━━[2] Left Camera Data Canvas                         |#
    #|            ┃       ┗[+] {Contents TBD}                                |#
    #|            ┃                                                          |#
    #|            ┗━━[2] Right Scope Canvas                                  |#
    #|                ┣━━[1] Right Camera Window                             |#
    #|                ┗━━[2] Right Camera Data Canvas                        |#
    #|                    ┗[+] {Contents TBD}                                |#
    #|                                                                       |#
    #|-----------------------------------------------------------------------|#  

        # Do nothing if program was already built
        if self.isInit: print("[WARN] Program already built."); return      
        # Initialize tkinter as ROOT
        self.ROOT = tk.Tk()                                                    
        self.ROOT.title(f"Stolle PACT Interface [Version {self.P.version}]") 
        # Set window size to default size
        if window_dims is None:
            self.ROOT.geometry(f"{self.P.window_x}x{self.P.window_y}")
        else:
            self.ROOT.geometry(f"{window_dims[0]}x{window_dims[1]}")
        # Update tasks first
        self.runUpdate()
        # First configuration of program rows and columnms
        self.ROOT.columnconfigure( 0, weight=1)
        self.ROOT.rowconfigure(0, weight=1)
        
    #|-----------------------------------------------------------------------|#        
    #|     LEVEL 00 INITIALIZATION                                           |#
    #|-----------------------------------------------------------------------|#      
        self.W = self.WidgetItem(
            tk.Frame( master=self.ROOT, bg=self.S.L0, borderwidth=1 ),
            [0,0],
            None)
        self.W.SetInGrid([[0,1]],[[0,1,200],[1,20]])
        
        
    #|-----------------------------------------------------------------------|#        
    #|     LEVEL 01 INITIALIZATION                                           |#
    #|-----------------------------------------------------------------------|#   
        # [1] PROGRAM CONTROLS PANEL
        #   ROOT > PANEL
        self.W1 = self.WidgetItem(
            tk.Frame( master=self.W.widget, bg=self.S.L0, borderwidth=1),
            [0,0],
            self.W)
        
        # [2] CAMERA SCOPES CANVAS
        #   ROOT > SCOPES
        self.W2 = self.WidgetItem(
            tk.Frame( master=self.W.widget, bg=self.S.L0, borderwidth=1),
            [0,1],
            self.W)
        
        # LEVEL 01 DEPLOYMENT
        self.W1.SetInGrid([[0,0,100,100],[1,1]],[[0,1,360]])  
        self.W2.SetInGrid([[0,1]],[[0,1],[1,1]]) 
    
    #|-----------------------------------------------------------------------|#        
    #|     LEVEL 02 INITIALIZATION                                           |#
    #|-----------------------------------------------------------------------|# 
        # [11] PROGRAM HEADER
        #   ROOT > PANEL > HEADER
        self.W11 = self.WidgetItem( # Program Title
            tk.Frame( master=self.W1.widget, bg=self.S.L1, borderwidth=0),
            [0,0],
            self.W1)
        
        # [12] PROGRAM CONTROLS
        #   ROOT > PANEL > CONTROLS
        self.W12 = self.WidgetItem( # Program Controls
            tk.Frame( master=self.W1.widget, bg=self.S.L1, borderwidth=0),
            [1,0],
            self.W1)
        
        # [21] LEFT SCOPE CANVAS
        #   ROOT > SCOPES > LSCOPE
        self.W21 = self.WidgetItem( # L.Scope Canvas
            tk.Frame( master=self.W2.widget, bg=self.S.L1, borderwidth=0),
            [0,0],
            self.W2,
            sticky="new")
        
        # [22] RIGHT SCOPE CANVAS
        #   ROOT > SCOPES > RSCOPE
        self.W22 = self.WidgetItem( # R.Scope Canvas
            tk.Frame( master=self.W2.widget, bg=self.S.L1, borderwidth=0),
            [0,1],
            self.W2,
            sticky="new")    
        
        # LEVEL 02 DEPLOYMENT
        self.W11.SetInGrid([[0,0,200,200]],[[0,1,250]])
        self.W12.SetInGrid([[0,1]],[[0,0,50,50],[1,1,250]])
        self.W21.SetInGrid([[0,1],[0,1]],[[0,1]])
        self.W22.SetInGrid([[0,1],[0,1]],[[0,1]])
        
        # INITIALIZE LOGO
        self.logo = self.loadImage(self.W11.widget,self.S.logoURL,300,200)
        
    #|-----------------------------------------------------------------------|#        
    #|     LEVEL 03 INITIALIZATION                                           |#
    #|-----------------------------------------------------------------------|#     
        # [111] PROGRAM IDENTIFIER/LOGO
        #   ROOT > PANEL > HEADER > LOGO
        self.W111 = self.WidgetItem(
            tk.Label( master=self.W11.widget, image=self.logo, bg=self.S.L1),
            [0,0],
            self.W11,
            sticky="ew")
        
        # [121] TAB CONTAINER
        #   ROOT > PANEL > CONTROLS > TABS
        self.W121 = self.WidgetItem(
            tk.Frame( master=self.W12.widget, bg=self.S.L2, borderwidth=0),
            [0,0],
            self.W12,
            sticky="ne",
            padding=[0,0])
        
        # [122] SHEET CONTAINER
        #   ROOT > PANEL > CONTROLS > SHEETS
        self.W122 = self.WidgetItem(
            tk.Frame( master=self.W12.widget, bg=self.S.L1, borderwidth=0),#, highlightbackground="white", highlightthickness=2),
            [0,1],
            self.W12,
            sticky="nsew",
            padding=[0,0])   
        
        # [211] LEFT SCOPE CAMERA FRAME
        #   ROOT > SCOPES > L_SCOPE > FRAME
        self.W211 = self.WidgetItem(
            tk.Frame( master=self.W21.widget, bg=self.S.L1, borderwidth=0),
            [0,0],
            self.W21,
            sticky="n")  
        
        # [212] LEFT SCOPE METADATA
        #   ROOT > SCOPES > L_SCOPE > DATA
        self.W212 = self.WidgetItem(
            tk.Frame( master=self.W21.widget, bg=self.S.L2, borderwidth=0),
            [1,0],
            self.W21,
            sticky="n")  
        
        # [221] RIGHT SCOPE CAMERA FRAME
        #   ROOT > SCOPES > R_SCOPE > FRAME
        self.W221 = self.WidgetItem(
            tk.Frame( master=self.W22.widget, bg=self.S.L1, borderwidth=0),
            [0,0],
            self.W22,
            sticky="n")
        
        # [222] RIGHT SCOPE METADATA
        #   ROOT > SCOPES > R_SCOPE > DATA
        self.W222 = self.WidgetItem(
            tk.Frame( master=self.W22.widget, bg=self.S.L2, borderwidth=0),
            [1,0],
            self.W22,
            sticky="n")                
        
        # LEVEL 03 DEPLOYMENT
        self.W111.SetInGrid([[0,0,80,80]],[[0,1]])
        self.W121.SetInGrid([[0,1],[1,1],[2,1],[3,1]],[[0,0,20]])
        self.W122.SetInGrid([[0,1]],[[0,1]])
        
        self.W211.SetInGrid([[0,1,150]],[[0,1,150]])
        self.W221.SetInGrid([[0,1,150]],[[0,1,150]])        
        
        # DATA ENTRY SIZES *********************************************************************
        self.W212.SetInGrid([[0,1],[1,1]],[[0,0,50],[1,0,50],[2,0,50],[3,0,50],[4,0,50],[5,0,50]])
        self.W222.SetInGrid([[0,1],[1,1]],[[0,0,50],[1,0,50],[2,0,50],[3,0,50],[4,0,50],[5,0,50]])
        
        # SIZE OF TABS (as an image)
        TabSz = [35,105]
        
        # INITIALIZE TAB IMAGES
        self.tab1 = self.loadImage(self.W121.widget,self.S.tab1,TabSz[0],TabSz[1])        
        self.tab2 = self.loadImage(self.W121.widget,self.S.tab2,TabSz[0],TabSz[1])        
        self.tab3 = self.loadImage(self.W121.widget,self.S.tab3,TabSz[0],TabSz[1])        
        self.tab4 = self.loadImage(self.W121.widget,self.S.tab4,TabSz[0],TabSz[1])
        
        
    #|-----------------------------------------------------------------------|#        
    #|     LEVEL 04 INITIALIZATION                                           |#
    #|-----------------------------------------------------------------------|# 
        # [1221] SHEET ONE: INDEX/MAIN
        #   ROOT > PANEL > CONTROLS > SHEETS > S_MAIN
        self.W1221 = self.WidgetItem(
            tk.Frame( master=self.W122.widget, bg=self.S.L2),
            [0,0],
            self.W122,
            sticky="nsew") 
        
        # [1222] SHEET TWO: VISION
        #   ROOT > PANEL > CONTROLS > SHEETS > S_VISION
        self.W1222 = self.WidgetItem( # Sheet Two
            tk.Frame( master=self.W122.widget, bg=self.S.L2),
            [0,0],
            self.W122,
            sticky="nsew") 
        
        # [1223] SHEET THREE: GUIDES
        #   ROOT > PANEL > CONTROLS > SHEETS > S_GUIDES
        self.W1223 = self.WidgetItem( # Sheet Three
            tk.Frame( master=self.W122.widget, bg=self.S.L2),
            [0,0],
            self.W122,
            sticky="nsew") 
        
        # [1224] SHEET FOUR: OTHER
        #   ROOT > PANEL > CONTROLS > SHEETS > S_OTHER
        self.W1224 = self.WidgetItem( # Sheet Four
            tk.Frame( master=self.W122.widget, bg=self.S.L2),
            [0,0],
            self.W122,
            sticky="nsew") 
        
        # SHEET DEPLOYMENT (sheets before tabs so they can be referenced)
        self.W1221.SetInGrid([[0,1]],[[0,1]])
        self.W1222.SetInGrid([[0,1]],[[0,1]])
        self.W1223.SetInGrid([[0,1]],[[0,1]])
        self.W1224.SetInGrid([[0,1]],[[0,1]])
        
        
        # [1211] TAB ONE: INDEX/MAIN
        #   ROOT > PANEL > CONTROLS > TABS > T_MAIN
        self.W1211 = self.WidgetItem( # Tab One
            tk.Label( master=self.W121.widget, image=self.tab1, bg=self.S.L2),
            [0,0],
            self.W121,
            sticky="e",
            padding=[0,10]) 
        
        # [1212] TAB TWO: VISION
        #   ROOT > PANEL > CONTROLS > TABS > T_VISION
        self.W1212 = self.WidgetItem( # Tab Two
            tk.Label( master=self.W121.widget, image=self.tab2, bg=self.S.L2),
            [1,0],
            self.W121,
            sticky="e",
            padding=[0,10]) 
        
        # [1213] TAB THREE: GUIDES
        #   ROOT > PANEL > CONTROLS > TABS > T_GUIDES
        self.W1213 = self.WidgetItem( # Tab Three
            tk.Label( master=self.W121.widget, image=self.tab3, bg=self.S.L2),
            [2,0],
            self.W121,
            sticky="e",
            padding=[0,10]) 
        
        # [1214] TAB FOUR: OTHER
        #   ROOT > PANEL > CONTROLS > TABS > T_OTHER
        self.W1214 = self.WidgetItem( # Tab Four
            tk.Label( master=self.W121.widget, image=self.tab4, bg=self.S.L2),
            [3,0],
            self.W121,
            sticky="e",
            padding=[0,10]) 
        
        # BINDING TAB FUNCTIONS TO ONCLICK() EVENT
        self.W1211.widget.bind('<Button-1>', self.setSheet1)
        self.W1212.widget.bind('<Button-1>', self.setSheet2)
        self.W1213.widget.bind('<Button-1>', self.setSheet3)
        self.W1214.widget.bind('<Button-1>', self.setSheet4)         
        # SHEET 01 IS ACTIVE AT PROGRAM INITIALIZATION.
        self.W1211.widget.config(bg=self.S.Active)    
        
        # TAB DEPLOYMENT        
        self.W1211.SetInGrid([[0,1]],[[0,1]])
        self.W1212.SetInGrid([[0,1]],[[0,1]])
        self.W1213.SetInGrid([[0,1]],[[0,1]])
        self.W1214.SetInGrid([[0,1]],[[0,1]])
        
        
        # [2211] LEFT CAMERA IMAGE
        #   ROOT > SCOPES > L_SCOPE > FRAME > IMAGE
        self.W2111 = self.WidgetItem(
            tk.Canvas( master=self.W211.widget, bg=self.S.L1),
            [0,0],
            self.W211,
            sticky="n") 
                
        # [2221] RIGHT CAMERA IMAGE
        #   ROOT > SCOPES > R_SCOPE > FRAME > IMAGE
        self.W2211 = self.WidgetItem(
            tk.Canvas( master=self.W221.widget, bg=self.S.L1),
            [0,0],
            self.W221,
            sticky="n") 
        
        
        # [2121] LEFT CAMERA DATA HEADER
        #   ROOT > SCOPES > L_SCOPE > DATA > HEADER
        self.W2121 = self.WidgetItem(
            tk.Label( master=self.W212.widget, text="Left Camera", bg=self.S.L2, font=self.F.h2(), fg="white"),
            [0,0],
            self.W212,
            sticky="n",
            spans=[1,6])  
        # [2122] 
        #   ROOT > SCOPES > L_SCOPE > DATA > T_FPS
        self.W2122 = self.WidgetItem(
            tk.Label( master=self.W212.widget, text="FPS", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [1,0],
            self.W212,
            sticky="n",
            spans=[1,2]) 
        # [2123] 
        #   ROOT > SCOPES > L_SCOPE > DATA > FPS
        self.W2123 = self.WidgetItem(
            tk.Label( master=self.W212.widget, text="XXX", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [1,2],
            self.W212,
            sticky="n",
            spans=[1,4]) 
        # [2124] 
        #   ROOT > SCOPES > L_SCOPE > DATA > T_DIST
        self.W2124 = self.WidgetItem(
            tk.Label( master=self.W212.widget, text="OFFSET", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [2,0],
            self.W212,
            sticky="n",
            spans=[1,2]) 
        # [2125] 
        #   ROOT > SCOPES > L_SCOPE > DATA > DIST_X
        self.W2125 = self.WidgetItem(
            tk.Label( master=self.W212.widget, text="XXX", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [2,2],
            self.W212,
            sticky="n",
            spans=[1,2]) 
        # [2126] 
        #   ROOT > SCOPES > L_SCOPE > DATA > DIST_Y
        self.W2126 = self.WidgetItem(
            tk.Label( master=self.W212.widget, text="YYY", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [2,4],
            self.W212,
            sticky="n",
            spans=[1,2]) 
        # [2127] 
        #   ROOT > SCOPES > L_SCOPE > DATA > DIST_X
        self.W2127 = self.WidgetItem(
            tk.Label( master=self.W212.widget, text="SKEWNESS", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [3,0],
            self.W212,
            sticky="n",
            spans=[1,2]) 
        # [2128] 
        #   ROOT > SCOPES > L_SCOPE > DATA > DIST_Y
        self.W2128 = self.WidgetItem(
            tk.Label( master=self.W212.widget, text="RRR", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [3,2],
            self.W212,
            sticky="n",
            spans=[1,4])
        
        # [2221] LEFT CAMERA DATA HEADER
        #   ROOT > SCOPES > R_SCOPE > DATA > HEADER
        self.W2221 = self.WidgetItem(
            tk.Label( master=self.W222.widget, text="Right Camera", bg=self.S.L2, font=self.F.h2(), fg="white"),
            [0,0],
            self.W222,
            sticky="n",
            spans=[1,6]) 
        # [2222] 
        #   ROOT > SCOPES > R_SCOPE > DATA > T_FPS
        self.W2222 = self.WidgetItem(
            tk.Label( master=self.W222.widget, text="FPS", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [1,0],
            self.W222,
            sticky="n",
            spans=[1,2]) 
        # [2223] 
        #   ROOT > SCOPES > R_SCOPE > DATA > FPS
        self.W2223 = self.WidgetItem(
            tk.Label( master=self.W222.widget, text="XXX", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [1,2],
            self.W222,
            sticky="n",
            spans=[1,4]) 
        # [2224] 
        #   ROOT > SCOPES > R_SCOPE > DATA > T_DIST
        self.W2224 = self.WidgetItem(
            tk.Label( master=self.W222.widget, text="POSITION", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [2,0],
            self.W222,
            sticky="n",
            spans=[1,2]) 
        # [2225] 
        #   ROOT > SCOPES > R_SCOPE > DATA > DIST_X
        self.W2225 = self.WidgetItem(
            tk.Label( master=self.W222.widget, text="XXX", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [2,2],
            self.W222,
            sticky="n",
            spans=[1,2]) 
        # [2226] 
        #   ROOT > SCOPES > R_SCOPE > DATA > DIST_Y
        self.W2226 = self.WidgetItem(
            tk.Label( master=self.W222.widget, text="YYY", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [2,4],
            self.W222,
            sticky="n",
            spans=[1,2]) 
        # [2227] 
        #   ROOT > SCOPES > L_SCOPE > DATA > DIST_X
        self.W2227 = self.WidgetItem(
            tk.Label( master=self.W222.widget, text="SKEWNESS", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [3,0],
            self.W222,
            sticky="n",
            spans=[1,2]) 
        # [2228] 
        #   ROOT > SCOPES > L_SCOPE > DATA > DIST_Y
        self.W2228 = self.WidgetItem(
            tk.Label( master=self.W222.widget, text="RRR", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [3,2],
            self.W222,
            sticky="n",
            spans=[1,4])
        
        
        # BIND INSPECTION CONTROLS FOR INTERACTING WITH IMAGES (LEFT, RIGHT CLICK)
        self.W2111.widget.bind('<Button-1>', lambda event: self.getxy(event, 0, 0, self.W2111.widget))
        self.W2111.widget.bind('<Button-3>', lambda event: self.getxy(event, 1, 0, self.W2111.widget))
        self.W2211.widget.bind('<Button-1>', lambda event: self.getxy(event, 0, 1, self.W2211.widget)) 
        self.W2211.widget.bind('<Button-3>', lambda event: self.getxy(event, 1, 1, self.W2211.widget))
                
        # CAMERA IMAGE DEPLOYMENT
        self.W2111.SetInGrid([[0,1]],[[0,1]])
        self.W2211.SetInGrid([[0,1]],[[0,1]])
        # CAMERA DATA DEPLOYMENT
        self.W2121.SetInGrid([[0,1]],[[0,1]])
        self.W2122.SetInGrid([[0,1]],[[0,1]])
        self.W2123.SetInGrid([[0,1]],[[0,1]])
        self.W2124.SetInGrid([[0,1]],[[0,1]])
        self.W2125.SetInGrid([[0,1]],[[0,1]])
        self.W2126.SetInGrid([[0,1]],[[0,1]])
        self.W2127.SetInGrid([[0,1]],[[0,1]])
        self.W2128.SetInGrid([[0,1]],[[0,1]])
        
        self.W2221.SetInGrid([[0,1]],[[0,1]])
        self.W2222.SetInGrid([[0,1]],[[0,1]])
        self.W2223.SetInGrid([[0,1]],[[0,1]])
        self.W2224.SetInGrid([[0,1]],[[0,1]])
        self.W2225.SetInGrid([[0,1]],[[0,1]])
        self.W2226.SetInGrid([[0,1]],[[0,1]])
        self.W2227.SetInGrid([[0,1]],[[0,1]])
        self.W2228.SetInGrid([[0,1]],[[0,1]])


    #|-----------------------------------------------------------------------|#        
    #|     LEVEL 05 INITIALIZATION                                           |#
    #|-----------------------------------------------------------------------|# 
        # [12211] SHEET ONE CANVAS
        #   ROOT > PANEL > CONTROLS > SHEETS > S_MAIN > CANVAS
        self.W12211 = self.WidgetItem( # Sheet One
            tk.Frame( master=self.W1221.widget, bg=self.S.L2, borderwidth=0),
            #tk.Label( master=self.W1221.widget, text="This is Sheet One", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [0,0],
            self.W1221,
            sticky="n",
            ipadding=[10,10])
        
        # TODO! SHEET 2 **************
        self.W12221 = self.WidgetItem( # Sheet Two
            tk.Label( master=self.W1222.widget, text="This is Sheet Two", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [0,0],
            self.W1222,
            sticky="n")
        
        # TODO! SHEET 3 **************
        self.W12231 = self.WidgetItem( # Sheet Three
            tk.Label( master=self.W1223.widget, text="This is Sheet Three", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [0,0],
            self.W1223,
            sticky="n")
        
        # TODO! SHEET 4 **************
        self.W12241 = self.WidgetItem( # Sheet Four
            tk.Label( master=self.W1224.widget, text="This is Sheet Four", bg=self.S.L2, font=self.F.h1(), fg="white"),
            [0,0],
            self.W1224,
            sticky="n")

        # LEVEL 05 DEPLOYMENT
        self.W12211.SetInGrid([[0,0],[1,0]],[[0,1]])
        self.W12221.SetInGrid([[0,1]],[[0,1]])
        self.W12231.SetInGrid([[0,1]],[[0,1]])
        self.W12241.SetInGrid([[0,1]],[[0,1]])
        # HIDE INACTIVE SHEETS
        self.W1222.HideFromGrid()
        self.W1223.HideFromGrid()
        self.W1224.HideFromGrid()
        
    #|-----------------------------------------------------------------------|#        
    #|     LEVEL 06 INITIALIZATION                                           |#
    #|-----------------------------------------------------------------------|# 
        # [122111] MAIN CONTROL BOX
        #   ROOT > PANEL > CONTROLS > SHEETS > S_MAIN > CANVAS > CTRL_BOX
        self.W122111 = self.WidgetItem(
            tk.Frame( master=self.W12211.widget, bg=self.S.L1, borderwidth=0, highlightbackground="white", highlightthickness=2),
            [0,0],
            self.W12211,
            sticky="new",
            padding=[0,10])
        
        # [122112] PREVIOUS CAPTURES BOX
        #   ROOT > PANEL > CONTROLS > SHEETS > S_MAIN > CANVAS > HISTORY
        self.W122112 = self.WidgetItem(
            tk.Frame( master=self.W12211.widget, bg=self.S.L1, borderwidth=0, highlightbackground="white", highlightthickness=2),
            [1,0],
            self.W12211,
            sticky="new",
            padding=[0,10])
        
        # LEVEL 06 DEPLOYMENT
        self.W122111.SetInGrid([[0,0,10,10],[1,0],[2,0],[3,0],[4,0]],[[0,1],[1,1]])
        self.W122112.SetInGrid([[0,1,10,10],[1,0],[2,0]],[[0,1],[0,1]])
        
    #|-----------------------------------------------------------------------|#        
    #|     LEVEL 07 INITIALIZATION                                           |#
    #|-----------------------------------------------------------------------|# 
        # [1221111] CONTROL BOX HEADER
        #   ... > SHEETS > S_MAIN > CANVAS > CTRL_BOX > HEADER
        self.W1221111 = self.WidgetItem(
            tk.Label( master=self.W122111.widget, text="Main Controls", bg=self.S.L1, font=self.F.h1(), fg="white"),
            [0,0],
            self.W122111,
            spans=[1,2],
            sticky="ew",
            padding=[20,0],
            ipadding=[0,0])
        
        # [1221112] CAPTURE BUTTON
        #   ... > SHEETS > S_MAIN > CANVAS > CTRL_BOX > B_CAPTURE
        self.W1221112 = self.WidgetItem( # S1 C1 Button for Capture
            tk.Button( master=self.W122111.widget, text="Capture", command=self.handleCapture),
            [1,0],
            self.W122111,
            sticky="n",
            padding=[10,10],
            ipadding=[20,0]) 
        
        # [1221113] RELEASE BUTTON
        #   ... > SHEETS > S_MAIN > CANVAS > CTRL_BOX > B_RELEASE
        self.W1221113 = self.WidgetItem( # S1 C1 Button for Release
            tk.Button( master=self.W122111.widget, text="Release", command=self.handleRelease),
            #tk.Label( master=self.W12211.widget, text="B2", bg=self.S.L3, font=self.F.h1(), fg="white"),
            [1,1],
            self.W122111,
            sticky="n",
            padding=[10,10],
            ipadding=[20,0]) 
        
        # [1221114] STATUS TEXT
        #   ... > SHEETS > S_MAIN > CANVAS > CTRL_BOX > T_STATUS
        self.W1221114 = self.WidgetItem( # S1 C1 Condition One
            tk.Label( master=self.W122111.widget, text="> Awaiting capture ...", bg=self.S.L1, fg="white", font=self.F.p()),
            [2,0],
            self.W122111,
            spans=[1,2],
            sticky="w",
            padding=[20,0],
            ipadding=[0,20])
                
        # [1221121] HISTORY BOX HEADER
        #   ... > SHEETS > S_MAIN > CANVAS > HISTORY > HEADER
        self.W1221121 = self.WidgetItem( # S1 C2 Header
            tk.Label( master=self.W122112.widget, text="Capture History", bg=self.S.L1, font=self.F.h1(), fg="white"),
            [0,0],
            self.W122112,
            sticky="ew",
            spans=[1,2],
            padding=[0,0],
            ipadding=[0,0])         
        
        # [1221122] HISTORY LISTBOX
        #   ... > SHEETS > S_MAIN > CANVAS > HISTORY > LISTBOX
        self.W1221122 = self.WidgetItem( # S1 C2 Listbox
            tk.Listbox( master=self.W122112.widget,bg=self.S.L3, fg="white",selectmode=tk.SINGLE),
            [1,0],
            self.W122112,
            sticky="new",
            spans=[1,2],
            padding=[20,10],
            ipadding=[0,0])         
        ## TODO! PLACEHOLDERS *****************
        self.W1221122.widget.insert(1,"CAP_251201_142506")
        self.W1221122.widget.insert(2,"CAP_251203_150003")   
        
        # [1221123] DELETE BUTTON
        #   ... > SHEETS > S_MAIN > CANVAS > HISTORY > B_DELETE
        self.W1221123 = self.WidgetItem( # S1 C1 Button for Capture
            tk.Button( master=self.W122112.widget, text="Delete", command=self.handleDelete),
            [2,0],
            self.W122112,
            sticky="w",
            spans=[1,1],
            padding=[20,10],
            ipadding=[20,0]) 
        
        # [1221124] LOAD BUTTON
        #   ... > SHEETS > S_MAIN > CANVAS > HISTORY > B_DELETE
        self.W1221124 = self.WidgetItem( # S1 C1 Button for Release
            tk.Button( master=self.W122112.widget, text="Load", command=self.handleLoad),
            [2,1],
            self.W122112,
            sticky="w",
            spans=[1,1],
            padding=[20,10],
            ipadding=[20,0]) 

        #________________________________________________
        # LEVEL 07 DEPLOYMENT
        self.W1221111.SetInGrid([[0,1]],[[0,1]])
        self.W1221112.SetInGrid([[0,1]],[[0,1]])
        self.W1221113.SetInGrid([[0,1]],[[0,1]])
        self.W1221114.SetInGrid([[0,1]],[[0,1]])
        self.W1221121.SetInGrid([[0,1]],[[0,1]])
        self.W1221122.SetInGrid([[0,0,100,100]],[[0,1]])
        self.W1221123.SetInGrid([[0,1]],[[0,1]])
        self.W1221124.SetInGrid([[0,1]],[[0,1]])
        
    #|-----------------------------------------------------------------------|#        
    #|     LEVEL 08 INITIALIZATION                                           |#
    #|-----------------------------------------------------------------------|# 
        


    #|-----------------------------------------------------------------------|#        
    #|     PROGRAMMER-FRIENDLY DEFINITIONS  [ left window , right window ]   |#
    #|-----------------------------------------------------------------------|#
        # Frames per second count
        self.ctrl_FPS = [self.W2123.widget,self.W2223.widget]
        # X-position to display
        self.ctrl_Px  = [self.W2125.widget,self.W2225.widget]
        # Y-position to display
        self.ctrl_Py  = [self.W2126.widget,self.W2226.widget]
        # Rotational skew to display
        self.ctrl_R   = [self.W2128.widget,self.W2228.widget]
        

    #|-----------------------------------------------------------------------|#        
    #|     END OF UI CONSTRUCTION                                            |#
    #|-----------------------------------------------------------------------|# 
        self.ROOT.update_idletasks()
        self.ROOT.update()
        
    def UpdateMetadata(self,camID,parameter,value):
        '''! '''
        disp = "-" if value is None else str(value)
        if parameter == "FPS":
            self.ctrl_FPS[camID].configure(text=(disp + " FPS"))
        elif parameter == "Px":
            self.ctrl_Px[camID].configure(text=disp)
        elif parameter == "Py":
            self.ctrl_Py[camID].configure(text=disp)
        elif parameter == "R":
            self.ctrl_R[camID].configure(text=(disp + "\u00B0"))
        return
        
        
    def __init__(self,CONFIG) -> None:  
        '''! Initializing function of PACT_UI.
             @param CONFIG  the configuration data.'''
        self.CONFIG = CONFIG
        self.loadConfig()
        self.RUNNING = True
        self.buildProgram([1400,800]) 
        
        self.isInit = True

##|=========================================================================|##
##|              S T A N D A L O N E      E X E C U T I O N                 |##
##|=========================================================================|##
    
if __name__ == "__main__":
    '''! Standalone testing of User Interface functionality. This is
         not called by pact_main.py.'''
    from pact_config import CONFIG
    UI_test = PACT_UI2(CONFIG())