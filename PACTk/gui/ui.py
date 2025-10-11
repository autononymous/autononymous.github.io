# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 13:07:46 2025

@author: rkiss
"""

import colorsys as cs

import tkinter as tk
from tkinter import (ttk, font)
from PIL import (Image, ImageTk)

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class FrontEnd:    
    class StyledFont:
        HeaderFont = 'Helvetica'
        BodyFont = 'Helvetica'
        def Title(self, parent): return font.Font(parent, family=self.HeaderFont, size=18, weight='bold')
        def Subtitle(self, parent): return font.Font(parent, family=self.HeaderFont, size=16, weight='bold', underline=True)
        def Label(self, parent): return font.Font(parent, family=self.BodyFont, size=14)
        def Body(self, parent): return font.Font(parent, family=self.BodyFont, size=10)
       
    def loadImage(self, mst,src): return ImageTk.PhotoImage( master=mst, image=Image.open(src),size=(250,150))
            
    def DeployFrame(self, CVimage, camID=0,wpos=0,hpos=0):
        TkCanvas = self.CFEED1_CAM if (camID == 0) else self.CFEED2_CAM
        PIL_img = Image.fromarray(CVimage)
        TkImage = ImageTk.PhotoImage(PIL_img, master=TkCanvas)
        TkCanvas.create_image(wpos,hpos,image=TkImage,anchor=tk.CENTER)
        TkCanvas.image = TkImage
        
    def DrawHistogram(self, cam, entries):
        HistPlt = self.RDAT_HIST1_PLT if cam==0 else self.RDAT_HIST2_PLT
        PltCanvas = self.RDAT_HIST1_CANV if cam==0 else self.RDAT_HIST2_CANV
        HistPlt.cla()
        N, bins, patches = HistPlt.hist(entries,bins=self.HISTBINS,rwidth=1.0,color=self.s_STOLLE)#range=(-45,45))
        PltCanvas.draw()
        #for i in range(self.HISTBINS):
        #    patches[i].set_facecolor(self.HISTCOLOR[i,:])
        PltCanvas.get_tk_widget().pack()
        
    def RunUpdate(self):
        self.ROOT.update_idletasks()
        self.ROOT.update()
        
    def getWindowSize(self) -> int:
        return int(self.CFEED1_FRAME.winfo_height()), int(self.CFEED1_FRAME.winfo_width())
        
    def GetAlpha(self):  # {0.0,1.0} => {0.05,0.95}
        value = (self.LCTRL_F1_W1.get() * 0.9) + 0.05
        return value
    def GetKernel(self): # {0.0,1.0} => {1, 25} INT
        value = int((self.LCTRL_F1_W2.get() * 24) + 1)
        return value
    def GetSamples(self):
        return self.LCTRL_F1_W3.get()
    
    def SetFPS(self,cam,val):
        PanelID = self.RDAT_FPS1_V if cam==0 else self.RDAT_FPS2_V
        PanelID.configure(text=str(np.round(val,2)))
        
    def SetOffset(self,cam,Cx,Cy):
        PanelID = self.RDAT_OFF1_V if cam==0 else self.RDAT_OFF2_V
        PanelID.configure(text="{ "+str(np.round(Cx,0)) + ", " +str(np.round(Cy,0)) + " }" )
        
    def SetAngle(self,cam,angle):
        PanelID = self.RDAT_ANG1_V if cam==0 else self.RDAT_ANG2_V
        PanelID.configure(text=str(np.round(angle,1)))
    
# %%        
    def __init__(self):
        self.ROOT = tk.Tk()
        
        self.ROOT.columnconfigure(0, weight=0, uniform=300)
        self.ROOT.columnconfigure(1, weight=2, minsize=400)
        self.ROOT.columnconfigure(2, weight=0, uniform=300)
        
        self.ROOT.rowconfigure(0, weight=1, minsize=200)
        self.ROOT.rowconfigure(1, weight=0, uniform=50)
        
        self.debugitem = None
        
        self.ROOT.title('Stolle PACT Interface')
        self.ROOT.configure(background="black")
        self.ROOT.geometry('1200x1000')
        
        self.i_LOGO = 'logo_white.png'
        
        self.STYLE = {
            'BG':   ['#121212','#323232','#505050','#636363','#8A8A8A','#ABABAB','#D0D0D0','#E2E2E2','#EEEEEE','#F7F7F7'],    
            'MAIN': ['#003F9A','#005DB9','#026DCB','#057FDE','#048DEC','#379DEF','#5DAEF1','#8BC5F5','#B8DBF9','#E2F1FC'],    
            'COMP': ['#B95D00','#C37105','#ca7f0c','#cf8d13','#d3971a','#d7a532','#dcb453','#e5c983','#efdeb4','#f8f2e1']
            }
        
        self.FONT = self.StyledFont()
        self.s_BACKGROUND = self.STYLE['BG'][0]
        self.s_DP1 = self.STYLE['BG'][1]
        self.s_DP2 = self.STYLE['BG'][2]
        self.s_BORDER = self.STYLE['BG'][2]
        self.s_H1 = self.STYLE['BG'][6]
        self.s_H2 = self.STYLE['BG'][5]
        self.s_BODY = self.STYLE['BG'][8]
        self.s_STOLLE = self.STYLE['MAIN'][1]
    
        self.HISTBINS = 21
        self.HISTCOLOR = np.ones([self.HISTBINS,4])
    
        # Establish histogram gradient
        
        for i in range(self.HISTBINS):
            rgb = cs.hsv_to_rgb((112/255) * (i/self.HISTBINS), 0.8, 0.8)
            for j in range(3):
                self.HISTCOLOR[i,j] = rgb[j]
            self.HISTCOLOR[i,0] = rgb[0]
    
        # %% |======================================================|
        #    |                LEFT PANEL ELEMENTS                   |
        #    |======================================================|
        #
        #    |------------[ PRIMARY ELEMENTS ]------------|
        self.LPANEL = tk.Frame(  
                            master=self.ROOT,
                            background=self.s_BORDER,
                            borderwidth=1,
                            )
        self.LPANEL.grid(        
                            row=0,
                            column=0,
                            sticky="nsew"
                            )
        
        
        #    |-----------[ SECONDARY ELEMENTS ]-----------|
        self.LGRID = tk.Frame(   
                            master=self.LPANEL,
                            background=self.s_DP1,
                            borderwidth=2
                            )
        self.LGRID.pack(         
                            fill=tk.BOTH, 
                            side=tk.LEFT, 
                            expand=True         
                            )
        
        # >> Logo in top bar...
        self.logo = self.loadImage(self.LGRID,self.i_LOGO)
        self.LLOGO = tk.Label(   
                            master=self.LGRID,
                            image=self.logo,
                            background=self.s_DP1,
                            )
        self.LLOGO.grid(         
                            row=0,
                            column=0,
                            ipadx=25,
                            sticky="ns"
                            )
        
        # >> Subtitle...
        self.LSUB = tk.Label(   
                            master=self.LGRID,
                            text="PACT Alignment Tool",
                            background=self.s_DP1,
                            foreground=self.s_H1,
                            font=self.FONT.Title(self.LGRID),
                            )
        self.LSUB.grid(
                            row=1,
                            column=0,
                            )
        
        # >> Control Panel...
        self.LCTRL = tk.Frame(
                            master=self.LGRID,
                            background=self.s_DP2,
                            borderwidth=1,
                            )
        self.LCTRL.grid(
                            row=2,
                            column=0,
                            padx=10,
                            pady=10
                            )
        # >> CTRL group ONE label:
        self.LCTRL_F1 = tk.Label(
                            master=self.LCTRL,
                            font=self.FONT.Subtitle(self.LCTRL),
                            text="Control Set",
                            background=self.s_DP2,
                            foreground=self.s_H2,
                            width=25,
                            )
        self.LCTRL_F1.grid(
                            row=0,
                            column=0,
                            columnspan=2,
                            padx=10,
                            pady=10,
                            )
        
        # >> CTRL group ONE setting ONE:
        self.LCTRL_F1_S1 = tk.Label(
                            master=self.LCTRL,
                            text="Alpha Level",
                            font=self.FONT.Label(self.LCTRL),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.LCTRL_F1_S1.grid( row=1, column=0, pady=10 )
        
        # >> CTRL group ONE setting ONE slider:
        self.LCTRL_F1_W1 = tk.Scale(
                            master=self.LCTRL,
                            sliderlength=20,
                            from_=0,
                            to=1, 
                            length=150,
                            resolution=0.01,
                            tickinterval=0.2,
                            orient=tk.HORIZONTAL,
                            background=self.s_DP2,
                            foreground=self.s_H1,
                            )
        self.LCTRL_F1_W1.set(0.500);
        self.LCTRL_F1_W1.grid( row=1, column=1, pady=10 )
        
        # >> CTRL group ONE setting TWO:
        self.LCTRL_F1_S2 = tk.Label(
                            master=self.LCTRL,
                            text="Blurring",
                            font=self.FONT.Label(self.LCTRL),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.LCTRL_F1_S2.grid( row=2, column=0, pady=10 )
        
        # >> CTRL group ONE setting TWO slider:
        self.LCTRL_F1_W2 = tk.Scale(
                            master=self.LCTRL,
                            sliderlength=20,
                            from_=0,
                            to=1, 
                            length=150,
                            resolution=0.01,
                            tickinterval=0.2,
                            orient=tk.HORIZONTAL,
                            background=self.s_DP2,
                            foreground=self.s_H1,
                            )
        self.LCTRL_F1_W2.set(0.750);
        self.LCTRL_F1_W2.grid( row=2, column=1, pady=10 )
        
        # >> CTRL group ONE setting THREE:
        self.LCTRL_F1_S3 = tk.Label(
                            master=self.LCTRL,
                            text="Sampling",
                            font=self.FONT.Label(self.LCTRL),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.LCTRL_F1_S3.grid( row=3, column=0, pady=10 )
        
        # >> CTRL group ONE setting THREE slider:
        self.LCTRL_F1_W3 = tk.Scale(
                            master=self.LCTRL,
                            sliderlength=20,
                            from_=1,
                            to=8, 
                            length=150,
                            resolution=1,
                            tickinterval=1,
                            orient=tk.HORIZONTAL,
                            background=self.s_DP2,
                            foreground=self.s_H1,
                            )
        self.LCTRL_F1_W3.set(4);
        self.LCTRL_F1_W3.grid( row=3, column=1, pady=10 )
        
                                              
        # %% |======================================================|
        #    |                CENTER WINDOW ELEMENTS                |
        #    |======================================================|
        #
        self.CPANEL = tk.Frame(  
                            master=self.ROOT,
                            background=self.s_BORDER,
                            borderwidth=1
                            )        
        self.CPANEL.grid(        
                            row=0,
                            column=1,
                            sticky="nsew"
                            )        
        self.CGRID = tk.Frame(   
                            master=self.CPANEL,
                            background=self.s_BACKGROUND,
                            borderwidth=2
                            )
        self.CGRID.pack(         
                            fill=tk.BOTH, 
                            side=tk.LEFT, 
                            expand=True         
                            )
        
        self.CGRID.columnconfigure(      0, minsize=350, weight=0)
        self.CGRID.rowconfigure(     [0,1], minsize=350, weight=0)
        
        self.CFEED1_FRAME = tk.Frame(   
                            master=self.CGRID,
                            background=self.s_BORDER,
                            borderwidth=2,
                            width=350,
                            height=350
                            )
        self.CFEED1_FRAME.grid(        
                            row=0,
                            column=0,
                            sticky="n",
                            pady=50,
                            padx=50
                            )
        self.CFEED1_FRAME.grid_propagate(False)
        self.CFEED1_CAM = tk.Canvas(
                            master=self.CFEED1_FRAME,
                            background=self.s_BACKGROUND,
                            width=350,
                            height=350,
                            )
        self.CFEED1_CAM.pack(         
                            fill=tk.BOTH, 
                            side=tk.LEFT, 
                            expand=True
                            )
        
        self.CFEED2_FRAME = tk.Frame(   
                            master=self.CGRID,
                            background=self.s_BORDER,
                            borderwidth=2,
                            width=350,
                            height=350,
                            )
        self.CFEED2_FRAME.grid(        
                            row=1,
                            column=0,
                            sticky="n"
                            )
        self.CFEED2_CAM = tk.Canvas(
                            master=self.CFEED2_FRAME,
                            background=self.s_BACKGROUND,
                            width=350,
                            height=350,
                            )
        self.CFEED2_CAM.pack(         
                            fill=tk.BOTH, 
                            side=tk.LEFT, 
                            expand=True
                            )
        
        
        # %% |======================================================|
        #    |                RIGHT PANEL ELEMENTS                  |
        #    |======================================================|
        #
        self.RPANEL = tk.Frame(  
                            master=self.ROOT,
                            background=self.s_BORDER,
                            borderwidth=1
                            )
        self.RPANEL.grid(        
                            row=0,
                            column=2,
                            sticky="nsew"
                            )
        
        #    |-----------[ SECONDARY ELEMENTS ]-----------|
        self.RGRID = tk.Frame(   
                            master=self.RPANEL,
                            background=self.s_DP1,
                            borderwidth=2
                            )
        self.RGRID.pack(         
                            fill=tk.BOTH, 
                            side=tk.RIGHT, 
                            expand=True,
                            ipadx=25
                            )
        # FRAME 1, CAM 1 DATA ===================================
        self.RDAT_FRAME_1 = tk.Frame(
                            master=self.RGRID,
                            background=self.s_DP2,
                            borderwidth=1,
                            )
        self.RDAT_FRAME_1.grid(row=0, column=0, pady=10)
        
        self.RDAT_H1 = tk.Label(
                            master=self.RDAT_FRAME_1,
                            text="Camera 1 Analytics",
                            font=self.FONT.Subtitle(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_H1,                    
                            )
        self.RDAT_H1.grid( row=0, column=0, columnspan=2, pady=10 )
        
        # |-------------------------------------------
        # |  FRAMES PER SECOND:
        # |-------------------------------------------
        self.RDAT_FPS1_L = tk.Label(
                            master=self.RDAT_FRAME_1,
                            text="Frames Per Second [FPS]",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_FPS1_L.grid( row=1, column=0, pady=10 )        
        self.RDAT_FPS1_V = tk.Label(
                            master=self.RDAT_FRAME_1,
                            text="XX.XX",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_FPS1_V.grid( row=1, column=1, pady=10 )
        
        # |-------------------------------------------
        # |  OFFSET FROM CENTER:
        # |-------------------------------------------
        self.RDAT_OFF1_L = tk.Label(
                            master=self.RDAT_FRAME_1,
                            text="Center Offset",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_OFF1_L.grid( row=2, column=0, pady=10 )        
        self.RDAT_OFF1_V = tk.Label(
                            master=self.RDAT_FRAME_1,
                            text="XX.XX",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_OFF1_V.grid( row=2, column=1, pady=10 )
        
        # |-------------------------------------------
        # |  ESTIMATED ANGLE OF TARGET:
        # |-------------------------------------------
        self.RDAT_ANG1_L = tk.Label(
                            master=self.RDAT_FRAME_1,
                            text="Estimated Angle",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_ANG1_L.grid( row=3, column=0, pady=10 )        
        self.RDAT_ANG1_V = tk.Label(
                            master=self.RDAT_FRAME_1,
                            text="XX.XX",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_ANG1_V.grid( row=3, column=1, pady=10 )
        
        # |-------------------------------------------
        # |  ANGULAR HISTOGRAM:
        # |-------------------------------------------
        self.RDAT_HIST1 = tk.Label(
                            master=self.RDAT_FRAME_1
                            )
        self.RDAT_HIST1.grid( row=4, column=0, columnspan=2, pady=10)
        self.RDAT_HIST1_FIG = plt.Figure(figsize= (3,3), dpi = 80)
        self.RDAT_HIST1_PLT = self.RDAT_HIST1_FIG.add_subplot(111)
        self.RDAT_HIST1_PLT.get_yaxis().set_visible(False)
        self.RDAT_HIST1_PLT.spines[:].set_visible(False)
        #self.debugitem = self.RDAT_HIST1_PLT
        self.RDAT_HIST1_CANV = FigureCanvasTkAgg(
                            self.RDAT_HIST1_FIG,
                            master=self.RDAT_HIST1
                            )
        #self.RDAT_HIST1_FIG.set_facecolor(self.s_DP2)
        #self.RDAT_HIST1_PLT.set_facecolor(self.s_DP2)
        
        
        
        
        # FRAME 2, CAM 2 DATA ===================================
        self.RDAT_FRAME_2 = tk.Frame(
                            master=self.RGRID,
                            background=self.s_DP2,
                            borderwidth=1,
                            )
        self.RDAT_FRAME_2.grid(row=1, column=0, pady=10)
        
        self.RDAT_H2 = tk.Label(
                            master=self.RDAT_FRAME_2,
                            text="Camera 2 Analytics",
                            font=self.FONT.Subtitle(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_H1,                    
                            )
        self.RDAT_H2.grid( row=0, column=0, columnspan=2, pady=10 )
        
        # |-------------------------------------------
        # |  FRAMES PER SECOND:
        # |-------------------------------------------
        self.RDAT_FPS2_L = tk.Label(
                            master=self.RDAT_FRAME_2,
                            text="Frames Per Second [FPS]",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_FPS2_L.grid( row=1, column=0, pady=10 )        
        self.RDAT_FPS2_V = tk.Label(
                            master=self.RDAT_FRAME_2,
                            text="XX.XX",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_FPS2_V.grid( row=1, column=1, pady=10 )
        
        # |-------------------------------------------
        # |  OFFSET FROM CENTER:
        # |-------------------------------------------
        self.RDAT_OFF2_L = tk.Label(
                            master=self.RDAT_FRAME_2,
                            text="Center Offset",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_OFF2_L.grid( row=2, column=0, pady=10 )        
        self.RDAT_OFF2_V = tk.Label(
                            master=self.RDAT_FRAME_2,
                            text="XX.XX",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_OFF2_V.grid( row=2, column=1, pady=10 )
        
        # |-------------------------------------------
        # |  ESTIMATED ANGLE OF TARGET:
        # |-------------------------------------------
        self.RDAT_ANG2_L = tk.Label(
                            master=self.RDAT_FRAME_2,
                            text="Estimated Angle",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_ANG2_L.grid( row=3, column=0, pady=10 )        
        self.RDAT_ANG2_V = tk.Label(
                            master=self.RDAT_FRAME_2,
                            text="XX.XX",
                            width=20,
                            font=self.FONT.Body(self.RGRID),
                            background=self.s_DP2,
                            foreground=self.s_BODY,                    
                            )
        self.RDAT_ANG2_V.grid( row=3, column=1, pady=10 )
        
        
        
        # |-------------------------------------------
        # |  ANGULAR HISTOGRAM:
        # |-------------------------------------------
        self.RDAT_HIST2 = tk.Label(
                            master=self.RDAT_FRAME_2
                            )
        self.RDAT_HIST2.grid( row=4, column=0, columnspan=2, pady=10)
        self.RDAT_HIST2_FIG = plt.Figure(figsize= (3,3), dpi=80)
        self.RDAT_HIST2_PLT = self.RDAT_HIST2_FIG.add_subplot(111)     
        self.RDAT_HIST2_PLT.get_yaxis().set_visible(False)
        self.RDAT_HIST2_PLT.spines[:].set_visible(False)
        
        self.RDAT_HIST2_CANV = FigureCanvasTkAgg(
                            self.RDAT_HIST2_FIG,
                            master=self.RDAT_HIST2
                            )
        #self.RDAT_HIST2_FIG.set_facecolor([0,0,0])
        #self.RDAT_HIST2_PLT.set_facecolor([0,0,0])
        
                                               
        # %% |======================================================|
        #    |                FOOTER ELEMENTS                       |
        #    |======================================================|
        #
        #    |------------[ PRIMARY ELEMENTS ]------------|
        self.FOOTER = tk.Frame(  
                            master=self.ROOT,
                            background=self.s_BORDER,
                            borderwidth=1
                            )        
        self.FOOTER.grid(        
                            row=1,
                            column=0,
                            columnspan=3,
                            sticky="nsew"
                            )
        
        
if __name__ == "__main__":
    FE = FrontEnd()
    while True:
        FE.RunUpdate()
                                        
                                        