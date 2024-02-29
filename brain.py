from importlib import import_module
from threading import Thread, Event
from colorama import Fore, Back, Style
from datetime import datetime
import json, os, random, threading

from vector2 import vector2
from timer import timer

class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def isrunning(self):
        return self.is_alive()  # Check if the thread is running

class valueconfig:
    def __init__(self, data: dict, timetolerance: int, valuetolerance: int):
        # values
        self.moodincrease = data["moodincrease"]
        self.mooddrop = data["mooddrop"]
        self.energyregain = data["energyregain"] # how much energy per second
        self.attentionsteps = data["attentionsteps"] # how much attention per second
        self.pivot = data["attentionpivot"] # value where the mood goes down or up

        # tolerances
        self.timetolerance = timetolerance
        self.valuetolerance = valuetolerance

        # timings
        self.moodswitch = data["moodswitch"] # time to wait till update
        self.energyidletime = data["energyidletime"] # time to wait till start regain energy
        self.attentionidletime = data["attentionidletime"] # time to wait till start lose attention
        
        self.regaintime = data["regaintime"] # time between regains
        self.attentiontime = data["attentiontime"] # time to wait for attention to go down
        
        # rt = Regain Time (regaintime +- timetolerance)
        # rg = ReGain (energyregain +- valuetolerance)
        # at = Attention Time (attentiontime +- timetolerance)
        # ast = Attention STeps (attentionsteps +- valuetolerance)
        self.rt = 0
        self.rg = 0
        self.at = 0
        self.ast = 0
        # CALL METHOD "setup" TO SETUP VALUES

        # boolean
        self.regaining = False
        self.attentionfall = False
        # last updates
        self.eupdate = timer() # last energy update
        self.aupdate = timer() # last attention update
        self.moodupdate = timer(self.moodswitch) # mood update
    
    def newrt(self):
        self.rt = random.randint(self.regaintime-self.timetolerance, self.regaintime+self.timetolerance)

    def newrg(self):
        self.rg = random.randint(self.energyregain-self.valuetolerance, self.energyregain+self.valuetolerance)

    def newat(self):
        self.at = random.randint(self.attentiontime-self.timetolerance, self.attentiontime+self.timetolerance)
    
    def newast(self):
        self.ast = random.randint(self.attentionsteps-self.valuetolerance, self.attentionsteps+self.valuetolerance)

    def setup(self):
        self.newrt()
        self.newrg()
        self.newat()
        self.newast()

