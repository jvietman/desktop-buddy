# lib imports
from tkinter import *
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from screeninfo import get_monitors
from datetime import datetime
import time, os, json, pygame

# custom imports
from vector2 import vector2
from gifconvert import *
from brain import *
from command import *
from animation import *
from timer import *
from fixedlist import *


# tkinter setup
root = Tk()
root.title("Pokebuddy")
root.overrideredirect(True)

monitor = get_monitors()[0]

# setup
## load buddy data
with open("settings.json") as f:
    data = json.load(f)
    f.close()

buddy = data["buddy"]
os.chdir("buddy/"+buddy)
with open("config.json") as f:
    buddy = json.load(f)
    f.close()

## setup values
updatetime = data["updatetime"]
ground = data["ground"]
res = vector2(buddy["size"][0], buddy["size"][1])
pos = vector2(data["position"][0], data["position"][1])
prev = pos
enabledgravity = data["enabledgravity"]
gravity = data["gravity"]
velocity = vector2(0, 0)
lastupdate = timer(data["gravitytime"]) # gravity time

# ai
ai = brain(buddy["mood"], buddy["stats"], valueconfig(buddy["valueconfig"], buddy["timetolerance"], buddy["valuetolerance"]))
if data["startwithvalue"]:
    ai.value = data["value"]
    ai.hunger = data["hunger"]
    ai.energy = data["energy"]
    ai.attention = data["attention"]
else:
    ai.value = random.randint(data["minvalue"], 100)
    ai.hunger = random.randint(data["minvalue"], 100)
    ai.energy = random.randint(data["minvalue"], 100)
    ai.attention = random.randint(data["minvalue"], 100)
print(ai.getmood())
aiupdate = timer(buddy["actiontime"])
"""
thread = thread object of class "customthread"
threadid = number of repetition (only if async)
threadvar = arguments given from "start" method
action = current action
"""
thread, threadid, threadvar, action = None, -1, [], None

# animation
frame = 0
lastframe = timer(data["frametime"])

files = list(buddy["sprites"].keys())
sprites = {}
for f in files:
    sprites[f] = animation(gifconvert("sprites/"+buddy["sprites"][f], res))

currentanim = ai.state["sprites"]
flipped = False
rotation = 0

# sound
soundplayed = timer(buddy["soundtime"])

# initialize pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# load sounds
sounds = {}
for i in buddy["sounds"].items():
    sounds[i[0]] = []
    for j in i[1]:
        sounds[i[0]].append(pygame.mixer.Sound("sfx/"+j))
        sounds[i[0]][len(sounds[i[0]])-1].set_volume(data["volume"])

def play(name: str):
    try:
        if len(sounds[name]) == 1:
            sounds[name][0].play()
        else:
            sounds[name][random.randint(0, len(sounds[name])-1)].play()
    except:
        print("sounderror")

# display
def place(x, y):
    root.geometry(str(res.x)+"x"+str(res.y)+"+"+str(x)+"+"+str(monitor.height-y-res.y+buddy["ground"]))

