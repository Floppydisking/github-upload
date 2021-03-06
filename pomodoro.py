#!/usr/bin/env python

# Copyright 2013-2015 Pervasive Displays, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.

from __future__ import print_function

import os
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import time
from papirus import Papirus

# Check EPD_SIZE is defined
EPD_SIZE=0.0
if os.path.exists('/etc/default/epd-fuse'):
    exec(open('/etc/default/epd-fuse').read())
if EPD_SIZE == 0.0:
    print("Please select your screen size by running 'papirus-config'.")
    sys.exit()

# Running as root only needed for older Raspbians without /dev/gpiomem
if not (os.path.exists('/dev/gpiomem') and os.access('/dev/gpiomem', os.R_OK | os.W_OK)):
    user = os.getuid()
    if user != 0:
        print("Please run script as root")
        sys.exit()

WHITE = 1
BLACK = 0

CLOCK_FONT_FILE = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'
DATE_FONT_FILE  = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'

pomo = [1500, 300, 1500, 300, 1500, 300, 1500, 1200]

def main(argv):

    """main program - draw and display time and date"""

    papirus = Papirus(rotation = int(argv[0]) if len(sys.argv) > 1 else 0)

    print('panel = {p:s} {w:d} x {h:d}  version={v:s} COG={g:d} FILM={f:d}'.format(p=papirus.panel, w=papirus.width, h=papirus.height, v=papirus.version, g=papirus.cog, f=papirus.film))

    papirus.clear()

    demo(papirus, 1500)

def demo(papirus, sec):
    """simple partial update demo - draw a clock"""

    # initially set all white background
    image = Image.new('1', papirus.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    width, height = image.size

    clock_font_size = int((width - 4)/(8*0.65))      # 8 chars HH:MM:SS
    clock_font = ImageFont.truetype(CLOCK_FONT_FILE, clock_font_size)
    date_font_size = int((width - 4)/(10*0.70))     # 10 chars YYYY-MM-DD
    date_font = ImageFont.truetype(DATE_FONT_FILE, date_font_size)

    # clear the display buffer
    draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)
    previous_second = 0
    previous_day = 0
    


    
    while True:
        while True:
            now = datetime.today()
            if now.second != previous_second:
                break
            time.sleep(0.1)

        if now.day != previous_day:
            draw.rectangle((2, 2, width - 2, height - 2), fill=WHITE, outline=BLACK)
            previous_day = now.day
        else:
            draw.rectangle((5, 10, width - 5, 10 + clock_font_size), fill=WHITE, outline=WHITE)
            draw.rectangle((2, 2, width - 2, height - 2), fill=WHITE, outline=BLACK)
        
        
        #pomo = [1500, 300, 1500, 300, 1500, 300, 1500, 1200]
        
        minn, secc = divmod(sec, 60)
        timeformat = '{:02d}:{:02d}'.format(minn, secc)
        sec -= 1
        if sec == 0:
            print('popping')
            #print(now_last)
            pomo.append(pomo.pop(0))
            print(pomo)
            sec = pomo[0]
        

        draw.text((5, 10), '{h:02d}:{m:02d}:{s:02d}'.format(h=now.hour, m=now.minute, s=now.second), fill=BLACK, font=clock_font)
        draw.text((105, 60), '{:02d}:{:02d}'.format(minn, secc), fill=BLACK, font=date_font)
        if sec > 1200:
            draw.text((5,60), 'Focus-', fill=BLACK, font=date_font)
        else:
            draw.text((5,60), 'Rest-', fill=BLACK, font=date_font)
        # display image on the panel
        papirus.display(image)
        if now.second < previous_second:
            papirus.update()    # full update every minute
        else:
            papirus.partial_update()
        previous_second = now.second

# main
if "__main__" == __name__:
    if len(sys.argv) < 1:
        sys.exit('usage: {p:s}'.format(p=sys.argv[0]))

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass

