import os
import datetime
import json
import random
import httpx
from PIL import Image, ImageFont, ImageDraw


class ImageBuildError(Exception):
    pass


with open("config.json") as config:
    cdata = json.loads(config.read())
    WEATHER_LAT = cdata["weather"]["latitude"]
    WEATHER_LONG = cdata["weather"]["longitude"]
    PHOTO_ROOT = cdata["photos"]["root"]


def weather():
    base = "https://api.weather.gov"
    payload = httpx.get(f"{base}/points/{WEATHER_LAT},{WEATHER_LONG}")

    blob = json.loads(payload.text)

    forecast = blob["properties"]["forecast"]

    print(forecast)
    payload = httpx.get(forecast)
    forecast = blob["properties"]["observationStations"]
    print(forecast)
    payload = httpx.get(forecast)

    print(payload.text)

    pass


def crop_to(im, width, height):
    # target x & y
    t_x, t_y = width, height
    # photo x & y
    p_x, p_y = im.size

    # compute "new" x & y
    if t_x / p_x > t_y / p_y:
        # photo is taller than target aspect ratio
        n_x = p_x
        n_y = int(n_x * t_y / t_x)
    else:
        # photo is wider than target aspect ratio
        n_y = p_y
        n_x = int(n_y * t_x / t_y)

    # half x & y
    h_x, h_y = p_x / 2, p_y / 2
    i_x, i_y = n_x / 2, n_y / 2

    left, upper, right, lower = h_x - i_x, h_y - i_y, h_x + i_x, h_y + i_y

    return im.crop((left, upper, right, lower))


def dated(im):
    edit = ImageDraw.Draw(im)

    font_ratio = 0.09
    epsilon = 0.005
    target = im.size[1] * font_ratio

    height = None
    points = 200
    for i in range(3):
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/lato/Lato-Heavy.ttf", points
        )

        _, height = font.getsize("0")
        if abs(height / im.size[1] - font_ratio) < epsilon:
            break
        else:
            points = int(points / (height / target))
            print(f"Retrying with points {points}")

    date = datetime.datetime.now()
    line1 = f"{date:%I:%M %p}".strip("0")
    line2 = f"{date:%B} {date.day}"
    line3 = "aslkdf"

    p_x, p_y = im.size

    for index, line in enumerate([line1, line2, line3]):
        width, _ = font.getsize(line)
        edit.text(
            (p_x - 15 - width, p_y - height * 1.1 * ((3 - index) + 0.5)),
            line,
            (0, 0, 0),
            font,
        )

    return im


def image(fn, width=300, height=500):
    with Image.open(fn) as im:
        i_x, i_y = im.size
        if i_x < width / 3:
            raise ImageBuildError("width is too small")
        if i_y < height / 3:
            raise ImageBuildError("height is too small")

        im = crop_to(im, width=width, height=height)

        im = dated(im)

        im.save("output.jpg")

        # os.system("xdg-open output.jpg")


# weather()


def get_files(root):
    for root, dirs, files in os.walk(root):
        for name in files:
            if name.lower().endswith(".jpg"):
                yield os.path.join(root, name)


photos = list(get_files(PHOTO_ROOT))

ph = random.choice(photos)

# image(ph)
