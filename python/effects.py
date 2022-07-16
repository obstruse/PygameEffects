#!/usr/bin/python3

import pygame
import pygame.camera
from pygame.locals import *
import os
from PIL import Image
import PIL.ImageOps
#import antigravity
import shlex, subprocess

from configparser import ConfigParser

# read config
config = ConfigParser()
config.read('config.ini')
width = config.getint('Effects','width',fallback=800)
height = config.getint('Effects','height',fallback=600)
videoDev = config.get('Effects','videoDev',fallback='/dev/video0')
whiteBalance = config.getint('Effects','whiteBalance',fallback=5500)

pygame.init()

res = (width,height)
font = pygame.font.Font(None, 30)

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
#lcd = pygame.display.set_mode(res,pygame.FULLSCREEN)
lcd = pygame.display.set_mode(res)

# edge detect surface
thresholded = pygame.surface.Surface(res)
thresholded.set_colorkey((0,255,0))

# menu surfaces
menu1 = pygame.surface.Surface(res)
menu1.set_colorkey((0,0,0))
menu1Text = font.render('Set Focus, White Balance, Exposure',True,WHITE)
menu1TextPos = menu1Text.get_rect(center=(width/2,height/2))
menu1.blit(menu1Text, menu1TextPos)
pygame.draw.rect(menu1,WHITE, menu1TextPos,3)

menu2 = pygame.surface.Surface(res)
menu2.set_colorkey((0,0,0))

inverted = pygame.surface.Surface(res)
inverted.set_colorkey((255,0,255))

capture = pygame.surface.Surface(res)
capture.fill((0,255,0))
capture.set_colorkey((0,255,0))
imageCaptured = False

outline = pygame.surface.Surface(res)
outline.set_colorkey((0,0,0))

whiteSurf = pygame.surface.Surface(res)
whiteSurf.fill((255,255,255))

background = pygame.surface.Surface(res)

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

# background images
images = [
    'corner800.jpg',
    'Brick-800.jpg',
    'stream800.jpg',
    'Studio-3-800.jpg',
    'Studio-4-800.jpg',
    'Studio-5-800.jpg',
    'Studios-1-800.jpg',
    'Tunnel-1-800.jpg',
    'Decay-1-800.jpg'
    ]
imageIndex = 0

road = pygame.image.load(os.path.join("../images",images[imageIndex]))

crect = pygame.Rect(0,0,10,10)
ccolor = (0,0,0)
paper = (115,141,138)


#utility functions
def menuButton( menuText, menuCenter, menuSize ) :
        mbSurf = font.render(menuText,True,WHITE)
        mbRect = mbSurf.get_rect(center=menuCenter)
        menu.blit(mbSurf,mbRect)

        mbRect.size = menuSize
        mbRect.center = menuCenter
        pygame.draw.rect(menu,WHITE,mbRect,3)

        return mbRect

def setV4L2( ctrl, value ) :
    return subprocess.run(shlex.split(f"v4l2-ctl -d {videoDev} --set-ctrl {ctrl}={value}"),stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL).returncode

def getV4L2( ctrl ) :
    ret = subprocess.run(shlex.split(f"v4l2-ctl -d {videoDev} --get-ctrl {ctrl}"),capture_output=True, text=True)
    if ret.returncode == 0 :
        return ret.stdout.split(" ")[1].strip()
    else :
        return ""

def getBackground() :
    # get average background surface
    bg = []
    for i in range(0,10): 
        bg.append(cam.get_image(background))
    pygame.transform.average_surfaces(bg,background)
    # creates 'background' == average background surface over five frames
    
    # the average color of the average surface. Used for the 'w' background color
    paper = pygame.transform.average_color(background)

    return

# set exposure, focus, white balance
# ...since it's probably going to shooting against a green-screen,
# ...auto whitebalance probably isn't going to work
whiteErr=setV4L2( "white_balance_temperature_auto",0 )
whiteErr=setV4L2( "white_balance_temperature",whiteBalance )
exposeErr=setV4L2( "exposure_auto",3)
focusErr=setV4L2( "focus_auto",1)
print(f"white balance: {whiteErr}, exposure: {exposeErr}, focus: {focusErr}")
zoom = 100

going = True
while going:
    events = pygame.event.get()
    for e in events:
        if (e.type == KEYUP and e.key == K_SPACE):
            going = False

        if (e.type == KEYUP and e.key == K_e):
            exposure = getV4L2( "exposure_absolute" )
            focus = getV4L2( "focus_absolute" )
            print (f"Exposure: {exposure}, Focus: {focus}")

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

    image = cam.get_image()
    #image = pygame.transform.flip(cam.get_image(),True,False)
    lcd.blit(image, (0,0))
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

# get the average background surface, and the average color of the average surface
# also called using 'z' command
getBackground()

th = 25
diffColor = (0,255,0)

# flags
backgroundType = 0
multiImage = False
alphaBlend = False
outlineImage = False
imageInverted = False

