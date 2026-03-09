# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 13:25:49 2026

@author: rkiss
"""

import numpy as np
from matplotlib import pyplot as plt

# ohms = (volts * count) / current

volt = 5.00
counts = [5,10,12,16,20]
currents = np.linspace(0.10,1.00,10);

ohms = np.zeros([len(currents),len(counts)]);

i = j = -1
for current in currents:
    i += 1
    for count in counts:
        j += 1
        ohms[i][j] = (volt * count) / current
        

print(ohms)