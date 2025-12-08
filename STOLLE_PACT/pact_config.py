# -*- coding: utf-8 -*-
"""
@file pact_config.py
@author Ryan Kissinger

@brief Organizes graphical styles and common descriptive text strings
       from config.json file.
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
##|                  ░█▀▀░█▀█░█▀█░█▀▀░▀█▀░█▀▀░░░░█▀█░█░█░                   |##
##|                  ░█░░░█░█░█░█░█▀▀░░█░░█░█░░░░█▀▀░░█░░                   |##
##|                  ░▀▀▀░▀▀▀░▀░▀░▀░░░▀▀▀░▀▀▀░▀░░▀░░░░▀░░                   |##
##|=========================================================================|##
##|            :                                                            |##
##|   PROJECT <|> Project "PACT" -- Plate Alignment Calibration Tool        |##
##|            :  AKA the "Pre-Registration Fixture"                        |##
##|            :                                                            |##
##|   COMPANY <|> STOLLE MACHINERY COMPANY, LLC                             |##
##|            :  6949 S. POTOMAC STREET                                    |##
##|            :  CENTENNIAL, COLORADO, 80112                               |##
##|            :                                                            |##
##|      FILE <|> pact_config.py                                            |##
##|            :                                                            |##
##|    AUTHOR <|> Ryan Kissinger                                            |##
##|            :                                                            |##
##|   VERSION <|> '-' - 09/29/25                                            |##
##|            :                                                            |##
##|------------+------------------------------------------------------------|##
##|            :                                                            |##
##|   PURPOSE <|> Loading and deploying configurations.                     |##
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
import json

import tkinter as tk
from tkinter import (ttk, font)

class CONFIG:   
    '''! Loads in all entries from config.json for use by system.'''     
    class PACT_Theme:
        '''! Subclass containing visual styles.'''
        def __init__(self,cfg):
            '''! Initializing function for CONFIG.'''
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
            self.Inactive       = self.L1
            self.Active         = self.L3
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
            self.tab1           = s['tab1']
            self.tab2           = s['tab2']
            self.tab3           = s['tab3']
            self.tab4           = s['tab4']
            
    class SHORTHANDS:
        '''! Subclass containing recurring information strings.'''
        def __init__(self,cfg):
            '''! Initializing function for SHORTHANDS.'''
            self.c = c = cfg
        #> Update this with friendly names for JSON entries when added. #TODO
            self.theme          = c['settings']['theme']
            self.window_x       = c['window'][0]
            self.window_y       = c['window'][1]
            self.version        = c['version']
    class FONTS():
        '''! Stores, instantiates, and deploys fonts to User Interface.'''
        def __init__(self,theme):
            '''! Initializing function for FONTS.'''
            self.f = f = theme.s['fonts']
            self.f_p              = f['p']
            self.f_h1             = f['h1']
            self.f_h2             = f['h2']            
        def p(self,parent=None): 
            '''! The PARAGRAPH style.'''
            return font.Font(
                parent,
                family    = self.f_p[0],
                size      = self.f_p[1],
                weight    = self.f_p[2],
                slant     = self.f_p[3],
                underline = self.f_p[4]
                )                
        def h1(self,parent=None): 
            '''! The HEADER level one style.'''
            return font.Font(
                parent,
                family    = self.f_h1[0],
                size      = self.f_h1[1],
                weight    = self.f_h1[2],
                slant     = self.f_h1[3],
                underline = self.f_h1[4]
                )
        def h2(self,parent=None): 
            '''! The HEADER level two style.'''
            return font.Font(
                parent,
                family    = self.f_h2[0],
                size      = self.f_h2[1],
                weight    = self.f_h2[2],
                slant     = self.f_h2[3],
                underline = self.f_h2[4]
                )    
        
            
    def Parse(self):
        '''! Load configuration and deploy into a class variable.'''
        with open('config.json', 'r') as f: self.CONFIG = json.load(f)
        self.style = self.PACT_Theme(self.CONFIG)
        self.param = self.SHORTHANDS(self.CONFIG)
        self.fonts = self.FONTS(self.style)
    
    def __init__(self):  
        '''! Initializing function for CONFIG.'''
        self.Parse()
        
    
    