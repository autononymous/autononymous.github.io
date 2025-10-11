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
##|                  ░█▀▀░█▀█░█▀█▀█░█▀▀░█▀▄░█▀█░░░░█▀█░█░█                  |##
##|                  ░█░░░█▀█░█░█░█░█▀▀░█▀▄░█▀█░░░░█▀▀░░█░                  |##
##|                  ░▀▀▀░▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀░▀░▀░░▀░░░░▀░                  |##
##|=========================================================================|##
##|            :                                                            |##
##|   PROJECT <|> Project "PACT" -- Plate Alignment Calibration Tool        |##
##|            :  AKA the "Pre-Registration Fixture"                        |##
##|            :                                                            |##
##|   COMPANY <|> STOLLE MACHINERY COMPANY, LLC                             |##
##|            :  6949 S. POTOMAC STREET                                    |##
##|            :  CENTENNIAL, COLORADO, 80112                               |##
##|            :                                                            |##
##|      FILE <|> pact_camera.py                                            |##
##|            :                                                            |##
##|    AUTHOR <|> Ryan Kissinger                                            |##
##|            :                                                            |##
##|   VERSION <|> '-' - 09/29/25                                            |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|   PURPOSE <|>                                                           |##
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
import sys, cv2, time
from cv2 import VideoCapture
from PIL import Image
from PIL import ImageTk
import numpy as np

# Custom Functions
from pact_mastermind import Timer, ConditionFlag
from pact_debug import Debug


