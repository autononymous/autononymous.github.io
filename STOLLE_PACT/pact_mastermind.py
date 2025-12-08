# -*- coding: utf-8 -*-
"""
@file pact_mastermind.py
@author Ryan Kissinger

@brief Logical operations for the PACT system.
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
##|         ░█▀█▀█░█▀█░█▀▀░▀█▀░█▀▀░█▀▄░█▀█▀█░▀█▀░█▀█░█▀▄░░░░█▀█░█░█░        |##
##|         ░█░█░█░█▀█░▀▀█░░█░░█▀▀░█▀▄░█░█░█░░█░░█░█░█░█░░░░█▀▀░░█░░        |##
##|         ░▀░▀░▀░▀░▀░▀▀▀░░▀░░▀▀▀░▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀░░▀░░▀░░░░▀░░        |##
##|=========================================================================|##
##|            :                                                            |##
##|   PROJECT <|> Project "PACT" -- Plate Alignment Calibration Tool        |##
##|            :  AKA the "Pre-Registration Fixture"                        |##
##|            :                                                            |##
##|   COMPANY <|> STOLLE MACHINERY COMPANY, LLC                             |##
##|            :  6949 S. POTOMAC STREET                                    |##
##|            :  CENTENNIAL, COLORADO, 80112                               |##
##|            :                                                            |##
##|      FILE <|> pact_mastermind.py                                        |##
##|            :                                                            |##
##|    AUTHOR <|> Ryan Kissinger                                            |##
##|            :                                                            |##
##|   VERSION <|> '-' - 09/29/25                                            |##
##|            :                                                            |##
##|------------+------------------------------------------------------------|##
##|            :                                                            |##
##|   PURPOSE <|> Logic systems for PACT.                                   |##
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
import time

class Timer:
    '''! Provides program time since init() and measures time passed. 
         Return elapsed time in a resetting stopwatch style.'''
    def __init__(self, limit):
        '''! The Timer class initializer.
             @param limit  Threshold of the timer.'''
        self.t_old = time.time() 
        # "bookmark" of last overflow.
        self.dt = 0.0         
        # relative time since last call
        self.limit = limit
        
    def setLimit(self, limit):
        '''! Setter function for changing timer limit.'''
        self.limit = limit
        
    def tick(self,reset=True):
        '''! Get time elapsed. Either check without reset, or 
             reset timer on overflow.           
             @param reset  Whether or not to reset timer on overflow.        
             @return  FLOAT The elapsed time.'''
        t_new = time.time()
        # New time for program
        self.dt = t_new - self.t_old
        if reset: self.t_old = t_new
        return self.dt      
      
    def tock(self,reset=True):
        '''! Query if stopwatch has exceeded limit, and reset if desired.        
             @param reset  Whether or not to reset timer on overflow.        
             @return  BOOL whether or not time has exceeded limit.'''
        if self.tick(reset) > self.limit:
            if reset: self.t_old = time.time()
            return True
        else:
            return False
        
class ConditionFlag:
    '''! A class that stores a flag for later handshake.'''
    def __init__(self, Initial=False) -> None: 
        '''! The ConditionFlag class initializer.
             @param Initial  Defaults to initializing FALSE flag, 
             but can start TRUE.
             @var wasActive  Defines whether flag has been true before.'''
        self.State = Initial
        self.wasActive = False # Has been set to TRUE at least once before.
    def check(self) -> bool: 
        '''! Just check the state without handshake.'''
        return self.State
    def shake(self):
        '''! Make the handshake if TRUE and set State back to FALSE.
             @return  Whether handshake was made.'''
        if self.State:
            self.State = False
            return True
        else:
            return False          
    def deactivate(self) -> None: 
        '''! Setter function setting State to FALSE.'''
        self.State = False;            
    def activate(self) -> None: 
        '''! Setter function setting State to TRUE.'''
        self.State = True
        self.wasActive = True
        
