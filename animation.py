from PIL import Image

class animation:
    def __init__(self, frames):
        self.frames = frames
        self.currentframe = 1

    def getframe(self, flipped=False):
        frame = self.currentframe
        self.nextframe()
        if flipped:
            return self.frames[frame].transpose(Image.FLIP_LEFT_RIGHT)
        return self.frames[frame]
    
    def nextframe(self):
        self.currentframe += 1
        if self.currentframe > len(self.frames)-1:
            self.currentframe = 1