class brain:
    def __init__(self, mood: dict, stats: dict, valueconfig: valueconfig):
        self.mood = mood
        self.moods = ["happy", "neutral", "angry"]
        self.value = 50
        self.stats = stats
        
        self.valueconfig = valueconfig
        self.valueconfig.setup()
        
        self.actions = []
        self.loadactions()

        self.states = []
        self.loadstates()
        self.state = self.states[0]

        self.hunger = float(100)
        self.energy = float(100)
        self.attention = float(100)

        self.asyncspeed = 0.2
        self.asyncupdate = timer()
        self.asyncmove = vector2(0, 0)

    def loadactions(self):
        # load actions
        with open("scripts/actions.json") as f:
            self.actions = json.load(f)
            f.close()
        
        # import scripts
        print("Importing "+str(len(self.actions))+" actions...")
        for action in self.actions:
            try:
                action["module"] = import_module("buddy."+os.path.basename(os.getcwd())+".scripts.actions."+action["name"])
                action["module"].load()
            except ModuleNotFoundError:
                print(Fore.RED+"ERROR: Script \""+action["name"]+"\" not found")
            except AttributeError:
                print(Fore.YELLOW+"WARNING: Script \""+action["name"]+"\" is incomplete, no \"start()\" method found")
            except:
                print(Fore.RED+"ERROR: Script \""+action["name"]+"\" could not be imported")
        print(Style.RESET_ALL)
    
    def loadstates(self):
        # load actions
        with open("scripts/states.json") as f:
            self.states = json.load(f)
            f.close()
        
        # import scripts
        print("Importing "+str(len(self.states))+" states...")
        for state in self.states:
            try:
                state["module"] = import_module("buddy."+os.path.basename(os.getcwd())+".scripts.states."+state["name"])
                state["module"].load()
            except ModuleNotFoundError:
                print(Fore.RED+"ERROR: Script \""+state["name"]+"\" not found")
            except AttributeError:
                print(Fore.YELLOW+"WARNING: Script \""+state["name"]+"\" is incomplete, no \"start()\" method found")
            except:
                print(Fore.RED+"ERROR: Script \""+state["name"]+"\" could not be imported")
        print(Style.RESET_ALL)

    def getactions(self, split=True):
        mood = self.getmood()
        moodindex = self.moods.index(mood[0])

        # get all actions with this mood and strength
        actions1 = []
        for i in self.actions:
            if mood[0] in i["moods"] and mood[1] >= i["strength"][moodindex] and self.energy >= i["energy"]:
                actions1.append(i)

        if not split:
            return actions1
        
        # split actions into rare and common
        # (<common>, <rare>)
        actions = ([], [])
        for i in actions1:
            if i["rare"]:
                actions[1].append(i)
            else:
                actions[0].append(i)
        
        # if common or rare is empty, give at least one action to do
        if not actions[0] and actions[1]:
            actions[0].append(actions[1][0])
        if not actions[1] and actions[0]:
            actions[1].append(actions[0][0])

        return actions

    def action(self, action=""):
        rare = 0

        if action:
            for i in self.actions:
                if i["name"] == action:
                    return i
        else:
            actions = self.getactions()
            if not actions:
                return None
            
            if random.randint(0, 10) <= 4: # rare: 40%; common: 60%
                rare = 1

            try:
                action = actions[rare][random.randint(0, len(actions[rare])-1)]
            except Exception as e:
                print(Fore.RED)
                print(e)
                print(Style.RESET_ALL)

            return action

    def percentage(self, value, total):
        if total == 0:
            return 0
        return int(value / total * 100)

    def getmood(self):
        # ("<mood>", <percentage>)
        if self.value < self.mood["angry"]:
            return (
                "angry",
                self.percentage(self.value, self.mood["angry"])
            )
        elif self.mood["angry"] <= self.value < self.mood["happy"]:
            return (
                "neutral",
                self.percentage(self.value-self.mood["angry"], self.mood["happy"]-self.mood["angry"])
            )
        elif self.mood["happy"] <= self.value:
            return (
                "happy",
                self.percentage(self.value-self.mood["happy"], 100-self.mood["happy"])
            )
    
    def interaction(self, value): # increase attention, stop drop, reset update
        self.attention += value
        self.valueconfig.newast()
        self.valueconfig.newat()
        self.valueconfig.attentionfall = False
        self.valueconfig.aupdate.reset()
    
    def useenergy(self, value): # lower energy, stop rise, reset update
        self.energy -= value
        self.valueconfig.newrg()
        self.valueconfig.newrt()
        self.valueconfig.regaining = False
        self.valueconfig.eupdate.reset()

    def updatevalues(self):
        vc = self.valueconfig

        # mood
        if self.attention > 90:
            self.value += vc.moodincrease
            self.attention = 90

        if vc.moodupdate.reached():
            if self.attention >= vc.pivot:
                self.value += vc.moodincrease
            else:
                self.value -= vc.mooddrop
            
            if self.value > self.hunger * 1.5:
                self.value = self.hunger * 1.5
            vc.moodupdate.reset()
        
        if self.value > 100:
            self.value = 100

        # energy regain
        if self.energy >= self.hunger:
            if self.energy > self.hunger:
                self.energy = self.hunger
        else:
            if vc.regaining and vc.eupdate.timepassed() >= vc.rt or vc.eupdate.timepassed() >= vc.energyidletime:
                self.energy += vc.rg
                self.hunger -= 1
                self.valueconfig.newrg()
                self.valueconfig.newrt()

                if vc.eupdate.timepassed() >= vc.energyidletime:
                    self.valueconfig.regaining = True
                self.valueconfig.eupdate.reset()
        
        # attention fall
        if self.attention >= 100:
            if self.attention > 100:
                self.attention = 100
        else:
            if vc.attentionfall and vc.aupdate.timepassed() >= vc.at or vc.aupdate.timepassed() >= vc.attentionidletime:
                self.attention -= vc.ast
                self.valueconfig.newast()
                self.valueconfig.newat()

                if vc.aupdate.timepassed() >= vc.attentionidletime:
                    self.valueconfig.attentionfall = True
                self.valueconfig.aupdate.reset()