import tkinter
import customtkinter as ctk
from tkinter import Event, filedialog
from defaults import *

CLOSE_BUTTON_COLOR = "#242424"

class ImportImageWithDialog(ctk.CTkFrame):
    # class for importing an image into the editor
    def __init__(self, parent, importer):
        super().__init__(master=parent)
        self.grid(column=0, columnspan=2, row=0, sticky='nsew')
        self.importer = importer
        ctk.CTkButton(self, text='Open Image', command=self.OpenDialog).pack(expand=True)

    def OpenDialog(self):
        # open file using tkinter built in method
        filepath = filedialog.askopenfile().name
        self.importer(filepath)

class ImportImageDirectoryWithDialog(ctk.CTkFrame):
    # class for importing a directory of images into the editor
    def __init__(self, parent, importer):
        super().__init__(master=parent)
        self.grid(column=0, columnspan=2, row=0, sticky='nsew')
        self.importer = importer
        ctk.CTkButton(self, text='Open Images Folder', command=self.OpenDialog).pack(expand=True)
        self.filepath = None

    def OpenDialog(self):
        # open directory using tkinter built in method
        self.filepath = filedialog.askdirectory()
        self.importer(self.filepath)

class ShowImage(tkinter.Canvas):
    def __init__(self, parent, resizer):
        super().__init__(master=parent, bd=0, highlightthickness=0, relief='ridge')
        self.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        self.bind('<Configure>', resizer)

class CloseImageViewerButton(ctk.CTkButton):
    def __init__(self, parent, closer):
        super().__init__(master=parent, text='X',
                         text_color=CLOSE_BUTTON_COLOR,
                         fg_color='transparent',
                         hover_color='firebrick2',
                         border_color='gray25',
                         width=40, height=40, command=closer)
        self.place(relx = 0.99, rely = 0.02, anchor = 'ne')