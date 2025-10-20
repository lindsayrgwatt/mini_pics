import time
import board
import json
import adafruit_touchscreen
import neopixel
import gc
import microcontroller
from adafruit_pyportal import PyPortal

# ---- Load Secrets ----
try:
    from secrets import secrets
except ImportError:
    print("Secrets file missing! Create secrets.py with Wi-Fi credentials and API key.")
    while True:
        pass

# ---- Configuration ----
BASE_URL = "http://www.lindsayrgwatt.com/api/device-images/random/2/"
API_KEY = secrets["api_key"]
API_URL = f"{BASE_URL}{API_KEY}/"
BLACK_IMAGE = "/sd/black.bmp"

# ---- Hardware Setup ----
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.5

pyportal = PyPortal(url=API_URL)
display = board.DISPLAY
display.rotation = 270  # portrait

screen_width = display.width
screen_height = display.height

ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL, board.TOUCH_XR,
    board.TOUCH_YD, board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)),
    size=(screen_width, screen_height),
)

# ---- State ----
screen_on = True  # start with screen on
pyportal.set_background(BLACK_IMAGE)


# ---- Error Handling ----
def handle_socket_error(e):
    """Hard reset the whole board on socket failure."""
    print("Socket or timeout error detected:", e)
    pixel.fill((255, 0, 0))   # red flash before reset
    time.sleep(0.5)
    pixel.fill((0, 0, 0))
    print("Performing full microcontroller reset...")
    microcontroller.reset()


# ---- Network Fetch Helpers ----
def fetch_json():
    """Fetch JSON using pyportal.fetch(); reset on socket errors."""
    try:
        gc.collect()
        print(f"Fetching JSON from {API_URL}")
        response_text = pyportal.fetch()
        gc.collect()
        return json.loads(response_text)
    except Exception as e:
        if any(x in str(e).lower() for x in ("socket", "already connected", "timeout", "etimedout")):
            handle_socket_error(e)
        else:
            print("Fetch error:", e)
        return None


def download_image(image_url, filename="/sd/background.bmp"):
    """Download an image via wget; reset on socket errors."""
    print(f"Downloading image: {image_url}")
    try:
        pyportal.wget(image_url, filename)
        print(f"Image saved as {filename}")
        gc.collect()
        return filename
    except Exception as e:
        if any(x in str(e).lower() for x in ("socket", "already connected", "timeout", "etimedout")):
            handle_socket_error(e)
        else:
            print("Image download error:", e)
        return None


# ---- Display Logic ----
def update_display():
    """Fetch image metadata, download and display it."""
    print("Started update_display")

    data = fetch_json()
    if not data:
        print("Fetch failed; retrying later.")
        return 5 * 60  # retry after 5 minutes

    display_time = data.get("display_time", 5)
    image_url = data.get("image")

    print(f"Display Time: {display_time}s")
    print(f"Image URL: {image_url}")

    if image_url:
        local_filename = download_image(image_url)
        if local_filename:
            pyportal.set_background(local_filename)
            gc.collect()
            pixel.fill((0, 64, 255))  # blue flash to confirm success
            time.sleep(0.2)
            pixel.fill((0, 0, 0))

    return display_time * 60


# ---- Screen Control ----
def turn_off_screen():
    global screen_on
    screen_on = False
    print("Turning OFF screen")
    display.brightness = 0
    pyportal.set_background(BLACK_IMAGE)


def turn_on_screen():
    global screen_on
    screen_on = True
    print("Turning ON screen")
    display.brightness = 1.0
    return update_display()


# ---- Main Logic ----
print("PyPortal image display starting...")
display.brightness = 1.0
delay = update_display()  # fetch and display on boot
next_update = time.monotonic() + delay

while True:
    # Handle touch toggle
    touch = ts.touch_point
    if touch:
        pixel.fill((0, 255, 0))
        time.sleep(0.1)
        pixel.fill((0, 0, 0))
        print("Touch detected — toggling screen")
        time.sleep(0.2)
        if screen_on:
            turn_off_screen()
        else:
            delay = turn_on_screen()
            next_update = time.monotonic() + delay

    # Periodic update
    if screen_on and time.monotonic() >= next_update:
        delay = update_display()
        next_update = time.monotonic() + delay

    time.sleep(0.1)