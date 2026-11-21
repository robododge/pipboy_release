import json
import math
import os
import time
import pygame

# The Vault 4 spin room: pick an instructor, book one of their weekly classes
# and see the phrases they shout. Each instructor rides the corner bike
# animation a little differently (cadence, lean, bounce, arm pump).
instructors = [
    {"name":"COACH STEEL", "format":"PWR (POWER)",
     "slots":["MON 6:00 AM","THU 5:30 PM"],
     "ride":{"cadence":2.2, "lean":0.55, "bounce":1, "armPump":0},
     "phrases":[("No recovery",23), ("Bump it",31), ("One Click",18),
                ("We're gonna blow this up",9), ("Stay Up",27), ("Two Clicks",12),
                ("Have you heard about the Halloween party 2026?",6)]},
    {"name":"SAGE", "format":"PWR (POWER)",
     "slots":["TUE 7:00 AM","SAT 9:00 AM"],
     "ride":{"cadence":1.1, "lean":0.15, "bounce":0, "armPump":0},
     "phrases":[("Breathe into the climb",19), ("Find your inner meadow",8),
                ("Let the hawk set your cadence",5), ("Feel the forest in your legs",11),
                ("Heal through the hill",14), ("Smell the lavender candle",7),
                ("Namaste on the downstroke",4)]},
    {"name":"DJ VEGA", "format":"AMP",
     "slots":["WED 6:30 PM","FRI 6:00 PM"],
     "ride":{"cadence":1.8, "lean":0.35, "bounce":3, "armPump":1},
     "phrases":[("I love you so much",26), ("You're all my favorites",21),
                ("Is that all you got?",17), ("Tap it back, tap it back!",24),
                ("Cute. Now do it for real.",13), ("My grandma climbs harder",8),
                ("Did I say you could sit?",11)]},
]

# index of the instructor being viewed, or None for the chooser
selected=None
bookingsFile="spin_bookings.json"
lineHeight=19


def loadBookings():
    try:
        with open(bookingsFile) as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


bookings=loadBookings()


def saveBookings():
    with open(bookingsFile,"w") as f:
        json.dump(sorted(bookings),f)


def chooserRect(i):
    return pygame.Rect(40,90+i*48,400,38)


def backRect():
    return pygame.Rect(0,24,70,22)


def slotRect(i):
    return pygame.Rect(0,52+i*24,250,22)


def bikeBox():
    return pygame.Rect(338,24,140,104)


def drawChooser(screen,font,color):
    title=font.render("VAULT 4 SPIN ROOM",False,color)
    screen.blit(title,((480-title.get_width())/2,30))
    prompt=font.render("CHOOSE INSTRUCTOR & CLASS FORMAT",False,color)
    screen.blit(prompt,((480-prompt.get_width())/2,54))
    for i,instructor in enumerate(instructors):
        area=chooserRect(i)
        pygame.draw.rect(screen,color,area,1)
        screen.blit(font.render(instructor["name"],False,color),(area.x+12,area.y+10))
        fmt=font.render(instructor["format"],False,color)
        screen.blit(fmt,(area.right-fmt.get_width()-12,area.y+10))


def drawDetail(screen,font,smallFont,color):
    instructor=instructors[selected]
    back=backRect()
    pygame.draw.rect(screen,color,back,1)
    screen.blit(font.render("< BACK",False,color),(back.x+4,back.y+2))
    screen.blit(font.render(instructor["name"]+" - "+instructor["format"],False,color),(80,26))

    for i,slot in enumerate(instructor["slots"]):
        area=slotRect(i)
        booked=instructor["name"]+" "+slot in bookings
        label="{}  {}".format(slot,"[BOOKED]" if booked else "[BOOK]")
        screen.blit(font.render(label,False,color),(area.x+4,area.y+2))
        if booked:
            pygame.draw.rect(screen,color,area,1)

    drawBike(screen,color,bikeBox(),instructor["ride"])

    top=136
    screen.blit(font.render("COMMON PHRASES",False,color),(4,top))
    header=smallFont.render("AVG. SPOKEN/CLASS",False,color)
    screen.blit(header,(476-header.get_width(),top+4))
    pygame.draw.line(screen,color,(4,top+lineHeight+1),(476,top+lineHeight+1),1)
    rowHeight=smallFont.get_linesize()+3
    for i,(phrase,count) in enumerate(instructor["phrases"]):
        y=top+lineHeight+6+i*rowHeight
        screen.blit(smallFont.render('"'+phrase+'"',False,color),(8,y))
        countText=smallFont.render(str(count),False,color)
        screen.blit(countText,(476-countText.get_width()-24,y))


