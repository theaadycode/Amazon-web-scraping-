from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from tqdm import tqdm
import random
from concurrent.futures import ThreadPoolExecutor
import queue
import logging
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Configure logging
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def scroll_to_bottom(driver):
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument(f"user-agent={get_random_user_agent()}")
    service = Service(r"C:\Users\HP\Desktop\data analystic\chromedriver-win64\chromedriver.exe")  # Ensure this path is correct
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_more_image_links(driver):
    more_img_urls = []
    sections = [
        "//h2[contains(text(), 'From the manufacturer')]/following-sibling::div",
        "//h2[contains(text(), 'Product Description')]/following-sibling::div",
        "//div[contains(@class, 'content-grid-block')]"  # Specific class for additional images
    ]
    
    try:
        for section_xpath in sections:
            try:
                section = driver.find_element(By.XPATH, section_xpath)
            except NoSuchElementException:
                continue
            
            # Find all subsequent div elements within this section
            image_containers = section.find_elements(By.XPATH, ".//div")
            for container in image_containers:
                images = container.find_elements(By.TAG_NAME, 'img')
                for img in images:
                    src = img.get_attribute('src')
                    data_src = img.get_attribute('data-src')
                    if src and (src.endswith('.jpg') or src.endswith('.png') or src.endswith('.jpeg') or src.endswith('.tif') or src.endswith('.tiff')):
                        more_img_urls.append(src)
                    elif data_src and (data_src.endswith('.jpg') or data_src.endswith('.png') or data_src.endswith('.jpeg') or data_src.endswith('.tif') or data_src.endswith('.tiff')):
                        more_img_urls.append(data_src)
                
    except Exception as e:
        logging.error(f"Error extracting more image links: {e}")
    
    return list(set(more_img_urls))

def extract_model_name(driver):
    model_name = "N/A"
    
    try:
        product_overview = driver.find_element(By.ID, 'productOverview_feature_div')
        rows = product_overview.find_elements(By.CSS_SELECTOR, 'tr')
        for row in rows:
            if any(term in row.text for term in ["Model Name", "Model", "Item model number"]):
                cells = row.find_elements(By.CSS_SELECTOR, 'td')
                if len(cells) > 1:
                    model_name = cells[1].text
                    break
    except Exception as e:
        logging.error(f"Error extracting model name from productOverview_feature_div: {e}")

    if model_name == "N/A":
        try:
            product_details = driver.find_element(By.ID, 'prodDetails')
            rows = product_details.find_elements(By.CSS_SELECTOR, 'tr')
            for row in rows:
                th_element = row.find_element(By.CSS_SELECTOR, 'th')
                if any(term in th_element.text for term in ["Model Name", "Model", "Item model number"]):
                    td_element = row.find_element(By.CSS_SELECTOR, 'td')
                    model_name = td_element.text
                    break
        except Exception as e:
            logging.error(f"Error extracting model name from prodDetails: {e}")

    return model_name

def extract_aspect_ratings(driver):
    positive = []
    average = []
    negative = []
    
    try:
        aspect_buttons = driver.find_elements(By.CSS_SELECTOR, 'div[data-hook="cr-insights-widget-aspects"] button')
        
        # Check if there are any aspect buttons found
        if aspect_buttons:
            for button in aspect_buttons:
                text = button.text
                if 'POSITIVE' in button.get_attribute('aria-describedby'):
                    positive.append(text)
                elif 'NEGATIVE' in button.get_attribute('aria-describedby'):
                    negative.append(text)
                else:
                    average.append(text)
        else:
            # Handle case where no aspect buttons are found
            positive.append("Nothing found")
            average.append("Nothing found")
            negative.append("Nothing found")
    except Exception as e:
        logging.error(f"Error extracting aspect ratings: {e}")
    
    return positive, average, negative

