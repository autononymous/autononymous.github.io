# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 14:52:52 2026

@author: rkiss
"""

class DebugLog:
    '''! A class that handles debug messages, and stores them until deployment
         is requested.'''
    def flush(self):
        '''! Retrieve all currently stored messages.'''
        for parcel in self.log:
            infotype = (f'[{parcel[0]}]') if parcel[0] != '' else ''
            source = (f'in {parcel[1]}') if parcel[1] != '' else ''
            message = parcel[2]            
            print(f" {infotype} {source}: {message}")
        self.log = []
    def append(self, message, infotype='', source='', pri=0, flush=True):
        '''! Add a string to the sequential debug message ticker.
             @param message  A string to deploy in the console.
             @param infotype  e.g. ERROR, WARN, INFO
             @param source  Function/class of origin.
             @param pri     Priority of this message.
             @param flush   Whether or not to print message immediately.
             '''
        if pri <= self.priorityLevel:
            self.log.append([infotype,source,str(message)])
            if flush is True:
                self.flush()    
    def __init__(self, priority=0):
        '''! Initializing function of DebugLog.
             @param priorit  Messages at or below this level will be read.'''
        self.priorityLevel = priority
        self.log = []    