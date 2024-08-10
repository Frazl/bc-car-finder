from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
import json

LOGGER = logging.getLogger()
LOGGER.setLevel("DEBUG")


# Base links are all links with full search parameters set, ordered by most recent.
base_links = [
    # Honda CRV
    'https://www.autotrader.ca/cars/honda/cr-v/bc/?rcp=100&rcs=0&srt=9&pRng=5000%2C20000&prx=-2&prv=British%20Columbia&loc=BC&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch',
    # Rav 4 
    'https://www.autotrader.ca/cars/toyota/rav4/bc/?rcp=100&rcs=0&srt=9&pRng=5000%2C20000&prx=-2&prv=British%20Columbia&loc=BC&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch',
    # Mazda CX5 | Trim -> GT 
    'https://www.autotrader.ca/cars/mazda/cx-5/bc/?rcp=100&rcs=0&srt=9&trim=GT&pRng=5000%2C20000&prx=-2&prv=British%20Columbia&loc=BC&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch',
]

MAX_DAMAGE = 10_000
MAX_INDIVIDUAL_DAMAGE = 3_000

def main():
    LOGGER.info(msg="Starting the script")
    driver = webdriver.Chrome()
    for base_link in base_links:
         driver.get(base_link)
         car_links = get_cars(driver)
         car_links = filter_seen_previous(car_links)
         for car_link in car_links:
             driver.get(car_link)
             car_info = get_car_info(driver)
             input('Waiting...')
             exit()
             

def get_cars(driver):
    link_elements = driver.find_elements(By.CLASS_NAME, 'inner-link')
    links = [link_element.get_attribute('href') for link_element in link_elements]
    LOGGER.debug(msg="Found " + str(len(links)) + " links")
    return links

def get_car_info(driver):
    return {}


def get_id_from_link(link):
    return link.split("/")[-2]


def filter_seen_previous(car_links):
    previous = set()
    with open('previous_seen.json', 'r') as fp:
        previous = json.load(fp)
        previous = set(previous)
    ids = [get_id_from_link(car_link) for car_link in car_links]
    car_links = [id for id in ids if id not in previous]
    LOGGER.info(f'Previously seen ${len(ids) - len(car_links)} cars, which will be skipped')
    return car_links

def get_carfax(driver):
    # ...
    pass 
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