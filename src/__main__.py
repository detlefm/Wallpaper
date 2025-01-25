import os
import requests
from datetime import datetime
from xml.etree import ElementTree as ET
import ctypes
from pathlib import Path

# Bing Wallpapers
# Fetch the Bing wallpaper image of the day
# <https://github.com/timothymctim/Bing-wallpapers>
#
# Copyright (c) 2015 Tim van de Kamp
# License: MIT license
# Translated 2025 to python by DeepSeek 

def get_screen_resolution():
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)

    if width <= 1024:
        return "1024x768"
    elif width <= 1280:
        return "1280x720"
    elif width <= 1366:
        return "1366x768"
    elif height <= 1080:
        return "1920x1080"
    else:
        return "1920x1200"


def download_bing_wallpapers(
    locale="auto", files=0, resolution="auto", download_folder=None
):
    if download_folder is None:
        download_folder = os.path.join(
            os.path.expanduser("~"), "Pictures", "Wallpapers"
        )

    # Max item count: the number of images we'll query for
    max_item_count = max(1, max(files, 8))

    # URI to fetch the image locations from
    if locale == "auto":
        market = ""
    else:
        market = f"&mkt={locale}"

    hostname = "https://www.bing.com"
    uri = f"{hostname}/HPImageArchive.aspx?format=xml&idx=0&n={max_item_count}{market}"

    # Get the appropriate screen resolution
    if resolution == "auto":
        resolution = get_screen_resolution()

    # Check if download folder exists and otherwise create it
    Path(download_folder).mkdir(parents=True, exist_ok=True)

    # Fetch the XML content
    response = requests.get(uri)
    content = ET.fromstring(response.content)

    items = []
    for xml_image in content.findall("image"):
        image_date = datetime.strptime(xml_image.find("startdate").text, "%Y%m%d")
        image_url = f"{hostname}{xml_image.find('urlBase').text}_{resolution}.jpg"

        # Add item to our list
        items.append({"date": image_date, "url": image_url})

    # Keep only the most recent $files items to download
    if files != 0 and len(items) > files:
        items.sort(key=lambda x: x["date"])
        items = items[-files:]


    count = 0
    for item in items:
        base_name = item["date"].strftime("%Y-%m-%d")
        destination = os.path.join(download_folder, f"{base_name}.jpg")
        url = item["url"]

        # Download the image if we haven't done so already
        if not os.path.exists(destination):
            print(f"Downloading image to {destination}")
            response = requests.get(url)
            with open(destination, "wb") as f:
                f.write(response.content)
            count +=1
    return count

    # if files > 0:
    #     # We do not want to keep every file; remove the old ones
    #     print("Cleaning the directory...")
    #     files_in_folder = sorted(Path(download_folder).glob("????-??-??.jpg"), key=os.path.getmtime, reverse=True)
    #     for i, file_path in enumerate(files_in_folder):
    #         if i >= files:
    #             print(f"Removing file {file_path}")
    #             os.remove(file_path)


# Example usage:
# download_bing_wallpapers(locale='en-US', files=5, resolution='1920x1080')

if __name__ == "__main__":
    print("Downloading images... ",end='',flush=True)    
    print(f'found {download_bing_wallpapers()} images')
