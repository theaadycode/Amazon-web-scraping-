import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, WebDriverException

def get_asin_from_page(driver):
    asins = []
    # Locate the product containers by the data-asin attribute
    products = driver.find_elements(By.XPATH, "//div[contains(@class, 's-main-slot')]//div[contains(@data-asin, '')]")
    for product in products:
        asin = product.get_attribute("data-asin")
        if asin:
            asins.append(asin)
    return asins

def scrape_asin(product_name):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    # Set up WebDriver using WebDriver Manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Open Amazon
        driver.get("https://www.amazon.in/?&tag=googhydrabk1-21&ref=pd_sl_7hz2t19t5c_e&adgrpid=155259815513&hvpone=&hvptwo=&hvadid=674842289437&hvpos=&hvnetw=g&hvrand=10512852750506254097&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9301027&hvtargid=kwd-10573980&hydadcr=14453_2316415&gad_source=1")

        # Find the search bar and search for the product
        search_bar = driver.find_element(By.ID, "twotabsearchtextbox")
        search_bar.clear()
        search_bar.send_keys(product_name)
        search_bar.send_keys(Keys.RETURN)

        asins = []
        page_number = 1

        while True:
            print(f"Scraping page {page_number}...")
            asins.extend(get_asin_from_page(driver))

            try:
                # Try to navigate to the next page
                next_page = driver.find_element(By.XPATH, "//a[contains(@class, 's-pagination-next')]")
                next_page.click()
                time.sleep(3)  # Allow some time for the next page to load
                page_number += 1
            except NoSuchElementException:
                # Break the loop if there's no next page
                print("No more pages found.")
                break

    except WebDriverException as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()

    return asins 

if __name__ == "__main__":
    product_name = input("Enter the product name: ")
    asin_list = scrape_asin(product_name)
    
    # Save to CSV
    if asin_list:
        df = pd.DataFrame(asin_list, columns=["ASIN"])
        df.to_csv("asin_codes.csv", index=False)
        print(f"Scraped {len(asin_list)} ASIN codes.")
        print("ASIN codes saved to 'asin_codes.csv'.")
    else:
        print("No ASIN codes found.")

