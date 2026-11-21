import os
import pygame

# The MAP screen shows either the location map or a green rendition of a
# route from CrankFeed (a cycling workout feed), picked with the MAP /
# CRANKFEED buttons in the right column.
showRoute=False
screensPath="UIScreens"
routeMap=pygame.image.load(os.path.join(screensPath,"CRANKFEED_MAP.png"))
feedIcon=pygame.image.load(os.path.join(screensPath,"CRANKFEED_ICON.png"))
# CRANKFEED_MAP.png is a 340x276 placeholder - swap in a green rendition of your own route
routeCaption=["ROUTE:","SAMPLE LOOP"]
columnLeft=352


def buttonRect(i):
    return pygame.Rect(columnLeft,30+i*36,124,30)


def drawButtons(screen,font,color):
    for i,route in enumerate((False,True)):
        area=buttonRect(i)
        if route:
            screen.blit(feedIcon,(area.x+5,area.centery-feedIcon.get_height()//2))
            label=font.render("CRANKFEED",False,color)
            screen.blit(label,(area.x+31,area.centery-label.get_height()//2))
        else:
            label=font.render("MAP",False,color)
            screen.blit(label,(area.centerx-label.get_width()//2,area.centery-label.get_height()//2))
        if route==showRoute:
            pygame.draw.rect(screen,color,area,1)


def drawRoute(screen,font,color):
    screen.blit(routeMap,(0,22))
    top=buttonRect(1).bottom+20
    for lineNum,text in enumerate(routeCaption):
        screen.blit(font.render(text,False,color),(columnLeft+4,top+font.get_linesize()*lineNum))


# switch maps, returns False if the tap missed the buttons
def handleTap(pos):
    global showRoute
    for i,route in enumerate((False,True)):
        if buttonRect(i).collidepoint(pos):
            showRoute=route
            return True
    return False
