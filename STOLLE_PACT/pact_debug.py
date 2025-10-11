class Debug:
    def __init__(self, level=0):
        self.txt = ""
        self.level = level;
    def console(self, line, level=0, doFlush=True):
        if self.level >= level:
            self.txt += "\n > " + str(line) if self.txt != "" else str(line)
            if doFlush:
                print(self.txt)
                self.txt = ""
            return