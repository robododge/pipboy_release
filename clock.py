import time

# big digital clock for the DATA screen, the colons blink every other second
def drawClock(screen,timeFont,dateFont,color,screenX,top):
    now=time.localtime()
    sep=":" if now.tm_sec%2==0 else " "
    hour=now.tm_hour%12 or 12
    text="{:d}{}{:02d}{}{:02d}".format(hour,sep,now.tm_min,sep,now.tm_sec)
    timeSurface=timeFont.render(text,False,color)
    screen.blit(timeSurface,((screenX-timeSurface.get_width())/2,top))

    detail=dateFont.render(time.strftime("%p  %a %b %d %Y",now).upper(),False,color)
    screen.blit(detail,((screenX-detail.get_width())/2,top+timeSurface.get_height()+8))
