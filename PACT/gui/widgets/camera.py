# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 13:13:38 2025

@author: rkiss
"""

import sys, cv2, time

from timer import Timer

import numpy as np
from PySide6.QtCore import (
    QThread, 
    Signal
)

# %%

class CameraWorker(QThread):
    #
    # Create variable to hold signal for new image data
    frame_ready = Signal()
    isNewImageAvailable = False
    #    
    kernel = 5 # Kernel for blurring image (must be 5^n)    
    resolution = 512 # Resolution of image displayed      
    channel = 1 # Camera channel
    normal_latency = 100; # Latency of mask update [ms]
    
    threshold = 0.300; 
    
    doOverlay = Timer(normal_latency)
    
    ## [SETTER FUNCTIONS]
    def setChannel(self,value): self.channel = value;
    def setKernel(self,value): self.kernel = value;
    def setResolution(self,value): self.resolution = value; 
    #    
    ## [CLASS FUNCTIONS] 
    
    def getFrame(self):
        ret = False;
        while ret is not True:
            ret, img = self.cap.read();
            self.size = np.array(img.shape);
        return img;
    
    def Crop(self,img,shape=None,scaling=1,square=False):
        if shape is not None:
            size_x = shape[0] if (shape[0] < self.size[0]) else self.size[0];
            size_y = shape[1] if (shape[1] < self.size[1]) else self.size[1];
        elif scaling > 0 and scaling != 1:
            if scaling < 1:
                scaling *= (1/scaling);
            else:
                scale_x = int(self.size[0] / scaling);
                scale_y = int(self.size[1] / scaling);
                size_x = scale_x if not square else min(scale_x,scale_y);
                size_y = scale_y if not square else min(scale_x,scale_y);
        elif not square:
            return img;
        else:
            size_x = min(self.size[0],self.size[1]);
            size_y = min(self.size[0],self.size[1]);
        mid_x = size_x * 0.5;
        mid_y = size_y * 0.5;
        xlim = np.array( [-mid_x, mid_x] + (self.size[0]*0.5) , dtype='uint16');
        ylim = np.array( [-mid_y, mid_y] + (self.size[1]*0.5) , dtype='uint16');
        result = img[xlim[0]:xlim[1],ylim[0]:ylim[1],:]        
        return result
    
    def Filter(self, img, kernel=5):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
        img_blur = cv2.GaussianBlur(img_gray,(kernel,kernel),0);
        return img_blur;
    
    def Process(self, img, imdims=None):
        imraw = self.Filter(self.Crop(img,shape=imdims,square=True),self.kernel);
        return imraw;
    
    def Normalize(self, array):
        dims = np.array(array).shape;
        a_maxima = np.array([np.min(array),np.max(array)]);
        a_range = a_maxima[1] - a_maxima[0];
        for x in range(dims[0]):
            for y in range(dims[1]):
                array[x,y] = (array[x,y] - a_maxima[0]) / a_range;
        return array;
                
    def NormalMap(self, mag, ang):          
        self.NormMap = np.zeros([self.cropsize[0],self.cropsize[1],4],dtype='uint8');
        self.NormMap[:,:,2] = (255 - (128 * (mag)))
        self.NormMap[:,:,1] = (127 + (128 * np.sin(ang) * mag))
        self.NormMap[:,:,0] = (127 + (128 * np.cos(ang) * mag))
        self.NormMap[:,:,3] = 255 * mag
        
        self.SqrMap = np.zeros([self.cropsize[0],self.cropsize[1],4],dtype='uint8');
        self.SqrMap[:,:,2] = (255 - (128 * (mag)))
        self.SqrMap[:,:,1] = (127 + (128 * np.cos((ang * 4)) * mag))
        self.SqrMap[:,:,0] = (127 + (128 * np.sin((ang * 4)) * mag))
        self.SqrMap[:,:,3] = self.NormMap[:,:,3]
        
        return self.SqrMap;
    
    def SquarenessMap(self):
        for i in range(self.cropsize[0]):
            for j in range(self.cropsize[1]):
                while self.NormDr[i,j] > 45:
                    self.NormDr[i,j] -= 90;
                while self.NormDr[i,j] <= -45:
                    self.NormDr[i,j] += 90;
                self.Squareness[i,j] = 1 - (np.abs(self.NormDr[i,j]) / 45)
        return;
    
    def GradFilter(self, img, samples=8):
        (self.NormX,self.NormY) = np.gradient(img,samples);
        self.NormM = self.Normalize(np.sqrt((self.NormX*self.NormX) + (self.NormY*self.NormY)))
        self.NormR = np.arctan2(self.NormY,self.NormX)
        self.NormD = self.NormR * 180 / 3.1416;
        self.Squareness = np.zeros([self.cropsize[0],self.cropsize[1]]);
        self.NormDr=self.NormD
        return self.NormalMap(self.NormM,self.NormR);
        
    def run(self):
        self.cap = cv2.VideoCapture(self.channel)
        while self.cap.isOpened():
            ok, frame = self.cap.read()
            if not ok: break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            self.size = np.array(rgb.shape)
            gray = self.Process(rgb,[self.resolution,self.resolution])
            self.cropsize = [self.resolution,self.resolution]
            if self.doOverlay.toc():
                self.overlay = self.GradFilter(gray)
            self.rawimg = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGBA)
            threshmask = np.ones([self.resolution,self.resolution]) * self.threshold
            try:
                alp = (self.overlay[:,:,3] > threshmask) * 255
                self.image = (self.overlay)
            except:
                self.image = self.rawimg
                
            
            self.IsNewImageAvailable = True
            self.frame_ready.emit()
        self.cap.release();
