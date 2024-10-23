import json
import time
import os
import gc
import board
import displayio
import random
from secrets import secrets
import adafruit_touchscreen
from adafruit_pyportal import PyPortal
import adafruit_requests as requests
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import neopixel

url = "http://www.lindsayrgwatt.com/api/device-images/2/" + secrets['api_key'] + "/"

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)  # 1 pixel on PyPortal
pixel.brightness = 0.5  # Set the brightness level (0.0 to 1.0)

# Setup PyPortal
pyportal = PyPortal(url=url,
                    json_path=None,  # Will parse full JSON response
                    default_bg="")  # No default background, we control images
display = board.DISPLAY
display.rotation = 270  # Portrait mode

# Screen dimensions (for the touchscreen calibration)
screen_width = display.width
screen_height = display.height

# Set up the touchscreen with calibration values
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(screen_width, screen_height))
screen_on = False
last_touch_time = time.monotonic()

# File path for SD card
SD_PATH = "/sd/"

IMAGE_CHECK_FAILURE_THRESHOLD = 5 # Get 0 images this many time and fail

# Constants for fade in/out
FADE_TIME = 5  # in seconds
MAX_BRIGHTNESS = 1.0
MIN_BRIGHTNESS = 0.0

# Variables to hold state
shown_images = []
current_image = None
display_time = 60  # Default to 5 minutes, in seconds
refresh_interval = 300  # 5 min in seconds
last_refresh_time = time.monotonic()
failed_image_check = 0 # How many times we check for images
first_run = True

# Load and parse the image list from the API
def fetch_image_data():
    print(f"{time.monotonic()} :: Calling server to get image data")
    global display_time
    response = pyportal.fetch() # Response is string text
    data = json.loads(response)
    print(f"{time.monotonic()} :: Here is raw data")
    print(data)
    print(f"{time.monotonic()} :: Display time is {display_time} before update")
    display_time = data['display_time'] * 60  # Convert to seconds
    print(f"{time.monotonic()} :: Display time is {display_time} after update")
    return data['images']

# Check if a file exists
def file_exists(filepath):
    try:
        os.stat(filepath)
        print(f"{time.monotonic()} :: {filepath} exists")
        return True
    except OSError:
        print(f"{time.monotonic()} :: {filepath} does not exist")
        return False

# Download image if it's not already saved
def download_image(image_url):
    image_name = image_url.split('/')[-1]
    image_path = SD_PATH + "/" + image_name  # Concatenate paths manually
    if not file_exists(image_path):  # Use custom function to check file existence
        print(f"{time.monotonic()} :: Downloading {image_name}...")
        pyportal.wget(image_url, image_path)
    else:
        print(f"{time.monotonic()} :: {image_name} already exists")
    return image_path

# Delete images not in the current list
def clean_up_images(current_images):
    local_images = [f for f in os.listdir(SD_PATH) if f.endswith(".bmp")]

    for image in local_images:
        image_path = SD_PATH + '/' + image
        if image_path not in current_images:
            print(f"{time.monotonic()} :: Deleting {image}...")
            os.remove(image_path)

# Fade effect for image display
def fade_image(image, fade_in=True):
    for i in range(6):

        brightness = i * 20 / 100 if fade_in else (100 - i * 20) / 100
        display.brightness = brightness
        time.sleep(1)

# Display image for set time
# VERY SLOW; screen will go black while happening
def display_image(image_path):
    global current_image

    image_path = SD_PATH + '/' + image_path

    current_image = displayio.OnDiskBitmap(image_path)
    image = displayio.TileGrid(current_image, pixel_shader=current_image.pixel_shader)
    group = displayio.Group()
    group.append(image)
    display.root_group = group

    fade_image(image, fade_in=True)

print(f"{time.monotonic()} :: Display time is {display_time} before main_loop runs")

# Main loop
def main_loop():
    global last_touch_time, screen_on

    current_image_paths = [f for f in os.listdir(SD_PATH) if f.endswith(".bmp")]

    # Select and display images without repeating until all are shown
    available_images = set(current_image_paths) - set(shown_images)
    if not available_images:
        shown_images.clear()
        available_images = current_image_paths

    image_to_show = random.choice(list(available_images))
    display_image(image_to_show)
    shown_images.append(image_to_show)

    # Non-blocking wait for display_time with touch check
    start_time = time.monotonic()
    while time.monotonic() - start_time < display_time:
        handle_touch()
        time.sleep(0.1)  # Small delay to reduce CPU usage

    # Fade out unless handle_touch event occurred
    if screen_on:
        fade_image(image_to_show, fade_in=False)

# Handle touch to turn screen on/off
def handle_touch():
    global screen_on, last_touch_time
    touch = ts.touch_point  # Get the current touch point
    if touch and time.monotonic() - last_touch_time > 1:
        print(f"{time.monotonic()} :: Screen touched!")
        
        # Blink NeoPixel to show that touch registered
        pixel.fill((0, 255, 0))  # Green color
        time.sleep(0.1)  # Keep the NeoPixel on for 0.1 seconds
        pixel.fill((0, 0, 0))  # Turn off NeoPixel
        
        last_touch_time = time.monotonic()
        if screen_on:
            display.brightness = 0  # Turn off screen
            screen_on = False
        else:
            display.brightness = 1  # Turn on screen
            screen_on = True

def load_local_images():
    local_images = [f for f in os.listdir(SD_PATH) if f.endswith(".bmp")]
    return local_images

def update_images():
    global failed_image_check

    image_urls = fetch_image_data()

    if len(image_urls) == 0:
        failed_image_check += 1
    else:
        failed_image_check = 0

    if failed_image_check >= IMAGE_CHECK_FAILURE_THRESHOLD:
        raise ValueError(f"{time.monotonic()} :: No images to show despite multiple attempts")

    current_image_paths = [download_image(img) for img in image_urls]
    clean_up_images(current_image_paths)

    return current_image_paths

images = load_local_images() # Load local file system to start

if len(images) > 0:
    print(f"{time.monotonic()} :: There are %d images to show" % len(images))
    for image in images:
        print(f"{time.monotonic()} :: {image}")
else:
    print(f"{time.monotonic()} :: There are no images on device to show")

# Main execution loop
while True:
    if first_run:
        images = update_images()
        first_run = False
    
    current_time = time.monotonic()

    if screen_on:
        if len(images) > 0:
            main_loop()
        else:
            try:
                images = update_images()
            except ValueError as e:
                print(f"{time.monotonic()} :: Error occurred while updating images (Loc 1): {e}")
    else:
        if current_time - last_refresh_time >= refresh_interval:
            last_refresh_time = current_time
            print(f"{time.monotonic()} :: Refreshing image list from API...")
            try:
                images = update_images()
            except ValueError as e:
                print(f"{time.monotonic()} :: Error occurred while updating images (Loc 2): {e}")
        else:
            handle_touch()
            time.sleep(0.1)  # Small delay to reduce CPU usage