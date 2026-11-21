from pyky040 import pyky040
import threading
import time
import pygame
import RPi.GPIO as GPIO
import sys
import queue
import os
import noise


from gauge import moveGauge
from greenFilter import remap
from menuItem import MenuItem
from pipboyScreen import PipboyScreen
import statBoxes
import radio
import clock
import audioOutput
import spin
import gear
import bikeMonitor
import mapView


# Setup the GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

screenX=480
screenY=320
halfWidth=int(screenX/2)
dR=60
dG=243
dB=170
dColor = (dR,dG,dB)
screensPath="UIScreens"

#TODO you can get fontsize from get_linesize() so I dont need to pass it everywhere, come clean this up
pygame.font.init()
menuFontSize=20
menuFont = pygame.font.SysFont("Liberation Mono", menuFontSize)
bodyFontSize=16
bodyFont = pygame.font.SysFont("Liberation Mono", bodyFontSize)
statFontSize=12
statFont = pygame.font.SysFont("Liberation Mono", statFontSize)
clockFont = pygame.font.SysFont("Liberation Mono", 92, bold=True)
clockDateFont = pygame.font.SysFont("Liberation Mono", 24, bold=True)
monitorFont = pygame.font.SysFont("Liberation Mono", 44, bold=True)
# the DATA screen clock redraws when the second changes
lastClockSecond = -1

# top left of the 249x216 STAT vault boy image, where the stat bars are measured from
statsOrigin=(int((screenX-249)/2), int(((screenY-216)/2)-20)+menuFontSize+1)

screenNames = ["STAT","INV", "MAP", "DATA", "RADIO", "SPIN"]
menu = []
menuItem = 0
pipboyScreen = []


# draw the entire menu and high light the selected item
def drawMenu(s,f,menu,hlItem):
    global menuFontSize
    yoffset=0
    xoffset=0
    #miHeight=menuFontSize+10
    miWidth=0

    selectedBarH=menuFontSize*0.3
    selectedBarW=3
    for i in range(0,len(menu)):
        miWidth=menu[i].drawItem(s,xoffset,yoffset)

        if (i==hlItem):
            pygame.draw.line(s,dColor,(xoffset,menuFontSize),(xoffset,selectedBarH),1)
            pygame.draw.line(s,dColor,(xoffset,selectedBarH),(xoffset+selectedBarW,selectedBarH),1)
            pygame.draw.line(s,dColor,(xoffset+miWidth,menuFontSize),(xoffset+miWidth,selectedBarH),1)
            pygame.draw.line(s,dColor,(xoffset+miWidth,selectedBarH),(xoffset+miWidth-selectedBarW,selectedBarH),1)
        else:
            pygame.draw.line(s,dColor,(xoffset,menuFontSize),(xoffset+miWidth,menuFontSize),1)

        xoffset+=miWidth
        
    pygame.draw.line(s,dColor,(xoffset,menuFontSize),(480,menuFontSize),1)



# work out which screen a tap selects: a tap on a menu tab picks that tab,
# a tap anywhere else steps on to the next screen
def screenFromTap(pos, currentItem):
    x, y = pos
    if y <= menuFontSize*2:
        xoffset = 0
        for i in range(0, len(menu)):
            xoffset += menu[i].textSurface.get_width()
            if x < xoffset:
                return i
    return (currentItem+1) % len(menu)


# render the text for a status bar
def drawStatusBar(s,f, status):
    global menuFontSize
    textSurface = f.render(status, False, dColor)
    s.blit(textSurface,(0,screenY-menuFontSize))


# END of menu setup section



# START of LED Gauge setup section
pin_green = 16
pin_yellow = 20
pin_red = 21

GPIO.setup(pin_green,GPIO.OUT)
GPIO.setup(pin_yellow,GPIO.OUT)
GPIO.setup(pin_red,GPIO.OUT)
GPIO.output(pin_green,GPIO.LOW)
GPIO.output(pin_yellow,GPIO.LOW)
GPIO.output(pin_red,GPIO.LOW)

# The following vars relate to the 3-led gauge state and update interval
gState = 0
gTicks = 0
gTimeDelta = 0
# END of LED Gauge setup section



