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
##|                     ░█▀█▀█░█▀█░▀█▀░█▀█░░░░█▀█░█░█                       |##
##|                     ░█░█░█░█▀█░░█░░█░█░░░░█▀▀░░█░                       |##
##|                     ░▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀░░▀░░░░▀░                       |##
##|=========================================================================|##
##|            :                                                            |##
##|   PROJECT <|> Project "PACT" -- Plate Alignment Calibration Tool        |##
##|            :  AKA the "Pre-Registration Fixture"                        |##
##|            :                                                            |##
##|   COMPANY <|> STOLLE MACHINERY COMPANY, LLC                             |##
##|            :  6949 S. POTOMAC STREET                                    |##
##|            :  CENTENNIAL, COLORADO, 80112                               |##
##|            :                                                            |##
##|      FILE <|> pact_main.py                                              |##
##|            :                                                            |##
##|    AUTHOR <|> Ryan Kissinger                                            |##
##|            :                                                            |##
##|   VERSION <|> '-' - 11/20/25                                            |##
##|            :    > "Initial project demo for approval from management.   |##
##|            :    >  Contains basic UI elements and Normal overlay,       |##
##|            :    >  as well as Boolean Mode, Freeze, and Blur."          |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|   PURPOSE <|> Setting up structure of the Finite State Machine.         |##
##|           <|> Connecting camera(s), user interface, and other modules   |##
##|            :  for deployment in the FSM structure.                      |##
##|           <|> Setting up the "mastermind": the task that makes all the  |##
##|            :  programmatical decisions while the other tasks simply     |##
##|            :  act on them.                                              |##
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
##|                          FUNCTION DEFINITIONS                           |##
##|-------------------------------------------------------------------------|##
##|   TASK_USER_INTERFACE (User Interface Control)                          |##
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|   PURPOSE <|>                                                           |##
##|            :                                                            |##
##|            :                                                            |##
##|            :                                                            |##
##|            :                                                            |##
##|=========================================================================|##

# Standard functions
import sys, cv2, time
import numpy as np
import json

# Custom functions
from pact_ui import PACT_UI
from pact_config import CONFIG
from pact_camera import PACT_Cam

class DebugConsole:
    def __init__(self):
        self.str = ""
        self.t_init = time.time()
    def send(self, message):
        t = time.strftime("%H:%M:%S", time.gmtime())
        msg = str(message)
        print(f"{t} |\t> {msg}") 

##|=========================================================================|##
##|            :                                                            |##
##|    CLASS  <:> FSM_PACT                                                  |##
##|            :     A finite state machine / task-state system ordering    |##
##|            :     tasks across different functions.                      |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##

class FSM_PACT():    
    isInit = False
    isRunning = True       
    
    class Profile:        
                    
        def saveProfile(self,dic=None):
            if dic is None: dic = self.PROFILE;
            json_str = json.dumps(dic, indent=4)
            with open("profile.json", "w") as f:
                f.write(json_str)
            return
        
        def updateProfile(self, paramName, value):
            if paramName in self.PROFILE.keys():
                self.PROFILE[paramName] = value
                self.saveProfile()
                self.DC.send("Program profile updated: " + str(paramName) + " is now " + str(value) + ".")
                return
            else:
                self.DC.send('Unable to update profile: "' + str(paramName) + '" does not exist.')
                return
        
        def newProfile(self) -> None:
            self.PROFILE = {
                "User":None,
                "AlphaLevel":128,
                "FreezeLevel":128,
                "BlurLevel":4,
                "BoolLevel":128,
                "DoBool":False,
                "BoolSpan":5
            }
            self.saveProfile(self.PROFILE)
            return
        
        def __init__(self):
            self.DC = DebugConsole()
            errstr = ""
            try:
                errstr = "File does not exist. "
                with open('profile.json', 'r') as f: self.PROFILE = json.load(f) 
                for param in "User","AlphaLevel","FreezeLevel","BlurLevel","BoolLevel","DoBool","BoolSpan":
                    errstr = "Corrupted PROFILE document with entry " + param + ". "    
                    test = self.PROFILE[param]                
                self.DC.send("Profile loaded. ")
            except:                
                self.DC.send("Unable to load profile: " + errstr + "Generating default profile.")  
                self.newProfile()
       
            
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|     FUNC  <:> INITIALIZATION                                            |##
##|            :     > [DC ] Initialize debug console.                      |##
##|            :     > [CFG] Load in configuations from config JSON file.   |##
##|            :     > [CAM] For each camera, create a camera object.       |##
##|            :     > [GUI] Create an instance of the tkinter GUI.         |##
##|            :                                                            |##
##|            :  ARGUMENTS                                                 |##
##|            :     > cameras - Number of cameras to read.                 |##
##|            :     > startindex - Camera start index (e.g. skip webcam)   |##
##|            :                                                            |##
##|            :  RETURNS                                                   |##
##|            :     > none                                                 |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##

    def __init__(self,cameras,startindex) -> None:  
