import ffmpeg

# Audio extracting
class AudioExtractor:
    def __init__(self, extractMP3, extractOGG, inputPath):
        self.extractMP3 = extractMP3
        self.extractOGG = extractOGG
        self.inputPath = inputPath
        self.outputFileName = 'output/'+inputPath.split('/')[1].split('.')[0]
        self.processes = {'mp3': None, 'ogg': None}

    def getProcesses(self):
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
        return self.processes

    def startProcessMP3(self):
        processMP3 = (
            ffmpeg
            .input(self.inputPath.as_posix())
            .output(self.self.outputFileName+'.mp3', format='mp3', map='0:a')
            .global_args('-progress', 'pipe:1', '-stats_period', '0.1')
            .overwrite_output()
            .run_async(pipe_stdout = True)
        )
        return processMP3

    def startProcessOGG(self):
        processOGG = (
            ffmpeg
            .input(self.inputPath.as_posix())
            .output(self.self.outputFileName+'.ogg', format='ogg', map='0:a')
            .global_args('-progress', 'pipe:1', '-stats_period', '0.1')
            .overwrite_output()
            .run_async(pipe_stdout = True)
        )
        return processOGG