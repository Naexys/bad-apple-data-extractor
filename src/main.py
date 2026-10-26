import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pathlib import Path
import ffmpeg
import math
from . import extractor
from . import diskspace

class Application:
    def __init__(self):
        # Display welcome message
        messagebox.showinfo(title='Welcome !', message='This GUI will allow you to ajust some settings before starting.')

        # Check for input file
        self.inputExists, self.inputWidth, self.inputHeight, self.inputFPS, self.inputLength, self.inputPath, errorCode = self.checkInput()

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

            # Infos
            self.inputLengthSeconds = self.inputLength / 1000000
            self.varNbFrames = tk.IntVar(value=math.floor(self.varFPS.get() * self.inputLengthSeconds))
            self.varTextSizePreview = tk.StringVar(value=f'Estimated frames output size : {diskspace.getFramesDiskSpace(self.varChars.get(),self.varWidthRes.get(),self.varHeightRes.get(),self.varNbFrames.get())}')

            # Populate window
            self.buildContent(self.window)

            # Window loop
            self.window.mainloop()
        # Handle input file related errors
        else:
            match errorCode:
                # File does not exist
                case 'pathError':
                    messagebox.showerror(title='Error', message='Something went wrong', detail='The input file seems to be missing or misnamed.\nCheck the content of the \'input\' folder and read the \'README.md\' file for additionnal infos.')
                # ffprobe error
                case 'ffprobeError':
                    messagebox.showerror(title='Error', message='Something went wrong', detail='FFmpeg was not able to extract the file\'s metadata.')
                # FFmpeg installation error
                case 'ffmpegError':
                    messagebox.showerror(title='Error', message='Something went wrong', detail='There was an issue with FFmpeg, it is either not installed or not properly installed.\nType \'ffmpeg\' in a terminal to see if it exists on your system.')
                # Other (should not happend)
                case _:
                    messagebox.showerror(title='Error', message='Something went wrong')

    # Checks if the input video exists
    def checkInput(self):
        input = [Path('input/bad-apple.mp4'), Path('input/input.mp4')]
        path = -1
        for p in input:
            if p.exists():
                path = p
        if path == -1:
            # Input does not exist
            return 0, 0, 0, 0, 0, 0, 'pathError'

        try:
            probe = ffmpeg.probe(path.as_posix())
        except:
            # FFmpeg does not exist or is no properly installed
            return 0, 0, 0, 0, 0, 0, 'ffmpegError'

        try:
            # Isolate main video stream
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            # Get video infos from the stream
            width = video_stream['width']
            height = video_stream['height']
            length = float(video_stream['duration'])
            length = round(length * 1000000)
            frameNumerator, frameDenominator = video_stream['r_frame_rate'].split('/')
            fps = int(frameNumerator)//int(frameDenominator)
        except:
            # ffprobe failed to retreive metadata
            return 0, 0, 0, 0, 0, 0, 'ffprobeError'
                   
        # returns inputExists (0/1), inputWidth (width in pixel), inputHeight (height in pixel), inputFPS (1 or more)
        return 1, width, height, fps, length, path, -1

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

        # File size preview
        self.textSizePreview = tk.Label(window, textvariable=self.varTextSizePreview)
        self.textSizePreview.grid(column=0, columnspan=5, row=10)
        
        # Start button
        self.buttonStart = tk.Button(window, text='Start rendering', command=self.startRender)
        self.buttonStart.grid(column=0, columnspan=5, row=11)

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
        
        self.textRatio = tk.Label(window, text='Keep original aspect ratio :')
        self.textRatio.grid(column=6, columnspan=2, row=12, sticky='e')
        
        self.checkbuttonRatio = tk.Checkbutton(window, variable=self.varKeepRatio, onvalue=1, offvalue=0)
        self.checkbuttonRatio.grid(column=8, row=12, sticky='w')

        # User user input control and effects
        def updateTextSizePreview():
            self.varTextSizePreview.set(f'Estimated frames output size : {diskspace.getFramesDiskSpace(self.varChars.get(),self.varWidthRes.get(),self.varHeightRes.get(),self.varNbFrames.get())}')

        # Handle FPS spinbox
        def varFPSCallback(a, b, c):
            try:
                if self.varFPS.get() > self.inputFPS:
                    self.varFPS.set(self.inputFPS)
                if self.varFPS.get() < 0.1:
                    self.varFPS.set(0.1)
                self.varNbFrames.set(math.floor(self.varFPS.get() * self.inputLengthSeconds))
                # If possible, update frame output size estimation
                try:
                    self.varWidthRes.get()
                    self.varHeightRes.get()
                    updateTextSizePreview()
                except:
                    pass
            except:
                pass

        self.varFPS.trace_add('write', varFPSCallback)

        # Handle character use check
        def varCharsCallback(a, b, c):
            # Enable or disable character fields
            if self.entryCharWhite['state'] == 'disabled':
                self.entryCharWhite['state'] = 'normal'
            else:
                self.entryCharWhite['state'] = 'disabled'
            if self.entryCharBlack['state'] == 'disabled':
                self.entryCharBlack['state'] = 'normal'
            else:
                self.entryCharBlack['state'] = 'disabled'
            # If possible, update frame output size estimation
            try:
                self.varWidthRes.get()
                self.varHeightRes.get()
                updateTextSizePreview()
            except:
                pass

        self.varChars.trace_add('write', varCharsCallback)

        # Handle too much characters in entry (max 1)
        def varCharColourTrim(colour):
            if colour == 'white' and len(self.varCharWhite.get()) > 0:
                self.varCharWhite.set(self.varCharWhite.get()[0])
            if colour == 'black' and len(self.varCharBlack.get()) > 0:
                self.varCharBlack.set(self.varCharBlack.get()[0])

        self.varCharWhite.trace_add('write', lambda a, b, c : varCharColourTrim('white'))
        self.varCharBlack.trace_add('write', lambda a, b, c : varCharColourTrim('black'))

        # Create
        self.rectRatioPreview = self.canvasPreview.create_rectangle(0, 0, 0, 0, fill='black')
        # Update target espect ratio preview
        def updateRatioPreview():
            canvasSize = int(self.canvasPreview['width'])
            size = {'width': self.varWidthRes.get(), 'height': self.varHeightRes.get()}
            if size['width'] >= size['height']:
                previewWidth = int(canvasSize * 0.8)
                previewHeight = (previewWidth*size['height'])//size['width']
                xStart = (canvasSize - previewWidth)//2
                yStart = (canvasSize - previewHeight)//2
                self.canvasPreview.coords(self.rectRatioPreview, xStart, yStart, xStart + previewWidth, yStart + previewHeight)
            elif size['width'] < size['height']:
                previewHeight = int(canvasSize * 0.8)
                previewWidth = (previewHeight*size['width'])//size['height']
                xStart = (canvasSize - previewWidth)//2
                yStart = (canvasSize - previewHeight)//2
                self.canvasPreview.coords(self.rectRatioPreview, xStart, yStart, xStart + previewWidth, yStart + previewHeight)
            self.canvasPreview.update()

        updateRatioPreview()

        # Handle target resolution change
        def varResCallback(changed):
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
                self.traceIDHeight = self.varHeightRes.trace_add('write', lambda a, b, c : varResCallback('height'))
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
                self.traceIDWidth = self.varWidthRes.trace_add('write', lambda a, b, c : varResCallback('width'))
            # If possible, update ratio preview and frame output size estimation
            try:
                self.varHeightRes.get()
                self.varWidthRes.get()
                updateRatioPreview()
                updateTextSizePreview()
            except:
                pass

        # Handle ratio checkbox status changes
        def varFPSCallback(a, b, c):
            if self.varKeepRatio.get():
                try:
                    self.varWidthRes.get()
                    self.varHeightRes.get()
                    varResCallback('width')
                except:
                    pass

        # Add input control on resolution settings
        self.traceIDWidth = self.varWidthRes.trace_add('write', lambda a, b, c : varResCallback('width'))
        self.traceIDHeight = self.varHeightRes.trace_add('write', lambda a, b, c : varResCallback('height'))
        self.varKeepRatio.trace_add('write', varFPSCallback)

    # Check inputs one last time and start render
    def startRender(self):
        # Check inputs
        isOK = True
        try:
            self.varFPS.get()
            self.varWidthRes.get()
            self.varHeightRes.get()
            if self.varChars.get():
                if self.varCharWhite.get() == '' or self.varCharBlack.get() == '':
                    isOK = False
        except:
            isOK = False
        # If tests are good, start rendering
        if isOK:
            self.window.destroy()
            extractor.Extractor(
                self.varMP3.get(),
                self.varOGG.get(),
                self.varFPS.get(),
                self.varWidthRes.get(),
                self.varHeightRes.get(),
                self.varChars.get(),
                self.varCharWhite.get(),
                self.varCharBlack.get(),
                self.inputLength,
                self.inputPath,
                self.varDemo.get()
            )
            pass

app = Application()

# TODO: add disk size preview (to avoid 1.89Go surprises :P)