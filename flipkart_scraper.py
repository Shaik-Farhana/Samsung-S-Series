import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import json
import os

# List of S series models to scrape (latest 2025)
SAMSUNG_MODELS = [
    'Samsung Galaxy S25 Ultra',
    'Samsung Galaxy S25+',
    'Samsung Galaxy S25',
    'Samsung Galaxy S25 Edge',
    'Samsung Galaxy S25 FE',
    'Samsung Galaxy S24 Ultra',
    'Samsung Galaxy S24+',
    'Samsung Galaxy S24',
    'Samsung Galaxy S24 FE',
    'Samsung Galaxy S23 Ultra',
    'Samsung Galaxy S23+', 
    'Samsung Galaxy S22',
    'Samsung Galaxy S23 FE',
    'Samsung Galaxy S23',
]

# Embedded helpers
def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
    ]
    return random.choice(user_agents)

def add_delay(min_delay=3, max_delay=6):
    delay = random.uniform(min_delay, max_delay)
    print(f"    Delaying {delay:.1f}s...")
    time.sleep(delay)

def clean_price(price_str):
    if not price_str: return None
    return int(''.join(filter(str.isdigit, price_str.replace(',', ''))))

def clean_rating(rating_str):
    if not rating_str: return None
    try:
        return float(rating_str.split()[0])
    except:
        return None

def clean_review_count(count_str):
    if not count_str: return None
    try:
        return int(''.join(filter(str.isdigit, count_str.replace(',', ''))))
    except:
        return None

def get_timestamp():
    return datetime.now().isoformat()

def save_to_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} phones to {filename}")

class FlipkartScraper:
    def __init__(self):
        self.base_url = "https://www.flipkart.com"
        self.session = requests.Session()
        self.phones_data = []

    def search_phone(self, model_name):
        search_url = f"{self.base_url}/search?q={requests.utils.quote(model_name)}"
        headers = {'User-Agent': get_random_user_agent()}
        try:
            response = self.session.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error searching {model_name}: {e}")
            return None

    def parse_search_results(self, html, model_name):
        if not html: return None
        soup = BeautifulSoup(html, 'html.parser')
        products = soup.find_all('div', {'class': lambda x: x and ('_2kHMtA' in x or '_13oc-S' in x)})
        for product in products[:3]:
            try:
                title = product.find('a', {'class': 'IRpwTa'}) or product.find('div', {'class': '_4rR01T'})
                title = title.get_text(strip=True) if title else ''
                if model_name.upper().replace('SAMSUNG GALAXY ', '') not in title.upper():
                    continue

                price = clean_price(product.find('div', {'class': '_30jeq3'}).get_text() if product.find('div', {'class': '_30jeq3'}) else None)
                rating = clean_rating(product.find('div', {'class': '_3LWZlK'}).get_text() if product.find('div', {'class': '_3LWZlK'}) else None)
                reviews = clean_review_count(product.find('span', {'class': '_2_R_DZ'}).get_text() if product.find('span', {'class': '_2_R_DZ'}) else None)
                url = self.base_url + product.find('a', href=True)['href'] if product.find('a', href=True) else None

                phone_data = {
                    'model_name': model_name,
                    'title': title,
                    'price_inr': price or 0,
                    'rating': rating or 0.0,
                    'review_count': reviews or 0,
                    'url': url,
                    'source': 'flipkart',
                    'last_updated': get_timestamp()
                }
                return phone_data
            except Exception as e:
                continue
        return None

    def scrape_all_models(self):
        print("\nStarting Flipkart scraping for Samsung S series...")
        for model in SAMSUNG_MODELS:
            print(f"\nSearching: {model}")
            html = self.search_phone(model)
            data = self.parse_search_results(html, model)
            if data:
                self.phones_data.append(data)
                print(f"  Found: ₹{data['price_inr']:,} | Rating: {data['rating']} | Reviews: {data['review_count']:,}")
            else:
                print("  No match found")
            add_delay()
        save_to_json(self.phones_data, 'data/raw/flipkart_data.json')
        return self.phones_data

if __name__ == "__main__":
    FlipkartScraper().scrape_all_models()