# display effects
going = True
while going:
    for e in pygame.event.get():
        if (e.type == MOUSEBUTTONDOWN):
            pos = pygame.mouse.get_pos()
            crect.center = pos
            #ccolor = pygame.transform.average_color(image, crect)
            ccolor = pygame.transform.average_color(lcd, crect)
            print (ccolor)

        if (e.type == KEYUP and e.key == K_RIGHT):
            imageIndex += 1
            if (imageIndex >= len(images)):
                imageIndex = 0
            road = pygame.image.load(images[imageIndex])
        if (e.type == KEYUP and e.key == K_LEFT):
            imageIndex -= 1
            if (imageIndex < 0) :
                imageIndex = len(images) -1
            road = pygame.image.load(images[imageIndex])

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

        if (e.type == KEYDOWN and e.key == K_ESCAPE):
            going = False

        if (e.type == KEYUP and e.key == K_w):
            backgroundType = 0
        if (e.type == KEYUP and e.key == K_b):
            backgroundType = 1
        if (e.type == KEYUP and e.key == K_i):
            backgroundType = 2

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
                thresholded.set_alpha(30)
                thresholded.set_colorkey(None)
                diffColor = (0,0,0)
            else:
                multiImage = False
                thresholded.set_alpha(None)
                diffColor = (0,255,0)
                thresholded.set_colorkey(diffColor)

        if (e.type == KEYUP and e.key == K_SPACE):
            imageCaptured = True
            capture.blit(thresholded, (0,0))

        if (e.type == KEYUP and e.key == K_z):
            getBackground()


    # setup surfaces
    #thresholded.blit(image, (0,0))
    # threshold(dest_surf, surf, search_color, threshold=(0,0,0,0), set_color=(0,0,0,0), set_behavior=1, search_surf=None, inverse_set=False)
    # pygame.transform.threshold(thresholded,image,(0,255,0),(th,th,th),diffColor,2,background,True)
    # pygame.transform.threshold(thresholded,image,(96,176,112),(th,th,th),(0,255,0),1,None,True)

    #pygame.transform.threshold(thresholded,image,None,(th,th,th),(255,0,0),1,background,True)
    # sure seems like this is backward and shouldn't work:
    # the way I read the docs, a match between background and image should copy pixels
    # from background to thresholded, but instead it's copying image to thresholded
    # 'False' says copy the pixels that are different
    # also, it's working different that when first written.  Didn't need to fill the thresholded
    # surface with diffColor for example.
    
    # camera image with transparent background == thresholded
    #... diffColor??
    #image = pygame.transform.flip(cam.get_image(),True,False)
    image = cam.get_image()
    thresholded.fill(diffColor)
    pygame.transform.threshold(thresholded,background,None,(th,th,th),None,2,image,False)

    # color tracking, two colors/modes
    if (mode1 > 0) :
        mask = pygame.mask.from_threshold(image, ccolor1, (20,20,20))
        connected = mask.connected_component()
        if connected.count() > 15:
            coord = connected.centroid()
            if lastPos1 == (0,0) :
                lastPos1 = coord
            else :
                pygame.draw.line(vpath1, ccolor1, lastPos1, coord, 5)
                lastPos1 = coord
    if (mode2 > 0) :
        mask = pygame.mask.from_threshold(image, ccolor2, (20,20,20))
        connected = mask.connected_component()
        if connected.count() > 15:
            coord = connected.centroid()
            if lastPos2 == (0,0) :
                lastPos2 = coord
            else :
                pygame.draw.line(vpath2, ccolor2, lastPos2, coord, 5)
                lastPos2 = coord


    # background: black, white, or image
    #... why multiImage check?  Because means don't reset the background for each frame, just blit the layers on top
    #... so multiImage is a variation on backgroundType... "accumulate"
    #... and alphablend is a variation of multiImage with the camera image background black non-transparent and alpha set to 30
    if ( not multiImage):
        if backgroundType == 0:
            # fill with average color of background
            lcd.fill(paper)
        elif backgroundType == 1:
            lcd.fill((0,0,0))
        elif backgroundType == 2:
            lcd.blit(road, (0,0))

    # background sprites:
    if (mode1 == 2) :
        lcd.blit(vpath1, (0,0))
    if (mode2 == 2) :
        lcd.blit(vpath2, (0,0))

    # middle: threshold mask image
    #... Huh? why.... the capture surface is the thresholded surface...
    if (imageCaptured) :
        lcd.blit(capture, (0,0))

    # display camera image "thresholded"
    if (outlineImage) :
        laplace = pygame.transform.laplacian(thresholded)
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
        inverted.fill((255,255,255))
        inverted.blit(thresholded, (0,0), None, BLEND_RGB_SUB)
        lcd.blit(inverted, (0,0))
    else:
        lcd.blit(thresholded, (0,0))

    # foreground sprites:
    if (mode1 == 1) :
        lcd.blit(vpath1, (0,0))
    if (mode2 == 1) :
        lcd.blit(vpath2, (0,0))

    pygame.display.flip()

cam.stop()
# set exposure, focus, white balance
#subprocess.call(shlex.split('uvcdynctrl --set="White Balance Temperature, Auto" 1'))
#subprocess.call(shlex.split('uvcdynctrl --set="Exposure, Auto" 3'))
#subprocess.call(shlex.split('uvcdynctrl --set="Focus, Auto" 1'))

