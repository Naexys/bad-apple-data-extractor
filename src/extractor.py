import ffmpeg
from pathlib import Path
import math
from collections import deque
import threading
import tkinter
from tkinter import ttk
import numpy as np
import json
from tkinter import messagebox
import subprocess
from . import demo

# Audio extracting
class AudioExtractor:
    def __init__(self, extractMP3, extractOGG, inputPath):
        # Booleans to select desired output formats
        self.extractMP3 = extractMP3
        self.extractOGG = extractOGG
        # Input path
        self.inputPath = inputPath
        # Output file name and path (without extension), retrived from input file path
        self.outputFileName = 'output/'+inputPath.as_posix().split('/')[1].split('.')[0]
        # Rename file to 'output' if name was 'input'
        if self.outputFileName == 'output/input':
            self.outputFileName = 'output/output'
        # Progress log files
        self.progressLogMP3 = Path('tmp/mp3Progress.log')
        self.progressLogMP3.parent.mkdir(parents=True, exist_ok=True)
        self.progressLogOGG = Path('tmp/oggProgress.log')
        self.progressLogOGG.parent.mkdir(parents=True, exist_ok=True)
        with open(self.progressLogMP3.as_posix(), 'w') as logFile:
            pass
        with open(self.progressLogOGG.as_posix(), 'w') as logFile:
            pass
        # Processes list
        self.processes = {'mp3': None, 'ogg': None}

    # Returns processes after starting them
    def getProcesses(self):
        # Start desired processes
        if self.extractMP3:
            self.processes['mp3'] = self.startProcessMP3()
        if self.extractOGG:
            self.processes['ogg'] = self.startProcessOGG()
        # Return started processes
        return self.processes

    # Return mp3 extraction process after starting it
    def startProcessMP3(self):
        processMP3 = (
            ffmpeg
            # Input
            .input(self.inputPath.as_posix())
            # Output (+ desired format and stream selection = only audio)
            .output(self.outputFileName+'.mp3', format='mp3', map='0:a')
            # Progress log every 0.1s
            .global_args('-progress', self.progressLogMP3.as_posix(), '-stats_period', '0.2')
            # Replace output if exists
            .overwrite_output()
            # Run async, allowing multiple FFmpeg processes at the same time
            .run_async()
        )
        return processMP3

    # Return ogg extraction process after starting it
    def startProcessOGG(self):
        processOGG = (
            ffmpeg
            # Input
            .input(self.inputPath.as_posix())
            # Output (+ desired format and stream selection = only audio)
            .output(self.outputFileName+'.ogg', format='ogg', map='0:a')
            # Progress log every 0.1s
            .global_args('-progress', self.progressLogOGG.as_posix(), '-stats_period', '0.2')
            # Replace output if exists
            .overwrite_output()
            # Run async, allowing multiple FFmpeg processes at the same time
            .run_async()
        )
        return processOGG

# Frames extracting
class FrameExtractor:
    def __init__(self, fps, widthRes, heightRes, inputPath):
        # User settings
        self.fps = fps
        self.widthRes = widthRes
        self.heightRes = heightRes
        # Input path
        self.inputPath = inputPath
        # Output file name and path (without extension), retrived from input file path
        self.outputFileName = 'output/'+inputPath.as_posix().split('/')[1].split('.')[0]
        # If input name was 'input', set to 'output'
        if self.outputFileName == 'input':
            self.outputFileName = 'output'
        # Progress log file
        self.progressLog = Path('tmp/frameProgress.log')
        self.progressLog.parent.mkdir(parents=True, exist_ok=True)
        with open(self.progressLog.as_posix(), 'w') as logFile:
            pass

    # Return process after starting it
    def getProcess(self):
        return self.startProcessFrames()

    # Return frame extracting process after starting it
    def startProcessFrames(self):
        processFrames = (
            ffmpeg
            # Input
            .input(self.inputPath.as_posix())
            # Select only video stream
            .video
            # Apply framerate
            .filter('fps', self.fps)
            # Rescale
            .filter('scale', self.widthRes, self.heightRes)
            # Output: pipe receiving frame data
            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
            # Progress log every 0.1s
            .global_args('-progress', self.progressLog.as_posix(), '-stats_period', '0.2')
            # Replace output if exists
            .overwrite_output()
            # Run async, allowing multiple FFmpeg processes at the same time
            .run_async(pipe_stdout = True)
        )
        return processFrames