class PACT_Cam(VideoCapture):
    
    ##|---------------------------------------------------------------------|##
    ##|                   >> ORGANIZING CAMERA DATA <<                      |##
    ##|---------------------------------------------------------------------|##
    class CaptureFrame: 
        raw = []
        read = []
        processed = []
        overlay = []
        composited = []
        frozen = []        
    norm = []; 
    ang = []; 
    mag = []; 
    dx = []; 
    dy = [];
    
    ##|---------------------------------------------------------------------|##
    ##|                  >> GETTER & SETTER FUNCTIONS <<                    |##
    ##|---------------------------------------------------------------------|##
    def setFrameLimit(self, hertz): 
        self.FRAMERATE = hertz 
        return
    def setMaskFreq(self, hertz):   
        self.MASKRATE = hertz
        return
    def setKernel(self, kernel):         
        self.KERNEL = kernel
        return    
    def setThreshold(self, thresh):
        self.THRESHOLD = thresh
    def setImageSize(self,size):
        if len(size) == 2:
            self.ImageSize = size
        else:
            print("[WARN] Invalid image size. Defaulting to 300 x 300.")
            self.ImageSize = size
            return
    def CountFPS(self,rounding=0) -> None:
        if rounding == 0: self.FPS = int(1/self.T_TRUEFPS.tick(reset=True))
        else: self.FPS = np.round(1/self.T_TRUEFPS.tick(reset=True),rounding)
        return
        
    ##|---------------------------------------------------------------------|##
    ##|                       >> INITIALIZATION <<                          |##
    ##|---------------------------------------------------------------------|##    
    def __init__(self, camID, startindex=0, framerate=None, maskrate=None, crop_size=None, *args, **kwargs) -> None:
        self.CameraIndex = camID + startindex
        super().__init__(*args, self.CameraIndex, **kwargs) 
        
        self.image = self.CaptureFrame() 
        
        self.CameraID = camID
        
        self.FRAMERATE = (1 / 60.0) if framerate is None else framerate
        self.T_FRAME = Timer(self.FRAMERATE)
        self.MASKRATE  = (1 / 10.0) if maskrate is None else maskrate
        self.T_MASK = Timer(self.MASKRATE)      
        self.T_TRUEFPS = Timer(999)
        self.FPS = 0.0
        
        self.KERNEL = 4
        self.THRESHOLD = 40 # out of 255 on Alpha transparency layer
        self.FREEZE_ALPHA = 0.4
        
        self.ImageScale = [480,480]
        
        self.F_newGrab = ConditionFlag(False)
        self.F_newRead = ConditionFlag(False)
        self.F_newProc = ConditionFlag(False)
        self.F_newOver = ConditionFlag(False) 
        self.F_newFull = ConditionFlag(False) 
        
        self.isGradReady = False
        self.isActive = False
        self.isNewFreeze = True
        
        if self.isOpened():
            self.isActive = True
            ok, frame = self.read()
            test = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.h_nat, self.w_nat = test.shape[:2]
            self.h = self.h_nat
            self.w = self.w_nat 
            
            #print(f"[INFO] init(): Camera initialized at {self.CameraIndex}.")
        else:
            self.isActive = False
            #print(f"[WARN] init(): Camera not detected at {self.CameraIndex}.")
            return
        
        RawSize = min(self.h_nat,self.w_nat)
        self.ImageSize = [RawSize,RawSize] if ( (crop_size is None) or ( len(crop_size) != 2) ) else crop_size
        self.image.frozen = np.zeros(self.ImageScale)

    ##|---------------------------------------------------------------------|##
    ##|                       >> IMAGE GRABBING <<                          |##
    ##|---------------------------------------------------------------------|##
    def grabImage(self) -> None:
        if not self.isActive: 
            print(f"[WARN] grabImage(): Unable to grab image. Camera {self.CameraID} not initialized.")
            return;
        grabbed = self.grab()
        if grabbed:
            self.image.raw = grabbed
            self.F_newGrab.activate()
        return
    
    ##|---------------------------------------------------------------------|##
    ##|                       >> IMAGE READING <<                           |##
    ##|---------------------------------------------------------------------|##        
    def readImage(self) -> None:
        if not self.isActive: 
            print(f"[WARN] readImage(): Unable to read image. Camera {self.CameraID} not initialized.")
            return;
        read = self.retrieve(self.image.raw)
        if read[0]:
            self.image.read = read[1]
            self.F_newRead.activate()
        return
    
    # def getImage(self) -> None:
    #     if not self.isActive: 
    #         print(f"[WARN] getImage(): Unable to grab image. Camera {self.CameraID} not initialized.")
    #         return;
    #     read = self.read()
    #     if read is True:
    #         self.image.read = read
    #         self.F_newRead.activate()            
    #         print(read)
    
    ##|---------------------------------------------------------------------|##
    ##|                      >> IMAGE PROCESSING <<                         |##
    ##|---------------------------------------------------------------------|##
    def cropImage(self, img, dims) -> int:
        h0, w0 = img.shape[:2]
        h1, w1 = dims
        # Is the requested crop size bigger than the actual image?
        if h1 > h0: raise Exception(f"[ERROR] cropImage(): Crop size height = {h1} is larger than {h0}."); return
        if w1 > w0: raise Exception(f"[ERROR] cropImage(): Crop size width = {h1} is larger than {h0}."); return
        h_min = int( (h0-h1)/2 ) # min bound of new centered image
        w_min = int( (w0-w1)/2 )
        return img[ h_min:h_min+h1 , w_min:w_min+w1 ]        
    
    def FreezeFrame(self):        
        print(f"Froze image for {self.CameraID}")
        self.image.frozen = np.zeros(self.ImageScale)
        self.image.frozen = self.image.processed
        
    def processImage(self) -> None:
        if not self.isActive: 
            print(f"[WARN] processImage(): Unable to process image: Camera {self.CameraID} not initialized.")
            return;
        i_color = cv2.cvtColor(self.image.read, cv2.COLOR_BGR2GRAY)
        i_crop = self.cropImage(i_color, self.ImageSize)
        i_resize = cv2.resize(i_crop,self.ImageScale)
        i_blur = cv2.blur(i_resize, (self.KERNEL,self.KERNEL))
        self.image.processed = i_blur
        self.F_newProc.activate()
        return
    
          
    ##|---------------------------------------------------------------------|##
    ##|                   >> OVERLAY GENERATION <<                          |##
    ##|---------------------------------------------------------------------|##
    def Normalize(self, array) -> float:
        h,w = array.shape[:2]
        a_min = np.min(array)
        a_max = np.max(array)        
        a_rng = a_max - a_min
        if a_rng == 0: 
            print(f"[WARN] Normalize(): Zero value detected in Normalize() for Camera {self.CameraID}.")
            return (array - a_min)
        return (array - a_min) / a_rng
    
    def Gradient(self, array, n_samples=None) -> float:
        samples = 8 if n_samples is None else n_samples
        dx, dy = np.gradient(array, samples)
        mag = self.Normalize(np.sqrt( (dx * dx) + (dy * dy) ))
        ang = np.arctan2(dy,dx)
        return dx, dy, mag, ang
    
    def makeOverlay(self, mag, ang, mode='square', alpha=True) -> float:
        if not self.F_newProc.wasActive:
            print(f"[WARN] makeOverlay(): Unable to makeOverlay for Camera {self.CameraID} without processed image yet. Skipping.")
            return
        h,w = mag.shape
        overlay = np.zeros([h,w,3+alpha],dtype='uint8')
        if (mode == "square") or (mode == 2):
            overlay[:,:,0] = ( 255 - ( 128 * mag))                     # BLUE
            overlay[:,:,1] = ( 127 + ( 128 * np.cos(ang * 4) * mag ))  # GREEN
            overlay[:,:,2] = ( 127 + ( 128 * np.sin(ang * 4) * mag ))  # RED
        else:
            overlay[:,:,0] = ( 255 - ( 128 * mag))                     # BLUE
            overlay[:,:,1] = ( 127 + ( 128 * np.sin(ang) * mag ))      # GREEN
            overlay[:,:,2] = ( 127 + ( 128 * np.cos(ang) * mag ))      # RED
        if alpha: overlay[:,:,3] = 255 * mag
        return overlay
    
    def AddCrosshairs(self, array):
        h,w = array.shape[:2]
        cv2.line(array, [0,int(h/2)], [w,int(h/2)], (0,0,0))
        cv2.line(array, [int(w/2),0], [int(w/2),h], (0,0,0))
        return array
    
    def processOverlay(self, mode='square', alpha=True, n_samples=None) -> None:
        self.dx, self.dy, self.mag, self.ang = self.Gradient(self.image.processed, n_samples)
        self.image.overlay = self.makeOverlay(self.mag, self.ang, mode, alpha)
        self.F_newOver.activate() 
        # NOTE: No deactivation of F_newProc since it is also used for something else.
        return
       
    ##|---------------------------------------------------------------------|##
    ##|                  >> COMPOSITING (MIX IMAGES) <<                     |##
    ##|---------------------------------------------------------------------|##
    def doCompositing(self, doAbsolute=True, threshold=None) -> None:
        if threshold is None:
            threshold = self.THRESHOLD
        if not (self.F_newProc.wasActive and self.F_newOver.wasActive):
            print(f"[WARN] doCompositing(): Unable to composite for Camera {self.CameraID} without processed and overlay. Skipping.")
            return
        procShape = self.image.processed.shape
        if len(procShape) < 3:
            proc3 = np.ones([procShape[0],procShape[1],3])
            for i in range(3): proc3[:,:,i] = self.image.processed
        else:
            proc3 = self.image.processed
        alpha = (1.0 * (self.image.overlay[:,:,3] > threshold)) if doAbsolute else (self.image.overlay[:,:,3] / 255.0)       
        composite = np.zeros([procShape[0],procShape[1],3])
        for i in range(3):
            composite[:,:,i] = (proc3[:,:,i] * (1.0-alpha)) + (self.image.overlay[:,:,i] * alpha)
        self.image.composited = self.AddCrosshairs(np.array(composite,dtype='uint8'))
        self.F_newFull.activate()  
        return
    
    def FlatComposite(self, underlay=None, overlay=None, alpha=None) -> None:
        if underlay == None: underlay = self.image.processed
        if overlay == None: overlay = self.image.frozen            
        #print(np.mean(overlay))
        
        if alpha is None:
            alpha = self.FREEZE_ALPHA
        under_dims = underlay.shape
        if len(under_dims) < 3:
            und3 = np.zeros([under_dims[0],under_dims[1],3])
            for i in range(3): und3[:,:,i] = underlay
        elif under_dims[2] > 3: und3 = underlay[:,:,0:3]
        else: und3 = underlay
        
        over_dims = overlay.shape
        if len(over_dims) < 3:
            ovr3 = np.zeros([over_dims[0],over_dims[1],3])
            for i in range(3): ovr3[:,:,i] = overlay
        elif over_dims[2] > 3: ovr3 = overlay[:,:,0:3]
        else: ovr3 = overlay
        self.image.composited = self.AddCrosshairs(np.array( (underlay * (1.0 - alpha)) + (overlay * (alpha)), dtype='uint8'))
        self.F_newFull.activate()        
        return 
    