def scrape_amazon_product(url, results_queue, retry_count=1):
    for attempt in range(retry_count):
        driver = init_driver()
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(random.uniform(2, 4))  # Randomize sleep time to avoid detection
            
            # Scroll to the bottom of the page to load all images and content
            scroll_to_bottom(driver)
            
            try:
                product_overview = driver.find_element(By.ID, 'productOverview_feature_div')
                rows = product_overview.find_elements(By.CSS_SELECTOR, 'tr')
                details = "\n".join([row.text for row in rows])
            except Exception as e:
                details = "N/A"
                logging.error(f"Error extracting product details for {url}: {e}")
            
            try:
                feature_bullets = driver.find_element(By.ID, 'feature-bullets')
                bullet_points = feature_bullets.find_elements(By.CSS_SELECTOR, 'li span.a-list-item')
                more_details = "\n".join([bullet.text for bullet in bullet_points])
            except Exception as e:
                more_details = "N/A"
                logging.error(f"Error extracting more details for {url}: {e}")
            
            try:
                price_div = driver.find_element(By.ID, 'corePriceDisplay_desktop_feature_div')
                discount_percentage = price_div.find_element(By.CSS_SELECTOR, 'span.savingsPercentage').text.replace("-", "").replace("%", "")
                discounted_price = price_div.find_element(By.CSS_SELECTOR, 'span.a-price-whole').text.replace(",", "")
                
                if discount_percentage and discounted_price:
                    discount_percentage = int(discount_percentage)
                    discounted_price = int(discounted_price)
                    mrp = price_div.find_element(By.CSS_SELECTOR, 'span.a-text-price').text.replace("₹", "").replace(",", "")
                    mrp = int(mrp)
                    amazon_info = f"MRP: ₹{mrp} | DISCOUNT: {discount_percentage}% | PRICE: ₹{discounted_price} | URL: {url}"
                else:
                    amazon_info = "Not available"
                    discounted_price = "Currently Unavailable"
            except Exception as e:
                amazon_info = "Currently Unavailable"
                discounted_price = "Currently Unavailable"
                logging.error(f"Error extracting price information for {url}: {e}")
            
            try:
                img_element = driver.find_element(By.ID, 'landingImage')
                dynamic_image_data = img_element.get_attribute('data-a-dynamic-image')
                image_dict = json.loads(dynamic_image_data)
                largest_image_url = max(image_dict, key=lambda k: image_dict[k][0] * image_dict[k][1])
                img_urls_str = largest_image_url
            except Exception as e:
                img_urls_str = "N/A"
                logging.error(f"Error extracting image URL for {url}: {e}")
            
            more_img_urls = extract_more_image_links(driver)
            more_img_urls_str = "|".join(more_img_urls) if more_img_urls else "N/A"
            
            model_name = extract_model_name(driver)
            
            positive, average, negative = extract_aspect_ratings(driver)
            positive_str = "|".join(positive)
            average_str = "|".join(average)
            negative_str = "|".join(negative)
            
            product_details = {
                'URL': url,
                'Amazon Info': amazon_info,
                'Discounted Price': discounted_price,
                'Image URL': img_urls_str,
                'More Image Links': more_img_urls_str,
                'Model Name': model_name,
                'Details': details,
                'More Details': more_details,
                'Positive': positive_str,
                'Average': average_str,
                'Negative': negative_str
            }
            
            results_queue.put(product_details)
            driver.quit()
            break
        except Exception as e:
            driver.quit()
            logging.error(f"Attempt {attempt + 1} failed for URL {url}: {e}")
            if attempt < retry_count - 1:
                logging.info(f"Retrying URL {url} (Attempt {attempt + 2}/{retry_count})")
                time.sleep(3)  # Wait before retrying
            else:
                logging.error(f"Failed to scrape URL {url} after {retry_count} attempts")

def scrape_amazon_products_concurrently(asins, max_workers=5):
    results_queue = queue.Queue()
    base_url = "https://www.amazon.in/dp/"
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scrape_amazon_product, base_url + asin, results_queue) for asin in asins]
        
        for future in tqdm(futures, desc="Scraping Amazon Products"):
            future.result()
    
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())
    
    return pd.DataFrame(results)

# Function to read ASINs from CSV
def read_asins_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    print("Columns in CSV:", df.columns)  # Print the columns to debug the issue
    if 'ASIN' in df.columns:
        return df['ASIN'].to_list()  # Use 'ASIN' instead of 'ASINS'
    else:
        logging.error(f"Column 'ASIN' not found in CSV. Available columns: {df.columns}")
        raise KeyError("The column 'ASIN' does not exist in the provided CSV file.")

def main():
    # Load ASINs from a CSV file
    csv_path = r'C:\Users\HP\Desktop\data analystic\asin_codes.csv'  # Update with the path to your CSV file
    asins = read_asins_from_csv(csv_path)

    # Scrape the Amazon products
    scraped_data = scrape_amazon_products_concurrently(asins)

    # Save the scraped data to a CSV file
    scraped_data.to_csv('scraped_amazon_products.csv', index=False)

if __name__ == "__main__":
    main()
