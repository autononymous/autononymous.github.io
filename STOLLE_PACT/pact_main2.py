# -*- coding: utf-8 -*-
"""
@file pact_main.py
@author Ryan Kissinger

@brief  The main function referencing all the other functions.
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
##|   VERSION <|> '-' 09/01/25 THRU 11/25/25                                |##
##|            :    > "Initial project demo for approval from management.   |##
##|            :       Contains basic UI elements and Normal overlay,       |##
##|            :       as well as Boolean Mode, Freeze, and Blur."          |##
##|           <|> 'A' 11/26/25 THRU [NOW]                                   |##
##|            :    >  Redevelopment of User Interface for new project      |##
##|            :       direction established in Design Review.              |##
##|            :    >                                                       |##
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
##|------------------------------------------------ -------------------------|##
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
from pact_ui import PACT_UI2
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
##|            :  CLASS "FSM_PACT"                                          |##
##|            :   > A finite state machine / task-state system ordering    |##
##|            :     tasks across different functions.                      |##
##|-------------------------------------------------------------------------|##
class FSM_PACT():    
    isInit = False
    isRunning = True           
##|-|-----------------------------------------------------------------------|##
##| |          :  SUBCLASS "Profile"                                        |##
##| |          :   > Gathers profile information from config.json and       |##
##| |          :     assists in deployment of themes and settings saved     |##
##| |          :     in previous program states.                            |##
##|-|-----------------------------------------------------------------------|##
    class Profile:  
##|-----|-------------------------------------------------------------------|## 
##|     |      :  FUNCTION "saveProfile"                                    |##     
##|     |      :   > Interprets current settings into JSON string and       |##
##|     |      :     overwrites existing profile.JSON file.                 |##  
##|-----|-------------------------------------------------------------------|## 
        def saveProfile(self,dic=None):
            if dic is None: dic = self.PROFILE;
            json_str = json.dumps(dic, indent=4)
            with open("profile.json", "w") as f:
                f.write(json_str)
            return        
##|-----|-------------------------------------------------------------------|## 
##|     |      :  FUNCTION "updateProfile"                                  |##     
##|     |      :   > Updates dictionary object in PROFILE with a new value. |## 
##|-----|-------------------------------------------------------------------|## 
        def updateProfile(self, paramName, value):
            if paramName in self.PROFILE.keys():
                self.PROFILE[paramName] = value
                self.saveProfile()
                self.DC.send("Program profile updated: " + str(paramName) + " is now " + str(value) + ".")
                return
            else:
                self.DC.send('Unable to update profile: "' + str(paramName) + '" does not exist.')
                return
##|-----|-------------------------------------------------------------------|## 
##|     |      :  FUNCTION "newProfile"                                     |##     
##|     |      :   > Generates a new profile from pre-defined template and  |## 
##|     |      :     saves it using function saveProfile.                   |## 
##|-----|-------------------------------------------------------------------|##          
        def newProfile(self) -> None:
            self.PROFILE = {
                "User":None,
                "AlphaLevel":128,
                "FreezeLevel":128,
                "BlurLevel":4,
                "BoolLevel":128,
                "DoBool":False,
                "BoolSpan":5}
            self.saveProfile(self.PROFILE)
            return
##|-----|-------------------------------------------------------------------|## 
##|     |      :  INITIALIZATION FUNCTION                                   |##     
##|     |      :   > Opens a new DebugConsole for the profile functions.    |##    
##|     |      :   > Handles loading or creating profiles whether or not    |##   
##|     |      :     they exist for the User.                               |##  
##|-----|-------------------------------------------------------------------|##         
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

##|-|-----------------------------------------------------------------------|## 
##| |          :  INITIALIZATION FUNCTION                                   |##     
##| |          :   > Opens a new DebugConsole for the main program.         |##    
##| |          :   >  
##|-|-----------------------------------------------------------------------|##  
    def __init__(self,startindex) -> None:  
        self.DC = DebugConsole()
        self.DC.send("Starting STOLLE PACT...")
        self.n_cameras = 2
        self.DC.send("Loading in configuration parameters...")
        self.CFG = CONFIG()         
        self.DC.send("Building graphical user interface...")
        self.GUI = PACT_UI2(self.CFG)
            
        self.CAM = []
        for i in range(self.n_cameras):    
            self.DC.send(f"Initializing camera 0{i}...") 
            self.CAM.append(PACT_Cam(i,startindex))  
        
        self.CAM[0].bindWidget(self.GUI.W2111.widget)
        self.CAM[1].bindWidget(self.GUI.W2211.widget)
        
        self.CAM[0].bindContainer(self.GUI.W21.widget)
        self.CAM[1].bindContainer(self.GUI.W22.widget)
        
        self.passnum = 0 
        self.WindowHeight = [999,999]
        self.WinHeightThreshold = 10;
        self.WinHeightScaling = 1.25;
        
        self.isInit = True 
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
        pass #TODO with new setup.
           
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
            self.CAM[cap].doCompositing( doAbsolute=True, 
                                         threshold=self.CAM[cap].THRESHOLD,
                                         ptdata = self.GUI.SelectData)
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
        #TODO update data in this subtask for metadata window
           
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
                                      self.CAM[cap].WidgetFrame)
                self.CAM[cap].CountFPS()
                self.GUI.UpdateMetadata(cap, "FPS", self.CAM[cap].FPS)
                # @TODO Metric versus Imperial selection.
                self.GUI.UpdateMetadata(cap, "Px", self.CAM[cap].PointQ.Origin.X.GetInches(3))
                self.GUI.UpdateMetadata(cap, "Py", self.CAM[cap].PointQ.Origin.Y.GetInches(3))
                self.GUI.UpdateMetadata(cap, "R", self.CAM[cap].PointQ.GetDegrees(3))
                self.WindowHeight[0] = int(self.CAM[cap].WidgetContainer.winfo_width() / self.WinHeightScaling)                      
                if np.abs(self.WindowHeight[1] - self.WindowHeight[0]) > self.WinHeightThreshold:
                    self.WindowHeight[1] = self.WindowHeight[0]
                    for caps in self.CAM:                        
                        caps.ImageScale = [self.WindowHeight[0],self.WindowHeight[0]]
           
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
    PACT = FSM_PACT(0)
    ok = True
    while ok:
        ok = PACT.COMMAND_LOOP()
    PACT.GUI.ROOT.destroy()