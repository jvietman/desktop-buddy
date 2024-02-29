# Desktop Buddy Documentation

> #### State of development
> Im actively working on this project and Im committed to keeping you in the loop.

## Structure
- 

## Info
This documentation explains how the buddy works. With this knowledge you will be able to understand the behaviour of your buddy better. You will also know how to change existing buddies or make your own ones. I try to explain everything as thoroughly as possible. If there are any questions how into the "credits" topic.

## Introduction
Desktop Buddy is a program that lets a buddy walk around your desktop. You can interact with them in many ways like and they can also do stuff on their own.

Interacting with the buddy is the job of the main file. All of the values, the buddy itself and methods like grabbing the buddy or playing sounds are defined in the main file. All of the functions there are hard coded, but it would be usefull to know how it works. This knowledge could be usefull for debugging your own buddy or to understand why the buddy does what it does. Every about the main file is explained in the "main" topic.

The buddy can do random actions in specific time intervals. They have their own mind with basic needs (energy, hunger) and demands (attention). The buddy can also be in states (standing, sitting, laying, etc.) which limit the actions it can perform but makes the selection of actions more resonable. For example the buddy can only jump when its standing and it can roll when its standing, stitting or laying. All of this is what the brain/ AI does the whole time. It updates the values and chooses actions depending on those values.

Those two major parts of the whole program are explained in their seperate topics with their own sub-topics.


## AI

## Scripts
### Script templates
action script template:
``` python
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
```

state script template:
``` python
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
```