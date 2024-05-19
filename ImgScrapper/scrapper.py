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
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error checking URL: {e}")
        return False

def main():
    download_path = input("Download Path [Enter For Default]: ")
    url = input("URL To Scrape: ")
    keyword = input("Keyword For Image To Download [Enter For None]: ")

    download_folder = download_path if download_path else "images"

    if is_valid_url(url):
        print('Valid URL Connection')
        download_images_with_browser(url, download_folder, keyword)
    else:
        print('Failed To Connect To URL')

def download_images_with_browser(url, download_folder, keyword=''):
    driver = webdriver.Chrome()

    try:
        driver.get(url)

        img_count = 1
        processed_urls = set()
        new_images_downloaded = True

        while new_images_downloaded:
            new_images_downloaded = False
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "img")))

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            img_tags = soup.find_all('img')

            for img_tag in img_tags:
                img_url = img_tag.get('src')
                if img_url and not img_url.startswith(('data:', 'http:', 'https:')):
                    img_url = urljoin(url, img_url)

                if img_url in processed_urls:
                    continue
                
                processed_urls.add(img_url)
                img_filename = f"image{img_count}.jpg"

                if not keyword or keyword.lower() in img_filename.lower():
                    download_image(img_url, download_folder, img_filename)
                    img_count += 1
                    new_images_downloaded = True

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        print("All images have been downloaded.")
    finally:
        driver.quit()

def download_image(url, download_folder, img_filename):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    img_path = os.path.join(download_folder, img_filename)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(img_path, 'wb') as img_file:
                img_file.write(response.content)
            print(f"Downloaded: {url} -> Saved to: {img_path}")
        else:
            print(f"Failed to download {url}: HTTP status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    main()
