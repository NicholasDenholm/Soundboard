from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
import requests
import os
from pathlib import Path
from path_making import get_script_directory, make_dir_path, find_geckodriver

def setup_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    
    script_path = get_script_directory()
    dir_path = make_dir_path("drivers", script_path)
    full_path = find_geckodriver(dir_path)
    
    if not full_path:
        raise FileNotFoundError("GeckoDriver not found in: " + dir_path)
    
    # Create a Firefox Service with the path to the GeckoDriver
    service = Service(executable_path=full_path)
    
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def search_sound(driver, query):
    driver.get("https://www.myinstants.com")
    time.sleep(2)
    
    # Locate the search bar and search for the sound
    search_box = driver.find_element(By.NAME, "name")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

def get_home_page_sounds(driver):
    driver.get("https://www.myinstants.com")
    time.sleep(2)
    return get_all_sounds(driver)

# YES THIS IS IT
def print_sound_names_and_urls(driver, element:str):
    instant_divs = driver.find_elements(By.CLASS_NAME, element)
    
    print(f"Found {len(instant_divs)} instant divs. Extracting sounds...\n")
    
    for div in instant_divs:
        try:
            button = div.find_element(By.CSS_SELECTOR, "button.small-button")
            onclick = button.get_attribute("onclick")
            
            # Extract URL from play('URL', ...)
            mp3_path = onclick.split("'")[1]
            full_url = f"https://www.myinstants.com{mp3_path}"
            
            # Get sound name from sibling <a class="instant-link">
            link = div.find_element(By.CSS_SELECTOR, "a.instant-link")
            sound_name = link.text.strip()
            
            print(f"Name: {sound_name}\nURL: {full_url}\n")
        except Exception as e:
            print(f"Error processing one sound: {e}")
            continue

def get_all_sounds(driver):
    sounds = []
    instant_divs = driver.find_elements(By.CLASS_NAME, "instant")

    for div in instant_divs:
        try:
            button = div.find_element(By.CSS_SELECTOR, "button.small-button")
            onclick = button.get_attribute("onclick")
            mp3_path = onclick.split("'")[1]
            full_url = f"https://www.myinstants.com{mp3_path}"

            link = div.find_element(By.CSS_SELECTOR, "a.instant-link")
            sound_name = link.text.strip()

            sounds.append((sound_name, full_url))
        except Exception as e:
            print(f"Error extracting sound info: {e}")
            continue

    return sounds
# ------------------------- Download Sounds ------------------------- #

def download_first_sound(driver, save_folder="sounds"):
    try:
        # Wait for at least one instant container to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "instant"))
        )
    except:
        print("No sound buttons loaded within timeout.")
        return

    instant_divs = driver.find_elements(By.CLASS_NAME, "instant")
    if not instant_divs:
        print("No sound buttons found after waiting.")
        return

    first_div = instant_divs[0]
    try:
        button = first_div.find_element(By.CSS_SELECTOR, "button.small-button")
        onclick = button.get_attribute("onclick")
        mp3_path = onclick.split("'")[1]
    except Exception as e:
        print(f"Failed to extract sound URL: {e}")
        return

    full_url = f"https://www.myinstants.com{mp3_path}"
    filename = full_url.split("/")[-1]

    # Setup save folder path relative to this script
    script_dir = Path(__file__).resolve().parent
    save_path = script_dir / save_folder
    save_path.mkdir(parents=True, exist_ok=True)

    # Download the mp3 file
    try:
        response = requests.get(full_url)
        response.raise_for_status()  # Raise HTTPError for bad responses
    except Exception as e:
        print(f"Failed to download file: {e}")
        return

    # Save the file
    destination = save_path / filename
    with open(destination, 'wb') as f:
        f.write(response.content)

    print(f"Downloaded: {filename} to {destination}")


def download_first_sound_first(driver, save_folder="downloads"):
    # Find the first button
    buttons = driver.find_elements(By.CLASS_NAME, "instant-play")
    if not buttons:
        print("No sound buttons found.")
        return
    
    sound_button = buttons[0]
    sound_url = sound_button.get_attribute("onmousedown").split("'")[1]  # Extract partial URL
    full_url = f"https://www.myinstants.com{sound_url}"

    # Extract file name
    filename = full_url.split("/")[-1]

    # Create folder if not exists
    os.makedirs(save_folder, exist_ok=True)

    # Download the mp3
    response = requests.get(full_url)
    with open(os.path.join(save_folder, filename), 'wb') as f:
        f.write(response.content)
    
    print(f"Downloaded: {filename} to {save_folder}/")


# ------------------------- Main ------------------------- # 

def main():
    driver = setup_driver(headless=False)
    
    
    try: 
        script_path = get_script_directory()
        dir_path = make_dir_path(script_path, "sounds")
        
        sounds = get_home_page_sounds(driver)
        for name, url in sounds:
            try:
                print(f"Searching for: {name}")
                search_sound(driver, name) # Searches for the sound
                download_first_sound(driver, dir_path)

                driver.get("https://www.myinstants.com") # Goes back to home page
            except Exception as e:
                print(f"❌ Failed on '{name}': {e}")
                continue
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
