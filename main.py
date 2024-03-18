import os
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

logger = setup_logger('shopee info logger', 'logs/shopee_spider.log')

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'

chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument(f'user-agent={USER_AGENT}')
chrome_options.page_load_strategy = 'eager'
chrome_options.accept_insecure_certs = True

ZYTE_APIKEY = os.environ.get("ZYTE_APIKEY")
ZYTE_PROXY_URL = f"http://{ZYTE_APIKEY}:@api.zyte.com:8011/"
# ZYTE_PROXY_URL = f"http://{ZYTE_APIKEY}:@proxy.crawlera.com:8011/"
# seleniumwire_options = {
#     'proxy': {
#         'http': f"http://{ZYTE_APIKEY}:@api.zyte.com:8011/",
#         'verify_ssl': False,
#     },
# }
seleniumwire_options = {
    "proxy": {"http": ZYTE_PROXY_URL, "https": ZYTE_PROXY_URL, "no_proxy": ""}
}


class BrowserThread(Thread):
    def __init__(self, link):
        super(BrowserThread, self).__init__()
        self.link = link

    def run(self):
        try:
            print("self.link ::: ", self.link)
            self.open_link_in_tabs(self.link)
        except Exception as e:
            logger.error(f"Error occurred while processing link: {self.link} - {e}")

    def open_link_in_tabs(self, link):
        driver = webdriver.Chrome(options=chrome_options)
        try:
            logger.info(f"Opening link in multiple tabs: {link}")
            driver.get(link)
            for _ in range(50):  # Open 50 tabs
                driver.execute_script(f"window.open('{link}');")
            time.sleep(10)  # Adjust the sleep time as needed
            # Wait until all tabs are loaded
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(51))  # Assuming the original window is included
            # Close all tabs except the original window
            original_window = driver.window_handles[0]
            for window in driver.window_handles[1:]:
                driver.switch_to.window(window)
                driver.close()
            # Switch back to the original window
            driver.switch_to.window(original_window)
            logger.info(f"All tabs for link {link} have been closed.")
        finally:
            driver.quit()


class shopeeSpider:
    def __init__(self, product_keywords, start_page=1, end_page=5):
        self.keywords = product_keywords
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       seleniumwire_options=seleniumwire_options, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self):
        # Wait until the main content is loaded
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hww4XZ")))
        # Add login logic here
        email_input = self.driver.find_element(By.NAME, "loginKey")
        password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
        login_button = self.driver.find_element(By.CLASS_NAME, "DYKctS")

        # Add your email and password
        EMAIL = os.environ.get("SHOPEE_EMAIL")
        PASSWORD = os.environ.get("SHOPEE_PASSWORD")
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DYKctS")))
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

        links = []
        for li in product_ads_links:
            # Extract the href attribute from the <a> tag within the <li>
            link = li.find_element(By.TAG_NAME, "a").get_attribute("href")
            logger.info(f"Original Link: {link}")
            links.append(link)
        return links

    def start_scraping(self):
        BASE_URL = "https://shopee.co.id/search?keyword={}"
        for keyword in self.keywords:
            try:
                url = BASE_URL.format(keyword)
                self.driver.get(url)
                logger.info(f"[STARTING] ### Keyword: {keyword} ### {url}")
                # Wait until the main content is loaded
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
                # Add login logic here
                self.login()
                # Wait until redirected back to the main page after login
                self.wait.until(EC.url_contains("search?keyword="))
                # Solve the Captcha
                print("Solving Captcha")
                CAPTCHA_API = os.environ.get("2CAPTCHA_API")
                solver = TwoCaptcha(CAPTCHA_API)
                SITE_KEY = self.driver.find_element(By.CLASS_NAME, "g-recaptcha")
                response = solver.recaptcha(sitekey=SITE_KEY, url=self.driver)
                code = response['code']
                print(f"Successfully solved the Captcha. The solve code is {code}")
                # Set the solved Captcha
                recaptcha_response_element = self.driver.find_element(By.ID, 'g-recaptcha-response')
                self.driver.execute_script(f'arguments[0].value = "{code}";', recaptcha_response_element)

                # Submit the form
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                submit_btn.click()
                self.scroll_to_bottom()
                # Now proceed with scraping
                links = self.extract_links()
                for link in links:
                    thread = BrowserThread(link)
                    thread.start()
                self.driver.quit()
            except Exception as err:
                print("err ::: ", err)

    def close(self):
        self.driver.quit()


keywords = input("Enter keywords seperated by commas: ").strip().split(",")
# Usage
spider = shopeeSpider(keywords)
spider.start_scraping()
spider.close()
