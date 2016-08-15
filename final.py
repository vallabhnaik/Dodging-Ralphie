
import Tkinter
import tkMessageBox

top = Tkinter.Tk()

def level1():
   import tempo
def level2():
    import level2   
B1 = Tkinter.Button(top, text ="Level 1", command = level1)
B2 = Tkinter.Button(top, text ="Level 2", command = level2)

B1.pack()
B2.pack()

top.mainloop()