import adafruit_sdcard
import board
import busio
import digitalio
import storage

import adafruit_imageload
import displayio
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

group = displayio.Group(max_size=1)

#counter = 0
while True:
    base_path = "/sd/topics/"
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
        time.sleep(6)

    # Show each image for 3 minutes
    time.sleep(180)

    # Fade out
    for x in range(10):
        display.brightness = 1 - ((x + 1) * 0.1)
        time.sleep(6)

    group.pop()
    del tile_grid
    del image
    del palette

    gc.collect()