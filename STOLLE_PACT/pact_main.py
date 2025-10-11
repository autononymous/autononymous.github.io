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
##|   VERSION <|> '-' - 09/29/25                                            |##
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

# Custom functions
from pact_ui import PACT_UI
from pact_config import CONFIG
from pact_camera import PACT_Cam

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
    
    class DebugConsole:
        def __init__(self):
            self.str = ""
            self.t_init = time.time()
        def send(self, message):
            t = time.strftime("%H:%M:%S", time.gmtime())
            msg = str(message)
            print(f"{t} |\t> {msg}")          
            
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
        self.DC = self.DebugConsole()
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
        for cap in range(self.n_cameras):
            self.CAM[cap].THRESHOLD = self.GUI.GetAlpha()
            self.CAM[cap].FREEZE_ALPHA = self.GUI.GetFreezeAlpha()
           
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
        return self.isRunning
           
##|=========================================================================|##
##|              S T A N D A L O N E      E X E C U T I O N                 |##
##|=========================================================================|##
if __name__ == "__main__":    
    cameras = 2
    PACT = FSM_PACT(cameras,0)
    ok = True
    while ok:
        ok = PACT.COMMAND_LOOP()