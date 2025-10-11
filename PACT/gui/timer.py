# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 16:41:23 2025

@author: rkiss
"""
import time
    
class Timer:
    def __init__(self, limit):
        self.tick = 0.0         # "bookmark" of last overflow
        self.tock = 0.0         # relative time since last call
        self.limit = limit / 100
    def tic(self): # Get time elapsed
        self.tock = time.time() - self.tick
        return self.tock
        
    def toc(self,reset=True):
        if self.tic() > self.limit:
            if reset: self.tick = time.time()
            return True
        else:
            return False
            
if __name__ == "__main__":
    T = Timer(5.0)
    while True:
        if(T.toc()): print(T.tick)