import random
import pygame

# The six condition bars on the STAT screen vault boy. Each entry maps one bar
# in UIScreens/STAT.png (x,y,w,h of the solid bar, relative to the image) to a
# stat, which side of the image its label goes, and a quip for low/mid/high values.
# Change names, values and quips here to make your own stats.
stats = [
    {"name":"MOOD",     "bar":(105,5,41,5),   "side":"left",  "value":80,
     "quips":["Do not talk to me before coffee.", "Cautiously optimistic.", "Ready to explore the wasteland!"]},
    {"name":"SARCASM",  "bar":(5,60,42,6),    "side":"left",  "value":95,
     "quips":["Suspiciously sincere today.", "Mildly snarky.", "Oh great. Another stat. Wonderful."]},
    {"name":"CAFFEINE", "bar":(202,60,42,6),  "side":"right", "value":40,
     "quips":["Running on fumes.", "Functional. Barely.", "I can hear colours."]},
    {"name":"HEALTH",   "bar":(105,96,41,5),  "side":"right", "value":70,
     "quips":["Seek a doctor. Or a stimpak.", "Mostly intact.", "Fit as a brahmin."]},
    {"name":"DRUNK",    "bar":(5,168,42,7),   "side":"left",  "value":15,
     "quips":["Stone cold sober.", "Feeling warm and fuzzy.", "Who moved the floor?"]},
    {"name":"CHEMS",    "bar":(202,168,42,7), "side":"right", "value":40, "unit":"mg", "drift":False,
     "quips":["Clean as a vault floor.", "Mind slightly altered. Snacks recommended.", "Fully chemmed up. Do not operate the Pip-Boy."]},
]
# optional per stat: "unit" shows the value as e.g. 40/100mg instead of a percentage,
# "drift":False keeps the value fixed instead of wandering

imageWidth=249
labelGap=4
hitPadding=8

# index into stats of the stat whose detail popup is showing, or None
popupStat=None


def quipFor(stat):
    return stat["quips"][min(2,stat["value"]//34)]


# short value for the side label, and the longer form for the popup title
def valueText(stat,long=False):
    if "unit" not in stat:
        return "{:d}%".format(stat["value"])
    if long:
        return "{:d}/100{}".format(stat["value"],stat["unit"])
    return "{:d}{}".format(stat["value"],stat["unit"])


# randomly nudge one stat up or down, like the gauge LEDs
def driftStats():
    stat=random.choice([s for s in stats if s.get("drift",True)])
    stat["value"]=max(0,min(100,stat["value"]+random.randrange(-3,4)))


def barRect(stat,origin):
    x,y,w,h=stat["bar"]
    return pygame.Rect(origin[0]+x,origin[1]+y,w,h)


# where the two label lines for a stat go, in the margin beside the image
def labelRect(stat,font,origin):
    bar=barRect(stat,origin)
    height=font.get_linesize()*2
    top=bar.centery-height//2
    if stat["side"]=="left":
        return pygame.Rect(0,top,origin[0]-labelGap,height)
    left=origin[0]+imageWidth+labelGap
    return pygame.Rect(left,top,480-left,height)


def drawStats(screen,font,color,origin):
    for stat in stats:
        # empty the bar then fill it to the stat value
        bar=barRect(stat,origin)
        pygame.draw.rect(screen,(0,0,0),bar)
        fillWidth=int(bar.width*stat["value"]/100)
        pygame.draw.rect(screen,color,(bar.x,bar.y,fillWidth,bar.height))
        pygame.draw.rect(screen,color,bar,1)

        area=labelRect(stat,font,origin)
        for lineNum,text in enumerate([stat["name"],valueText(stat)]):
            textSurface=font.render(text,False,color)
            if stat["side"]=="left":
                x=area.right-textSurface.get_width()
            else:
                x=area.left
            screen.blit(textSurface,(x,area.top+font.get_linesize()*lineNum))


# index of the stat whose bar or label was tapped, or None
def statAt(pos,font,origin):
    for i,stat in enumerate(stats):
        if barRect(stat,origin).inflate(hitPadding*2,hitPadding*2).collidepoint(pos):
            return i
        if labelRect(stat,font,origin).collidepoint(pos):
            return i
    return None


def drawPopup(screen,titleFont,font,color):
    stat=stats[popupStat]
    box=pygame.Rect(0,0,320,150)
    box.center=(240,170)
    pygame.draw.rect(screen,(0,0,0),box)
    pygame.draw.rect(screen,color,box,2)

    title=titleFont.render("{}  {}".format(stat["name"],valueText(stat,long=True)),False,color)
    screen.blit(title,(box.x+12,box.y+10))

    bar=pygame.Rect(box.x+12,box.y+40,box.width-24,14)
    pygame.draw.rect(screen,color,(bar.x,bar.y,int(bar.width*stat["value"]/100),bar.height))
    pygame.draw.rect(screen,color,bar,1)

    # word wrap the quip to fit the box
    lines=[""]
    for word in quipFor(stat).split():
        attempt=(lines[-1]+" "+word).strip()
        if font.size(attempt)[0]>box.width-24:
            lines.append(word)
        else:
            lines[-1]=attempt
    for lineNum,text in enumerate(lines):
        screen.blit(font.render(text,False,color),(box.x+12,box.y+66+font.get_linesize()*lineNum))

    hint=font.render("TAP TO CLOSE",False,color)
    screen.blit(hint,(box.right-hint.get_width()-12,box.bottom-hint.get_height()-8))
