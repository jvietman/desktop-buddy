from command import *
from brain import brain
from vector2 import vector2

from datetime import datetime

# when loaded
def load():
    print("happy.py imported!")

# when started
def start(brain: brain, pos: vector2):
    print("happy")

# when called
def main(id: int, args: tuple, brain: brain):
    return [
        command(cmdtype.VELOCITY, vector2(0, brain.stats["jumpforce"])),
        command(cmdtype.PLAYSOUND, "excited")
    ]