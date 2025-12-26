import requests
from bs4 import BeautifulSoup
from utils.helpers import get_random_user_agent, add_delay, clean_price, clean_rating, clean_review_count, get_timestamp
from config import SAMSUNG_MODELS, SCRAPING_CONFIG

class AmazonScraper:
    """Scraper for Amazon Samsung phone data"""
    
    def __init__(self):
        self.base_url = "https://www.amazon.in"
        self.session = requests.Session()
        self.phones_data = []
    
    def search_phone(self, model_name):
        search_url = f"{self.base_url}/s"
        params = {'k': model_name}
        
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept-Language': 'en-IN,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        try:
            response = self.session.get(search_url, params=params, headers=headers, timeout=SCRAPING_CONFIG['timeout'])
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"✗ Error searching for {model_name} on Amazon: {e}")
            return None
    
    def parse_search_results(self, html, model_name):
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        products = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for product in products[:3]:
            try:
                title_elem = product.find('h2', class_='a-size-mini')
                title = title_elem.text.strip() if title_elem else ''
                
                if not self._is_correct_model(title, model_name) or 'S' not in model_name.upper():
                    continue
                
                price_elem = product.find('span', class_='a-price-whole')
                price = clean_price(price_elem.text.strip() if price_elem else None)
                
                rating_elem = product.find('span', class_='a-icon-alt')
                rating = clean_rating(rating_elem.text.strip() if rating_elem else None)
                
                review_elem = product.find('span', class_='a-size-base s-underline-text')
                review_count = clean_review_count(review_elem.text.strip() if review_elem else None)
                
                link_elem = product.find('a', class_='a-link-normal s-no-outline')
                product_url = self.base_url + link_elem['href'] if link_elem else None
                
                details = self.scrape_product_details(product_url) if product_url else {}
                
                phone_data = {
                    'model_name': model_name,
                    'title': title,
                    'price_inr': price,
                    'rating': rating or 0.0,
                    'review_count': review_count or 0,
                    'url': product_url,
                    'source': 'amazon',
                    'last_updated': get_timestamp(),
                    'features': details.get('features', []),
                    'colors': details.get('colors', []),
                    'storage_options': details.get('storage', []),
                    'processor': details.get('processor', 'N/A'),
                    'os_version': details.get('os', 'N/A'),
                    'specs': details.get('specs', {})
                }
                
                return phone_data
            except Exception as e:
                print(f"  Error parsing Amazon product: {e}")
                continue
        
        return None
    
    def scrape_product_details(self, product_url):
        headers = {'User-Agent': get_random_user_agent()}
        try:
            response = self.session.get(product_url, headers=headers, timeout=SCRAPING_CONFIG['timeout'])
            soup = BeautifulSoup(response.text, 'lxml')
            
            details = {}
            
            # Features
            features_section = soup.find('div', id='feature-bullets')
            details['features'] = [li.text.strip() for li in features_section.find_all('span', class_='a-list-item')] if features_section else []
            
            # Colors (from variants)
            colors = soup.find_all('img', alt=lambda x: x and 'colour' in x.lower())
            details['colors'] = list(set([img['alt'].strip() for img in colors if img.get('alt')]))
            
            # Storage (from title or variants)
            storage_options = soup.find_all('span', class_='selection')
            details['storage'] = list(set([opt.text.strip() for opt in storage_options if 'GB' in opt.text]))
            
            # Specs (from table)
            specs_table = soup.find('table', id='productDetails_techSpec_section_1')
            if specs_table:
                specs = {}
                rows = specs_table.find_all('tr')
                for row in rows:
                    key = row.find('th').text.strip()
                    value = row.find('td').text.strip()
                    specs[key] = value
                details['specs'] = specs
                details['processor'] = specs.get('Processor', 'N/A')
                details['os'] = specs.get('OS', 'N/A')
            
            return details
        except Exception as e:
            print(f"✗ Error scraping Amazon details: {e}")
            return {}
    
    def _is_correct_model(self, title, model_name):
        title_upper = title.upper()
        model_upper = model_name.upper()
        key_terms = model_upper.replace('SAMSUNG GALAXY ', '').split()
        return all(term in title_upper for term in key_terms)
    
    def scrape_all_models(self):
        print("\n" + "="*60)
        print("🔍 AMAZON SCRAPER - Starting Data Collection")
        print("="*60)
        
        for idx, model in enumerate(SAMSUNG_MODELS, 1):
            if 'S' not in model.upper():
                continue
            print(f"\n[{idx}/{len(SAMSUNG_MODELS)}] Searching: {model}")
            
            html = self.search_phone(model)
            phone_data = self.parse_search_results(html, model)
            
            if phone_data:
                self.phones_data.append(phone_data)
                print(f"  ✓ Found: ₹{phone_data['price_inr']:,} | Rating: {phone_data['rating']} | Reviews: {phone_data['review_count']:,}")
            else:
                print(f"  ✗ No data found")
            
            add_delay(SCRAPING_CONFIG['delay_between_requests'], SCRAPING_CONFIG['delay_between_requests'] + 2)
        
        print(f"\n✓ Amazon scraping complete. Found data for {len(self.phones_data)} phones.")
        return self.phones_data

def main():
    scraper = AmazonScraper()
    data = scraper.scrape_all_models()
    from utils.helpers import save_to_json
    save_to_json(data, 'data/raw/amazon_data.json')
    return data

if __name__ == "__main__":
    main()