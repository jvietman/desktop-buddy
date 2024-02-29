from command import *
from brain import brain
from vector2 import vector2



# when loaded
def load():
    print("flip.py imported!")

# when started
def start(brain: brain, pos: vector2):
    print("flip")
    return (brain.stats,)

# when called
def main(id: int, args: tuple, brain: brain):
    flipspeed = args[0]["flipspeed"]
    if id == 0:
        return command(cmdtype.VELOCITY, vector2(0, brain.stats["jumpforce"]))

    if id*flipspeed < 360:
        return command(cmdtype.ROTATE, (id*flipspeed)*-1)
    elif id*flipspeed == 360:
        return command(cmdtype.ROTATE, 0)
    else:
        return