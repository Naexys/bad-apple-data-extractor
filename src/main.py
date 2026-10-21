import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pathlib import Path
import ffmpeg

class Application:
    def __init__(self):
        # Display welcome message
        messagebox.showinfo(title='Welcome !', message='This GUI will allow you to ajust some settings before starting.')

        # Check for input file
        self.inputExists, self.inputWidth, self.inputHeight, self.inputFPS = self.checkInput()

        if self.inputExists:
            # Window
            self.window = tk.Tk()
            self.window.title('Settings')
            
            self.window.resizable(False, False)

            # Settings
            self.varWidthRes = tk.IntVar(value=self.inputWidth) # Target horizontal resolution
            self.varHeightRes = tk.IntVar(value=self.inputHeight) # Target vertical resolution
            self.traceIDWidth = None
            self.traceIDHeight = None
            self.varKeepRatio = tk.IntVar(value=1) # Keep ratio when editing target res
            self.varChars = tk.IntVar() # Use chars instead of bin
            self.varCharWhite = tk.StringVar() # White Char if used
            self.varCharBlack = tk.StringVar() # Black Char if used
            self.varFPS = tk.DoubleVar(value=self.inputFPS) # Target FPS
            self.varMP3 = tk.IntVar(value=1) # Extract MP3
            self.varOGG = tk.IntVar() # Extract OGG
            self.varDemo = tk.IntVar() # Show demo when done
            
            self.buildContent(self.window)
            
            self.window.mainloop()
        else:
            # TODO: if input does not exist
            pass 

    # Checks if the input video exists
    def checkInput(self):
        input = [Path('input/bad-apple.mp4'), Path('input/input.mp4')]
        path = -1
        for p in input:
            if p.exists():
                path = p
        if path == -1:
            return 0, 0, 0, 0

        probe = ffmpeg.probe(path.as_posix())

        # Isolate main video stream
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video' and stream['profile'] == 'Main'), None)
        # Get video infos from the stream
        width = video_stream['width']
        height = video_stream['height']
        frameNumerator, frameDenominator = video_stream['r_frame_rate'].split('/')
        fps = int(frameNumerator)//int(frameDenominator)
                   
        # returns inputExists (0/1), inputWidth (width in pixel), inputHeight (height in pixel), inputFPS (1 or more)
        return 1, width, height, fps

    # Add components to the settings window
    def buildContent(self, window):
        # FPS setting
        self.textFPS = tk.Label(window, text='Target FPS :')
        self.textFPS.grid(column=0, columnspan=2, row=1)

        self.spinboxFPS = tk.Spinbox(window, width=5, from_=0, to=self.inputFPS, increment=0.1, textvariable=self.varFPS)
        self.spinboxFPS.grid(column=2, row=1)

        # Characters settings
        self.textChars = tk.Label(window, text='Use characters :')
        self.textChars.grid(column=3, row=1, sticky='e')

        self.checkbuttonChars = tk.Checkbutton(window, variable=self.varChars, onvalue=1, offvalue=0)
        self.checkbuttonChars.grid(column=4, row=1, sticky='w')

        # Separator
        ttk.Separator(window, orient='horizontal').grid(column=0, columnspan=5, row=2, sticky='ew', pady=5)

        self.textCharWhite = tk.Label(window, text='Character for white :')
        self.textCharWhite.grid(column=0, columnspan=3, row=3, pady=0)

        self.entryCharWhite = tk.Entry(window, state='disabled', textvariable=self.varCharWhite)
        self.entryCharWhite.grid(column=0, columnspan=3, row=4, sticky='ew')

        self.textCharBlack = tk.Label(window, text='Character for black :')
        self.textCharBlack.grid(column=3, columnspan=2, row=3, pady=0)

        self.entryCharBlack = tk.Entry(window, state='disabled', textvariable=self.varCharBlack)
        self.entryCharBlack.grid(column=3, columnspan=2, row=4, sticky='ew')

        # Separator
        ttk.Separator(window, orient='horizontal').grid(column=0, columnspan=5, row=5, sticky='ew', pady=5)

        # Audio selection
        self.textMP3 = tk.Label(window, text='Extract audio as MP3 :')
        self.textMP3.grid(column=0, columnspan=2, row=6, sticky='e')

        self.textOGG = tk.Label(window, text='Extract audio as OGG :')
        self.textOGG.grid(column=3, row=6, sticky='e')

        self.checkbuttonMP3 = tk.Checkbutton(window, variable=self.varMP3, onvalue=1, offvalue=0)
        self.checkbuttonMP3.grid(column=2, row=6, sticky='w')

        self.checkbuttonOGG = tk.Checkbutton(window, variable=self.varOGG, onvalue=1, offvalue=0)
        self.checkbuttonOGG.grid(column=4, row=6, sticky='w')

        # Separator
        ttk.Separator(window, orient='horizontal').grid(column=0, columnspan=5, row=7, sticky='ew', pady=5)

        # Demo setting
        self.textDemo = tk.Label(window, text='Show demo when done :')
        self.textDemo.grid(column=0, columnspan=2, row=8, sticky='e')

        self.checkbuttonDemo = tk.Checkbutton(window, variable=self.varDemo, onvalue=1, offvalue=0)
        self.checkbuttonDemo.grid(column=2, row=8, sticky='w')

        # Separator
        ttk.Separator(window, orient='horizontal').grid(column=0, columnspan=5, row=9, sticky='ew', pady=5)
        
        # Start button
        self.buttonStart = tk.Button(window, text='Start rendering', command=self.startRender)
        self.buttonStart.grid(column=0, columnspan=5, row=10)

        # Separator
        ttk.Separator(window, orient='vertical').grid(column=5, row=0, rowspan=13, sticky='ns')

        # Preview / Resolution settings
        self.textPreview = tk.Label(window, text='Target aspect ratio preview :')
        self.textPreview.grid(column=6, columnspan=3, row=0)

        self.canvasPreview = tk.Canvas(window, width=200, height=200, bg='white')
        self.canvasPreview.grid(column=6, columnspan=3, row=1, rowspan=9)
        
        self.textWidthRes = tk.Label(window, text='Horizontal resolution :')
        self.textWidthRes.grid(column=6, columnspan=2, row=10)

        self.spinboxWidthRes = tk.Spinbox(window, from_=1, to=self.inputWidth, increment=1, textvariable=self.varWidthRes)
        self.spinboxWidthRes.grid(column=6, columnspan=2, row=11, sticky='ew')
        
        self.textHeightRes = tk.Label(window, text='Horizontal resolution :')
        self.textHeightRes.grid(column=8, row=10)

        self.spinboxHeightRes = tk.Spinbox(window, from_=1, to=self.inputHeight, increment=1, textvariable=self.varHeightRes)
        self.spinboxHeightRes.grid(column=8, row=11)
        
        self.textRatio = tk.Label(window, text='Keep aspect ratio :')
        self.textRatio.grid(column=6, row=12, sticky='e')
        
        self.checkbuttonRatio = tk.Checkbutton(window, variable=self.varKeepRatio, onvalue=1, offvalue=0)
        self.checkbuttonRatio.grid(column=7, row=12, sticky='w')

        # User user input control and effects
        def varCharsCallback(a, b, c):
            if self.entryCharWhite['state'] == 'disabled':
                self.entryCharWhite['state'] = 'normal'
            else:
                self.entryCharWhite['state'] = 'disabled'
            if self.entryCharBlack['state'] == 'disabled':
                self.entryCharBlack['state'] = 'normal'
            else:
                self.entryCharBlack['state'] = 'disabled'

        self.varChars.trace_add('write', varCharsCallback)

        def varCharColourTrim(colour):
            if colour == 'white' and len(self.varCharWhite.get()) > 0:
                self.varCharWhite.set(self.varCharWhite.get()[0])
            if colour == 'black' and len(self.varCharBlack.get()) > 0:
                self.varCharBlack.set(self.varCharBlack.get()[0])

        self.varCharWhite.trace_add('write', lambda a, b, c : varCharColourTrim('white'))
        self.varCharBlack.trace_add('write', lambda a, b, c : varCharColourTrim('black'))
        
        def resolutionRatioControl(changed):
            # Width changed
            if changed == 'width':
                self.varHeightRes.trace_remove('write', self.traceIDHeight)
                # Handle manually entered too high / low value
                try:
                    if self.varWidthRes.get() > self.inputWidth:
                        self.varWidthRes.set(self.inputWidth)
                    if self.varWidthRes.get() < 1:
                        self.varWidthRes.set(1)
                except:
                    pass
                # Adjust height to match ratio
                try:
                    if self.varKeepRatio.get() :
                        self.varHeightRes.set(round((self.varWidthRes.get()*self.inputHeight)/self.inputWidth))
                except:
                    pass
                self.traceIDHeight = self.varHeightRes.trace_add('write', lambda a, b, c : resolutionRatioControl('height'))
            
            # Height changed
            if changed == 'height':
                self.varWidthRes.trace_remove('write', self.traceIDWidth)
                # Handle manually entered too high / low value
                try:
                    if self.varHeightRes.get() > self.inputHeight:
                        self.varHeightRes.set(self.inputHeight)
                    if self.varHeightRes.get() < 1:
                        self.varHeightRes.set(1)
                except:
                    pass
                # Adjust width to match ratio
                try:
                    if self.varKeepRatio.get() :
                        self.varWidthRes.set(round((self.varHeightRes.get()*self.inputWidth)/self.inputHeight))
                except:
                    pass
                self.traceIDWidth = self.varWidthRes.trace_add('write', lambda a, b, c : resolutionRatioControl('width'))

        # Add input control on resolution settings
        self.traceIDWidth = self.varWidthRes.trace_add('write', lambda a, b, c : resolutionRatioControl('width'))
        self.traceIDHeight = self.varHeightRes.trace_add('write', lambda a, b, c : resolutionRatioControl('height'))

        # TODO: add target aspect ratio preview
        
    def startRender(self):
        # TODO: actual render process
        pass

app = Application()