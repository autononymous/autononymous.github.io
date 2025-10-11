# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 11:08:34 2025

@author: rkiss
"""

import sys, cv2

import numpy as np
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt

from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QDockWidget,
    QFrame,
    QLabel,
    QLayout,
    QLayoutItem,
    QGridLayout,
    QTextBrowser,
    QWidget,
    QWidgetItem,
    QStatusBar,
    QSlider
)
from PySide6.QtCore import (
    QThread, 
    Signal, 
    Qt
)
from PySide6.QtGui import (
    QImage, 
    QIcon,
    QPixmap
)

MIN_IMAGE_BASE2 = 7  # 2^8  = 256
MAX_IMAGE_BASE2 = 10  # 2^10 = 1024

ALPHAIMAGE = False
OPACITY = 0.3
THRESH = 0.160
RESOLUTION = 256

class OverlayWorker(QThread):
    overlay_ready = Signal(QImage)
    
    def run(self): ...


class CameraWorker(QThread):
    frame_ready = Signal(QImage)
    kernel = 5
    resolution = RESOLUTION
    threshold = int(255 * THRESH)
    
    threshfilter = np.ones([resolution,resolution]) * threshold
    
    def setKernel(self,value): self.kernel = value;
    def setResolution(self,value): self.resolution = value;   
    def setThresh(self,value): self.threshold = value; 
    
    def getFrame(self):
        ret = False;
        while ret is not True:
            ret, img = self.cap.read();
            self.size = np.array(img.shape);
        self.frame = img;
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
        result = img[xlim[0]:xlim[1],ylim[0]:ylim[1]]        
        return result
    
    def Filter(self, img, kernel=5):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
        img_blur = cv2.GaussianBlur(img_gray,(kernel,kernel),0);
        return img_blur;
    
    def Process(self, img, imdims=None):
        self.imraw = self.Filter(self.Crop(img,shape=imdims,square=True),self.kernel);
        return self.imraw;
    
    
    def Normalize(self, array):
        dims = np.array(array).shape;
        a_maxima = np.array([np.min(array),np.max(array)]);
        a_range = a_maxima[1] - a_maxima[0];
        for x in range(dims[0]):
            for y in range(dims[1]):
                array[x,y] = (array[x,y] - a_maxima[0]) / a_range;
        return array;
                
    def NormalMap(self, mag, ang, doAlpha=False):  
        zdim = 3
        dims = np.array(mag).shape;
        self.threshfilter = np.ones([dims[0],dims[1]]) * self.threshold
        if doAlpha: zdim = 4
        self.NormMap = np.zeros([self.cropsize[0],self.cropsize[1],zdim],dtype='uint8');
        self.NormMap[:,:,2] = (255 - (128 * (mag)));
        self.NormMap[:,:,1] = (127 + (128 * np.sin(ang) * mag));
        self.NormMap[:,:,0] = (127 + (128 * np.cos(ang) * mag));
        
        self.SqrMap = np.zeros([self.cropsize[0],self.cropsize[1],zdim],dtype='uint8');
        self.SqrMap[:,:,2] = (255 - (128 * (mag)));
        self.SqrMap[:,:,1] = (127 + (128 * np.cos((ang * 4)) * mag));
        self.SqrMap[:,:,0] = (127 + (128 * np.sin((ang * 4)) * mag));
        
        if doAlpha:
            self.NormMap[:,:,3] = (mag > self.threshfilter) * 255
            self.SqrMap[:,:,3] = self.NormMap[:,:,3]            
        
        return self.SqrMap;
    
    def SquarenessMap(self):
        for i in range(self.ImageDims):
            for j in range(self.ImageDims):
                while self.NormDr[i,j] > 45:
                    self.NormDr[i,j] -= 90;
                while self.NormDr[i,j] <= -45:
                    self.NormDr[i,j] += 90;
                self.Squareness[i,j] = 1 - (np.abs(self.NormDr[i,j]) / 45)
        return;
    
    def GradFilter(self, img, samples=4, Alpha=False):
        self.cropsize = np.array(img.shape);
        (self.NormX,self.NormY) = np.gradient(img,samples);
        self.NormM = self.Normalize(np.sqrt((self.NormX*self.NormX) + (self.NormY*self.NormY)))
        self.NormR = np.arctan2(self.NormY,self.NormX)
        self.NormD = self.NormR * 180 / 3.1416;
        self.Squareness = np.zeros([self.cropsize[0],self.cropsize[1]]);
        self.NormDr=self.NormD
        return self.NormalMap(self.NormM,self.NormR,doAlpha=Alpha);
    
    def run(self):
        cap = cv2.VideoCapture(1)
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok: break
            self.size = np.array(frame.shape)
            
            self.imraw = self.Process(frame,[self.resolution,self.resolution])
            self.imnorm = self.GradFilter(self.imraw, Alpha=ALPHAIMAGE)
            if ALPHAIMAGE:
                self.normalpha = self.imnorm[:,:,3] / 255.0
                self.img = np.zeros([self.cropsize[0],self.cropsize[1],3],dtype='uint8')            
                for channel in range(3):
                    addend1 = (self.imraw * (1 - (self.normalpha)))
                    addend2 = (self.imnorm[:,:,channel] * self.normalpha)
                    self.img[:,:,channel] = addend1 + addend2
                self.img = cv2.resize(self.img,[512,512])
                h, w, ch = self.img.shape
                qimg = QImage(self.img.data, w, h, ch*w, QImage.Format_RGB888).copy()
            else:
                self.img = self.imnorm
                h, w, ch = self.img.shape
                qimg = QImage(self.img.data, w, h, ch*w, QImage.Format_RGB888).copy()
            
            # h, w = self.img.shape
            # qimg = QImage(self.img.data, w, h, QImage.Format_Grayscale8)
            self.frame_ready.emit(qimg.copy())  # copy to detach from buffer


class MainWidget(QWidget):
    valueKernel = np.power(5,1);
    valueSquare = np.power(2,MIN_IMAGE_BASE2)
    def __init__(self):
        super().__init__()
        self.grid = QGridLayout()  # Create QGridLayout object
        self.setLayout(self.grid)  # Set parent widget layout
        
        self.label = QLabel(alignment=Qt.AlignCenter)
        self.grid.addWidget(self.label,0,0)
        
        self.CamWorker = CameraWorker()
        self.CamWorker.frame_ready.connect(self.update_frame)
        self.CamWorker.start()
        
        self.OverWorker = OverlayWorker();
        
    def update_frame(self, qimg):
        self.label.setPixmap(QPixmap.fromImage(qimg))       
        
    def update_overlay(self): ...
        
        
        
class ImageControl(QWidget): 
    
    valueKernel = np.power(5,1);
    valueSquare = np.power(2,MIN_IMAGE_BASE2)    
    valueThresh = THRESH
    
    def __init__(self, Image):
        super().__init__()
        
        self.Image = Image
        
        self.controlgrid = QGridLayout()
        self.setLayout(self.controlgrid)
        
        self.setKernel = QLabel('Gaussian Kernel')
        self.KernelSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.KernelSlider.setRange(1,3)
        self.KernelSlider.setTickInterval(1)
        self.KernelValue = QLabel('K = '+str(self.valueKernel),self)
        self.KernelSlider.valueChanged.connect(self.update_value_kernel)
        
        self.setSquare = QLabel('Image Scaling')
        self.SquareSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.SquareSlider.setRange(MIN_IMAGE_BASE2,MAX_IMAGE_BASE2)
        self.SquareSlider.setTickInterval(1)
        self.SquareValue = QLabel('px = '+str(self.valueSquare),self)
        self.SquareSlider.valueChanged.connect(self.update_value_imsquare)  
        
        self.setThresh = QLabel('Normal Threshold')
        self.ThreshSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.ThreshSlider.setRange(0,1000)
        self.ThreshSlider.setTickInterval(5)
        self.ThreshValue = QLabel('th = '+str(self.valueThresh),self)
        self.ThreshSlider.valueChanged.connect(self.update_value_thresh)
        
        self.HistNorm = QLabel('Histogram')
        
        self.controlgrid.addWidget(self.KernelSlider,1,0)
        self.controlgrid.addWidget(self.KernelValue,1,1)
        
        self.controlgrid.addWidget(self.SquareSlider,2,0)
        self.controlgrid.addWidget(self.SquareValue,2,1)
        
        self.controlgrid.addWidget(self.ThreshSlider,3,0)
        self.controlgrid.addWidget(self.ThreshValue,3,1)
        
        self.controlgrid.addWidget(self.HistNorm,4,0,1,2)
                
    def update_value_kernel(self, value):
        self.valueKernel = np.power(5,value)
        self.Image.CamWorker.setKernel(self.valueKernel);
        self.KernelValue.setText(f'K = {self.valueKernel}')
        
    def update_value_imsquare(self, value):
        self.valueSquare = np.power(2,value)
        self.Image.CamWorker.setResolution(self.valueSquare);
        self.SquareValue.setText(f'px = {self.valueSquare}')
        
    def update_value_thresh(self, value):
        self.valueThresh = value / 1000;
        self.Image.CamWorker.setThresh(self.valueThresh);
        self.ThreshValue.setText(f'px = {self.valueThresh}')
        
    def PlotNormalData(self,threshold=0.850):
        if not self.isPlotInit:
            self.NormHist = plt.figure();
            self.isPlotInit = True;
        self.HistVals = [];
        self.AngleEstimate = 0;
        valct = 0;
        for i in range(self.Image.cropsize):
            for j in range(self.ImageDims):
                if self.NormM[i,j] > threshold:
                    HistApp = self.NormD[i,j];
                    while HistApp > 45:
                        HistApp -= 90;
                    while HistApp <= -45:
                        HistApp += 90;
                    self.HistVals.append(HistApp);#np.abs(HistApp));#1 - (np.abs(HistApp)/45)  );#self.NormD[i,j]);
                    self.AngleEstimate += HistApp;#(np.abs(HistApp))
                    valct += 1;
        #self.Hcounts, self.Hbins = np.histogram(self.HistVals,bins=20,range=(-180,180),density=False)
        #self.Hcenters = (self.Hbins[:-1] + self.Hbins[1:]) / 2;
                
        self.AngleEstimate *= (1/valct);
        N = 80
        width = (2*np.pi) / N
        bottom = 5;
        self.NormHist.clf();
        
        #plt.title('Estmated Angle = ' + str(np.round(self.AngleEstimate,1)));
        ax1 = plt.subplot(1,3,(1,2));#, polar=True)
        ax1.hist(self.HistVals,bins=30, density=True, range=(-45,45))
        ax2 = plt.subplot(1,3,3);
        ax2.imshow(np.flip(self.img,2))
        ax2.axis('off')
        plt.title(str(np.round(self.AngleEstimate,2)));
        print('Estmated Angle = ' + str(np.round(self.AngleEstimate,1)))
        #bars = ax.bar(self.Hcenters, self.Hcounts, width=width, bottom=bottom)
        self.NormHist.show();
        
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.menu = self.menuBar();
        
        self.setWindowTitle('STOLLE PACT')
        self.setWindowIcon(QIcon('./stolleicon.png'))
        self.setGeometry(100, 100, 800, 600)
        self.WidgetImage = MainWidget()
        self.setCentralWidget(self.WidgetImage)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Copyright (c) Stolle Machinery 2025. All rights reserved.')
       
        self.dock = QDockWidget('Image Controls')
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.controls = ImageControl(self.WidgetImage)
        self.dock.setWidget(self.controls)       
        

if __name__ == "__main__":
    if not QApplication.instance(): app = QApplication(sys.argv)
    else: app = QApplication.instance() 
    window = MainWindow();
    window.show();    
    sys.exit(app.exec());
           