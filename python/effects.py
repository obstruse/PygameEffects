#!/usr/bin/python2

import pygame
import pygame.camera
from pygame.locals import *
import os
from PIL import Image
import PIL.ImageOps
#import antigravity
import shlex, subprocess

pygame.init()
pygame.camera.init()

res = (800,600)
lcd = pygame.display.set_mode(res,pygame.FULLSCREEN)
#lcd = pygame.display.set_mode(res)

cam = pygame.camera.Camera("/dev/video2",res,"RGB")
cam.start()

thresholded = pygame.surface.Surface(res)
thresholded.set_colorkey((0,255,0))

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

road = pygame.image.load(images[imageIndex])

crect = pygame.Rect(0,0,10,10)
ccolor = (0,0,0)
paper = (115,141,138)

# set exposure, focus, white balance
print "White Balance, manual, 5500"
#subprocess.call(shlex.split('uvcdynctrl --set="White Balance Temperature, Auto" 1'))
subprocess.call(shlex.split('uvcdynctrl --set="White Balance Temperature, Auto" 0'))
subprocess.call(shlex.split('uvcdynctrl --set="White Balance Temperature" 5500'))

print "Exposure, auto aperture priority"
subprocess.call(shlex.split('uvcdynctrl --set="Exposure, Auto" 3'))
#subprocess.call(shlex.split('uvcdynctrl --set="Exposure, Auto" 1'))
#subprocess.call(shlex.split('uvcdynctrl --set="Exposure (Absolute)" 333'))

print "Focus, auto"
subprocess.call(shlex.split('uvcdynctrl --set="Focus, Auto" 1'))
#subprocess.call(shlex.split('uvcdynctrl --set="Contrast" 150'))

print "...loop..."

going = True
while going:
	events = pygame.event.get()
	for e in events:
		if (e.type == KEYUP and e.key == K_SPACE):
			going = False

		if (e.type == KEYUP and e.key == K_e):
			print "Exposure:"
			exposure = subprocess.check_output(shlex.split('uvcdynctrl --get="Exposure (Absolute)"'))
			print exposure
			print "White Balance:"
			subprocess.call(shlex.split('uvcdynctrl --get="White Balance Temperature"'))
			print "Focus"
			focus = subprocess.check_output(shlex.split('uvcdynctrl --get="Focus (absolute)"'))
			print focus


	image = cam.get_image()
	lcd.blit(image, (0,0))
	pygame.display.flip()

print "...loop end..."

print "White Balance, manual"
subprocess.call(shlex.split('uvcdynctrl --set="White Balance Temperature, Auto" 0'))

print "Exposure, manual"
subprocess.call(shlex.split('uvcdynctrl --set="Exposure, Auto" 1'))
subprocess.check_output(shlex.split('uvcdynctrl --set="Exposure (Absolute)" '+ str(exposure)))
subprocess.call(shlex.split('uvcdynctrl --get="Exposure (Absolute)"'))

print "Focus, manual"
subprocess.call(shlex.split('uvcdynctrl --set="Focus, Auto" 0'))
subprocess.check_output(shlex.split('uvcdynctrl --set="Focus (absolute)" '+ str(focus)))
subprocess.call(shlex.split('uvcdynctrl --get="Focus (absolute)"'))


# get background
going = True
bg = []
for i in range(0,5): 
	bg.append(cam.get_image(background))
pygame.transform.average_surfaces(bg,background)

paper = pygame.transform.average_color(background)

backgroundType = 0
th = 25
multiImage = False
alphaBlend = False
diffColor = (0,255,0)
outlineImage = False
imageInverted = False

# display effects
while going:
	events = pygame.event.get()
	for e in events:
		if (e.type is MOUSEBUTTONDOWN):
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

		if (e.type == KEYUP and e.key == K_e):
			print "Exposure:"
			subprocess.call(shlex.split('uvcdynctrl --get="Exposure (Absolute)"'))


	# setup surfaces
	image = cam.get_image()
	pygame.transform.threshold(thresholded,image,(0,255,0),(th,th,th),diffColor,2,background,True)

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


	# back: black, white, or image
	if ( not multiImage):
		if backgroundType == 0:
			#lcd.fill((255,255,255))
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
	if (imageCaptured) :
		lcd.blit(capture, (0,0))

	if (outlineImage) :
		laplace = pygame.transform.laplacian(thresholded)
		if backgroundType == 0:
			outlineEdge = (1,1,1)
		elif backgroundType == 1:
			outlineEdge = (255,255,255)
		else : 
			outlineEdge = (255,0,0)
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

	# top: mask from color
	if (mode1 == 1) :
		lcd.blit(vpath1, (0,0))
	if (mode2 == 1) :
		lcd.blit(vpath2, (0,0))

	pygame.display.flip()

cam.stop()
# set exposure, focus, white balance
subprocess.call(shlex.split('uvcdynctrl --set="White Balance Temperature, Auto" 1'))
subprocess.call(shlex.split('uvcdynctrl --set="Exposure, Auto" 3'))
subprocess.call(shlex.split('uvcdynctrl --set="Focus, Auto" 1'))