canvas = Canvas(root, bg="#696969", highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

def printimage(photoimage):
    canvas.delete('all')
    canvas.create_image(0, 0, image=photoimage, anchor=NW)

def point(x, y, width=10, height=10):
    canvas.create_rectangle(x, y, x+width, y+height, fill="blue", outline="blue")

root.wm_attributes('-transparentcolor','#696969')
root.wm_attributes('-topmost', True)

place(pos.x, pos.y)

# events
mousepressed = False # if mouse pressed
mouseinteract = False # if interacted
mousesince = timer(0.15) # mouse hold time
holdpos = vector2(0, 0)
mousemotion = timer(0.1) # last motion detected in window
mouseinwin = False # if mouse inside window
currentpos = vector2(0, 0)
mousepos = fixedlist(10)

petpos = buddy["petpos"]
petdetect = buddy["petdetect"]
petcount = 0
petidle = 5

def mousedown(event):
    global mousepressed, mousesince, holdpos
    mousesince.reset()
    mousepressed, holdpos = True, vector2(event.x, event.y)

def mouseup(event):
    global mousepressed, velocity
    mousepressed = False
    if mousesince.reached():
        velocity = vector2(pos.x-prev.x, prev.y-pos.y)

def motion(event):
    global currentpos, mouseinwin
    x, y = event.x, event.y
    mouseinwin = True
    currentpos = vector2(x, y)

root.bind('<Motion>', motion)
root.bind("<ButtonPress-1>", mousedown)
root.bind("<ButtonRelease-1>", mouseup)

def doaction(aaction=""):
    global action, aiupdate, actiontime

    action = ai.action(action=aaction)
    try:
        ai.useenergy(action["energy"])
    except Exception as e:
        print(Fore.RED)
        print(e)
        print(Style.RESET_ALL)

    aiupdate.reset()
    actiontime = random.randint(buddy["actiontime"]-buddy["timetolerance"], buddy["actiontime"]+buddy["timetolerance"])
    print(actiontime)

def displaymood():
    mood = ai.getmood()
    txt = []

    if mood[0] == "happy":
        if mood[1] >= 50:
            txt.append("Your buddy is very happy :3")
        else:
            txt.append("Your buddy is happy :))")
    elif mood[0] == "neutral":
        if mood[1] >= 50:
            txt.append("Your buddy is satisfied :)")
        else:
            txt.append("Your buddy is fine :|")
    elif mood[0] == "angry":
        if mood[1] >= 50:
            txt.append("Your buddy is not so happy :(")
        elif mood[1] >= 30:
            txt.append("Your buddy is angry >:(")
        else:
            txt.append("Fuck off")
    
    if ai.hunger < buddy["hungry"]:
        txt.append("Your buddy is hungry")
    elif ai.hunger < int(buddy["hungry"] / 2):
        txt.append("YOUR BUDDY IS STARVING")
    
    if ai.attention < ai.valueconfig.pivot:
        txt.append("Your buddy is kinda bored")
    elif ai.attention < int(ai.valueconfig.pivot / 2):
        txt.append("Your buddy need attention!")
    
    msg = ""
    for i in txt:
        msg += i+"\n"

    messagebox.showinfo("Info", msg)

buddymenu = Menu(root, tearoff=0)
actionmenu = Menu(root, tearoff=0)
buddymenu.add_cascade(label="Get mood", command=displaymood)
buddymenu.add_cascade(label="Make him...", menu=actionmenu)
# for i in ai.actions:
    # actionmenu.add_command(label=i["name"], command=lambda current_action=i: action(current_action["name"]))

if data["debug"]:
    actionmenu = Menu(root, tearoff=0)
    actionmenu.add_command(label="random action", command=doaction)
    for i in ai.actions:
        actionmenu.add_command(label=i["name"], command=lambda current_action=i: doaction(current_action["name"]))
    buddymenu.add_cascade(label="Do something", menu=actionmenu)
else:
    buddymenu.add_command(label="Do something", command=doaction)

def openmenu(event):
    try:
        buddymenu.tk_popup(event.x_root, event.y_root)
    finally:
        buddymenu.grab_release()

root.bind("<Button-3>", openmenu)

# debug window
if data["debugwindow"]:
    debugwin = Toplevel(root)
    debugwin.geometry("700x500")
    debugwin.title("debug window")
    vallbox = Listbox(debugwin)
    vallbox.place(x=0, y=0, relwidth=0.7, relheight=.5)

    vallabel = Label(debugwin, text="mood\n\nenergy\n\nhunger\n\nattention\n\npetcount\n\nsound", font=("", 8))
    vallabel.place(anchor=W, x=0, rely=.75)

    actionvar = IntVar()
    actionbar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=actionvar)
    actionbar.place(anchor=CENTER, relx=.5, rely=.5, relwidth=.75)
    moodtimevar = IntVar()
    moodtimebar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=moodtimevar)
    moodtimebar.place(anchor=W, relx=.1, rely=.6, relwidth=.2)
    moodvar = IntVar()
    moodbar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=moodvar)
    moodbar.place(anchor=E, relx=.9, rely=.6, relwidth=.6)
    energytimevar = IntVar()
    energytimebar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=energytimevar)
    energytimebar.place(anchor=W, relx=.1, rely=.65, relwidth=.2)
    energyvar = IntVar()
    energybar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=energyvar)
    energybar.place(anchor=E, relx=.9, rely=.65, relwidth=.6)
    hungervar = IntVar()
    hungerbar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=hungervar)
    hungerbar.place(anchor=E, relx=.9, rely=.7, relwidth=.6)
    attentiontimevar = IntVar()
    attentiontimebar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=attentiontimevar)
    attentiontimebar.place(anchor=W, relx=.1, rely=.75, relwidth=.2)
    attentionvar = IntVar()
    attentionbar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=attentionvar)
    attentionbar.place(anchor=E, relx=.9, rely=.75, relwidth=.6)
    petidlevar = IntVar()
    petidlebar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=petidlevar)
    petidlebar.place(anchor=W, relx=.1, rely=.8, relwidth=.2)
    petcountvar = IntVar()
    petcountbar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=petcountvar)
    petcountbar.place(anchor=E, relx=.9, rely=.8, relwidth=.6)
    soundvar = IntVar()
    soundbar = ttk.Progressbar(debugwin, orient=HORIZONTAL, length=100, variable=soundvar)
    soundbar.place(anchor=E, relx=.9, rely=.85, relwidth=.6)

