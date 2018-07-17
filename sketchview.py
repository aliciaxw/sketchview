import glob
import os
import random
import tkFileDialog
from Tkinter import *
from PIL import Image


class SketchView:

    def __init__(self, window):

        self.CONST_ZOOM = 100
        self.STARTED = False
        self.window = window

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

    """
    Updates visibility of canvas and init message upon STARTED change.
    """
    def changeVisbility(self):
        if self.STARTED:
            self.canvas.pack(fill=BOTH, expand=True)
            self.lbl_start.pack_forget()
        else:
            self.lbl_start.pack(fill=BOTH, expand=True)
            self.canvas.pack_forget()

    """
    Starts the round when you select a folder. Acts as initialization.
    For now displays a random file in the directotry.
    """
    def openFolder(self):
        self.window.folder_path = tkFileDialog.askdirectory(initialdir=os.getcwd(), title='Select folder')  
        self.STARTED = True
        self.img_files = glob.glob(str(self.window.folder_path+'\*.ppm')) # returns list
        random.shuffle(self.img_files) # randomizes list order
        self.img_ptr = 0 # start at first element of list
        self.selectImage()
        self.updateImage()
        self.changeVisbility()
        #self.clicked()
        
    """
    Keeps track of the current image being displayed.
    TODO: allow change based on time.
    """
    def selectImage(self):
        self.img_current = self.img_files[self.img_ptr]
        self.img = PhotoImage(file=self.img_current)
        self.lbl_filename.configure(text=self.img_current) # change filename

    """
    Clears the canvas and displays the image.
    """
    def updateImage(self):
        self.canvas.delete('all')
        self.window.update()
        self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=self.img)

    """
    Changes to next image in img_files.
    """
    def nextImage(self):
        if self.STARTED and self.img_ptr<len(self.img_files)-1:
            self.img_ptr += 1
            self.selectImage()
            self.updateImage()
            self.clicked()

    """
    Changes to prev image in img_files.
    """
    def prevImage(self):
        if self.STARTED and self.img_ptr>0:
            self.img_ptr -= 1
            self.selectImage()
            self.updateImage()
            self.clicked()

    """
    Sets state back to unstarted. 
    """
    def reset(self):
        self.window.folder_path = None
        self.img_files = None
        self.img_ptr = None
        self.img_current = None
        self.img = None
        self.lbl_filename.configure(text='')
        self.STARTED = False
        self.changeVisbility()
        self.clicked()

    """
    Recenters image when window is resized.
    """
    def repositionImage(self, event):
        # print('reposition called')
        new_x = event.width/2
        new_y = event.height/2
        # print(new_x)
        # print(new_y)
        self.canvas.delete('all')
        self.canvas.create_image(new_x, new_y, image=self.img)