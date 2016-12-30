# Remote Raspberry Pi
A Python Script to use the Raspberry Pi as a kind of a Multimedia Device

### Introduction
I started this Project over a Year ago. At the beginning it was just a script to stream some YouTube Videos on my TV. Later i added a WebRadio Stream and created an Android APP for it. This app will be added in the next days.

### Installation
Install livestreamer:
```
    sudo apt-get install livestreamer
```
Download Remote Raspberry Pi:
```
    git clone https://github.com/flatt3rn/rrpi
```
or

Install Remote Raspberry Pi:
```
    cd rrpi
    sudo python setup.py install
```
Uninstall Remote Raspberry Pi:
```
    sudo python setup.py uninstall
```

### How Does it Work
This Script starts a Server which listen to the Port 5563.
You can connect to it with my Android APP or jut with netcat or every other software.
Use these commands to control the server

Command | Example | Description
--- | --- | ---
yv | yv_https://www.youtube.com/watch?v=KK9bwTlAvgo | Stream a Youtube Video (This works with a lot of other pages)
ya | ya_https://www.youtube.com/watch?v=KK9bwTlAvgo | Same as above but just with the audio line
dl | dl_http://thisisaurl.com/stream.mp4 | Stream a Video with a Stream Link (eg. Radio Streams)
p | | Pause the Player
r | | 30 Seconds Forward
rr | | 10 Minuntes Forward
l | | 30 Seconds Back
ll | | 10 Minutes Back
q | | Quit the Player
vu | | Increases the Volume
vd | | Decreases the Volume
bg | bg_0 | Change the Background (Its there from the beginning, but never really used it)
re | | Reload the Stream
rd | rd_/home/pi/ | Read a Directory
cr | cr_0 | Change Ripper (0: youtube-dl 1: livestreamer)
gd | | Shutdown
gr | | Reboot
