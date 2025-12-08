# -*- coding: utf-8 -*-
"""
@file pact_camera.py
@author Ryan Kissinger

@brief Handles camera operations.
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
from pact_config import CONFIG
from pact_maths import CrossProd, Hmat_Z    

class PACT_Cam(VideoCapture):
    '''! Class that handles interpreting and deploying camera information. 
         Inherits characteristics of cv2.VideoCapture class.'''
    ## ORGANIZING CAPTURE DATA:
    norm = [];      # Array of computed Normals by neighbor values {0,255}.
    ang = [];       # Vector angles.
    mag = [];       # Vector magnitudes.
    dx = [];        # X-component computed from angle + magnitude.
    dy = [];        # Y-component computed from angle + magnitude.
    CFG = CONFIG()  # CONFIG data from config.json file.
    S = CFG.style   # Shorthand for styles in CONFIG.
        
    # Queried positions, in units of PIXELS.
    xp0 = None; yp0 = None; xp1 = None; yp1 = None
    # Queried positions, in units of INCHES or MILLIMETERS.
    xm0 = None; ym0 = None; xm1 = None; ym1 = None
    # Rotation result, in DEGREES.
    rot = None
    
    # Will store active computed Frames Per Second value.
    FPS = 0.0
    
    # Scale of the image to draw.
    ImageScale = [360,360]  
    
    class PointData():  
        '''! This class organizes data interpreted from the camera system.
             It also converts between measures.
             Heirarchy is as follows:
             > Data
                 > Origin
                     > ViewScale (real-world size of window)
                     > Gradiation (spacing of crosshair circles)
                     > X-value
                        > Position in inches
                        > Position in millimeters
                        > Position in pixels
                     > Y-value
                        > ""
                 > Orientation
                     > ""
               > R_deg (Rotation/skew in degrees)
               > R_rad (Rotation/skew in radians)
             e.g. Data.Origin.X.GetInches()
                 '''
        class Measurands:
            def UpdateInches(self, meas):
                self.Inches = meas
                self.Millis = meas * 25.4
            def UpdateMillis(self, meas):
                self.Inches = meas / 25.4
                self.Millis = meas
            def UpdatePixels(self, meas):
                self.Pixels = meas;
            def __init__(self,inches):
                self.UpdateInches(inches) 
                self.UpdatePixels(0)
            # This returns Inches as a rounded value (for displaying values)
            def GetInches(self,res):
                exp = np.power(10,res);
                return int(self.Inches * exp) / exp
            def GetMillis(self,res):
                exp = np.power(10,res);
                return int(self.Millis * exp) / exp
            def GetPixels(self): return self.Pixels;
        class PointDatum:
            X = None
            Y = None            
            def isDefined(self):
                return (self.X is not None) and (self.Y is not None)
        def __init__(self,scale,grad):
            # The size, in inches, of the smallest 
            # window dimension from raw capture.
            self.ViewScale = self.Measurands(scale)
            # The spacing of gradiations with the crosshair circle.
            self.Gradiation = self.Measurands(grad)
            # Origin data (left click, origin of crosshairs)
            self.Origin = self.PointDatum()
            self.Origin.X = self.Measurands(0)
            self.Origin.Y = self.Measurands(0)
            # Orientation data (right click, orients crosshairs' angle)
            self.Orient = self.PointDatum()
            self.Orient.X = self.Measurands(0)
            self.Orient.Y = self.Measurands(0)       
            # Rotation data
            self.R_deg = 0
            self.R_rad = 0
        def SetDegrees(self,deg): 
            self.R_deg = deg
            self.R_rad = deg * np.pi / 180
        def SetRadians(self,rad):
            self.R_deg = rad * 180 / np.pi
            self.R_rad = rad
        def ComponentsToAngle(self):
            self.R_rad = np.arctan2((self.Orient.Y.Inches-self.Origin.Y.Inches),
                                    (self.Orient.X.Inches-self.Origin.X.Inches))
            self.R_deg = self.R_rad * 180 / np.pi            
            while self.R_deg >  45: self.R_deg -= 90;
            while self.R_deg < -45: self.R_deg += 90;
            self.SetDegrees(self.R_deg)
        def GetDegrees(self,res):
            exp = np.power(10,res);
            return int(self.R_deg * exp) / exp
        def GetRadians(self,res):
            exp = np.power(10,res);
            return int(self.R_rad * exp) / exp
                                    
        
    # ***IMPORTANT***  Query points for selections in camera UI
    # Arg 1: Width of camera view IRL (in real life, in millennial speak)
    # Arg 2: Width of each gradiation to draw as circles.
    PointQ = PointData(0.200,0.015) 
    
    class CaptureFrame: 
        '''! Subclass that organizes each image frame as arrays, in different
             states of processing as they move through the Finite State
             Machine. '''
        raw = []            # Raw image grab information.
        read = []           # The raw image array that has been read.
        processed = []      # The processed image after crop/other operations.
        overlay = []        # Image overlay(s) to putover the processed image.
        composited = []     # Processed image + overlay image.
        frozen = []         # A still capture when freeze is requested.
        selectionbool = []  # @DEPRECATE
        selection = []      # @DEPRECATE       

    def CountFPS(self,rounding=0) -> None:
        '''! Get the frames per second measure from the camera.
        @param rounding  Decimal place to round result.'''
        # If no rounding, just return the raw value.
        if rounding == 0: 
            self.FPS = int(1/self.T_TRUEFPS.tick(reset=True))       
        # Otherwise, return the rounded result.
        else: 
            self.FPS = np.round(1/self.T_TRUEFPS.tick(reset=True),rounding)
        return
    
    WidgetContainer = None
    def bindContainer(self,wcontainer):
        '''! A setter function for higher-level manipulation. Bind container.'''
        self.WidgetContainer = wcontainer
        return
    WidgetFrame = None
    def bindWidget(self,widget):
        '''! A setter function for higher-level manipulation. Bind widget.'''
        self.WidgetFrame = widget
        return
        
    ##|---------------------------------------------------------------------|##
    ##|                       >> INITIALIZATION <<                          |##
    ##|---------------------------------------------------------------------|##    
    def __init__(self, camID, startindex=0, framerate=None, maskrate=None, crop_size=None, *args, **kwargs) -> None:
        '''! Initializing function for PACT_Cam. Sets up class for capture.
             @param camID  Integer value to identify this camera from others.
             @param startindex  The true start index of the camera as seen by the computer software.
             @param framerate  The allowed threshold of framerate.
             @param maskrate  The allowed threshold of masking. DEPRECATED.
             @param crop_size  [x,y] integer array describing target crop size. Automatically smallest image dim if None. '''
        # This index identifies the camera from the start index (skipping others).
        self.CameraIndex = camID + startindex
        # Inherit the VideoCapture class parameters.
        super().__init__(*args, self.CameraIndex, **kwargs) 
        # Instantiate image data as a CaptureFrame class object.
        self.image = self.CaptureFrame() 
        # Identify the index of this CaptureFrame object.
        self.CameraID = camID
        # Set the frame rate limit if not None.
        self.FRAMERATE = (1 / 60.0) if framerate is None else framerate
        # Generate Timer object to time the frame rate.
        self.T_FRAME = Timer(self.FRAMERATE)
        # Set the masking rate limit if not None. 
        self.MASKRATE  = (1 / 10.0) if maskrate is None else maskrate
        # Generate Timer object to time the masking rate.
        self.T_MASK = Timer(self.MASKRATE)      
        # A Timer that keeps the true camera FPS.
        self.T_TRUEFPS = Timer(999)
        
        # @DEPRECATE these and update with new system parameters.
        self.KERNEL = 4
        self.THRESHOLD = 40 # out of 255 on Alpha transparency layer
        self.FREEZE_ALPHA = 0.4
        self.DO_BOOL_MASK = False
        self.BOOL_THRESHOLD = 100 # out of 255
        self.BOOL_SPAN = 1
        
        # Flags describing whether or not new information is available/updated.
        self.F_newGrab = ConditionFlag(False)
        self.F_newRead = ConditionFlag(False)
        self.F_newProc = ConditionFlag(False)
        self.F_newOver = ConditionFlag(False) 
        self.F_newFull = ConditionFlag(False)         
        self.isGradReady = False
        self.isActive = False
        self.isNewFreeze = True
        
        # Theming setup from CONFIG Styles.
        self.c_true = tuple(int((self.S.true).lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.c_false = tuple(int((self.S.false).lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.c_theme = tuple(int((self.S.stolle).lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.c_dark = (10,10,10)
        self.c_light = (250,250,250)
        
        # Begin capture of image arrays. 
        if self.isOpened():
            self.isActive = True
            ok, frame = self.read()
            # First captured image bounds stored as the image size.
            test = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.h_nat, self.w_nat = test.shape[:2]
            self.h = self.h_nat
            self.w = self.w_nat
        else:
            self.isActive = False
            return
        # If cropping size is not defined, just use the smallest dimension for square size.
        RawSize = min(self.h_nat,self.w_nat)
        self.ImageSize = [RawSize,RawSize] if ( (crop_size is None) or ( len(crop_size) != 2) ) else crop_size
        # Create zeros array to instantiate variable for frozen image to store later.
        self.image.frozen = np.zeros(self.ImageScale)

    def InchesToPixels(self,window_size_px,inches) -> int:     
        '''! Convert inches to pixels according to defined view scale.'''
        return int(inches * (window_size_px/self.PointQ.ViewScale.Inches))
    
    def PixelsToInches(self,window_size_px,pixels) -> float:   
        '''! Convert pixels to inches according to defined view scale.'''     
        return pixels * (self.PointQ.ViewScale.Inches/window_size_px)
    
    ## IMAGE MANIPULATION OPERATIONS:
    def grabImage(self) -> None:
        '''! Only return a BOOLEAN whether or not OpenCV2 was able to grab an image.'''
        if not self.isActive: 
            print(f"[WARN] grabImage(): Unable to grab image. Camera {self.CameraID} not initialized.")
            return;
        grabbed = self.grab()
        if grabbed:
            self.image.raw = grabbed
            self.F_newGrab.activate()
        return
     
    def readImage(self) -> None:
        '''! If image was grabbed, pull the actual image now.'''
        if not self.isActive: 
            print(f"[WARN] readImage(): Unable to read image. Camera {self.CameraID} not initialized.")
            return;
        read = self.retrieve(self.image.raw)
        if read[0]:
            self.image.read = read[1]
            self.F_newRead.activate()
        return
    
    def getImage(self) -> None:
        '''! This function combines grab() and read(). See https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-read'''
        if not self.isActive: 
            print(f"[WARN] getImage(): Unable to get image. Camera {self.CameraID} not initialized.")
            return;
        read = self.read()
        if read is True:
            self.image.read = read
            self.F_newRead.activate()            
            print(read)
    
    def cropImage(self, img, dims) -> int:
        '''! Given an image, crop to specified dimensions. 
             NOTE that this does not resize images. Crops about the CENTROID.
             @param img  The array image object.
             @param dims  Dimensions for resulting crop.
             @return  Cropped image array.'''
        h0, w0 = img.shape[:2]
        h1, w1 = dims
        # Is the requested crop size bigger than the actual image?
        if h1 > h0: raise Exception(f"[ERROR] cropImage(): Crop size height = {h1} is larger than {h0}."); return
        if w1 > w0: raise Exception(f"[ERROR] cropImage(): Crop size width = {h1} is larger than {h0}."); return
        # min bound of new centered image
        h_min = int( (h0-h1)/2 ) 
        w_min = int( (w0-w1)/2 )
        return img[ h_min:h_min+h1 , w_min:w_min+w1 ]        
    
    def FreezeFrame(self):
        '''! Stores the current frame for use as frozen image.'''
        self.image.frozen = np.zeros(self.ImageScale)
        self.image.frozen = self.image.processed
        
    def processImage(self) -> None:
        '''! Apply designated transformations to unprocessed image.'''
        if not self.isActive: 
            print(f"[WARN] processImage(): Unable to process image: Camera {self.CameraID} not initialized.")
            return;
        # Make it grayscale.
        i_color = cv2.cvtColor(self.image.read, cv2.COLOR_BGR2GRAY)
        # Crop the unprocessed image.
        i_crop = self.cropImage(i_color, self.ImageSize)
        # Resize the cropped image to specified image scale. Why? Processsing time/latency.
        i_resize = cv2.resize(i_crop,self.ImageScale)
        # Blur the resized image for smoother data.
        i_blur = cv2.blur(i_resize, (self.KERNEL,self.KERNEL))
        # If boolean mask is requested, run a SATURATION FUNCTION on the image.
        if self.DO_BOOL_MASK is True:
            # Upper bound of saturation function
            upper = self.BOOL_THRESHOLD + self.BOOL_SPAN
            # Lower bound of saturation function
            lower = self.BOOL_THRESHOLD - self.BOOL_SPAN
            # This is an array of TRUE/FALSE whether pixel is in threshold.
            is_inrange = (i_blur >= lower) * (i_blur <= upper) 
            # Resulting image array will be...
            i_bool = np.array(
                # ...empty array (all black at 0)...
                (i_blur * 0)
                # ...plus rescaled values for values in threshold (e.g. {18,178} -> {0,255}) ...
                + ((i_blur - lower) * (255/(self.BOOL_SPAN*2))) * is_inrange
                # ...plus 255 to zeroed values larger than upper (for white at 255).
                + (i_blur >= upper) * 255
                # And it is a 2^8 integer array {0,255} so it works with displaying images.
                , dtype='uint8')
            # If processed image will be this boolean mask, save it.
            self.image.processed = i_bool
        else:      
            # If no boolean mask, save blurred image.
            self.image.processed = i_blur
        # Flag that a new processed image is available for handshake.
        self.F_newProc.activate()
        return
    
    ## GENERATING THE OVERLAY:
    def Normalize(self, array) -> float:
        '''! Scale any general array from {a,b} to {0.0,1.0}.
             @param array  The image/array to transform.
             @return  Normalized array.'''
        h,w = array.shape[:2]
        a_min = np.min(array)
        a_max = np.max(array)        
        a_rng = a_max - a_min
        # Can't divide by zero. No zero ranges.
        if a_rng == 0: 
            print(f"[WARN] Normalize(): Zero value detected in Normalize() for Camera {self.CameraID}.")
            return (array - a_min)
        return (array - a_min) / a_rng
    
    def Gradient(self, array, n_samples=None) -> float:
        '''! Take the derivative of an image. 
             @param array  The image/array to transform.
             @param n_samples  Nearest neighbors to consider in calculation.
             @return array of x-components, y-components, magnitude, and angle.'''
        samples = 8 if n_samples is None else n_samples
        # thanks NumPy, but for real.
        dx, dy = np.gradient(array, samples)
        # Derive magnitude and angle from dx, dy.
        mag = self.Normalize(np.sqrt( (dx * dx) + (dy * dy) ))
        ang = np.arctan2(dy,dx)
        return dx, dy, mag, ang
    
    def makeOverlay(self, mag, ang, mode='square', alpha=True) -> float:
        '''! Create an overlay representing 3D geometries from 2D image.'''
        if not self.F_newProc.wasActive:
            print(f"[WARN] makeOverlay(): Unable to makeOverlay for Camera {self.CameraID} without processed image yet. Skipping.")
            return
        h,w = mag.shape
        # instantiate empty array to hold computed values
        overlay = np.zeros([h,w,3+alpha],dtype='uint8')
        # Result showing SQUARENESS, or correlation with being perfectly horizontal/vertical
        # GREEN means angle is closer to 0, 90, 180, 270, 360, ..., degrees.
        if (mode == "square") or (mode == 2):
            overlay[:,:,0] = ( 255 - ( 128 * mag))                     # BLUE
            overlay[:,:,1] = ( 127 + ( 128 * np.cos(ang * 4) * mag ))  # GREEN
            overlay[:,:,2] = ( 127 + ( 128 * np.sin(ang * 4) * mag ))  # RED
        # Traditional Normal map representation, like in video games/rendering. 
        # Please read https://en.wikipedia.org/wiki/Normal_mapping for more information.
        else:
            overlay[:,:,0] = ( 255 - ( 128 * mag))                     # BLUE  (upness, out of the page)
            overlay[:,:,1] = ( 127 + ( 128 * np.sin(ang) * mag ))      # GREEN (northness)
            overlay[:,:,2] = ( 127 + ( 128 * np.cos(ang) * mag ))      # RED   (westness)
        if alpha: overlay[:,:,3] = 255 * mag
        return overlay
    
    def ComputeRealData(self, PQ, clickdata, screen_w, screen_h, resolution=3):
        '''! Get some real world values from clicking the screen.'''
        # Control the base-10 resolution
        resolution = 3 if resolution > 3 else 1 if resolution < 1 else resolution
        
        # These values are ratios of how far across the screen the click was. 
        # [x,y] {0.0,1.0}
        # The pact_main.py pulls this from pact_camera.py.
        R_origin = [clickdata[0][0],clickdata[0][1]]
        R_orient = [clickdata[1][0],clickdata[1][1]]     
        
        # Is datum defined yet?
        if (R_origin[0] is not None) and (R_origin[1] is not None):
            # Get pixel coordinates from screen percentages
            PQ.Origin.X.Pixels = int(screen_w * R_origin[0])
            PQ.Origin.Y.Pixels = int(screen_h * R_origin[1])
            # Get real world measures in inches
            PQ.Origin.X.UpdateInches( self.PixelsToInches( screen_w, PQ.Origin.X.Pixels - (screen_w / 2) ))
            PQ.Origin.Y.UpdateInches( self.PixelsToInches( screen_w, PQ.Origin.Y.Pixels - (screen_h / 2) ))   
            
        # Is origin defined yet?
        if (R_orient[0] is not None) and (R_orient[1] is not None):
            # Get pixel coordinates from screen percentages
            PQ.Orient.X.Pixels = int(screen_w * R_orient[0])
            PQ.Orient.Y.Pixels = int(screen_h * R_orient[1])
            # Get real world measures in inches
            PQ.Orient.X.UpdateInches( self.PixelsToInches( screen_w, PQ.Orient.X.Pixels - (screen_w / 2) ))
            PQ.Orient.Y.UpdateInches( self.PixelsToInches( screen_w, PQ.Orient.Y.Pixels - (screen_h / 2) ))
            
        # Are both defined?
        if PQ.Origin.isDefined() and PQ.Orient.isDefined():
            PQ.ComponentsToAngle() # Derive angle from arctangent of X,Y vals            
    
    def AddCrosshairs(self, array, pointdata=None):
        '''! Superimpose crosshairs and gradiation circles on an image array.'''
        # @TODO move the pointdata stuff to a different function call for latency. Shouldn't have to call every damn time? flag NEWDATA or something.
        h,w = array.shape[:2]
        cv2.line(array, [0,int(h/2)], [w,int(h/2)], (0,0,0), 1)
        cv2.line(array, [int(w/2),0], [int(w/2),h], (0,0,0), 1)
        
        # Configuration parameters for drawing overlays
        PointDims = [int(w/50),int(w/200)]        
        LineDims  = [int(w/60),int(w/100)]
        
        # Number of gradiation circles is smallest possible circle radius 
        # bounding the square camera view, divided by width of each gradiation.
        ViewHypotenuse = np.sqrt(2 * np.power(self.PointQ.ViewScale.Inches * 0.5, 2))
        CirclesToDraw = int(ViewHypotenuse / self.PointQ.Gradiation.Inches )
        for i in range(CirclesToDraw):
            radius = self.InchesToPixels(w,(i+1)*self.PointQ.Gradiation.Inches)
            cv2.circle(array,[int(w/2)+1,int(h/2)+1],radius,(0,0,0),1)
            cv2.putText(array,str(int(self.PointQ.Gradiation.Inches*(i+1)*1000)),[int(w/2)+radius+3,int(h/2)-3],cv2.FONT_HERSHEY_SIMPLEX,w*0.001,self.c_light, 2, cv2.LINE_AA)
            cv2.putText(array,str(int(self.PointQ.Gradiation.Inches*(i+1)*1000)),[int(w/2)+radius+3,int(h/2)-3],cv2.FONT_HERSHEY_SIMPLEX,w*0.001,self.c_dark, 1, cv2.LINE_AA)
            cv2.putText(array,str(f"{w}x{h}"),[10,int(h)-10],cv2.FONT_HERSHEY_SIMPLEX,w*0.001,self.c_dark, 1, cv2.LINE_AA)
        if pointdata is not None:           
            self.ComputeRealData(self.PointQ, pointdata[self.CameraID].data, w, h)                
            if self.PointQ.Origin.isDefined and self.PointQ.Orient.isDefined:    
                X1 = np.array([[-w,0,0,1],[w,0,0,1],[0,h,0,1],[0,-h,0,1]]) 
                H = Hmat_Z(self.PointQ.R_rad,0,0)
                X2 = CrossProd(H,np.transpose(X1))

                L11 = [int(X2[0][0] + self.PointQ.Origin.X.Pixels),
                       int(X2[1][0] + self.PointQ.Origin.Y.Pixels)]
                L12 = [int(X2[0][1] + self.PointQ.Origin.X.Pixels),
                       int(X2[1][1] + self.PointQ.Origin.Y.Pixels)]
                L21 = [int(X2[0][2] + self.PointQ.Origin.X.Pixels),
                       int(X2[1][2] + self.PointQ.Origin.Y.Pixels)]
                L22 = [int(X2[0][3] + self.PointQ.Origin.X.Pixels),
                       int(X2[1][3] + self.PointQ.Origin.Y.Pixels)]

                cv2.line(array, L11, L12, self.c_dark, LineDims[0],cv2.LINE_AA)
                cv2.line(array, L11, L12, self.c_theme, LineDims[1],cv2.LINE_AA)    
                cv2.line(array, L21, L22, self.c_dark, LineDims[0],cv2.LINE_AA)
                cv2.line(array, L21, L22, self.c_theme, LineDims[1],cv2.LINE_AA)                
            
            if pointdata[self.CameraID].data[0][0] is not None: # meaning Datum is defined
                cv2.circle(array,[self.PointQ.Origin.X.Pixels,self.PointQ.Origin.Y.Pixels],0,self.c_false,PointDims[0]*2)
                cv2.circle(array,[self.PointQ.Origin.X.Pixels,self.PointQ.Origin.Y.Pixels],PointDims[0],(0,0,0),PointDims[1])   
            if pointdata[self.CameraID].data[1][0] is not None: # meaning Orientation is defined    
                cv2.circle(array,[self.PointQ.Orient.X.Pixels,self.PointQ.Orient.Y.Pixels],0,self.c_true,PointDims[0]*2)
                cv2.circle(array,[self.PointQ.Orient.X.Pixels,self.PointQ.Orient.Y.Pixels],PointDims[0],(0,0,0),PointDims[1])                 
        return array  # aka the image, which is an array.
    
    def processOverlay(self, mode='square', alpha=True, n_samples=None) -> None:
        '''! Generates overlay and saves into class variable.'''
        self.dx, self.dy, self.mag, self.ang = self.Gradient(self.image.processed, n_samples)
        self.image.overlay = self.makeOverlay(self.mag, self.ang, mode, alpha)
        self.F_newOver.activate() 
        # NOTE: No deactivation of F_newProc since it is also used for something else.
        return
       
    ## COMPOSITING (aka mixing of images):
    def doCompositing(self, doAbsolute=True, threshold=None, ptdata=None) -> None:
        '''! Overlay the overlay images on the processed image, and save 
             internally as composited.'''
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
        # self.image.composited = self.AddCrosshairs(np.array(composite,dtype='uint8'),ptdata) Removing this temp ********************** TODO ***********
        self.image.composited = self.AddCrosshairs(np.array(proc3,dtype='uint8'),ptdata)
        self.F_newFull.activate()  
        return
    
    def FlatComposite(self, underlay=None, overlay=None, alpha=None, ptdata=None) -> None:
        if underlay == None: underlay = self.image.processed
        if overlay == None: overlay = self.image.frozen
        
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
        self.image.composited = self.AddCrosshairs(np.array( (underlay * (1.0 - alpha)) + (overlay * (alpha)), dtype='uint8'),ptdata)
        self.F_newFull.activate()        
        return 
    
    def SelectionVolume(self, array=None, mode=None, rgb=[0,0,30], spandim=50):
        if array is None: array = self.image.processed
        h,w = array.shape[:2]
        cv2.circle(self.image.processed,[int(h/2),int(w/2)],spandim,rgb)
        self.image.selection = self.image.processed          
        return
            
                        
     
if __name__ == "__main__":
    PC0 = PACT_Cam(1)
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
