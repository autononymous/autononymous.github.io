# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 22:37:19 2026

@author: rkiss
"""

from pathlib import Path

import pdfkit as pdf

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]

filein = PROJECT_ROOT / "scripts" / "pdf" / "templateFile.html"
fileout = PROJECT_ROOT / "build" / "pdf" / "test.pdf"
fileout.parent.mkdir(parents=True, exist_ok=True)

print(filein, fileout)
a = pdf.from_file(str(filein), str(fileout))