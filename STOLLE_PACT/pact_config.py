# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 12:34:25 2025

@author: rkiss
"""
import json

import tkinter as tk
from tkinter import (ttk, font)

class CONFIG:        
    class PACT_Theme:
        def __init__(self,cfg):
            self.s = s = cfg['scheme'][cfg['settings']['theme']]
        # >> Text styles
            self.p              = s['text']['p']
            self.h1             = s['text']['h1']
            self.h2             = s['text']['h2']        
        # >> Background styles and layering
            self.L0             = s['background']['layer0']
            self.L1             = s['background']['layer1']
            self.L2             = s['background']['layer2']
            self.L3             = s['background']['layer3']
        # >> Lighter themed colors (for text)
            self.lightred       = s['light']['red']
            self.lightorange    = s['light']['orange']
            self.lightyellow    = s['light']['yellow']
            self.lightgreen     = s['light']['green']
            self.lightblue      = s['light']['blue']
            self.lightviolet    = s['light']['violet']
        # >> Darker themed colors (modals)
            self.darkred        = s['dark']['red']
            self.darkgreen      = s['dark']['green']
            self.darkblue       = s['dark']['blue']
        # >> Colors representing conditions
            self.true           = s['condition']['true']
            self.false          = s['condition']['false']
            self.warn           = s['condition']['warn']
            self.info           = s['condition']['info']        
        # >> Special theme colors
            self.stolle         = '#005CB9'
        # >> Other theme elements
            self.logoURL        = s['logo']
            
    class SHORTHANDS:
        def __init__(self,cfg):
            self.c = c = cfg
        #> Update this with friendly names for JSON entries when added. #TODO
            self.theme          = c['settings']['theme']
            self.window_x       = c['window'][0]
            self.window_y       = c['window'][1]
            self.version        = c['version']
    class FONTS():
        def __init__(self,theme):
            self.f = f = theme.s['fonts']
            self.f_p              = f['p']
            self.f_h1             = f['h1']
            self.f_h2             = f['h2']            
        def p(self,parent=None): 
            return font.Font(
                parent,
                family    = self.f_p[0],
                size      = self.f_p[1],
                weight    = self.f_p[2],
                slant     = self.f_p[3],
                underline = self.f_p[4]
                )                
        def h1(self,parent=None): 
            return font.Font(
                parent,
                family    = self.f_h1[0],
                size      = self.f_h1[1],
                weight    = self.f_h1[2],
                slant     = self.f_h1[3],
                underline = self.f_h1[4]
                )
        def h2(self,parent=None): 
            return font.Font(
                parent,
                family    = self.f_h2[0],
                size      = self.f_h2[1],
                weight    = self.f_h2[2],
                slant     = self.f_h2[3],
                underline = self.f_h2[4]
                )    
        
            
    def Parse(self):
        with open('config.json', 'r') as f: self.CONFIG = json.load(f)
        self.style = self.PACT_Theme(self.CONFIG)
        self.param = self.SHORTHANDS(self.CONFIG)
        self.fonts = self.FONTS(self.style)
        
    
    def __init__(self):         
        self.Parse()
        
        