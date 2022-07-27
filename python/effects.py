#!/usr/bin/python3

import pygame
import pygame.camera
from pygame.locals import *
import os
from PIL import Image
import PIL.ImageOps
#import antigravity
import shlex, subprocess
import time

import glob

from configparser import ConfigParser

# change to the python directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# read config
config = ConfigParser()
config.read('config.ini')
width = config.getint('Effects','width',fallback=800)
height = config.getint('Effects','height',fallback=600)
videoDev = config.get('Effects','videoDev',fallback='/dev/video0')
whiteBalance = config.getint('Effects','whiteBalance',fallback=5500)
backgroundDirectory = config.get('Effects','backgroundDirectory',fallback='../background')
captureDirectory = config.get('Effects','captureDirectory',fallback='../capture')
blinkDirectory = config.get('Effects','blinkDirectory',fallback='../blink')
FPS = config.getint('Effects','FPS',fallback=20)

pygame.init()

res = (width,height)
font = pygame.font.Font(None, 25)

WHITE = (255,255,255)
BLACK = (0,0,0)

# initialize display environment
pygame.display.init()
pygame.display.set_caption('Effects')


# initialize camera
pygame.camera.init()
cam = pygame.camera.Camera(videoDev,res,"RGB")
cam.start()

# create surfaces
# display surface
#lcd = pygame.display.set_mode(res,pygame.FULLSCREEN)
lcd = pygame.display.set_mode(res)
# place to save lcd without the red 'capture' box
lcdSave = pygame.surface.Surface(res)

# raw camera surface
camImage = pygame.surface.Surface(res)

# transparent camera surface
transparent = pygame.surface.Surface(res)
transparent.set_colorkey((0,255,0))

# menu surface
menu1 = pygame.surface.Surface(res)
menu1.set_colorkey((0,0,0))
menu1Text = font.render('Set Focus,White Balance,Exposure',True,WHITE)
menu1TextPos = menu1Text.get_rect(center=(width/2,height/2))
menu1.blit(menu1Text, menu1TextPos)
pygame.Rect.inflate_ip(menu1TextPos, 25, 25)
pygame.draw.rect(menu1,WHITE, menu1TextPos,3)

inverted = pygame.surface.Surface(res)
inverted.set_colorkey((255,0,255))

capture = pygame.surface.Surface(res)
capture.fill((0,255,0))
capture.set_colorkey((0,255,0))
imageCaptured = False

# edge detect surface
outline = pygame.surface.Surface(res)
outline.set_colorkey((0,0,0))

background = pygame.surface.Surface(res)
backgroundColor = (0,0,0)

# tracking surfaces
vpath1 = pygame.surface.Surface(res)
vpath1.set_colorkey((0,0,0))
ccolor1 = (0,0,0)
lastPos1 = (0,0)
mode1 = 0

vpath2 = pygame.surface.Surface(res)
vpath2.set_colorkey((0,0,0))
ccolor2 = (0,0,0)
lastPos2 = (0,0)
mode2 = 0

# fade out surface
fader = pygame.surface.Surface(res)
fader.fill((0,0,0))
fader.set_alpha(10)


# blink images
blinks = sorted(glob.glob(f"{blinkDirectory}/*.png"))
blinkIndex = 0

# display background images
images = sorted(glob.glob(f"{backgroundDirectory}/*.jpg"), key=str.lower)
imageIndex = 0


crect = pygame.Rect(0,0,10,10)
ccolor = (0,0,0)


#utility functions
def setV4L2( ctrl, value ) :
    return subprocess.run(shlex.split(f"v4l2-ctl -d {videoDev} --set-ctrl {ctrl}={value}"),stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL).returncode

def getV4L2( ctrl ) :
    ret = subprocess.run(shlex.split(f"v4l2-ctl -d {videoDev} --get-ctrl {ctrl}"),capture_output=True, text=True)
    if ret.returncode == 0 :
        return ret.stdout.split(" ")[1].strip()
    else :
        return ""

def getBackground() :
    # get average camra background surface
    bg = []
    for i in range(0,10): 
        bg.append(cam.get_image(background))
    pygame.transform.average_surfaces(bg,background)
    # creates 'background' == average background surface over five frames
    
    # the average color of the average surface. Used for the 'w' background color
    global backgroundColor 
    backgroundColor = pygame.transform.average_color(background)
    print(f"backgroundColor: {backgroundColor}")

    return

