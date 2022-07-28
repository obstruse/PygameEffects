# Pygame Effects
![](/images/M.png)

**Pygame Green Screen, with Color Tracking, Edge Detect, etc** (experimental)

When the program starts it captures the scene background.  The current camera image is compared to the saved background; pixels that are the same (within a threshold) are given a transparent color key.  Multiple layers are combined for different effects.

## Setup
- python 3.10.4
- pygame 2.1.2
- Logitech HD 1080p USB camera


## Running the Program

The background should be a color that contrasts with the foreground (not necessarily green).  It should be well-lit, with no shadows cast by the foreground object.

When the program starts it will display:

![startup](/images/startup.png)

Place your foreground object in front of the camera
- use the `up` / `down` keys to adjust white balance
- use the `,` / `.` keys to zoom in/out
- wait a moment for auto-exposure/auto-focus to settle
- press `space` (or click mouse) to continue

Remove the object from in front of the camera
- press `z` to capture the current image as the **green screen**
- if lighting changes, re-capture the image
- use `kp+`/`kp-` to adjust **green screen** threshold if necessary

Color tracking
- use mouse to select a color on screen
- press `kp7` or `kp8` to store the color in track1 or 2
- press `kp1` or `kp2` to start tracking foreground
- press again for background, or to stop tracking
- press `c` to clear track

Image capture
- press `right mouse` to start/stop capturing images
- images are stored in `captureDirectory` with timestamp
- red border will appear on screen during capture
- maximum frame rate determined by `FPS` setting in `config.ini`
---
![track](images/20220727-174332.gif)
![eyeball](images/20220727-170403.gif)

---

&nbsp;|Keyboard Commands
-|-
 |
&nbsp;|**Startup**
 |
`space`| accept focus, white balance, exposure and continue
`,` / `.` | zoom in/out
`up` / `down`| adjust white balance
 |
&nbsp;|**Tracking**
 | 
`mouse` | select color
`kp7` / `kp8` | set color 1 / 2
`kp1` / `kp2` | cycle through tracking modes: front, back, off
`c` | clear tracking
 |
&nbsp;|**Display Background**
 |
`w` | white
`b` | black
`g` | average of green screen
`i` | image
`left`/`right`|previous/next background image
`z` | capture green screen
|
&nbsp;|**Processing**
 |
`o` | outline
`v` | inverted
`m` | multiImage
`a` | alpha blend
`space` | freeze image
`kp+`/`kp-` | threshold
`right mouse`| capture image sequence

---

## Configuration

Program settings can be changed by modifying `config.ini` located in the same directory as `effects.py`


&nbsp;|Configuration Settings|&nbsp;
-|-|-
|
**Key**|**Description**|**Default**
|
width | display width|800
height | display height|600
videoDev | video device|/dev/video0
whiteBalance | white balance|5500
backgroundDirectory | directory of images for the display background|../background
captureDirectory | directory for capatured images|../capture
blinkDirectory | directory for _blink_ images|../blink
FPS | maximum FPS during image capture|20


