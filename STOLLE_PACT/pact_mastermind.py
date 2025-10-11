# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 09:41:59 2025

@author: rkiss
"""
import time

class Timer:
    def __init__(self, limit):
        self.t0 = time.time() # "bookmark" of last overflow
        self.dt = 0.0         # relative time since last call
        self.limit = limit
    def setLimit(self, limit):
        self.limit = limit
    def tick(self,reset=True): # Get time elapsed
        t1 = time.time()
        self.dt = t1 - self.t0
        if reset: self.t0 = t1
        return self.dt            
    def tock(self,reset=True):
        if self.tick(reset) > self.limit:
            if reset: self.t0 = time.time()
            return True
        else:
            return False
        
class ConditionFlag:
    def __init__(self, Initial=False) -> None: 
        self.State = Initial
        self.wasActive = False # Has been set to TRUE at least once before.
    def check(self) -> bool: return self.State            
    def shake(self):
        if self.State:
            self.State = False
            return True
        else:
            return False          
    def deactivate(self) -> None: self.State = False;            
    def activate(self) -> None: 
        self.State = True
        self.wasActive = True
        
