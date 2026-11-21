import os
import pygame

# The stations listed on the RADIO screen. Each plays an mp3 from the radio
# directory (not kept in git - copy your own files there).
radioPath="radio"
stations = [
    {"freq":"88.1", "name":"ENCLAVE RADIO", "file":"1. Enclave Radio.mp3"},
    {"freq":"101.0","name":"VAULT 101",     "file":"6. Vault 101 music.mp3"},
    {"freq":"77.7", "name":"P.R. AMERICA",  "file":"4. Fallout 3 Peoples Republic Of America Radio.mp3"},
]

# index into stations of what is playing, or None for silence
playing=None
listTop=40


def stationRect(i,font):
    return pygame.Rect(0,listTop+font.get_linesize()*2*i,230,font.get_linesize()*2)


def drawStations(screen,font,color):
    for i,station in enumerate(stations):
        area=stationRect(i,font)
        marker=">" if i==playing else " "
        missing="" if os.path.exists(os.path.join(radioPath,station["file"])) else " ?"
        screen.blit(font.render("{} {} FM".format(marker,station["freq"]),False,color),(area.x+4,area.y))
        screen.blit(font.render("  "+station["name"]+missing,False,color),(area.x+4,area.y+font.get_linesize()))
        if i==playing:
            pygame.draw.rect(screen,color,area,1)

    # off button, boxed while the radio is off
    area=offRect(font)
    screen.blit(font.render("[ RADIO OFF ]",False,color),(area.x+4,area.y+font.get_linesize()//4))
    if playing is None:
        pygame.draw.rect(screen,color,area,1)


def offRect(font):
    return pygame.Rect(0,stationRect(len(stations),font).y+font.get_linesize()//2,230,int(font.get_linesize()*1.5))


def offAt(pos,font):
    return offRect(font).collidepoint(pos)


# index of the station tapped, or None
def stationAt(pos,font):
    for i in range(len(stations)):
        if stationRect(i,font).collidepoint(pos):
            return i
    return None


# tune to a station, or switch off if it is already playing
def toggleStation(i):
    global playing
    if i==playing:
        pygame.mixer.music.stop()
        playing=None
        return
    filename=os.path.join(radioPath,stations[i]["file"])
    if not os.path.exists(filename):
        print("Not found: "+filename)
        return
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(loops=-1)
    playing=i


def stopRadio():
    global playing
    pygame.mixer.music.stop()
    playing=None