def getdisplayBackground(dir=1) :
    # background image scaled so that screen is filled with no distortion
    global imageIndex
    imageIndex += dir
    imageIndex = imageIndex % len(images)
    rawImage = pygame.image.load(images[imageIndex])
    w, h = rawImage.get_size()
    wScaled = width
    hScaled = height
    if w/h > width/height :
        # a wide image
        wScaled = int(w/h * height)
    else :
        # a narrow image
        hScaled = int(h/w * width)

    scaledImage = pygame.transform.smoothscale(rawImage,(wScaled,hScaled))
    scaledRect  = scaledImage.get_rect(center=(width/2, height/2))

    return scaledImage, scaledRect


# set exposure, focus, white balance
# ...since it's probably going to be shooting against a green-screen,
# ...auto whitebalance isn't going to work
whiteErr=setV4L2( "white_balance_temperature_auto",0 )
whiteErr=setV4L2( "white_balance_temperature",whiteBalance )
exposeErr=setV4L2( "exposure_auto",3)
focusErr=setV4L2( "focus_auto",1)
print(f"white balance: {whiteErr}, exposure: {exposeErr}, focus: {focusErr}")
zoom = 100

# throttle
timer = pygame.time.Clock()


going = True
while going:
    events = pygame.event.get()
    for e in events:
        if (e.type == MOUSEBUTTONDOWN):
            going = False
        if (e.type == KEYUP and e.key == K_SPACE):
            going = False

        if (e.type == KEYUP and e.key == K_e):
            exposure = getV4L2( "exposure_absolute" )
            focus = getV4L2( "focus_absolute" )
            print (f"Exposure: {exposure}, Focus: {focus}")

        if (e.type == KEYUP and e.key == K_UP):
            whiteBalance += 100
            setV4L2("white_balance_temperature",whiteBalance )
            whiteBalance = int(getV4L2("white_balance_temperature"))
            print(f"whiteBalance: {whiteBalance}")
        if (e.type == KEYUP and e.key == K_DOWN):
            whiteBalance -= 100
            setV4L2("white_balance_temperature",whiteBalance )
            whiteBalance = int(getV4L2("white_balance_temperature"))
            print(f"whiteBalance: {whiteBalance}")

        if (e.type == KEYUP and e.key == K_PERIOD):
            zoom += 2
            print (zoom)
            setV4L2( "zoom_absolute",zoom)
        if (e.type == KEYUP and e.key == K_COMMA):
            zoom -= 2
            if ( zoom < 100 ):
                zoom = 100
            print (zoom)
            setV4L2( "zoom_absolute",zoom)

    camImage = cam.get_image()
    #image = pygame.transform.flip(cam.get_image(),True,False)
    lcd.blit(camImage, (0,0))
    lcd.blit(menu1, (0,0))
    pygame.display.flip()


print ("Exposure, manual")
if not exposeErr :
    exposure = getV4L2( "exposure_absolute" )
    setV4L2( "exposure_absolute", exposure)
    setV4L2( "exposure_auto",1)

print ("Focus, manual")
if not focusErr :
    focus = getV4L2( "focus_absolute" )
    setV4L2( "focus_absolute", focus )
    setV4L2( "focus_auto", 0)

# get the camera average background surface, and the average color of the average surface
# also called using 'z' command
# ... actually I think it better to not do it here, only use 'z' command
#getBackground()

# display background
displayBackground, displayBackgroundRect = getdisplayBackground(0)

th = 25
diffColor = (0,255,0)

# streamCapture
fileNum = 0
fileDate = ""
start = 0
end = 0

# flags
backgroundType = 3
multiImage = False
alphaBlend = False
outlineImage = False
imageInverted = False
streamCapture = False


