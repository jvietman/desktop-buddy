from PIL import Image
from vector2 import *

def getframe(file, frame):
    gif = file

    try:
        gif.seek(frame)

        img = gif.copy()
        return img
    except EOFError:
        print("EOFError")

def gifconvert(file, res: vector2):
    gif = []
    img = Image.open(file)

    frame = 0
    while True:
        try:
            copy = img.copy()
            copy = copy.resize((res.x, res.y))

            gif.append(copy)

            img.seek(frame)
            frame += 1
        except EOFError:
            img.close()
            return gif