def debugupdate():
    vallbox.delete(0, END)
    vc = ai.valueconfig
    vallbox.insert(END, "MOOD: "+str(ai.getmood()))
    vallbox.insert(END, "VALUE: "+str(ai.value))
    vallbox.insert(END, "moodupdate: "+str(vc.moodupdate.timepassed())+" | "+str(vc.moodswitch))
    vallbox.insert(END, "ENERGY: "+str(ai.energy)+"/"+str(ai.hunger))
    vallbox.insert(END, "regaining: "+str(vc.regaining))
    vallbox.insert(END, "regain: "+str(vc.rg))
    vallbox.insert(END, "eupdate: "+str(vc.eupdate.timepassed())+" | "+str(vc.energyidletime)+" | "+str(vc.rt))
    vallbox.insert(END, "ATTENTION: "+str(ai.attention)+"/100")
    vallbox.insert(END, "attentionfall: "+str(vc.attentionfall))
    vallbox.insert(END, "attentionsteps: "+str(vc.ast))
    vallbox.insert(END, "aupdate: "+str(vc.aupdate.timepassed())+" | "+str(vc.attentionidletime)+" | "+str(vc.at))
    vallbox.insert(END, "mousepos: "+str(mousepos.getallvalues()))
    actionvar.set(ai.percentage(aiupdate.timepassed(), aiupdate.goal))
    moodtimevar.set(ai.percentage(vc.moodupdate.timepassed(), vc.moodupdate.goal))
    moodvar.set(ai.value)
    if vc.regaining: energytimevar.set(ai.percentage(vc.eupdate.timepassed(), vc.rt))
    else: energytimevar.set(ai.percentage(vc.eupdate.timepassed(), vc.energyidletime))
    energyvar.set(ai.energy)
    hungervar.set(ai.hunger)
    if vc.attentionfall: attentiontimevar.set(ai.percentage(vc.aupdate.timepassed(), vc.at))
    else: attentiontimevar.set(ai.percentage(vc.aupdate.timepassed(), vc.attentionidletime))
    attentionvar.set(ai.attention)
    petidlevar.set(100-ai.percentage(petidle, 5))
    petcountvar.set(ai.percentage(petcount, petdetect))
    soundvar.set(ai.percentage(soundplayed.timepassed(), soundplayed.goal))

