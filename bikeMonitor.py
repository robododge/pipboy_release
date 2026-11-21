import math
import random
import time
from collections import deque
import pygame

# Cycling monitor for the DATA screen, swapped with the clock by the
# CLOCK/RIDE buttons. There are no sensors, so the readings are simulated:
# slow waves plus a little jitter. HR sits implausibly low, 35-45 bpm.
showing=False
modes=[("CLOCK",False),("RIDE",True)]

graph=pygame.Rect(40,236,428,58)
hrLow,hrHigh=30,50
sampleSecs=0.25
hrHistory=deque(maxlen=graph.width//2)
lastSample=0


def wave(t,period,phase=0):
    return math.sin(2*math.pi*t/period+phase)


def readings(t):
    return {
        "POWER":("W",int(220+30*wave(t,23)+8*wave(t,5,1))),
        "CADENCE":("RPM",int(90+4*wave(t,17,2)+1.5*wave(t,3))),
        "SPEED":("MPH","{:.1f}".format(20+1.8*wave(t,29,1)+0.4*wave(t,7))),
        "HR":("BPM",int(round(heartRate(t)))),
    }


def heartRate(t):
    return max(35,min(45,40+4.5*wave(t,9)+random.uniform(-0.5,0.5)))


# add an HR sample when it is due, returns True if the graph moved
def sample():
    global lastSample
    now=time.monotonic()
    if now-lastSample<sampleSecs:
        return False
    lastSample=now
    hrHistory.append(heartRate(now))
    return True


def modeRect(i):
    return pygame.Rect(318+i*82,24,76,22)


def drawModeButtons(screen,font,color):
    for i,(name,ride) in enumerate(modes):
        area=modeRect(i)
        text=font.render(name,False,color)
        screen.blit(text,(area.centerx-text.get_width()//2,area.y+2))
        if ride==showing:
            pygame.draw.rect(screen,color,area,1)


# swap between the clock and the monitor, returns False if the tap missed
def handleTap(pos):
    global showing
    for i,(name,ride) in enumerate(modes):
        if modeRect(i).collidepoint(pos):
            showing=ride
            return True
    return False


def draw(screen,bigFont,font,smallFont,color):
    values=readings(time.monotonic())
    # 2x2 grid of big readouts
    for i,label in enumerate(["POWER","CADENCE","SPEED","HR"]):
        unit,value=values[label]
        x=12+(i%2)*236
        y=52+(i//2)*86
        screen.blit(smallFont.render(label,False,color),(x,y))
        number=bigFont.render(str(value),False,color)
        screen.blit(number,(x,y+12))
        screen.blit(font.render(unit,False,color),(x+number.get_width()+8,y+12+number.get_height()-font.get_linesize()-4))

    # scrolling heart rate trace, newest on the right
    screen.blit(smallFont.render("HR",False,color),(4,graph.y-14))
    for bpm in (35,45):
        y=graphY(bpm)
        screen.blit(smallFont.render(str(bpm),False,color),(4,y-smallFont.get_linesize()//2))
        for x in range(graph.x,graph.right,6):
            screen.set_at((x,y),color)
    pygame.draw.rect(screen,color,graph,1)
    points=[(graph.right-2-2*(len(hrHistory)-1-i),graphY(bpm)) for i,bpm in enumerate(hrHistory)]
    if len(points)>1:
        pygame.draw.lines(screen,color,False,points,2)


def graphY(bpm):
    return int(graph.bottom-2-(bpm-hrLow)/(hrHigh-hrLow)*(graph.height-4))
