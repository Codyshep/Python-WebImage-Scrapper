import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def is_valid_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200  # Check if the status code is 200 (OK)
    except requests.RequestException:
        return False  # If there's an exception, consider the URL invalid

def main():
    download_path = input("Download Path [Enter For Default]: ")
    url = input("URL To Scrape: ")
    keyword = input("Keyword For Image To Download [Enter For None]: ")

    data = {
        "url": url,
        "download_folder": download_path if download_path else "images",
        "keyword": keyword
    }

    for key, value in data.items():
        if key == "keyword":
            continue
        if value:
            print(f"Set {value}")
        else:
            print(f"Missing {key}")

    if is_valid_url(data['url']):
        print('Valid URL Connection')
        url = data['url']
        download_folder = data['download_folder'] 
        keyword = data.get('keyword', '')  # Get the keyword if provided, otherwise set it to an empty string
        if download_folder:  # Check if download_folder is set
            download_images_with_browser(url, download_folder, keyword)
        else:
            print('No Download Folder Set')
            time.sleep(5)
    else:
        print('Failed To Connect To URL')
        time.sleep(5)

def download_images_with_browser(url, download_folder, keyword=''):
    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome()

    try:
        # Navigate to the URL
        driver.get(url)

        # Keep track of the number of images downloaded
        img_count = 1

        # Set to store processed image URLs
        processed_urls = set()

        # Flag to track if new images have been downloaded
        new_images_downloaded = True

        while new_images_downloaded:
            new_images_downloaded = False  # Reset the flag at the beginning of each iteration

            # Scroll down to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for images to load
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "img")))

            # Parse the HTML content of the page
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find all image tags
            img_tags = soup.find_all('img')

            # Extract and download new images
            for img_tag in img_tags:
                img_url = img_tag.get('src')
                # If the image URL is relative, convert it to absolute URL
                if img_url and not img_url.startswith(('data:', 'http:', 'https:')):
                    img_url = urljoin(url, img_url)
                
                # Check if the image URL has been processed before
                if img_url in processed_urls:
                    continue
                
                # Add the image URL to the processed set
                processed_urls.add(img_url)
                
                # Extract the filename from the URL
                img_filename = f"image{img_count}.jpg"
                
                # Check if the keyword is present in the filename
                if not keyword or keyword.lower() in img_filename.lower():
                    # Download the image using requests
                    download_image(img_url, download_folder, img_filename)
                    img_count += 1
                    new_images_downloaded = True  # Set the flag to True if a new image is downloaded

            # Scroll down further if not all images have been downloaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for a short period before continuing
            time.sleep(1)

        print("All images have been downloaded.")

    finally:
        # Close the browser
        driver.quit()

def download_image(url, download_folder, img_filename):
    # Create download folder if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Download the image using requests
    img_path = os.path.join(download_folder, img_filename)
    with open(img_path, 'wb') as img_file:
        response = requests.get(url)
        if response.status_code == 200:
            img_file.write(response.content)
            print(f"Downloaded: {url} -> Saved to: {img_path}")
        else:
            print(f"Failed to download {url}: HTTP status code {response.status_code}")

if __name__ == "__main__":
    main()