#     >> Debug Console  
        self.DC = DebugConsole()
        self.DC.send("Starting STOLLE PACT...")
        self.n_cameras = cameras
        self.DC.send("Loading in configuration parameters...")
        self.CFG = CONFIG()         
        self.DC.send("Building graphical user interface...")
        self.GUI = PACT_UI(self.CFG,self.n_cameras)
            
        self.CAM = []
        for i in range(self.n_cameras):    
            self.DC.send(f"Initializing camera 0{i}...") 
            self.CAM.append(PACT_Cam(i,startindex))     
#     >> Create empty array for Alpha overlay
        self.GUI.SetAlpha(self.CAM[0].THRESHOLD)  
#     >> Set truth state for several booleans
    
        self.DC.send("Loading user configuration parameters...")
        self.PRF = self.Profile()                
        self.GUI.SetAlpha(self.PRF.PROFILE['AlphaLevel'])
        self.GUI.SetBlur(self.PRF.PROFILE['BlurLevel'])
        self.GUI.SetFreezeAlpha(self.PRF.PROFILE['FreezeLevel'])
        self.GUI.SetBoolMode(self.PRF.PROFILE['DoBool'])
        self.GUI.SetBoolThresh(self.PRF.PROFILE['BoolLevel'])
        self.GUI.SetBoolSpan(self.PRF.PROFILE['BoolSpan'])
                
        self.ALPHA = self.GUI.GetAlpha()
        self.FREEZE_ALPHA = self.GUI.GetFreezeAlpha()
        self.KERNEL = self.GUI.GetBlur()
        self.DO_BOOL_MASK = self.GUI.IsBoolMode()
        self.BOOL_THRESHOLD = self.GUI.GetBoolThresh()
        self.BOOL_SPAN = self.GUI.GetBoolSpan()

        self.isNewFreeze = True            
        self.isInit = True      
        
        self.passnum = 0      
        
        self.DC.send("Initialization complete.") 
            
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|     FUNC  <:> TASK_POLL_GUI                                             |##
##|            :     > Retrieve values from settings in the User Interface. |##
##|            :     > Deploy these settings to the visual/camera system.   |##
##|            :                                                            |##
##|            :  ARGUMENTS                                                 |##
##|            :     > none                                                 |##
##|            :                                                            |##
##|            :  RETURNS                                                   |##
##|            :     > none                                                 |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
    def TASK_POLL_GUI(self) -> None:
        # Get new parameter values
        ALPHA = self.GUI.GetAlpha()
        FREEZE_ALPHA = self.GUI.GetFreezeAlpha()
        KERNEL = self.GUI.GetBlur()
        DO_BOOL_MASK = self.GUI.IsBoolMode()
        BOOL_THRESHOLD = self.GUI.GetBoolThresh()
        BOOL_SPAN = self.GUI.GetBoolSpan()
        
        if ALPHA != self.ALPHA: 
            self.ALPHA = ALPHA
            self.PRF.updateProfile("AlphaLevel",ALPHA)
        if FREEZE_ALPHA != self.FREEZE_ALPHA: 
            self.FREEZE_ALPHA = FREEZE_ALPHA
            self.PRF.updateProfile("FreezeLevel",FREEZE_ALPHA)
        if KERNEL != self.KERNEL:
            self.KERNEL = KERNEL
            self.PRF.updateProfile("BlurLevel",KERNEL)
        if DO_BOOL_MASK != self.DO_BOOL_MASK:
            self.DO_BOOL_MASK = DO_BOOL_MASK
            self.PRF.updateProfile("DoBool",DO_BOOL_MASK)
        if BOOL_THRESHOLD != self.BOOL_THRESHOLD: 
            self.BOOL_THRESHOLD = BOOL_THRESHOLD
            self.PRF.updateProfile("BoolLevel",BOOL_THRESHOLD)
        if BOOL_SPAN != self.BOOL_SPAN: 
            self.BOOL_SPAN = BOOL_SPAN
            self.PRF.updateProfile("BoolSpan",BOOL_SPAN)
        
        for cap in range(self.n_cameras):
            self.CAM[cap].THRESHOLD = self.ALPHA
            self.CAM[cap].FREEZE_ALPHA = self.FREEZE_ALPHA
            self.CAM[cap].KERNEL = self.KERNEL
            self.CAM[cap].DO_BOOL_MASK = self.DO_BOOL_MASK
            self.CAM[cap].BOOL_THRESHOLD = self.BOOL_THRESHOLD
            self.CAM[cap].BOOL_SPAN = self.BOOL_SPAN
           
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|     FUNC  <:> TASK_CREATE_OVERLAY                                       |##
##|            :     > From processed image data, generate a new overlay.   |##
##|            :                                                            |##
##|            :  ARGUMENTS                                                 |##
##|            :     > cap - Camera identification number.                  |##
##|            :                                                            |##
##|            :  RETURNS                                                   |##
##|            :     > none                                                 |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##            
    def TASK_CREATE_OVERLAY(self, cap) -> None:        
        if not self.CAM[cap].isActive: return;
        if self.CAM[cap].F_newProc.check():# and self.CAM[cap].T_MASK.tock(True):
            self.CAM[cap].processOverlay( mode="square", 
                                          alpha=True, 
                                          n_samples=8 )
            #self.CAM[cap].SelectionVolume()
           
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|     FUNC  <:> TASK_GET_IMAGE                                            |##
##|            :     > Proceed through process of acquiring images at each  |##
##|            :       call of the task.                                    |##
##|            :     > If freeze command is invoked, update freeze image at |##
##|            :       first instance of FALSE -> TRUE.                     |##
##|            :                                                            |##
##|            :  ARGUMENTS                                                 |##
##|            :     > cap - Camera identification number.                  |##
##|            :                                                            |##
##|            :  RETURNS                                                   |##
##|            :     > none                                                 |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##    
    def TASK_GET_IMAGE(self, cap) -> None:
        if not self.CAM[cap].isActive: return;
        if self.CAM[cap].F_newOver.shake():
            if self.GUI.isFreezeActive:
                if self.CAM[cap].isNewFreeze:       
                    alp = self.CAM[cap].FREEZE_ALPHA*100
                    self.DC.send(f"Freezing image interface at {alp}%.") 
                    self.CAM[cap].isNewFreeze = False
                    self.CAM[cap].FreezeFrame()
                self.CAM[cap].FlatComposite()
            else:
                self.CAM[cap].isNewFreeze = True 
                self.CAM[cap].doCompositing( doAbsolute=True, 
                                             threshold=self.CAM[cap].THRESHOLD)
        if self.CAM[cap].F_newRead.shake():
            self.CAM[cap].processImage()            
        if self.CAM[cap].F_newGrab.shake():
            self.CAM[cap].readImage()
        if True:
            self.CAM[cap].grabImage()  
        # if True:
        #     self.CAM[cap].getImage()
            
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|     FUNC  <:> TASK_USER_INTERFACE                                       |##
##|            :     > Run standard tkinter updates built-in to module.     |##
##|            :     > Update data panel to the right of the camera.        |##
##|            :                                                            |##
##|            :  ARGUMENTS                                                 |##
##|            :     > none                                                 |##
##|            :                                                            |##
##|            :  RETURNS                                                   |##
##|            :     > none                                                 |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##   
    def TASK_USER_INTERFACE(self):
        self.GUI.runUpdate()
        for cap in range(self.n_cameras):
            self.GUI.UpdateData(cap,0,
                                "ERR" if not self.CAM[cap].isActive else ("FREEZE" if self.GUI.isFreezeActive else "OK"),
                                self.CFG.style.false if not self.CAM[cap].isActive else (self.CFG.style.lightblue if self.GUI.isFreezeActive else self.CFG.style.true)
                                )
            self.GUI.UpdateData(cap,1,self.CAM[cap].FPS)       
           
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|     FUNC  <:> TASK_UPDATE_DISPLAY                                       |##
##|            :     > Update camera feed with composited image(s).         |##
##|            :                                                            |##
##|            :  ARGUMENTS                                                 |##
##|            :     > cap - Camera identification number.                  |##
##|            :                                                            |##
##|            :  RETURNS                                                   |##
##|            :     > none                                                 |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##        
    def TASK_UPDATE_DISPLAY(self, cap) -> None:
        if self.CAM[cap].isActive:# and cap == 1:
            if self.CAM[cap].F_newFull.check() and self.CAM[cap].T_FRAME.tock(reset=False):
                self.CAM[cap].F_newFull.shake();
                self.CAM[cap].T_FRAME.tock(reset=True)
                self.GUI.deployImage( self.CAM[cap].image.composited,
                                      self.GUI.CAMFEED[cap] )
                self.CAM[cap].CountFPS()                  
                winh = int(self.GUI.PANEL[1].winfo_height() / 2.5)
                self.CAM[cap].ImageScale = [winh,winh]
           
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|     FUNC  <:> COMMAND_LOOP                                              |##
##|            :     > The finite state machine itself.                     |##
##|            :                                                            |##
##|            :  ARGUMENTS                                                 |##
##|            :     > none                                                 |##
##|            :                                                            |##
##|            :  RETURNS                                                   |##
##|            :     > [bool] - Whether loop is still running.              |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
    def COMMAND_LOOP(self) -> bool:
        self.TASK_POLL_GUI()

        self.passnum = not self.passnum              
        
        self.TASK_GET_IMAGE(self.passnum)
        self.TASK_CREATE_OVERLAY(self.passnum)          
        self.TASK_UPDATE_DISPLAY(self.passnum)
        self.TASK_USER_INTERFACE()
        
        if not self.GUI.RUNNING:
            self.DC.send("Closing program...")
            return False
        return True
           
##|=========================================================================|##
##|              S T A N D A L O N E      E X E C U T I O N                 |##
##|=========================================================================|##
if __name__ == "__main__":    
    cameras = 2
    PACT = FSM_PACT(cameras,1)
    ok = True
    while ok:
        ok = PACT.COMMAND_LOOP()
    PACT.GUI.ROOT.destroy()