import adafruit_sdcard
import adafruit_touchscreen
import board
import busio
import digitalio
import storage

import adafruit_imageload
import displayio
import neopixel
import gc
import os
import random
import time

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.SD_CS)

sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# All files will be in a folder called 'topics'. Each subfolder will contain a theme
path = "/sd/topics"

raw_topics = os.listdir(path)

topics = {}
for topic in raw_topics:
    if topic[0] != '.':
        topics[topic] = []

for topic in topics:
    raw_files = os.listdir(path + "/" + topic)
    for entry in raw_files:
        if entry[-3:] == 'bmp' and entry[0] != '.':
            topics[topic].append(entry)

display = board.DISPLAY
display.rotation=270
display.auto_brightness = False

screen_width = 240
screen_height = 320
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(screen_width, screen_height))

visible = True

group = displayio.Group(max_size=1)

base_path = "/sd/topics/"
print('starting up')

max_counter = 100000 # By experimentation
counter = max_counter


while True:
    if counter == max_counter:    
        directory = random.choice(list(topics.keys()))
        filename = random.choice(topics[directory])

        full_path = base_path + directory + "/" + filename

        image, palette = adafruit_imageload.load(full_path, bitmap=displayio.Bitmap, palette=displayio.Palette)
        tile_grid = displayio.TileGrid(image, pixel_shader=palette)

        group.append(tile_grid)

        board.DISPLAY.show(group)

        # Fade in
        for x in range(10):
            display.brightness = (x + 1) * 0.1
            time.sleep(1)
        
        counter = 0
    
    if visible:
        counter += 1
    
    touch = ts.touch_point # STRANGE: seems to be causing an audible whine in PyPortal board
    
    if touch:
        time.sleep(0.5) # Will get multiple touches so temporarily block so only get one
        if visible:
            visible = False
            display.brightness = 0
        else:
            visible = True
            display.brightness = 1
    
    gc.collect() # Even stranger: adding this stopped the audible whine
    
    # Fade out
    if counter == max_counter:
        for x in range(10):
            display.brightness = 1 - ((x + 1) * 0.1)
            time.sleep(1)

        group.pop()
        del tile_grid
        del image
        del palette

        gc.collect()