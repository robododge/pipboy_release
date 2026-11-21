# pipboy_release
public release of the pipboy UI code


This is the code for the User Interface for my Pipboy project. The code is messy and very hacky - I threw it together quickly with no real regard for reuse or future support. It was only for this with this project, but as I've had a few requests to share the code here it is in all its raw form.

I'm no longer actively coding this, so I wont be doing more updates, but if you have questions I'll do my best to get back to you.

Final note - Python is probably 3rd or 4th on my coding list, so I'm sure there are plent of examples of bad code here, I appologise in advance ;)

Project Structure:

pipboyUI.py - main entry point and update loop for the UI system. This is a good place to start, all the othe other code supports this module in some way.

menuItem.py - submodule to help manage the UI menu system.

pipboyScreen.py - submodule to help manage a UI screen.

location.py - this uses the IP addresses to lookup a geographic location and help setup the Map screen.

greenFilter.py - the image pulled down for the map is coloured and needs to be remapped to make it look right for an old school green screen, this utility code remaps an image to a green scale.

gauge.py - the pipboy has a 3-LED "guage" that I randomly set state on to make it look like the guage is reading something and going up and down, this is the code that manages that.

generateGraph.py - for the radio screen, I display some axis for the waveform part of the screen, I wrote this script to generate those scales and save them as an image.

generateTestPattern.py - in order to help test screen layout, I created a small script to create a test pattern on the screen.

getInfo - bash script to grab some info from the PI its running on and dump it to a text file for display on one of the UI screens.

updateScreens - bash script to refresh any screens that pull info from the outside world

UIScreens - directory where the UI screen images and text files are stored

displayChanges - basic scripts to make it easier to flip between the HDMI and LED outputs on the PI

prototypeVersions - old, experimental (and probably broken) code that I used to test out ideas on the way through.

notes - a few misc notes that I grabbed as I was working out how to do this.


## Additions in this fork

Runs on Raspberry Pi OS (Debian trixie) on a Pi 3 with a 7" HDMI touchscreen
(1024x600). The original 480x320 layout is scaled fullscreen with
`pygame.SCALED`, and everything can be driven by touch.

- `run-pipboy.sh` - launcher (refreshes the INV screen, starts the UI); add it to
  desktop autostart to boot straight into the pipboy
- touch: tap a menu tab, tap elsewhere for the next screen, hold 3 seconds to shut down
- `statBoxes.py` - the STAT vault boy's condition bars show tappable joke stats
- `gear.py` - INV lists bike equipment with a selectable wheelset
- `clock.py`, `bikeMonitor.py` - DATA swaps between a big clock and a simulated
  cycling monitor (power, cadence, speed, scrolling heart rate graph)
- `mapView.py` - MAP swaps to a green rendition of a Strava route
  (`UIScreens/STRAVA_MAP.png` is a placeholder - drop in your own)
- `radio.py`, `audioOutput.py` - RADIO plays mp3s from `radio/` (not in git) and
  switches output between the screen's HDMI speakers and a bluetooth speaker
- `spin.py` - SPIN tab: pick a spin class instructor, book classes, see their
  favourite phrases, with an animated rider on a spin bike

Python packages come from Raspberry Pi OS (`python3-pygame`, `python3-rpi-lgpio`,
`python3-requests`) plus `noise` and `pyky040` in a venv created with
`--system-site-packages`. Remove the `RPi.GPIO` that `pyky040` pulls in so the
system `rpi-lgpio` shim is used on newer kernels.
