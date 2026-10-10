import tkinter as tk
from tkinter import messagebox

class Application:
    def __init__(self):
        self.gui = GUI()

class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Parameters")
        self.buildContent()
        self.window.mainloop()

    def buildContent(self):
        # TODO : build the settings window
        messagebox.showinfo(title='Welcome !', message='This GUI will allow you to ajust some settings before starting.')

app = Application()