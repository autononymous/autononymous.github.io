# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 13:53:22 2025

@author: rkiss
"""
width = 40
length = 40

import random as rand

stringout = ""
RL = 0
for l in range(length):
    for w in range(width):
        r = rand.randint(65, 90)
        r = r if (r != RL) else rand.randint(65, 90)
        RL = r
        stringout += f"{chr(r)} "
    stringout += "\n"

print(stringout)