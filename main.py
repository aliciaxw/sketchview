from Tkinter import Tk
from sketchview import SketchView

def main():
    window = Tk()
    window.title('sketchview')
    window.geometry('800x600')
    window.option_add('*tearOff', False) # avoid dotted line
    run = SketchView(window)
    window.mainloop()

main()