import os
import threading
import time
from threading import Thread

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from twocaptcha import TwoCaptcha
from webdriver_manager.chrome import ChromeDriverManager

from custom_logging import setup_logger

from dotenv import load_dotenv

load_dotenv(".env")

logger = setup_logger('bukalapak info logger', 'logs/bukalapak_spider.log')

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'

chrome_options = Options()
# chrome_options.add_argument("--headless=new")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument(f'user-agent={USER_AGENT}')

ZYTE_APIKEY = os.environ.get("ZYTE_APIKEY")
ZYTE_PROXY_URL = f"http://{ZYTE_APIKEY}:@api.zyte.com:8011/"
# ZYTE_PROXY_URL = f"http://{ZYTE_APIKEY}:@proxy.crawlera.com:8011/"

# seleniumwire_options = {
#     "proxy": {"http": ZYTE_PROXY_URL, "https": ZYTE_PROXY_URL, "no_proxy": ""}
# }
seleniumwire_options = {}


class BrowserThread(Thread):
    def __init__(self, link, tabs):
        super(BrowserThread, self).__init__()
        self.driver = webdriver.Chrome(seleniumwire_options=seleniumwire_options, options=chrome_options)
        self.link = link
        self.tabs = tabs

    def run(self):
        try:
            self.open_link_in_tabs(self.link)
        except Exception as e:
            logger.error(f"Error occurred while processing link: {self.link} - {e}")

    def open_link_in_tabs(self, link):
        try:
            logger.info(f"Opening link in multiple tabs: {link}")
            print(f"Opening link in multiple tabs: {link}")
            self.driver.get(link)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "c-bl-media__image")))
            for _ in range(self.tabs):  # Open specified tabs
                self.driver.execute_script(f"window.open('{link}');")
            time.sleep(15)  # Adjust the sleep time as needed
            # Wait until all tabs are loaded
            WebDriverWait(self.driver, 2*self.tabs).until(EC.number_of_windows_to_be((self.tabs)+1))  # Assuming the original window is included
            # Close all tabs except the original window
            original_window = self.driver.window_handles[0]
            for window in self.driver.window_handles[1:]:
                self.driver.switch_to.window(window)
                self.driver.close()
            # Switch back to the original window
            self.driver.switch_to.window(original_window)
            logger.info(f"All tabs for link {link} have been closed.")
        except Exception as e:
            print("Error occurred ::; ", e)

class bukalapakSpider:
    def __init__(self, product_keywords, browser_tabs):
        self.keywords = product_keywords
        self.browser_tabs = browser_tabs
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       seleniumwire_options=seleniumwire_options, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 5)

    def scroll_to_bottom(self, prev_height = -1, scroll_count=0, max_scrolls=10):
        # Scroll to the bottom of the page to load more elements
        while scroll_count < max_scrolls:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == prev_height:
                break
            prev_height = new_height
            scroll_count += 1

    def extract_links(self):
        ADS_LINK_SELECTOR_PATH = "//div[contains(@class, 'te-product-card') and .//img[contains(@class, 'bl-product-card-new__ads-badge')]]"
        product_ads_links = self.driver.find_elements(By.XPATH, ADS_LINK_SELECTOR_PATH)

        links = []
        PRODUCT_SELECTOR_PATH = ".//p[contains(@class, 'bl-text--ellipsis__2')]/a"
        for product_ad in product_ads_links:
            link = product_ad.find_element(By.XPATH, PRODUCT_SELECTOR_PATH).get_attribute("href")
            links.append(link)
        return links

    def start_scraping(self):
        BASE_URL = "https://www.bukalapak.com/products?search[keywords]={}"
        for keyword in self.keywords:
            try:
                url = BASE_URL.format(keyword)
                self.driver.get(url)
                logger.info(f"[STARTING] ### Keyword: {keyword} ### {url}")
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'te-product-card')]")))
                self.scroll_to_bottom()
                links = self.extract_links()
                for link in links:
                    print("link ::: ", link)
                    thread = BrowserThread(link, self.browser_tabs)
                    thread.start()
                # # Wait for all threads to complete before quitting the driver
                # for thread in threading.enumerate():
                #     if thread != threading.main_thread():
                #         thread.join()
                self.driver.quit()
            except Exception as e:
                print(f"ERROR OCCURRED ::: {e}")

    def close(self):
        self.driver.quit()


keywords = input("Enter keywords seperated by commas: ").strip().split(",")
tabs = int(input("Enter the total tabs of browser to open links : "))
# Usage
spider = bukalapakSpider(keywords, tabs)
spider.start_scraping()
spider.close()