import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def replace_google_sites_url_with_content(input_string: str):
    pattern = r'https:\/\/sites\.google\.com\/view\/[a-zA-Z0-9_-]+'
    matches = re.findall(pattern, input_string.replace("?usp=sharing",""))
    if matches:
        replaced_string = ""
        for m in matches:
            print("ID",m)
            replaced_string += re.sub(pattern, get_all_google_site_content(m), input_string)
        return replaced_string, True
    return input_string, False

def get_all_google_site_content(site_url, visited_urls=None):
    if visited_urls is None:
        visited_urls = set()
    txt = ""
    try:
        print("requesting: ",site_url)
        response = requests.get(site_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            all_text = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for element in all_text:
                txt += element.get_text(separator='\n')

            visited_urls.add(site_url)

            links = soup.find_all('a', href=True)
            for link in links:
                page_url = urljoin(site_url, link['href'])

                if urlparse(page_url).netloc == urlparse(site_url).netloc and page_url not in visited_urls:
                    page_response = requests.get(page_url)

                    if page_response.status_code == 200:
                        page_soup = BeautifulSoup(page_response.text, 'html.parser')

                        page_text = page_soup.find_all(['p','h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                        for page_element in page_text:
                            txt += page_element.get_text(separator='\n')

                        time.sleep(0.2)
                        txt += get_all_google_site_content(page_url, visited_urls)

                    else:
                        print(f"\nFailed to retrieve page content. Status Code: {page_response.status_code}")

        else:
            print(f"Failed to retrieve content. Status Code: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
    return txt
