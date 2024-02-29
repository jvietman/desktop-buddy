from enum import Enum

class cmdtype(Enum):
    IGNORE = "ignore"
    
    SETPOS = "setpos"
    MOVE = "move"
    VELOCITY = "velocity"
    FLIP = "flip"
    ROTATE = "rotate"
    
    ANIMATION = "animation"
    RESETANIMATION = "resetanimation"
    
    PLAYSOUND = "playsound"

class command:
    def __init__(self, commandtype: cmdtype, value = None):
        self.commandtype = commandtype
        self.value = value
    
    def astuple(self):
        return (self.commandtype, self.value)