# Extractors manager
class Extractor:
    def __init__(self, extractMP3, extractOGG, fps, widthRes, heightRes, useChars, charWhite, charBlack, inputLength, inputPath, playDemo):
        # Store settings recieved from settings GUI
        self.extractMP3 = extractMP3
        self.extractOGG = extractOGG
        self.fps = float(fps)
        self.widthRes = int(widthRes)
        self.heightRes = int(heightRes)
        self.useChars = useChars
        self.charWhite = charWhite
        self.charBlack = charBlack
        self.inputLength = int(inputLength)
        self.inputPath = inputPath
        self.playDemo = playDemo
        self.processMP3 = None
        self.processOGG = None
        self.processFrames = None

        # Array to store frames
        self.frames = []

        # Number of frames to render
        inputLengthSeconds = inputLength / 1000000
        self.nbFrames = math.floor(fps * inputLengthSeconds)

        # Progress logs
        self.progressLogs = {
            'mp3':Path('tmp/mp3Progress.log'),
            'ogg':Path('tmp/oggProgress.log'),
            'frame':Path('tmp/frameProgress.log')
        }

        # GUI
        self.GUI()

    # Run processes
    def runProcesses(self):
        # Create both audio and frame extractors
        audioExtractor = AudioExtractor(self.extractMP3, self.extractOGG, self.inputPath)
        frameExtractor = FrameExtractor(self.fps, self.widthRes, self.heightRes, self.inputPath)

        # Start processes
        audioProcesses = audioExtractor.getProcesses()
        frameProcess = frameExtractor.getProcess()
        return frameProcess, audioProcesses

    # Return progress status (percent, frames[if process == 'frame'])
    def getProgress(self, process):
        # Read only the 20 last rows of the log
        lastLines = None
        with open(self.progressLogs[process], 'r') as log:
            lastLines = list(deque(log, 20))
        # Get last line giving time
        lastTime = next(
            (
                # Remove \n and keep only value
                line.strip().split('=')[1]
                # Browse from the end
                for line in reversed(lastLines)
                # If line contains the time in micro seconds
                if line.startswith('out_time_us')
            ), 0
        )
        # Get last line giving frame
        lastFrame = next(
            (
                # Remove \n and keep only value
                line.strip().split('=')[1]
                # Browse from the end
                for line in reversed(lastLines)
                # If line contains the actual frame
                if line.startswith('frame=')
            ), 0
        )
        return int(lastTime), int(lastFrame) if process == 'frame' else None

    # Handle progress display
    def GUI(self):
        # Start all processes
        frameProcess, audioProcesses =  self.runProcesses()

        # Processes status
        hasEnded = {
            'mp3':False,
            'ogg':False,
            'frame':False
        }

        # Create progress display window
        window = tkinter.Tk()
        window.title('Extracting ...')

        # Build progress bars and labels if process exist
        # MP3
        if self.extractMP3:
            # Variables
            varTextProgressMP3 = tkinter.StringVar(value='0 %')
            varProgressMP3 = tkinter.IntVar(value=0)

            # Components
            labelMP3 = tkinter.Label(text='MP3')
            textProgressMP3 = tkinter.Label(window, textvariable=varTextProgressMP3)
            progressMP3 = ttk.Progressbar(window, length=100, variable=varProgressMP3)

            # Placement
            labelMP3.grid(column=0, row=0)
            progressMP3.grid(column=1, row=0)
            textProgressMP3.grid(column=2, row=0)

        # OGG
        if self.extractOGG:
            # Variables
            varTextProgressOGG = tkinter.StringVar(value='0 %')
            varProgressOGG = tkinter.IntVar(value=0)

            # Components
            labelOGG = tkinter.Label(text='OGG')
            textProgressOGG = tkinter.Label(window, textvariable=varTextProgressOGG)
            progressOGG = ttk.Progressbar(window, length=100, variable=varProgressOGG)

            # Placement
            labelOGG.grid(column=0, row=1)
            progressOGG.grid(column=1, row=1)
            textProgressOGG.grid(column=2, row=1)

        # Frames
        # Variables
        varTextFrames = tkinter.StringVar(value=f'0/{self.nbFrames} Frame(s)')
        varTextProgressFrames = tkinter.StringVar(value='0 %')
        varProgressFrames = tkinter.IntVar(value=0)

        # Components
        textFrames = tkinter.Label(window, textvariable=varTextFrames)
        textProgressFrames = tkinter.Label(window, textvariable=varTextProgressFrames)
        progressFrames = ttk.Progressbar(window, length=100, variable=varProgressFrames)

        # Placement
        textFrames.grid(column=0, row=2)
        progressFrames.grid(column=1, row=2)
        textProgressFrames.grid(column=2, row=2)

        # Rendering the frame an outputting them
        def renderFrames():
            while True:
                # Read a frame
                in_bytes = frameProcess.stdout.read(self.widthRes*self.heightRes*3)
                if not in_bytes:
                    break

                # Convert bytes to 3D array: line(pixel(rgb))
                frame = (
                    np
                    .frombuffer(in_bytes, np.uint8)
                    .reshape(self.heightRes, self.widthRes, 3)
                    .tolist()
                )

                # Create an empty frame
                grayFrame = []

                for line in frame:
                    # Create an empty line
                    grayLine = []
                    for pixel in line:
                        # Get luminance (grayscale)
                        luminance = 0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]
                        # Create an empty pixel
                        grayPixel = None
                        # Populate pixel with either black or white values
                        if self.useChars:
                            if luminance < 128: grayPixel = self.charBlack
                            else: grayPixel = self.charWhite
                        else:
                            if luminance < 128: grayPixel = 0
                            else: grayPixel = 1
                        # Populate line with gray pixels
                        grayLine.append(grayPixel)
                    # Populate frame with gray lines
                    grayFrame.append(grayLine)
                self.frames.append(grayFrame)
                            
        # Start the frame processing thread
        threadFrames = threading.Thread(target=renderFrames, daemon=True)
        threadFrames.start()

        # Actualize progress bars
        def actualize():
            # Actualize MP3 bar if exists
            if self.extractMP3:
                if audioProcesses['mp3'].poll() == None:
                    mp3Progress = self.getProgress('mp3')[0]
                    percentMP3 = max(0, min(round((mp3Progress/self.inputLength)*100), 100))
                    varProgressMP3.set(percentMP3)
                    varTextProgressMP3.set(f'{percentMP3} %')
                else: hasEnded['mp3'] = True
            else: hasEnded['mp3'] = True
            # Actualize OGG bar if exists
            if self.extractOGG:
                if audioProcesses['ogg'].poll() == None:
                    oggProgress = self.getProgress('ogg')[0]
                    percentOGG = max(0, min(round((oggProgress/self.inputLength)*100), 100))
                    varProgressOGG.set(percentOGG)
                    varTextProgressOGG.set(f'{percentOGG} %')
                else: hasEnded['ogg'] = True
            else: hasEnded['ogg'] = True
            # Actualize Frame count and bar
            if frameProcess.poll() == None:
                frameProgress, frameCount = self.getProgress('frame')
                percentFrames = max(0, min(round((frameProgress/self.inputLength)*100), 100))
                varProgressFrames.set(percentFrames)
                varTextProgressFrames.set(f'{percentFrames} %')
                varTextFrames.set(f'{frameCount}/{self.nbFrames} Frame(s)')
            else: hasEnded['frame'] = True
            # Fill progress bars if process finished
            if self.extractMP3 and hasEnded['mp3']:
                varProgressMP3.set(100)
                varTextProgressMP3.set(f'{100} %')
            if self.extractOGG and hasEnded['ogg']:
                varProgressOGG.set(100)
                varTextProgressOGG.set(f'{100} %')
            if hasEnded['frame']:
                varProgressFrames.set(100)
                varTextProgressFrames.set(f'{100} %')
                varTextFrames.set(f'{self.nbFrames}/{self.nbFrames} Frame(s)')
            # Complete bars if process has ended
            if hasEnded['mp3'] and hasEnded['ogg'] and hasEnded['frame']:
                # Dump frames as JSON
                outputJSONPath = 'output/'+self.inputPath.as_posix().split('/')[1].split('.')[0]+'.json'
                # Rename output file to 'output' if it was 'input'
                if outputJSONPath == 'output/input.json':
                    outputJSONPath = 'output/output.json'
                with open(outputJSONPath, 'w') as JSONOutput:
                    json.dump(self.frames, JSONOutput)
                # Display end message
                messagebox.showinfo(title='Done !', message='You should find your output files in the \'output\' folder.\nThanks for using this program !')
                window.destroy()
                if self.playDemo:
                    fileName = self.inputPath.as_posix().split('/')[1].split('.')[0]
                    # If input file was named 'input', change to 'output'
                    if fileName == 'input':
                        fileName = 'output'
                    demo.startDemo(self.widthRes, self.heightRes, fileName, self.useChars, self.charWhite, self.charBlack, self.extractMP3, self.extractOGG, self.fps)
            else:
                # Set an 'alarm' to trigger again this function
                window.after(20, actualize)

        # Trigger the first actualization
        window.after(20, actualize)

        window.mainloop()

        # Terminate remaining processes once the window is closed
        # Terminate MP3 process
        if self.extractMP3:
            if audioProcesses['mp3'].poll() == None:
                # Terminate
                audioProcesses['mp3'].terminate()
                try:
                    # If not terminated after 2sec, kill
                    audioProcesses['mp3'].wait(timeout=2)
                except subprocess.TimeoutExpired:
                    audioProcesses['mp3'].kill()
                    audioProcesses['mp3'].wait()
        # Terminate OGG process
        if self.extractOGG:
            if audioProcesses['ogg'].poll() == None:
                # Terminate
                audioProcesses['ogg'].terminate()
                try:
                    # If not terminated after 2sec, kill
                    audioProcesses['ogg'].wait(timeout=2)
                except subprocess.TimeoutExpired:
                    audioProcesses['ogg'].kill()
                    audioProcesses['ogg'].wait()
        # Terminate frame process
        if frameProcess.poll() == None:
            # Terminate
            frameProcess.terminate()
            try:
                # If not terminated after 2sec, kill
                frameProcess.wait(timeout=2)
            except subprocess.TimeoutExpired:
                frameProcess.kill()
                frameProcess.wait()

        # TODO: play demo if asked for