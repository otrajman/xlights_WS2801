# xlights_WS2801
Web GUI and Runtime to control a string of WS2801 lights.

This group of scripts includes a configuration and Web UI to control a string of WS2801 lights.

Start with lights.py, which runs CherryPy and controls the light script and sets the number of lights (75 here)

The lights directory contains all the web files and scripts.

The lights.json file contains the saved configuration.

Check the paths in lights.rc (which you can configure to run at startup) and lights.conf

To start on boot, copy xlights.service to /lib/systemd/system as root and run 
# systemctl enable xlights

------------------
Pyton Dependencies:

RPi.GPIO
Adafruit_WS2801
Adafruit_GPIO.SPI as SPI
cherrypy
json

------------------
alternate.jpg  blink.jpg  cycle.jpg  rainbow.png  solid.jpg  trace.jpg
Image Credits:

rainbow.jpg “Rainbow” by Phil Fiddes is licensed under CC BY 2.0
trace.jpg “Light's Pulse” by Abdullah Bin Sahl is licensed under CC BY 2.0
solid.jpg “Rainbow” by John Morgan is licensed under CC BY 2.0
alternate.jpg “Strobing Colors” by Roberto Bouza is licensed under CC BY 2.0
blink.jpg “Strobe Idol” by Nana B Agyei is licensed under CC BY 2.0
cycle.jpg “Art Strobe” by Aaron Muszalski is licensed under CC BY 2.0
