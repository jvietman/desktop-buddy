from command import *
from brain import brain
from vector2 import vector2



# when loaded
def load():
    print("script.py imported!")

# when started
def start(brain: brain, pos: vector2):
    print("I got called!")
    return

# when called
def main(id: int, args: tuple, brain: brain):
    return