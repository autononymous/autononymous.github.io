# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 12:40:09 2025

@author: rkiss
"""
import sys
from main_window import MainWindow
#from widgets/screen import ScreenWidget
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    if not QApplication.instance(): app = QApplication(sys.argv)
    else: app = QApplication.instance() 
    window = MainWindow();
    window.show();        
    sys.exit(app.exec());