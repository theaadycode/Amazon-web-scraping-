

# Amazon Product Scraper

A Python script that uses Selenium to scrape detailed product information from Amazon. This tool extracts various details including product images, model names, aspect ratings, and more. It supports concurrent scraping of multiple ASINs and handles errors gracefully with logging and retry mechanisms.

## Features

- **Extract Product Details**: Retrieve model names, prices, discount percentages, and additional product details.
- **Image Extraction**: Collect primary product images and additional images from different sections.
- **Aspect Ratings**: Capture positive, average, and negative aspect ratings from product pages.
- **Concurrent Scraping**: Utilize `ThreadPoolExecutor` to scrape multiple products simultaneously.
- **Error Handling**: Includes robust error logging and retry mechanisms.

## Requirements

- Python 3.x
- Selenium
- tqdm
- pandas
- ChromeDriver

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/amazon-product-scraper.git
   cd amazon-product-scraper
Install Required Python Packages

pip install selenium tqdm pandas
Download ChromeDriver

Download ChromeDriver from here and place it in an appropriate directory. Update the path in the script to point to the ChromeDriver executable.

Configuration
Prepare Your ASINs CSV File

Ensure your CSV file (e.g., asin_codes.csv) contains a column named ASIN with the ASINs of the products you want to scrape.

Update Script Paths

Update the csv_path variable in the main() function to point to the location of your CSV file.
Ensure the path to the ChromeDriver executable in the init_driver() function is correctly set.
Usage
Run the Script

Execute the script using Python:


python scraper.py
The script will scrape product data for the ASINs listed in the CSV file and save the results to scraped_amazon_products.csv.

Functions
init_driver(): Initializes and configures the Selenium WebDriver.
scroll_to_bottom(driver): Scrolls to the bottom of the page to ensure all content is loaded.
get_random_user_agent(): Returns a random user agent string to help avoid detection.
extract_more_image_links(driver): Extracts additional image URLs from various sections of the product page.
extract_model_name(driver): Extracts the product model name from the page.
extract_aspect_ratings(driver): Extracts positive, average, and negative aspect ratings from the product page.
scrape_amazon_product(url, results_queue, retry_count=1): Scrapes data for a single Amazon product and handles retries on failure.
scrape_amazon_products_concurrently(asins, max_workers=5): Scrapes multiple products concurrently using threading.
read_asins_from_csv(csv_path): Reads ASINs from a CSV file.
main(): Main function that loads ASINs, scrapes the data, and saves it to a CSV file.
Logging
Errors encountered during scraping are logged in scraping_errors.log. This log file captures details of any issues that occur during the scraping process.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contributing
Contributions are welcome! Please fork the repository and submit pull requests. Ensure your changes are well-documented and tested.

Contact
For questions or feedback, please contact [your email] or [your GitHub profile].


### Instructions for Customization:

- **Replace `yourusername`** with your actual GitHub username.
- **Replace `[your email]`** and **`[your GitHub profile]`** with your actual contact information.
- **Update the paths** for the ChromeDriver executable and CSV file as per your environment.

Feel free to adjust any sections to better fit your project's specifics!





