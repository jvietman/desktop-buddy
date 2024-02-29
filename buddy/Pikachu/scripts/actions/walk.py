from command import *
from brain import brain
from vector2 import vector2

from screeninfo import get_monitors
import random

# when loaded
def load():
    print("walk.py imported!")

# when started
def start(brain: brain, pos: vector2):
    print("walk")
    monitor = get_monitors()[0]

    if pos.x < 200: direction = 1
    elif pos.x > monitor.width-200: direction = 0
    else: direction = random.randint(0, 1)
    steps = random.randint(brain.stats["steps"][0], brain.stats["steps"][1])

    return (direction, steps)

# when called
def main(id: int, args: tuple, brain: brain):
    if id == 0:
        if args[0] == 1:
            return command(cmdtype.FLIP, True)
        else:
            return command(cmdtype.FLIP, False)
        
    if id == 1:
        return command(cmdtype.ANIMATION, "walk")

    if id < args[1]:
        if args[0] == 1:
            return command(cmdtype.MOVE, vector2(brain.stats["walkspeed"], 0))
        else:
            return command(cmdtype.MOVE, vector2(brain.stats["walkspeed"]*-1, 0))
    if id == args[1]:
        return command(cmdtype.RESETANIMATION)

    return