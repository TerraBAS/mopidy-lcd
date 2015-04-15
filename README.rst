Mopidy-lcd is an MPC for Pi Music Box using  Adafruit's Character LCD with buttons

Features:
===========
MPC Features:
- Initializes to a clock display
- Scrolls Song Title and Artist
- Shows Play status as time into song
- Can select playlists (currently not working right)
- Allows you to turn shuffle and repeat on and off

RPI Commands:
- Can change the audio output
- Can shutdown or reboot
- can change the display colour

Necessary Items:
===========
- Raspberry Pi with Pi Music Box
- Adafruit Character LCD with buttons

Installation:
===========
First thing first is to make sure you have Pi Music Box setup
Their documentation is very easy to follow

Next follow the installation outlined in Adafruit's usage page:
https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi/usage

Running:
===========
To run, run the main.py with python.
<code>sudo python main.py</code>

if you want it to automatically run on startup, setup a cron for main.py
