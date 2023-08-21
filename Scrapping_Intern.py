import requests
from bs4 import BeautifulSoup
import csv
import time
from random import randint


def scrape_product_page(url):
    headers = {
        'User-Agent': 'Your User Agent Here'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    time.sleep(randint(1, 3))  # Adding a random delay between 1 and 3 seconds

    products = []

    
    for product in soup.find_all('div', class_='s-result-item'):
        product_data = {}
        
        try:
            product_link = product.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')
            if product_link:
                product_data['url'] ='https://www.amazon.in/'+ product_link['href']
            else:
                product_data['url'] = 'N/A'
        except AttributeError:
            product_data['url'] = 'N/A'
        
        try:
            product_name = product.find('span', class_='a-size-medium a-color-base a-text-normal')
            if product_name:
                product_data['name'] = product_name.get_text()
            else:
                product_data['name'] = 'N/A'
        except AttributeError:
            product_data['name'] = 'N/A'

        try:
            price_element = product.find('span', class_='a-price-whole')
            if price_element:
                product_data['price'] = price_element.get_text()
            else:
                product_data['price'] = 'N/A'
        except AttributeError:
            product_data['price'] = 'N/A'

        try:
            rating_element =product.find('span', class_='a-size-base puis-bold-weight-text')
            if rating_element:
                product_data['rating'] = rating_element.get_text()
            else:
                product_data['rating'] = 'N/A'
        except AttributeError:
            product_data['rating'] = 'N/A'
        
        if  product_data['price']=='N/A' or product_data['name']=='N/A': continue


        products.append(product_data)

    return products




# Function to scrape additional product information from product URLs
# Function to scrape additional product information from product URLs
def scrape_additional_info(product_data):
    headers = {
        'User-Agent': 'Your User Agent Here'
    }
    additional_info = []

    for product in product_data:
        url = product['url']
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        time.sleep(randint(1, 3))  # Adding a random delay between 1 and 3 seconds

        try:
            # Extract ASIN - Tabular format
            asin_th_element = soup.find('th', string='ASIN')
            if asin_th_element:
                asin_td_element = asin_th_element.find_next('td')
                product['asin'] = asin_td_element.get_text().strip()
            else:
                # Extract ASIN - List format
                asin_list_element = soup.find('li', string=re.compile(r'\bASIN\b'))
                if asin_list_element:
                    product['asin'] = asin_list_element.find('span').get_text().strip()
                else:
                    product['asin'] = 'N/A'
        except Exception as e:
            print(f"Error while scraping ASIN for {product['url']}: {e}")
            product['asin'] = 'N/A'

        try:
            # Extract Product Description
            product_desc_element = soup.find('div', {'id': 'product-description'})
            product['product_description'] = product_desc_element.get_text().strip() if product_desc_element else 'N/A'
        except Exception as e:
            print(f"Error while scraping product description for {product['url']}: {e}")
            product['product_description'] = 'N/A'

        try:
            # Extract Manufacturer Name - Tabular format
            manufacturer_th_element = soup.find('th', string='Manufacturer')
            if manufacturer_th_element:
                manufacturer_td_element = manufacturer_th_element.find_next('td')
                product['manufacturer'] = manufacturer_td_element.get_text().strip()
            else:
                # Extract Manufacturer Name - List format
                manufacturer_list_element = soup.find('li', string=re.compile(r'\bManufacturer\b'))
                if manufacturer_list_element:
                    product['manufacturer'] = manufacturer_list_element.find('span').get_text().strip()
                else:
                    product['manufacturer'] = 'N/A'
        except Exception as e:
            print(f"Error while scraping manufacturer name for {product['url']}: {e}")
            product['manufacturer'] = 'N/A'


        try:
            # Extract Rating
            rating_element = soup.find('span', {'id': 'acrPopover'})
            product['rating'] = rating_element.find('span', class_='a-icon-alt').get_text().split()[0] if rating_element else 'N/A'
        except Exception as e:
            print(f"Error while scraping rating for {product['url']}: {e}")
            product['rating'] = 'N/A'

        additional_info.append(product)

    return additional_info






# Main function to scrape multiple pages
def scrape_multiple_pages(base_url, num_pages):
    all_products = []

    for page_num in range(1, num_pages + 1):
        url = base_url + f'&page={page_num}'
        products = scrape_product_page(url)
        all_products.extend(products)
        print(f"Scraped page {page_num}")

    # breakpoint()
    additional_info = scrape_additional_info(all_products)

    for i in range(len(all_products)):
        all_products[i].update(additional_info[i])

    return all_products



base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
num_pages = 20



# Scraping data from multiple pages
all_products = scrape_multiple_pages(base_url, num_pages)

# Export data to CSV
csv_file = 'amazon_products.csv'
fieldnames = ['url', 'name', 'price', 'rating', 'reviews', 'asin', 'product_description', 'manufacturer']

with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_products)

print(f"Data exported to {csv_file}")
