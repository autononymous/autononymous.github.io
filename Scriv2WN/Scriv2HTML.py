# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 14:51:53 2026

@author: rkiss
"""

import json as js
import os, sys, glob, time, csv
from datetime import datetime, timedelta
from paragate_gpt_parse import GPT_Parse
import numpy as np
from matplotlib import pyplot as plt
import DebugLog

OnesNames = ["Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen","Eighteen","Nineteen","Twenty"]
TensNames = ["err","err","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]

def GetNumberName(number,spacechar='-'):
    '''! Interpret an integer into a word name.
         @param number  Integer to turn into a word number.
         @param spacechar  Separator to use between tens and ones.'''
    number = int(number)
    # Values not to accept ( @TODO add 100+ but shouldn't be necessary )
    if number > 99 or number < 1:
        debug.append(f'Number value "{number}" not accepted in GetNumberName.','INFO',pri=2)
    # Everything below 20 is unique. No TensName.
    if number < 21:
        OnesName = OnesNames[int(number)]
        TensName = ""
    else:
        # Making sure the number doesn't read "thirty-zero" or something
        if int(number) % 10 == 0:
            OnesName = ""
        else:
            OnesName = spacechar + OnesNames[int(number) % 10]
        TensName = TensNames[int((int(number) - int(number) % 10)/10)]
    return f"{TensName}{OnesName}"

def 