if __name__ == "__main__":
    PC0 = PACT_Cam(2)
    #PC1 = PACT_Cam(1)
    #PC2 = PACT_Cam(2)    
    print("-----------------------")
    print("Latency Testing:")
    print("-----------------------")
    time_latency = Timer(999)    
    PC0.grabImage()
    print("GRAB:   \t" + str(np.round(time_latency.tick(reset=True)*100,2)) + " ms")
    PC0.readImage()
    img = PC0.image.read
    print("READ:   \t" + str(np.round(time_latency.tick(reset=True)*100,2)) + " ms @ \t" + str(img.shape) + ", \trange " + str(np.min(img)) + " to " + str(np.max(img)))    
    if True:
        cv2.namedWindow("Read Image")
        cv2.imshow("Read Image",PC0.image.read)    
    PC0.processImage()
    img = PC0.image.processed
    print("PROCESS:\t" + str(np.round(time_latency.tick(reset=True)*100,2)) + " ms @ \t" + str(img.shape) + ", \trange " + str(np.min(img)) + " to " + str(np.max(img))) 
    if True:
        cv2.namedWindow("Processed Image")
        cv2.imshow("Processed Image",PC0.image.processed)
    PC0.processOverlay()
    img = PC0.image.overlay
    print("OVERLAY:\t" + str(np.round(time_latency.tick(reset=True)*100,2)) + " ms @ \t" + str(img.shape) + ", \trange " + str(np.min(img)) + " to " + str(np.max(img))) 
    if True:
        cv2.namedWindow("Overlay Preview")
        cv2.imshow("Overlay Preview",PC0.image.overlay)
    PC0.doCompositing()
    img = PC0.image.composited
    print("COMPOSITE:\t" + str(np.round(time_latency.tick(reset=True)*100,2)) + " ms @ \t" + str(img.shape) + ", \trange " + str(np.min(img)) + " to " + str(np.max(img))) 
    if True:
        cv2.namedWindow("Composited Image")
        cv2.imshow("Composited Image",PC0.image.composited)
    print("-----------------------")