count = 0
while True:
    time.sleep(updatetime)

    # debug value update
    if data["debugwindow"]:
        debugupdate()
    
    prev = pos

    # pets
    if petcount >= petdetect:
        doaction("happy")
        ai.interaction(4)
        petcount, petidle = 0, 5

    # mouse motion
    if mousemotion.reached():
        if mouseinwin:
            # check if pet
            if not mousepressed and mousepos.getlast():
                tmpx = (mousepos.getlast()[0] - currentpos.x)
                if tmpx < 0: tmpx *= -1
                tmpy = (mousepos.getlast()[1] - currentpos.y)
                if tmpy < 0: tmpy *= -1

                # check distance between last and current pos
                if tmpx >= petpos or tmpx >= petpos:
                    petidle = 5 # reset idle val
                    petcount += 1 # add to count
            
            # append mouse position
            mousepos.append(currentpos.tuple())
        else:
            # pet idle time
            if petcount > 0:
                petidle -= 1
            mousepos.append(None)

        # if pet idle time reached
        if petidle <= 0:
            # reset
            petcount, petidle = 0, 5

        mouseinwin = False
        currentpos = vector2(0, 0)

        mousemotion.reset()

    # if aiupdate reached do action
    if aiupdate.reached():
        doaction()

    # update values
    ai.updatevalues()

    # execute action
    if thread and not thread.isrunning():
        if threadid < 0:
            threadid += 1
            threadvar = ()
            if thread._return:
                threadvar = () + thread._return
            thread = CustomThread(target=action["module"].main, args=(threadid, threadvar, ai))
            thread.start()
        else:
            if thread._return:
                if isinstance(thread._return, list):
                    commands = thread._return
                else:
                    commands = [thread._return]
                thread._return = None
                
                for c in commands:
                    type, value = c.astuple()
                    # commands
                    if type == cmdtype.SETPOS:
                        pos = value
                    elif type == cmdtype.MOVE:
                        pos = pos.plus(value)
                    elif type == cmdtype.VELOCITY:
                        velocity = value
                    elif type == cmdtype.ANIMATION:
                        currentanim = value
                        frame = 0
                    elif type == cmdtype.RESETANIMATION:
                        currentanim = ai.state["sprites"]
                        frame = 0
                    elif type == cmdtype.FLIP:
                        flipped = value
                    elif type == cmdtype.ROTATE:
                        rotation = value
                    elif type == cmdtype.PLAYSOUND:
                        play(value)

                # if asnyc then repeat
                if action["async"]:
                    threadid += 1
                    thread = CustomThread(target=action["module"].main, args=(threadid, threadvar, ai))
                    thread.start()
            else:
                thread, threadid, threadvar, action = None, -1, [], None

    if action and not thread:
        thread = CustomThread(target=action["module"].start, args=(ai, pos))
        thread.start()

    # mouse dragging
    if mousepressed:
        if mousesince.reached():
            pos = vector2(root.winfo_pointerx()-holdpos.x, monitor.height-root.winfo_pointery()-holdpos.y-buddy["ground"])
            if not mouseinteract:
                mouseinteract = True
                ai.interaction(2)
    elif mouseinteract:
        mouseinteract = False

    # gravity
    elif lastupdate.reached() and enabledgravity:
        velocity.y += gravity

        pos.y = int(pos.y - velocity.y)
        pos.x = int(pos.x + velocity.x)
        if pos.y < ground:
            velocity.x = int(velocity.x / 2)
            velocity.y = int(velocity.y / 2 * -1)
        if pos.x < 0 or pos.x + res.x > monitor.width:
            velocity.x = int(velocity.x / 2 * -1)
            velocity.y = int(velocity.y / 2)
        if pos.y > monitor.height+1000:
            velocity.y = 0
        lastupdate.reset()
    
    if velocity.y <= 1 and velocity.y >= -1:
        velocity.y = 0
    if velocity.x <= 1 and velocity.x >= -1:
        velocity.x = 0

    if pos.y < ground:
        pos.y = ground
    if pos.x < 0:
        pos.x = 0
    if pos.x + res.x > monitor.width:
        pos.x = monitor.width - res.x
    if pos.y > monitor.height+1000:
        pos.y = monitor.height+500
    place(pos.x, pos.y)

    # sound
    if soundplayed.reached():
        play(ai.getmood()[0])
        soundplayed.reset()

    # animation
    if lastframe.reached():
        photoimage = ImageTk.PhotoImage(sprites[currentanim].getframe(flipped=flipped).rotate(rotation))
        lastframe.reset()
        printimage(photoimage)

    root.update()