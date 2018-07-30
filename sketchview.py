import glob
import os
import random
import time
import tkFileDialog
from Tkinter import *
from PIL import Image, ImageTk

# TODO: add customizable keyboard support
# TODO: add pause timer

class SketchView:

    def __init__(self, window):
        """
        Initialization of GUI widgets
        """
        self.filetypes = ('\*.bmp', '\*.gif', '\*.jpg', '\*.jpeg', '\*.png', '\*.ppm', '\*.tif') # accepted image files
        self.STARTED = False
        self.window = window
        self.zoom = 100

        # timer
        # self.TIMER_ON = True      DEBUG
        self.timeEvent = None
        self.countEvent = None
        self.timer_limit = 30       # in seconds
        self.time_left = 0

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
        self.btn_zoom = Button(self.btn_frame, text='%d' % (self.zoom)+'% Zoom', command=self.clicked)
        self.TIMER_OPTIONS = [
            '3 sec', # DEBUG
            '15 sec',
            '30 sec', 
            '60 sec', 
            '90 sec', 
            '120 sec', 
            '300 sec', 
            '600 sec', 
            '1800 sec'
        ]
        self.lbl_timer = StringVar(self.btn_frame)
        self.lbl_timer.set(self.TIMER_OPTIONS[2]) # default val
        self.lbl_timer.trace('w', self.updateTimerLimit)
        self.btn_timer = OptionMenu(self.btn_frame, self.lbl_timer, *self.TIMER_OPTIONS)
        self.lbl_count = Label(self.btn_frame, text='timer')
        self.lbl_filename = Label(self.btn_frame, text='')

        self.btn_frame.pack(anchor='nw', fill=X)
        self.btn_prev.pack(side=LEFT)
        self.btn_reset.pack(side=LEFT)
        self.btn_nxt.pack(side=LEFT)
        self.btn_zoom.pack(side=LEFT)
        self.btn_timer.pack(side=LEFT)
        self.lbl_count.pack(side=LEFT)
        self.lbl_filename.pack(side=RIGHT)

        # start message
        self.lbl_start = Label(self.window, text='Select a folder to get started')
        self.lbl_start.pack(fill=BOTH, expand=True)

        # canvas
        self.canvas = Canvas(self.window, width=800, height=600)
        self.canvas.bind('<Configure>', self.repositionImage)
        self.img = None

        # keyboard events
        self.window.bind('<Right>', self.nextImage)
        self.window.bind('d', self.nextImage)
        self.window.bind('<Left>', self.prevImage)
        self.window.bind('a', self.prevImage)
        self.window.bind('<Escape>', self.reset)
        self.window.bind('r', self.reset)




    def clicked(self):
        print('STARTED is %r' % self.STARTED)


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
        """
        self.window.folder_path = tkFileDialog.askdirectory(initialdir=os.getcwd(), title='Select folder')  
        self.STARTED = True

        self.img_files = []
        for files in self.filetypes:
            self.img_files.extend(glob.glob(str(self.window.folder_path+files))) 
        random.shuffle(self.img_files)
        self.img_ptr = -1
    
        self.changeVisbility()
        self.updateTimer()


    def selectImage(self):
        """
        Initializes currently displayed image and updates filename label.
        """
        self.img_current = self.img_files[self.img_ptr] # img_current is a path string
        self.img_tmp = Image.open(self.img_current)
        self.resizeImageToWindow()
        self.img = ImageTk.PhotoImage(self.img_tmp)
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
        Changes to next image in img_files and manages the countdown timer.
        Only effective if STARTED is True.
        """
        if self.STARTED:
            if self.img_ptr >= len(self.img_files)-1: # reached end of files
                self.reset()
            else:
                self.img_ptr += 1
                self.selectImage()
                self.displayImage()
                self.cancelCount()
                self.countdown(self.timer_limit)


    def nextImage(self, event=None):
        """
        Changes to next image in img_files. Used with the button.
        Only effective if STARTED is True.
        """
        if self.STARTED:
            if self.img_ptr >= len(self.img_files)-1: # reached end of files
                self.reset()
            else:
                self.cancelTimer()
                self.updateTimer()


    def prevImage(self, event=None):
        """
        Changes to prev image in img_files.
        Only effective if STARTED is True.
        """
        if self.STARTED and self.img_ptr > 0:
            self.img_ptr -= 2 # TODO: make this more intuitive
            self.cancelTimer()
            self.updateTimer()


    def updateTimer(self):
        """
        Updates to the next image after timer_limit number of seconds.
        """
        self.timeEvent = self.window.after(self.timer_limit*1000, self.updateTimer)
        self.updateImage()


    def countdown(self, time_left=None):
        """
        Controls the countdown timer.
        """
        if time_left is not None:
            self.time_left = time_left
        if self.time_left > 0:
            self.lbl_count.configure(text='%d' % self.time_left)
            self.time_left = self.time_left-1
            self.countEvent = self.window.after(1000, self.countdown)
        else:
            self.lbl_count.configure(text='time\'s up') # debug?


    def cancelTimer(self):
        """
        Cancels the timer.
        """
        if self.timeEvent is not None:
            self.window.after_cancel(self.timeEvent)
            self.timeEvent = None


    def cancelCount(self):
        """
        Cancels the countdown.
        """
        if self.countEvent is not None:
            self.time_left = 0
            self.window.after_cancel(self.countEvent)
            self.countEvent = None


    def updateTimerLimit(self, *args):
        """
        Updates the timer limit when option is changed in the timer drop down menu.
        """
        self.timer_limit = int(self.lbl_timer.get().split(' ')[0])


    def reset(self, event=None):
        """
        Sets state back to STARTED==False, i.e. the initial screen. 
        """
        self.STARTED = False
        self.cancelTimer()
        self.cancelCount()
        self.lbl_count.configure(text='time\'s up')
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
        new_x = event.width/2
        new_y = event.height/2
        self.canvas.delete('all')
        self.canvas.create_image(new_x, new_y, image=self.img)


    def resizeImageToWindow(self):
        """
        Fits the current image to window bounds with original image ratio intact.
        """
        cur_width, cur_height = self.img_tmp.size 
        self.window.update()
        win_width = self.window.winfo_width()
        win_height = self.window.winfo_height() - self.btn_frame.winfo_height()
        new_width = None
        new_height = None

        if cur_width > win_width:
            new_width = win_width 
            new_height = cur_height * new_width / cur_width
            cur_width = new_width       # updating current dimensions
            cur_height = new_height     # updating current dimensions
        if cur_height > win_height:
            new_height = win_height
            new_width = cur_width * new_height / cur_height
        if new_width is not None and new_height is not None:
            self.img_tmp = self.img_tmp.resize((new_width, new_height), Image.ANTIALIAS)