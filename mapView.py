import os
import pygame

# The MAP screen shows either the location map or a green rendition of a
# Strava route, picked with the MAP / STRAVA buttons in the right column.
showStrava=False
screensPath="UIScreens"
stravaMap=pygame.image.load(os.path.join(screensPath,"STRAVA_MAP.png"))
stravaIcon=pygame.image.load(os.path.join(screensPath,"STRAVA_ICON.png"))
# STRAVA_MAP.png is a 340x276 placeholder - swap in a green rendition of your own route
routeCaption=["ROUTE:","SAMPLE LOOP"]
columnLeft=352


def buttonRect(i):
    return pygame.Rect(columnLeft,30+i*36,124,30)


def drawButtons(screen,font,color):
    for i,strava in enumerate((False,True)):
        area=buttonRect(i)
        if strava:
            screen.blit(stravaIcon,(area.x+6,area.centery-stravaIcon.get_height()//2))
            label=font.render("STRAVA",False,color)
            screen.blit(label,(area.x+34,area.centery-label.get_height()//2))
        else:
            label=font.render("MAP",False,color)
            screen.blit(label,(area.centerx-label.get_width()//2,area.centery-label.get_height()//2))
        if strava==showStrava:
            pygame.draw.rect(screen,color,area,1)


def drawStrava(screen,font,color):
    screen.blit(stravaMap,(0,22))
    top=buttonRect(1).bottom+20
    for lineNum,text in enumerate(routeCaption):
        screen.blit(font.render(text,False,color),(columnLeft+4,top+font.get_linesize()*lineNum))


# switch maps, returns False if the tap missed the buttons
def handleTap(pos):
    global showStrava
    for i,strava in enumerate((False,True)):
        if buttonRect(i).collidepoint(pos):
            showStrava=strava
            return True
    return False
