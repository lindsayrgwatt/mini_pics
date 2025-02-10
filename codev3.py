import time
import board
import json
import displayio
import os
import adafruit_touchscreen
import neopixel

from adafruit_pyportal import PyPortal

# Load secrets (Wi-Fi credentials & API key)
try:
    from secrets import secrets
except ImportError:
    print("Secrets file missing! Create secrets.py with Wi-Fi credentials and API key.")
    while True:
        pass

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)  # 1 pixel on PyPortal
pixel.brightness = 0.5  # Set the brightness level (0.0 to 1.0)

# API URL
BASE_URL = "http://www.lindsayrgwatt.com/api/device-images/random/2/"
API_KEY = secrets["api_key"]
API_URL = f"{BASE_URL}{API_KEY}/"

# Initialize PyPortal (handles Wi-Fi and HTTP requests)
pyportal = PyPortal(url=API_URL)

display = board.DISPLAY
display.rotation = 270  # Portrait mode

# Screen dimensions (for the touchscreen calibration)
screen_width = display.width
screen_height = display.height

# Initialize touch input
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(screen_width, screen_height))

# Track screen state
screen_on = True  # Start with the screen ON
black_image = "/sd/black.bmp"
pyportal.set_background(black_image)

# Function to turn off display
def turn_off_screen():
    global screen_on
    screen_on = False
    print("Screen off")
    pyportal.display.brightness = 0  # Set brightness to 0 to simulate turning off

# Function to turn on display
def turn_on_screen():
    # Display a black image immediately before fetching a new one
    pyportal.set_background(black_image)

    global screen_on
    screen_on = True
    print("Screen on")
    pyportal.display.brightness = 1  # Restore brightness

    # Fetch a new image
    return update_display()

# Function to download and save an image locally
def download_image(image_url, filename="/sd/background.bmp"):
    try:
        pyportal.wget(image_url, filename)

        print(f"Image saved as {filename}")
        return filename
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

# Function to fetch and display image
def update_display():
    #try:
        print(f"Fetching image data from {API_URL}...")

        # Fetch raw JSON response first
        response = pyportal.fetch()  # Get the full response
        print("Full API Response:", response)  # Debugging

        data = json.loads(response)
        # Extract fields safely
        display_time = data.get("display_time", 5)
        image_url = data.get("image", None)

        print(f"Display Time: {display_time} seconds")
        print(f"Image URL: {image_url}")

        if image_url:
            # Download and save the image locally
            local_filename = download_image(image_url)

            if local_filename:
                print("Displaying image...")
                pyportal.set_background(local_filename)

        return display_time * 60
    #except Exception as e:
    #    print(f"Error fetching or displaying image: {e}")
        return 5 * 60  # Default wait time if error occurs

# Main loop
next_update = time.monotonic()  # Track the next update time
delay = None  # Initial image fetch

while True:
    # Check for touch input
    touch = ts.touch_point
    if touch:
        # Blink NeoPixel to show that touch registered
        pixel.fill((0, 255, 0))  # Green color
        time.sleep(0.1)  # Keep the NeoPixel on for 0.1 seconds
        pixel.fill((0, 0, 0))  # Turn off NeoPixel
 
        print("touch")
        time.sleep(0.2)  # Debounce
        if screen_on:
            print("turn off screen")
            turn_off_screen()
        else:
            print("turn on screen")
            delay = turn_on_screen()  # Fetch a new image

    # If screen is on and it's time to fetch a new image
    if screen_on and time.monotonic() >= next_update:
        delay = update_display()
        next_update = time.monotonic() + delay  # Schedule next update

    # Avoid busy-waiting
    time.sleep(0.1)