# display effects
going = True
while going:
    for e in pygame.event.get():
        if (e.type == MOUSEBUTTONDOWN):
            if pygame.mouse.get_pressed()[2] :
                streamCapture = not streamCapture
                print("left button")
            else :
                pos = pygame.mouse.get_pos()
                crect.center = pos
                #ccolor = pygame.transform.average_color(image, crect)
                ccolor = pygame.transform.average_color(lcd, crect)
                print (ccolor)

        if (e.type == KEYUP and e.key == K_RIGHT):
            displayBackground, displayBackgroundRect = getdisplayBackground(1)
        if (e.type == KEYUP and e.key == K_LEFT):
            displayBackground, displayBackgroundRect = getdisplayBackground(-1)

        if (e.type == KEYUP and e.key == K_KP7):
            ccolor1 = ccolor
        if (e.type == KEYUP and e.key == K_KP8):
            ccolor2 = ccolor

        if (e.type == KEYUP and e.key == K_KP1):
            mode1 += 1
            if (mode1 > 2):
                mode1 = 0
                lastPos1 = (0,0)
        if (e.type == KEYUP and e.key == K_KP2):
            mode2 += 1
            if (mode2 > 2):
                mode2 = 0
                lastPos2 = (0,0)
        if (e.type == KEYUP and e.key == K_c):
            vpath1.fill((0,0,0))
            vpath2.fill((0,0,0))
            imageCaptured = False
            capture.fill((0,255,0))
            multiImage = False

        if (e.type == KEYDOWN and e.key == K_ESCAPE):
            going = False

        if (e.type == KEYUP and e.key == K_w):
            backgroundType = 0
        if (e.type == KEYUP and e.key == K_b):
            backgroundType = 1
        if (e.type == KEYUP and e.key == K_i):
            backgroundType = 2
        if (e.type == KEYUP and e.key == K_g):
            backgroundType = 3


        # probably should try adjusting each color threshold?
        if (e.type == KEYUP and e.key == K_KP_MINUS):
            if (th > 1) :
                th -= 1
            print ("TH", th)
        if (e.type == KEYUP and e.key == K_KP_PLUS):
            if (th < 255) :
                th += 1
            print ("TH", th)

        if (e.type == KEYUP and e.key == K_o):
            outlineImage = not outlineImage
        if (e.type == KEYUP and e.key == K_v):
            imageInverted = not imageInverted

        if (e.type == KEYUP and e.key == K_m):
            multiImage = not multiImage
        if (e.type == KEYUP and e.key == K_a):
            alphaBlend = not alphaBlend
            if (alphaBlend) :
                multiImage = True
                transparent.set_alpha(30)
                transparent.set_colorkey(None)
                diffColor = (0,0,0)
            else:
                multiImage = False
                transparent.set_alpha(None)
                diffColor = (0,255,0)
                transparent.set_colorkey(diffColor)

        if (e.type == KEYUP and e.key == K_SPACE):
            imageCaptured = True
            capture.blit(transparent, (0,0))

        if (e.type == KEYUP and e.key == K_z):
            getBackground()



    # get camera image
    cam.get_image(camImage)

    # color tracking, two colors/modes
    if (mode1 > 0) :
        mask = pygame.mask.from_threshold(camImage, ccolor1, (20,20,20))
        connected = mask.connected_component()
        # fade the current path
        vpath1.blit(fader,(0,0))
        if connected.count() > 15:
            coord = connected.centroid()
            if lastPos1 == (0,0) :
                lastPos1 = coord
            else :
                pygame.draw.line(vpath1, ccolor1, lastPos1, coord, 5)
                lastPos1 = coord
        else :
            lastPos1 = (0,0)

    if (mode2 > 0) :
        mask = pygame.mask.from_threshold(camImage, ccolor2, (50,50,50))
        #connectedList = mask.connected_components(minimum=15)
        connected = mask.connected_component()
        #vpath2.blit(fader,(0,0))
        vpath2.fill((0,0,0))
        #for connected in connectedList :
        if connected.count() > 15:
            #coord = connected.centroid()
            trackRect = connected.get_bounding_rects()[0]
            diameter = max(trackRect.width, trackRect.height)
            #print (f"width: {trackRect.width} height: {trackRect.height}")
            blinkIndex += 1
            blinkIndex = blinkIndex % len(blinks)
            eyeBall = pygame.image.load(blinks[blinkIndex])
            vpath2.blit(pygame.transform.scale(eyeBall, (diameter, diameter)),trackRect)
            #vpath2.blit(pygame.transform.smoothscale(image, (trackRect.width, trackRect.height)),trackRect)
            #vpath2.fill(ccolor2, trackRect)
        #if lastPos2 == (0,0) :
        #        lastPos2 = coord
        #    else :
        #        pygame.draw.line(vpath2, ccolor2, lastPos2, coord, 5)
        #        lastPos2 = coord


    # background layer: black, white, or image
    #... why multiImage check?  Because multiImage means don't reset the background for each frame, just blit the layers on top
    #... multiImage is a variation on backgroundType... "accumulate"
    #... and alphablend is a variation of multiImage with the camera image background black non-transparent and alpha set to 30
    if ( not multiImage):
        if backgroundType == 0:
            # fill with white "w"
            lcd.fill(WHITE)
        elif backgroundType == 1:
            # fill with black "b"
            lcd.fill(BLACK)
        elif backgroundType == 2:
            # fill with background image "i"
            lcd.blit(displayBackground, displayBackgroundRect)
        elif backgroundType == 3:
            # fill with average color of background "g"
            lcd.fill(backgroundColor)


    # background tracks:
    if (mode1 == 2) :
        lcd.blit(vpath1, (0,0))
    if (mode2 == 2) :
        lcd.blit(vpath2, (0,0))


    # middle: 'snapped' image
    if (imageCaptured) :
        lcd.blit(capture, (0,0))


    # camera image layer with transparent background
    #
    # pygame.transfrom.threshold(dest_surf, surf, search_color, threshold, set_color, behavior, search_surface, inverse)
    # The documentation doesn't make sense to me:
    #   "If the optional 'search_surf' surface is given, it is used to threshold against rather than the specified 'set_color'."
    #   ...shouldn't that be threshold against 'search_color' not 'set_color'?
    #   "set_behavior=1 (default). Pixels in dest_surface will be changed to 'set_color'."
    #   "set_behavior=2 pixels set in 'dest_surf' will be from 'surf'."
    #   ...is not the way works when using search_surface
    #   The pixels copied to dest come from search_surf, not from surf
    #
    #... diffColor, the color key -- normally green, but black for alphablend 
    transparent.fill(diffColor)
    pygame.transform.threshold(transparent,background,None,(th,th,th),None,2,camImage,False)

    if (outlineImage) :
        laplace = pygame.transform.laplacian(transparent)
        if backgroundType == 0:
            outlineEdge = (1,1,1)
        elif backgroundType == 1:
            outlineEdge = (255,255,255)
        else : 
            outlineEdge = (255,0,0)
        outline.fill((0,0,0))
        pygame.transform.threshold(outline,laplace, (0,0,0), (40,40,40), outlineEdge, 1)
        #pygame.transform.threshold(outline,image, (0,0,0), (80,80,80), (5,5,5), 1)
        outline.set_colorkey((0,0,0))
        #lcd.blit(thresholded, (0,0))
        lcd.blit(outline, (0,0))
    elif (imageInverted) :
        # so, fill - GREEN == colorkey
        inverted.fill((255,255,255))
        inverted.set_colorkey((255,0,255))
        inverted.blit(transparent, (0,0), None, BLEND_RGB_SUB)
        lcd.blit(inverted, (0,0))
    else:
        lcd.blit(transparent, (0,0))
        

    # foreground tracks:
    if (mode1 == 1) :
        lcd.blit(vpath1, (0,0))
    if (mode2 == 1) :
        lcd.blit(vpath2, (0,0))

    if not streamCapture and fileDate != "" :
        fileDate = ""
        end = time.time()
        print(f"secs: {(end-start)}, frames: {fileNum}, FPS: {fileNum/(end-start)}")

    # display/stream capture
    if streamCapture :
        if fileDate == "" :
            fileDate = time.strftime("%Y%m%d-%H%M%S", time.localtime())
            fileNum = 0
            capturePath = os.path.join( captureDirectory, fileDate)
            print(f"capturePath {capturePath}")
            os.mkdir(capturePath)
            start = time.time()

        fileName = f"{capturePath}/effects{fileDate}-{fileNum:04d}.jpg"
        fileNum = fileNum + 1
        pygame.image.save(lcd, fileName)
        timer.tick(FPS)
        lcdSave.blit(lcd, (0,0))
        pygame.draw.rect(lcd,(255,0,0),(0,0, width, height),4)
        pygame.display.flip()
        lcd.blit(lcdSave,(0,0))
    else:
        pygame.display.flip()

cam.stop()
# set exposure, focus, white balance
#subprocess.call(shlex.split('uvcdynctrl --set="White Balance Temperature, Auto" 1'))
#subprocess.call(shlex.split('uvcdynctrl --set="Exposure, Auto" 3'))
#subprocess.call(shlex.split('uvcdynctrl --set="Focus, Auto" 1'))

