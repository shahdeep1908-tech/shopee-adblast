import os

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
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
# ZYTE_PROXY_URL = f"http://{ZYTE_APIKEY}:@api.zyte.com:8011/"
ZYTE_PROXY_URL = f"http://{ZYTE_APIKEY}:@proxy.crawlera.com:8011/"

seleniumwire_options = {
    "proxy": {"http": ZYTE_PROXY_URL, "https": ZYTE_PROXY_URL, "no_proxy": ""}
}
# seleniumwire_options = {}


class bukalapakSpider:
    def __init__(self, product_keyword, store_name):
        self.keyword = product_keyword
        self.store = store_name
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
        product_ad_link = None
        PRODUCT_SELECTOR_PATH = ".//p[contains(@class, 'bl-text--ellipsis__2')]/a"
        STORE_SELECTOR_PATH = ".//p[contains(@class, 'bl-product-card-new__store-name')]//a"
        for product_ad in product_ads_links:
            store_name_element = product_ad.find_element(By.XPATH, STORE_SELECTOR_PATH)
            store_name_txt = store_name_element.get_attribute('innerHTML').strip().replace('\n', '')
            if store_name_txt.upper().replace(" ", "") == self.store.upper().strip().replace(" ", ""):
                product_ad_link = product_ad.find_element(By.XPATH, PRODUCT_SELECTOR_PATH).get_attribute("href")
                print("product_ad ::: ", product_ad_link)
                print("store_name_txt ::: ", store_name_txt)
                break
        if product_ad_link:
            self.driver.get(product_ad_link)
            self.scroll_to_bottom()
        return product_ad_link

    def start_scraping(self):
        BASE_URL = "https://www.bukalapak.com/products?search[keywords]={}"
        try:
            url = BASE_URL.format(self.keyword)
            self.driver.get(url)
            logger.info(f"[STARTING] ### {url}")
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@class, '-hint')]")))
            self.scroll_to_bottom()
            while True:
                link = self.extract_links()
                if not link:
                    break
                self.driver.back()
            self.driver.quit()
            logger.info(f"[FINISHED] ::: {self.keyword} ### AdBlast ")
        except Exception as e:
            print(f"ERROR OCCURRED ::: {e}")

    def close(self):
        self.driver.quit()


keywords = input("Enter keywords: ").strip()
store_name = input("Enter Store Name: ").strip()

# Usage
spider = bukalapakSpider(keywords, store_name)
spider.start_scraping()
spider.close()