# knee position for a leg from hip to foot, bending forward like a rider
def knee(hip,foot,thigh,shin):
    dx,dy=foot[0]-hip[0],foot[1]-hip[1]
    d=max(1,min(thigh+shin-0.01,math.hypot(dx,dy)))
    angle=math.atan2(dy,dx)
    bend=math.acos((thigh*thigh+d*d-shin*shin)/(2*thigh*d))
    return (hip[0]+thigh*math.cos(angle-bend),hip[1]+thigh*math.sin(angle-bend))


def drawBike(screen,color,box,ride):
    dim=(color[0]//2,color[1]//2,color[2]//2)
    t=time.monotonic()
    crankAngle=t*ride["cadence"]*2*math.pi
    x,y=box.x,box.y
    bounce=ride["bounce"]*abs(math.sin(crankAngle))

    floor=y+100
    crank=(x+60,y+80)
    flywheel=(x+104,y+76)
    seat=(x+44,y+44)
    bars=(x+96,y+38)

    # bike frame, flywheel with turning spokes
    pygame.draw.line(screen,color,(x+24,floor),(x+124,floor),2)
    pygame.draw.line(screen,color,(x+36,floor),crank,2)
    pygame.draw.line(screen,color,crank,flywheel,2)
    pygame.draw.line(screen,color,crank,seat,2)
    pygame.draw.line(screen,color,(x+112,floor),flywheel,2)
    pygame.draw.line(screen,color,flywheel,(bars[0]-4,bars[1]+6),2)
    pygame.draw.line(screen,color,(seat[0]-7,seat[1]),(seat[0]+5,seat[1]),3)
    pygame.draw.line(screen,color,(bars[0]-6,bars[1]+6),(bars[0]+6,bars[1]),3)
    pygame.draw.circle(screen,color,flywheel,16,1)
    for spoke in range(4):
        a=crankAngle*1.5+spoke*math.pi/4
        pygame.draw.line(screen,color,
            (flywheel[0]-15*math.cos(a),flywheel[1]-15*math.sin(a)),
            (flywheel[0]+15*math.cos(a),flywheel[1]+15*math.sin(a)),1)

    # rider: hip on the seat, torso leaning towards the bars
    hip=(seat[0],seat[1]-3-bounce)
    shoulder=(hip[0]+26*math.sin(ride["lean"]),hip[1]-26*math.cos(ride["lean"]))
    head=(int(shoulder[0]+9*math.sin(ride["lean"])),int(shoulder[1]-9*math.cos(ride["lean"])))

    # far leg first and dimmer so the near leg reads in front
    for offset,legColor in ((math.pi,dim),(0,color)):
        a=crankAngle+offset
        foot=(crank[0]+9*math.cos(a),crank[1]+9*math.sin(a))
        k=knee(hip,foot,22,24)
        pygame.draw.line(screen,legColor,hip,k,2)
        pygame.draw.line(screen,legColor,k,foot,2)
        pygame.draw.line(screen,legColor,(foot[0]-3,foot[1]),(foot[0]+4,foot[1]),2)

    pygame.draw.line(screen,color,hip,shoulder,3)
    pygame.draw.line(screen,color,shoulder,(bars[0]-2,bars[1]+3),2)
    if not ride["armPump"]:
        pygame.draw.line(screen,dim,shoulder,(bars[0]-6,bars[1]+5),2)

    pygame.draw.circle(screen,(0,0,0),head,7)
    pygame.draw.circle(screen,color,head,7,1)
    # vault boy grin
    pygame.draw.arc(screen,color,(head[0]-3,head[1]-1,7,5),math.pi,2*math.pi,1)

    if ride["armPump"]:
        # one arm punching up and forward to the beat, drawn over the head
        pump=math.sin(crankAngle)
        elbow=(shoulder[0]+10,shoulder[1]-4)
        pygame.draw.line(screen,color,shoulder,elbow,2)
        pygame.draw.line(screen,color,elbow,(elbow[0]+6+3*pump,elbow[1]-12-8*pump),2)


def draw(screen,font,smallFont,color):
    if selected is None:
        drawChooser(screen,font,color)
    else:
        drawDetail(screen,font,smallFont,color)


# handle a tap on the SPIN screen, returns False if it was not on anything
def handleTap(pos):
    global selected
    if selected is None:
        for i in range(len(instructors)):
            if chooserRect(i).collidepoint(pos):
                selected=i
                return True
        return False
    if backRect().collidepoint(pos):
        selected=None
        return True
    for i,slot in enumerate(instructors[selected]["slots"]):
        if slotRect(i).collidepoint(pos):
            booking=instructors[selected]["name"]+" "+slot
            if booking in bookings:
                bookings.discard(booking)
            else:
                bookings.add(booking)
            saveBookings()
            return True
    return False


def animating():
    return selected is not None
