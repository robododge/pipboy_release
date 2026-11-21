import json
import pygame

# Bike equipment listed on the INV screen. The bike is fixed; tap a wheelset
# to fit it (highlighted), which is remembered in gear_selection.json.
bike="ROAD: ENVE MELEE"
wheels=["ENVE 65MM CARBON","CADEX 36MM CARBON SPOKES"]
selectionFile="gear_selection.json"
sectionTop=150


def loadSelection():
    try:
        with open(selectionFile) as f:
            return wheels.index(json.load(f)["wheels"])
    except (OSError, ValueError, KeyError):
        return 0


selectedWheels=loadSelection()


def wheelRect(i,font):
    return pygame.Rect(0,sectionTop+font.get_linesize()*3+i*30,330,26)


def draw(screen,font,color):
    screen.blit(font.render("BIKE EQUIPMENT",False,color),(4,sectionTop))
    pygame.draw.line(screen,color,(4,sectionTop+font.get_linesize()+1),(476,sectionTop+font.get_linesize()+1),1)
    screen.blit(font.render(bike,False,color),(4,sectionTop+font.get_linesize()+5))
    screen.blit(font.render("WHEELS:",False,color),(4,sectionTop+font.get_linesize()*2+5))
    for i,name in enumerate(wheels):
        area=wheelRect(i,font)
        marker=">" if i==selectedWheels else " "
        screen.blit(font.render("{} {}".format(marker,name),False,color),(area.x+4,area.y+4))
        if i==selectedWheels:
            pygame.draw.rect(screen,color,area,1)


# fit the tapped wheelset, returns False if the tap missed them
def handleTap(pos,font):
    global selectedWheels
    for i in range(len(wheels)):
        if wheelRect(i,font).collidepoint(pos):
            selectedWheels=i
            with open(selectionFile,"w") as f:
                json.dump({"wheels":wheels[i]},f)
            return True
    return False