# START of button setup section
pin_BTN1 = 12
pin_BTN2 = 5

def buttonPressed(channel):
    print("Button {} was pressed".format(channel))
    if channel==12:
        global mainLoop
        mainLoop=False
    if channel==5:
        global flipDisplayMode
        flipDisplayMode=True

GPIO.setup(pin_BTN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(pin_BTN1,GPIO.RISING,callback=buttonPressed, bouncetime=500)

GPIO.setup(pin_BTN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(pin_BTN2,GPIO.RISING,callback=buttonPressed, bouncetime=500)
# END of button setup section


# START OF Encoder setup section
# Default rotary position
rotaryPosition=0
q = queue.Queue()

# Call back functions for encoder
def encoderClicked():
    print("encoder clicked")

def turned(scale_position):
    global q
    print("turned to {}".format(scale_position))
    q.put(scale_position)

# Pins used by the encoder
pin_sw = 19
pin_dt = 13
pin_clk = 6
pin_3v3 = 26

# Define pin initial state
GPIO.setup(pin_3v3,GPIO.OUT)
GPIO.output(pin_3v3,GPIO.HIGH)




# Setup the perlin noise parameters
scale = 100.0
octaves = 4
persistence = 0.5
lacunarity = 2.0

ybaseline=screenY/2
# END of perlin noise parameters


# Init the display and setup for gfx
pygame.init()
# the speaker/bluetooth selector sits under the radio off button
outputTop=radio.offRect(bodyFont).bottom+10
audioOutput.start()
#screen = pygame.display.set_mode((screenX,screenY), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((screenX,screenY), pygame.FULLSCREEN | pygame.SCALED)
flipDisplayMode=False
fullScreenMode=True

# If the MAP doesnt exist, then there may not have been a cache built
# so we go ahead and create a filtered version to cache for display
if os.path.exists(os.path.join(screensPath,'MAP.png')) == False:
    print("Map cache missing - building")
    tempImage = pygame.image.load(os.path.join(screensPath,'rawMap.png')).convert()
    remap(tempImage)

    screen.blit(tempImage,(0,0))
    pygame.display.update()

    pygame.image.save(tempImage,os.path.join(screensPath,"MAP.png"))


print("Building UI...")
for item in screenNames:
    menu.append(MenuItem(menuFont,item,dColor))
    pipboyScreen.append(PipboyScreen(bodyFont,item,dColor))
    
for item in pipboyScreen:
    print(item)
    item.loadScreenUsingTextFile(screensPath)
    item.loadScreenUsingGfxFile(screensPath)
print("... UI Build complete")

# Create the encoder
encoder = pyky040.Encoder(CLK=pin_clk, DT=pin_dt, SW=pin_sw)

# Setup and launch the thread to monitor the encoder
encoder.setup(scale_min=0,scale_max=len(menu)-1, loop=False, step=1, sw_debounce_time=100, chg_callback=turned, sw_callback=encoderClicked)
encoderThread = threading.Thread(target=encoder.watch)
encoderThread.daemon=True;
encoderThread.start()

# the following vars all relate to the rotary encoder debug status bar
timeStamp_ms = int(time.monotonic_ns()/1000);
firstTimestamp = True
timeDelta = 0
rollingAverage = 0
# END of encoder setup section

print("watching...")


# Main control vars for the main loop and screen
mainLoop = True
updateScreen = True
perlinSeed=0
# when a finger went down on the screen; holding it for shutdownHoldSecs powers off
pressStart=None
shutdownHoldSecs=3
while mainLoop:
    time.sleep(0.01)
    
    perlinSeed=perlinSeed+1
    if perlinSeed>screenX:
        perlinSeed=0


    if (flipDisplayMode==True):
        #screen = pygame.display.set_mode((screenX,screenY),pygame.RESIZABLE | pygame.SCALED)
        print("Flip display called")
        if (fullScreenMode==False):
            screen = pygame.display.set_mode((screenX,screenY), pygame.FULLSCREEN | pygame.SCALED)
            fullScreenMode=True
            updateScreen=True
        else:
            screen = pygame.display.set_mode((screenX,screenY),pygame.RESIZABLE | pygame.SCALED)
            fullScreenMode=False
            updateScreen=True
        flipDisplayMode=False


    # Check for any pygame events, and react if any
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainLoop = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                mainLoop = False
                print("escape or space pressed")
            if event.key == pygame.K_0:
                q.put(0)
            if event.key == pygame.K_1:
                q.put(1)
            if event.key == pygame.K_2:
                q.put(2)
            if event.key == pygame.K_3:
                q.put(3)
            if event.key == pygame.K_4:
                q.put(4)
            if event.key == pygame.K_5:
                q.put(5)
        # touchscreen taps arrive as mouse clicks, act on release so a long hold
        # doesnt also change screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            pressStart=time.monotonic()
        if event.type == pygame.MOUSEBUTTONUP and pressStart is not None:
            # on STAT a tap closes an open stat popup, or opens the tapped stat
            tappedStat=statBoxes.statAt(event.pos,statFont,statsOrigin)
            if menuItem==0 and statBoxes.popupStat is not None:
                statBoxes.popupStat=None
                updateScreen=True
            elif menuItem==0 and tappedStat is not None:
                statBoxes.popupStat=tappedStat
                updateScreen=True
            # on RADIO a tap on a station tunes in, or switches it off
            elif menuItem==4 and radio.stationAt(event.pos,bodyFont) is not None:
                radio.toggleStation(radio.stationAt(event.pos,bodyFont))
            elif menuItem==4 and radio.offAt(event.pos,bodyFont):
                radio.stopRadio()
            elif menuItem==4 and audioOutput.outputAt(event.pos,bodyFont,outputTop) is not None:
                audioOutput.selectOutput(audioOutput.outputAt(event.pos,bodyFont,outputTop))
            # on SPIN taps pick an instructor, book a class or go back
            elif menuItem==5 and spin.handleTap(event.pos):
                updateScreen=True
            # on INV a tap fits a wheelset, on DATA it swaps clock and ride monitor
            elif menuItem==1 and gear.handleTap(event.pos,bodyFont):
                updateScreen=True
            elif menuItem==3 and bikeMonitor.handleTap(event.pos):
                updateScreen=True
            # on MAP a tap swaps between the location map and the strava route
            elif menuItem==2 and mapView.handleTap(event.pos):
                updateScreen=True
            else:
                q.put(screenFromTap(event.pos, menuItem))
            pressStart=None

    # long press anywhere - shut the pi down cleanly
    if pressStart is not None and time.monotonic()-pressStart >= shutdownHoldSecs:
        screen.fill((0,0,0))
        textSurface = menuFont.render("SHUTTING DOWN...", False, dColor)
        screen.blit(textSurface,((screenX-textSurface.get_width())/2,(screenY-textSurface.get_height())/2))
        pygame.display.update()
        print("long press - shutting down")
        os.system("sudo systemctl poweroff")
        mainLoop = False
        continue


    # Deal with tracking timing for the game
    gTicks+=1
    if (gTicks==50):
        gTicks=0
        gState=moveGauge(gState)
        statBoxes.driftStats()
        if menuItem==0:
            updateScreen = True
        # Turn off all the lights.
        GPIO.output(pin_green,GPIO.LOW)
        GPIO.output(pin_yellow,GPIO.LOW)
        GPIO.output(pin_red,GPIO.LOW)
        if gState == 3:
            GPIO.output(pin_red,GPIO.HIGH)
            GPIO.output(pin_yellow,GPIO.HIGH)
            GPIO.output(pin_green,GPIO.HIGH)
        elif gState == 2:
            GPIO.output(pin_yellow,GPIO.HIGH)
            GPIO.output(pin_green,GPIO.HIGH)
        elif gState == 1:
            GPIO.output(pin_green,GPIO.HIGH)

    newTimeStamp=int(time.monotonic_ns()/1000);
    timeDelta = newTimeStamp - timeStamp_ms;

    if (firstTimestamp==True):
        rollingAverage=timeDelta
        firstTimestamp=False
    else:
        rollingAverage = (rollingAverage + timeDelta)/2

    statusBar="T:{:d} A:{:f} S:{:f}".format(timeDelta,rollingAverage,rollingAverage/1000000)
    timeStamp_ms=newTimeStamp
    # End of time tracking section




    if not q.empty():
        # if the rotary dial has been turned then lets update the menu
        rotaryPosition=q.get()

        menuItem=rotaryPosition;
        statBoxes.popupStat=None

        updateScreen = True
    else:
        # certain menu items that have an animation we always update
        if menuItem==4:
            updateScreen = True
        if menuItem==5 and spin.animating():
            updateScreen = True
        if bikeMonitor.sample() and menuItem==3 and bikeMonitor.showing:
            updateScreen = True
        if menuItem==3 and time.localtime().tm_sec != lastClockSecond:
            lastClockSecond = time.localtime().tm_sec
            updateScreen = True

    if updateScreen == True:
        # clear the screen
        screen.fill((0,0,0))
        
        # redraw the menu and update the game engine
        #screenNames = ["STAT","INV", "MAP", "DATA", "RADIO"]
        drawMenu(screen,menuFont,menu,menuItem)
        if menuItem==0:
            #249x216
            xStatsOffset = (screenX - 249)/2
            yStatsOffset = ((screenY - 216)/2)-20
            pipboyScreen[menuItem].drawScreen(screen,bodyFont,xStatsOffset,yStatsOffset,menuFontSize)
            statBoxes.drawStats(screen,statFont,dColor,statsOrigin)
            if statBoxes.popupStat is not None:
                statBoxes.drawPopup(screen,bodyFont,statFont,dColor)
        if menuItem==1:
            pipboyScreen[menuItem].drawScreen(screen,bodyFont,5,0,menuFontSize)
            gear.draw(screen,bodyFont,dColor)
        if menuItem==2:
            if mapView.showStrava:
                mapView.drawStrava(screen,bodyFont,dColor)
            else:
                pipboyScreen[menuItem].drawScreen(screen,bodyFont,8,0,menuFontSize)
            mapView.drawButtons(screen,bodyFont,dColor)
        if menuItem==3:
            bikeMonitor.drawModeButtons(screen,bodyFont,dColor)
            if bikeMonitor.showing:
                bikeMonitor.draw(screen,monitorFont,bodyFont,statFont,dColor)
            else:
                clock.drawClock(screen,clockFont,clockDateFont,dColor,screenX,90)
        if menuItem==4:
            pipboyScreen[menuItem].drawScreen(screen,bodyFont,0,0,menuFontSize)
            radio.drawStations(screen,bodyFont,dColor)
            audioOutput.drawOutputs(screen,bodyFont,dColor,outputTop)
            # draw radio frequencies, just a faint ripple when nothing is playing
            amplitude=1.0 if radio.playing is not None else 0.2
            for i in range (halfWidth,screenX,3):

                n = noise.pnoise2(perlinSeed/scale,i/scale,octaves=octaves,persistence=persistence,lacunarity=lacunarity,repeatx=screenX,repeaty=screenX,base=0)
                offset=int(n*scale*amplitude)
                pygame.draw.line(screen,dColor,(i,ybaseline+offset-1),(i,ybaseline+offset),1)
                #pygame.draw.line(screen,dColor,(i,ybaseline/2),(i,(ybaseline/2)+offset),1)


                #n = noise.pnoise2(i/scale,perlinSeed/scale,octaves=octaves,persistence=persistence,lacunarity=lacunarity,repeatx=512,repeaty=512,base=0)
                offset=int(n*scale)
                #pygame.draw.line(screen,(dR/2,dG/2,dB/2),(i,ybaseline+offset-1),(i,ybaseline+offset),1)
                #pygame.draw.line(screen,(dR/2,dG/2,dB/2),(i,ybaseline+(ybaseline/2)),(i,ybaseline+(ybaseline/2)+offset),1)
        
            pygame.draw.line(screen,dColor,((perlinSeed%halfWidth)+halfWidth,bodyFontSize*2),((perlinSeed%halfWidth)+halfWidth,screenY),1)
        if menuItem==5:
            spin.draw(screen,bodyFont,statFont,dColor)

        drawStatusBar(screen,bodyFont,statusBar)
        pygame.display.update()

    # This means that we only update when strictly necessary
    # this will need to be relaxed if we want to do screen effects
    # later
    updateScreen = False

pygame.quit()
sys.exit()
exit()
