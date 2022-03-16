import pandas as pd
import datetime
import json
import logging

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

log = logging.getLogger(__name__)

# Store log to file with date in name
logging.basicConfig(
    filename="logs/scraping_mmsi_from_ocean_data_{}.log".format(
        datetime.datetime.now().strftime("%Y-%m-%d")
    ),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

credentials = {}

with open("credentials.json") as json_file:
    credentials = json.load(json_file)

download_folder = (
    "/Users/oysteinlondalnilsen/Documents/GitHub/TDT4861/data/vessel_mmsi_data"
)
time_out = 120

ship_passages_dataset = pd.read_excel("data/ship-passages-trondheim-fjord.xlsx")
# Remove duplicate MMSI rows
ship_passages_dataset.drop_duplicates(subset=["MMSI#"], inplace=True)

chrome_options = webdriver.ChromeOptions()
prefs = {"download.default_directory": download_folder}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get("https://vessel-emissions.prod.oceandata.xyz")

# LOGIN

username = WebDriverWait(driver, time_out).until(
    EC.presence_of_element_located((By.ID, "signInName"))
)
password = WebDriverWait(driver, time_out).until(
    EC.presence_of_element_located((By.ID, "password"))
)

# driver.find_element_by_id("signInName")
# password = driver.find_element_by_id("password")

username.send_keys(credentials["username"])
password.send_keys(credentials["password"])

driver.find_element_by_id("next").click()

for _, row in ship_passages_dataset["MMSI#"].iteritems():

    try:

        mmsi = str(row)

        # SELECT VESSEL

        select_vessel = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@aria-label='Selected EVER GIVEN | 353136000. ']")
            )
        )

        select_vessel.send_keys(mmsi)
        select_vessel.send_keys(Keys.ENTER)

        # PREPARE DATA

        download_btn = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Download vessel data')]")
            )
        )
        download_btn.click()

        # DOWNLOAD CSV FILE

        csv_button = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@type='button' and @value='Download CSV File']")
            )
        )
        csv_button.click()

        log.info(f"Scraped MMSI: {mmsi} successfully")

    except TimeoutException:
        log.error(f"Scraping MMSI: {mmsi} timed out")

    except Exception as e:
        log.error(f"Scraping MMSI: {mmsi} failed with error: {e}")  # Log error

    finally:
        # REFRESH WEB PAGE
        driver.refresh()

# CLOSE WEBDRIVER

driver.quit()
