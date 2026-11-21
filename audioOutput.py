import re
import subprocess
import threading
import time
import pygame

# Choose where the radio plays: the screen's own speakers (over HDMI) or a
# bluetooth speaker. Pair the speaker once with bluetoothctl, then set its
# address here (None uses the first paired device).
btSpeaker=None   # e.g. "AA:BB:CC:DD:EE:FF"

# what is in use now, "SPEAKER" or "BLUETOOTH", and a message while connecting
output="SPEAKER"
status=""
buttons=[("SPEAKER",0,100),("BLUETOOTH",108,122)]


def run(*cmd):
    return subprocess.run(cmd,capture_output=True,text=True,timeout=30).stdout


# id of the first audio sink whose node name contains text, or None
def findSink(text):
    audio=run("wpctl","status","--name").split("Video")[0]
    sinks=audio.split("Sinks:")[1].split("Sources:")[0] if "Sinks:" in audio else ""
    for sinkId,name in re.findall(r"(\d+)\.\s+(\S+)",sinks):
        if text in name:
            return sinkId
    return None


# work out which output is in use from the default sink - the bluetooth
# speaker can drop out on its own, and audio then falls back to the screen
def detectOutput():
    global output
    defaultSink=run("wpctl","inspect","@DEFAULT_AUDIO_SINK@")
    output="BLUETOOTH" if "bluez_output" in defaultSink else "SPEAKER"


def watchOutput():
    while True:
        if status!="CONNECTING...":
            detectOutput()
        time.sleep(3)


def useSpeaker():
    global output,status
    status=""
    sink=findSink(".hdmi")
    if sink is not None:
        run("wpctl","set-default",sink)
    output="SPEAKER"


# connecting takes a few seconds, so this runs on its own thread
def connectBluetooth():
    global output,status
    status="CONNECTING..."
    speaker=btSpeaker
    if speaker is None:
        paired=re.findall(r"Device (\S+)",run("bluetoothctl","devices","Paired"))
        speaker=paired[0] if paired else None
    if speaker is None:
        status="NO BT SPEAKER PAIRED"
        return
    run("bluetoothctl","connect",speaker)
    # the bluetooth sink shows up a moment after the connection
    for attempt in range(20):
        sink=findSink("bluez_output")
        if sink is not None:
            run("wpctl","set-default",sink)
            output="BLUETOOTH"
            status=""
            return
        time.sleep(0.5)
    status="BT SPEAKER NOT FOUND"


def selectOutput(name):
    if name=="SPEAKER":
        useSpeaker()
    elif status!="CONNECTING...":
        threading.Thread(target=connectBluetooth,daemon=True).start()


def start():
    threading.Thread(target=watchOutput,daemon=True).start()


def buttonRect(left,width,font,top):
    return pygame.Rect(left,top+font.get_linesize(),width,int(font.get_linesize()*1.5))


def drawOutputs(screen,font,color,top):
    screen.blit(font.render("OUTPUT:",False,color),(4,top))
    for name,left,width in buttons:
        area=buttonRect(left,width,font,top)
        screen.blit(font.render(name,False,color),(area.x+6,area.y+font.get_linesize()//4))
        if name==output:
            pygame.draw.rect(screen,color,area,1)
    if status!="":
        screen.blit(font.render(status,False,color),(4,top+int(font.get_linesize()*2.75)))


# name of the output button tapped, or None
def outputAt(pos,font,top):
    for name,left,width in buttons:
        if buttonRect(left,width,font,top).collidepoint(pos):
            return name
    return None
