import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def download_images(url, download_folder, keyword):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if request was successful
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all image tags
    img_tags = soup.find_all('img')
    
    # Extract and download images
    for img_tag in img_tags:
        img_url = img_tag.get('src')
        # If the image URL is relative, convert it to absolute URL
        if img_url and not img_url.startswith(('data:', 'http:', 'https:')):
            img_url = urljoin(url, img_url)
        
        # Extract the filename from the URL
        img_name = os.path.basename(urlparse(img_url).path)
        
        # Check if the keyword is present in the filename
        if keyword.lower() in img_name.lower():
            # Download the image
            try:
                download_image(img_url, download_folder, img_name)
            except Exception as e:
                print(f"Error downloading {img_url}: {e}")

def download_image(url, download_folder, img_name):
    # Create download folder if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Download the image
    img_path = os.path.join(download_folder, img_name)
    with open(img_path, 'wb') as img_file:
        response = requests.get(url)
        if response.status_code == 200:
            img_file.write(response.content)
            print(f"Downloaded: {url} -> Saved to: {img_path}")
        else:
            print(f"Failed to download {url}: HTTP status code {response.status_code}")

# Example usage
url = ""
download_folder = "images"
keyword = "bayer"
download_images(url, download_folder, keyword)
