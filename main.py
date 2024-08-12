from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
import json
from time import sleep
import sys
import traceback

LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)


# Base links are all links with full search parameters set, ordered by most recent.
base_links = [
    # Honda CRV
    'https://www.autotrader.ca/cars/honda/cr-v/bc/?rcp=100&rcs=0&srt=9&pRng=5000%2C20000&prx=-2&prv=British%20Columbia&loc=BC&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch',
    # Rav 4 
    'https://www.autotrader.ca/cars/toyota/rav4/bc/?rcp=100&rcs=0&srt=9&pRng=5000%2C20000&prx=-2&prv=British%20Columbia&loc=BC&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch',
    # Mazda CX5 | Trim -> GT 
    'https://www.autotrader.ca/cars/mazda/cx-5/bc/?rcp=100&rcs=0&srt=9&trim=GT&pRng=5000%2C20000&prx=-2&prv=British%20Columbia&loc=BC&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch',
]

MAX_DAMAGE = 15_000
MAX_INDIVIDUAL_DAMAGE = 5_000
global EMAIL
EMAIL = None

def main():
    LOGGER.info(msg="Starting the script")
    car_infos = []
    with open('car_infos.json', 'r') as fp:
        car_infos = json.load(fp)
    try:
        driver = webdriver.Chrome()
        # Setup mail 
        driver.get('https://internxt.com/temporary-email')
        global EMAIL
        EMAIL = driver.find_element(By.CLASS_NAME, 'border-gray-20').text
        LOGGER.info("Using the following email - " + EMAIL)
        driver.switch_to.new_window('tab')
        for base_link in base_links:
            driver.get(base_link)
            car_links = get_cars(driver)
            car_links = filter_seen_previous(car_infos, car_links)
            for car_link in car_links:
                print(car_link)
                driver.get(car_link)
                car_info = get_car_info(driver)
                car_info['link'] = car_link
                car_infos.append(car_info)
    except Exception as e:
        traceback.print_exc() 
    finally:
        with open('car_infos.json', 'w') as fp:
            json.dump(car_infos, fp)

def debug_listing(driver):
    driver.get('https://www.autotrader.ca/a/honda/cr-v/calgary/alberta/5_63381675_20190916130550228/?showcpo=ShowCpo&ncse=no&orup=1_15_0&sprx=-2')
    info = get_car_info(driver)
    print(info)

def get_cars(driver):
    link_elements = driver.find_elements(By.CLASS_NAME, 'inner-link')
    links = [link_element.get_attribute('href') for link_element in link_elements]
    LOGGER.debug(msg="Found " + str(len(links)) + " links")
    return links

def get_car_info(driver):
    info_template = {
        'price': '',
        'odometer': '',
        'location': '',
        'carfax': '',
        'title': '',
        'description': '',
    }
    sleep(2.5)
    info_template['title'] = driver.find_element(By.CLASS_NAME, 'hero-title').text
    info_template['price'] = driver.find_element(By.CLASS_NAME, 'hero-price').text
    hero_location = driver.find_element(By.CLASS_NAME, 'hero-location').text.split("|")
    info_template['location'] = hero_location[1].strip()
    info_template['odometer'] = hero_location[0].strip()
    info_template['description'] = driver.find_element(By.XPATH, '//*[@id="descriptionWidget"]/div/div/div[1]/collapsible-container').text

    sleep(2.5)
    maybe_carfax_element = driver.find_element(By.CLASS_NAME, 'carfax-link')
    info_template['carfax'] = handle_carfax_element(maybe_carfax_element, info_template, driver)
    sleep(2.5)

    return info_template

def get_id_from_link(link):
    return link.split("/")[-2]

def handle_carfax_element(maybe_carfax_element, car_info, driver):
    if maybe_carfax_element:
        LOGGER.info('Found carfax element, car has some form of report')
        carfax_text = maybe_carfax_element.text
        if 'Request' in carfax_text:
            global EMAIL
            # Handle email report scenario 
            maybe_carfax_element.click()
            sleep(2)
            input = driver.find_element(By.ID, 'name')
            input.clear()
            input.send_keys(EMAIL)
            input = driver.find_element(By.ID, 'email')
            input.clear()
            input.send_keys(EMAIL)
            driver.find_element(By.CLASS_NAME, 'submit-email').click()
            sleep(3)
            driver.find_element(By.CLASS_NAME, 'carfax-confirmation-button').click()
            # Todo 
            driver.switch_to.window(driver.window_handles[0])
            sleep(15)
            driver.find_elements(By.XPATH, "//*/div[@id='inbox']//button")[0].click()
            sleep(5)
            maybe_emails = driver.find_elements(By.XPATH, "//*/div[@id='inbox']//button")[1:-1]
            for maybe_email in maybe_emails:
                if 'History Report' in maybe_email.text:
                    maybe_email.click()
                    break
            sleep(5)
            carfax =  str(driver.find_element(By.XPATH, "//a[text()='View report']").get_attribute('href'))
            driver.switch_to.window(driver.window_handles[1])
            return carfax
        if 'Buy' in carfax_text:
            LOGGER.info('Skipping carfax as its purchase only')
            return 'Buy'
        else:
            # Free? 
            return maybe_carfax_element.get_attribute('href')

def filter_seen_previous(car_infos, car_links):
    previously_seen = set()
    for car in car_infos:
        previously_seen.add(get_id_from_link(car['link']))
    car_links = [car_link for car_link in car_links if get_id_from_link(car_link) not in previously_seen]
    LOGGER.info(f'Previously seen ${len(car_infos) - len(car_links)} cars, which will be skipped')
    return car_links

def get_carfax(driver):
    # ...
    pass 
    # Swap to email window 
    # Refresh
    # Click the first entry
    text = driver.find_element(By.ID, 'vhrBody').text
    text = text.replace("\\n", "")
    text = text.replace("\n", "")
    text = text.replace("\\t", "")
    text = text.replace("\t", "")
    text = text.replace("   ", "")
    text = text.replace("   ", "")
    text = text.replace("   ", "")
    ai_summary = ai_summarize(text)

def ai_summarize(car_fax):
    # ChatGPT method to summarize tables on carfax.
    # Ensures damage does not exceed set amount total or individual damage.
    pass 

def save_to_sheet(car, ai_summary):
    pass

if __name__ == '__main__':
    main()