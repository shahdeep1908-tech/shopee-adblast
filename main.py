import datetime
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from custom_logging import setup_logger

from dotenv import load_dotenv

load_dotenv(".env")

logger = setup_logger('shopee info logger', 'logs/shopee_spider.log')

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

ZYTE_APIKEY = os.environ.get("ZYTE_APIKEY")
ZYTE_PROXY_URL = f"http://{ZYTE_APIKEY}:@proxy.crawlera.com:8011/"

# Set up Chrome WebDriver with Zyte Smart Proxy
chrome_options.add_argument(f"--proxy-server={ZYTE_PROXY_URL}")


class shopeeSpider:
    def __init__(self, product_keywords, start_page=1, end_page=5):
        # self.start_page = int(start_page)
        # self.end_page = int(end_page)
        self.keywords = product_keywords
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        # Wait until the main content is loaded
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DYKctS")))
        # Add login logic here
        email_input = self.driver.find_element(By.NAME, "loginKey")
        password_input = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CLASS_NAME, "DYKctS")
        print(email_input, password_input, login_button)

        # Add your email and password
        EMAIL = os.environ.get("SHOPEE_EMAIL")
        PASSWORD = os.environ.get("SHOPEE_PASSWORD")
        email_input.send_keys(EMAIL)
        password_input.send_keys(PASSWORD)

        login_button.click()

    def scroll_to_bottom(self):
        # Scroll to the bottom of the page to load more elements
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-sqe='item']")))

    def extract_links(self):
        # Find <li> tags containing the specified class and "Ad" text
        ADS_LINK_SELECTOR_PATH = "//li[contains(@class, 'shopee-search-item-result__item') and .//div[contains(@class, '_1gAOYL') and text()='Ad']]"
        product_ads_links = self.driver.find_elements(By.XPATH, ADS_LINK_SELECTOR_PATH)

        for li in product_ads_links:
            # Extract the href attribute from the <a> tag within the <li>
            link = li.find_element(By.TAG_NAME, "a").get_attribute("href")
            logger.info(f"Original Link: {link}")


    def start_scraping(self):
        BASE_URL = "https://shopee.co.id/search?keyword={}"
        for keyword in self.keywords:
            try:
                url = BASE_URL.format(keyword)
                self.driver.get(url)
                logger.info(f"[STARTING] ### Keyword: {keyword} ### {url}")
                # Wait until the main content is loaded
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
                # Check if redirected to login page
                if "login" in self.driver.current_url or self.driver.find_elements(By.CLASS_NAME, "bp7sPl"):
                    # Add login logic here
                    self.login()
                    # Wait until redirected back to the main page after login
                    self.wait.until(EC.url_contains("search?keyword="))
                    self.scroll_to_bottom()
                # Now proceed with scraping
                self.extract_links()
            except Exception as err:
                print("err ::: ", err)
                pass

    def close(self):
        self.driver.quit()


keywords = input("Enter keywords seperated by commas: ").strip().split(",")
# Usage
spider = shopeeSpider(keywords)
spider.start_scraping()
spider.close()
