# Audio extracting
class AudioExtractor:
    def __init__(self, extract_mp3, extract_ogg):
        self.processes = None
        match (extract_mp3, extract_ogg):
            case (True, True):
                self.processes = (self.startProcessMP3(), self.startProcessOGG())
            case (True, False):
                self.processes = (self.startProcessMP3(), None)
            case(False, True):
                self.processes = (None, self.startProcessOGG())
            case _ :
                pass

    def getProcesses(self):
        return self.processes

    def startProcessMP3(self):
        return None

    def startProcessOGG(self):
        return None