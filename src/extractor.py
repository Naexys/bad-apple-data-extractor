import ffmpeg
from pathlib import Path

# Audio extracting
class AudioExtractor:
    def __init__(self, extractMP3, extractOGG, inputPath):
        # Booleans to select desired output formats
        self.extractMP3 = extractMP3
        self.extractOGG = extractOGG
        # Input path
        self.inputPath = inputPath
        # Output file name and path (without extension), retrived from input file path
        self.outputFileName = 'output/'+inputPath.split('/')[1].split('.')[0]
        # Processes list
        self.processes = {'mp3': None, 'ogg': None}

    # Returns processes after starting them
    def getProcesses(self):
        # Start desired processes
        match (self.extractMP3, self.extractOGG):
            case (True, True):
                self.processes['mp3'] = self.startProcessMP3()
                self.processes['ogg'] = self.startProcessOGG()
            case (True, False):
                self.processes['mp3'] = self.startProcessMP3()
            case(False, True):
                self.processes['ogg'] = self.startProcessOGG()
            case _ :
                pass
        # Return started processes
        return self.processes

    # Return mp3 extraction process after starting it
    def startProcessMP3(self):
        processMP3 = (
            ffmpeg
            # Input
            .input(self.inputPath.as_posix())
            # Output (+ desired format and stream selection = only audio)
            .output(self.self.outputFileName+'.mp3', format='mp3', map='0:a')
            # Progress log every 0.1s
            .global_args('-progress', 'pipe:1', '-stats_period', '0.1')
            # Replace output if exists
            .overwrite_output()
            # Run async, allowing multiple FFmpeg processes at the same time
            .run_async(pipe_stdout = True)
        )
        return processMP3

    # Return ogg extraction process after starting it
    def startProcessOGG(self):
        processOGG = (
            ffmpeg
            # Input
            .input(self.inputPath.as_posix())
            # Output (+ desired format and stream selection = only audio)
            .output(self.self.outputFileName+'.ogg', format='ogg', map='0:a')
            # Progress log every 0.1s
            .global_args('-progress', 'pipe:1', '-stats_period', '0.1')
            # Replace output if exists
            .overwrite_output()
            # Run async, allowing multiple FFmpeg processes at the same time
            .run_async(pipe_stdout = True)
        )
        return processOGG

# Frames extracting
class FrameExtractor:
    def __init__(self, fps, widthRes, heightRes, useChars, charWhite, charBlack, inputPath):
        # User settings
        self.fps = fps
        self.widthRes = widthRes
        self.heightRes = heightRes
        self.useChars = useChars
        self.charWhite = charWhite
        self.charBlack = charBlack
        # Input path
        self.inputPath = inputPath
        # Output file name and path (without extension), retrived from input file path
        self.outputFileName = 'output/'+inputPath.split('/')[1].split('.')[0]
        # Progress log file
        self.progressLog = Path('tmp/frameProgress.log')
        self.progressLog.parent.mkdir(parents=True, exist_ok=True)
        with open(self.progressLog.as_posix(), 'w') as logFile:
            pass

    # Return process after starting it
    def getProcess(self):
        return self.startProcessFrames(), self.progressLog.as_posix()

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
            .global_args('-progress', self.progressLog.as_posix(), '-stats_period', '0.1')
            # Replace output if exists
            .overwrite_output()
            # Run async, allowing multiple FFmpeg processes at the same time
            .run_async(pipe_stdout = True)
        )
        return processFrames