# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 12:42:20 2025

@author: rkiss
"""



# %%
import sys, cv2

from widgets.camera import CameraWorker

import numpy as np

from PySide6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QGridLayout,
    QLabel,
    QWidget,
    QStatusBar)
from PySide6.QtCore import Qt 
from PySide6.QtGui import (
    QImage, 
    QIcon,
    QPixmap)

CONFIG = {
    "titles":
    {
         "header":"Stolle Plate Alignment Calibration Tool (PACT)",
         "attrib":"Copyright (c) Stolle Machinery 2025. All rights reserved.",
         "sidebar":"Image Controls"
    },
    "locations":
    {
         "icon":"assets/stolleicon.png"         
    },
    "params":
    {
         "imagesize":[7,10]
    }
}

    
# %%
class MainWindow(QMainWindow):
    def __init__(self):
        # Initialize parent class
        super().__init__()
        #
        # Set window title and icon
        self.setWindowTitle(CONFIG["titles"]["header"])
        self.setWindowIcon(QIcon(CONFIG["locations"]["icon"]))
        #
        # Set initial shape of window
        self.setGeometry(100, 100, 800, 600)
        #
        # Set central widget to be the widget container
        self.WidgetImage = ContainerWidget() # create instance [==CLASS==]
        self.setCentralWidget(self.WidgetImage) # place widget into main window
        #
        # Create status (bottom) bar and set text
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(CONFIG["titles"]["attrib"])
        #
        # Create dock on right side of application
        self.dock = QDockWidget(CONFIG["titles"]["sidebar"])
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        #self.controls = ImageControl(self.WidgetImage)
        #self.dock.setWidget(self.controls)
        
        
# %%        
class ContainerWidget(QWidget):
    # Standard Class Variables
    valueKernel = np.power(5,1);
    valueSquare = np.power(2,CONFIG["params"]["imagesize"][1])
    def __init__(self):
        # Initialize parent class
        super().__init__()
        #
        # Set container to have a grid layout
        self.grid = QGridLayout()  # Create QGridLayout object
        self.setLayout(self.grid)  # Set parent widget layout
        #
        # Instantiate screen as QLabel object
        self.screen = QLabel(alignment=Qt.AlignCenter)
        self.grid.addWidget(self.screen,0,0)
        #
        # Create instance of QThread object CameraWorker
        self.CamWorker = CameraWorker()        
        self.CamWorker.frame_ready.connect(self.update_image) # Link new frame acquisition to function updating frame
        self.CamWorker.start() # Start worker for camera
        
    def update_image(self):
        h, w, ch = self.CamWorker.image.shape
        qimg = QImage(self.CamWorker.image.data, w, h, ch*w, QImage.Format_RGBA8888)
        self.screen.setPixmap(QPixmap.fromImage(qimg))
