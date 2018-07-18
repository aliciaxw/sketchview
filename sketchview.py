import glob
import os
import random
import time
import tkFileDialog
from Tkinter import *
from PIL import Image

# FIX PREV/NEXT TIMING

class SketchView:

    def __init__(self, window):
        """
        Initialization of GUI widgets
        """
        self.CONST_ZOOM = 100
        self.STARTED = False
        self.window = window

        # timer
        self.timer_limit = 1 #in seconds
        self.TIMER_ON = True
        self.timeEvent = None
        
        # menu
        self.menu = Menu(self.window)
        self.menu_file = Menu(self.menu)
        self.menu_view = Menu(self.menu)
        self.menu_settings = Menu(self.menu)
        self.menu_about = Menu(self.menu)

        self.menu_file.add_command(label='Paths...', command=self.openFolder)
        self.menu_view.add_command(label='Show Timer')
        self.menu_view.add_separator()
        self.menu_view.add_command(label='Horizontal Flip')
        self.menu_view.add_command(label='Vertical Flip')
        self.menu_view.add_separator()
        self.menu_view.add_command(label='Reset View')
        self.menu_settings.add_command(label='Background Color...')
        self.menu_settings.add_command(label='Shortcuts...')
        self.menu_about.add_command(label='by Alicia Wang')

        self.menu.add_cascade(label='File', menu=self.menu_file)
        self.menu.add_cascade(label='View', menu=self.menu_view)
        self.menu.add_cascade(label='Settings', menu=self.menu_settings)
        self.menu.add_cascade(label='About', menu=self.menu_about)
        self.window.config(menu=self.menu)

        # buttons
        self.btn_frame = Frame(self.window)
        self.btn_prev = Button(self.btn_frame, text='Prev', command=self.prevImage)
        self.btn_reset = Button(self.btn_frame, text='Reset', command=self.reset)
        self.btn_nxt = Button(self.btn_frame, text='Next', command=self.nextImage)
        self.btn_zoom = Button(self.btn_frame, text='%d' % (self.CONST_ZOOM)+'% Zoom', command=self.clicked)
        self.btn_length = Button(self.btn_frame, text='30 seconds', command=self.clicked)
        self.lbl_filename = Label(self.btn_frame, text='')
        
        self.btn_frame.pack(anchor='nw', fill=X)
        self.btn_prev.pack(side=LEFT)
        self.btn_reset.pack(side=LEFT)
        self.btn_nxt.pack(side=LEFT)
        self.btn_zoom.pack(side=LEFT)
        self.btn_length.pack(side=LEFT)
        self.lbl_filename.pack(side=RIGHT)
        
        # start message
        self.lbl_start = Label(self.window, text='Select a folder to get started')
        self.lbl_start.pack(fill=BOTH, expand=True)

        # canvas
        self.canvas = Canvas(self.window, width=800, height=600)
        self.canvas.bind('<Configure>', self.repositionImage)
        self.img = None




    # events
    def clicked(self):
        print(self.STARTED)
        
    
    def changeVisbility(self):
        """
        Updates visibility of canvas and init message upon STARTED change. 

        If STARTED, then the canvas is shown. 
        If not STARTED, then the welcome message is shown. 
        """
        if self.STARTED:
            self.canvas.pack(fill=BOTH, expand=True)
            self.lbl_start.pack_forget()
        else:
            self.lbl_start.pack(fill=BOTH, expand=True)
            self.canvas.pack_forget()        

    
    def openFolder(self):
        """
        Initializes and shuffles the chosen folder's images. Also starts the timer.
        
        Currently only supports .ppm files. 
        TODO: add general file support
        """
        self.window.folder_path = tkFileDialog.askdirectory(initialdir=os.getcwd(), title='Select folder')  
        self.STARTED = True
        self.img_files = glob.glob(str(self.window.folder_path+'\*.ppm')) # returns list
        random.shuffle(self.img_files) # randomizes list order
        self.img_ptr = -1 # start at first element of list
        self.changeVisbility()
        self.updateTime()

    
    def selectImage(self):
        """
        Initializes currently displayed image. Also updates filename label.
        """
        self.img_current = self.img_files[self.img_ptr]
        self.img = PhotoImage(file=self.img_current)
        self.lbl_filename.configure(text=self.img_current)

    
    def displayImage(self):
        """
        Clears the canvas and displays the new image.
        """
        self.canvas.delete('all')
        self.window.update()
        self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=self.img)


    def updateImage(self):
        """
        Changes to next image in img_files.
        Only effective if STARTED is True.
        """
        #print("updateImage called")
        if self.STARTED:
            if self.img_ptr==len(self.img_files)-1: # reached end of files
                #print("reset triggered by updateImage")
                self.reset()
            elif self.img_ptr<len(self.img_files)-1:
                #print("next image")
                self.img_ptr += 1
                self.selectImage()
                self.displayImage()


    def nextImage(self):
        """
        Changes to next image in img_files. Used with the button.
        Only effective if STARTED is True.
        """
        #print("nextImage called")
        if self.STARTED:
            if self.img_ptr==len(self.img_files)-1: # reached end
                #print("reset triggered by nextImage")
                self.reset()
            elif self.img_ptr<len(self.img_files)-1:
                #print("next image")
                #self.restartTime()
                self.cancelTime()
                self.updateTime()



    def prevImage(self):
        """
        Changes to prev image in img_files.
        Only effective if STARTED is True.
        """
        if self.STARTED and self.img_ptr>0:
            self.img_ptr -= 2 # jesus pleasus this is a bad fix
            #self.selectImage()
            #self.displayImage()
            self.cancelTime()
            self.updateTime()
            

    def updateTime(self):
        """
        Updates to the next image after a set amount of time.
        """
        #print("time updated")
        self.timeEvent = self.window.after(self.timer_limit*1000, self.updateTime)
        self.updateImage()


    def cancelTime(self):
        """
        Cancels the timer.
        """
        if self.timeEvent is not None:
            #print("timer canceled")
            self.window.after_cancel(self.timeEvent)
            self.timeEvent = None
    

    def reset(self):
        """
        Sets state back to STARTED==False, i.e. the initial screen. 
        """
        #print("reset triggered")
        self.STARTED = False
        self.cancelTime()
        self.window.folder_path = None
        self.img_files = None
        self.img_ptr = None
        self.img_current = None
        self.img = None
        self.lbl_filename.configure(text='')
        self.changeVisbility()
        

    def repositionImage(self, event):
        """
        Recenters image when window is resized.
        """
        # print('reposition called')
        new_x = event.width/2
        new_y = event.height/2
        # print(new_x)
        # print(new_y)
        self.canvas.delete('all')
        self.canvas.create_image(new_x, new_y, image=self.img)