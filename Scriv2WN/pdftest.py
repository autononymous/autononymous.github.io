# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 22:37:19 2026

@author: rkiss
"""

import pdfkit as pdf
import os

filein = os.getcwd() + r'\PDFcompiler\templateFile.html'
fileout = os.getcwd() + r'\PDFcompiler\test.pdf'
print(filein,fileout)
a = pdf.from_file(filein)