import requests
from bs4 import BeautifulSoup
import random

def mediamarkt_scraper(product_url):
    with open('scrapers/user_agents/user-agents.txt', 'r') as file:
        user_agents = file.readlines()

    random_user_agent = random.choice(user_agents)
    headers = {'User-Agent': random_user_agent.strip()}
    
    # Belirtilen ürün URL'sine istek gönder
    response = requests.get(product_url, headers=headers)
    
    # İstek başarılıysa
    if response.status_code == 200:
        # Sayfa içeriğini parçala
        soup = BeautifulSoup(response.text, 'html.parser')

        # Gerekli verileri çek ve düzenle
        details_div = soup.find('div', {'id': 'product-details'})
        title = details_div.find('h1', {'itemprop': lambda x: x and 'name' in x}).get_text().strip()
        price = soup.find('meta', {'itemprop': 'price'})['content']
        price = price + " TL"

        images = []
        img_tag = soup.find('ul', {'class': 'thumbs'})
        if img_tag:
            img_elements = img_tag.find_all('a')
            for img in img_elements:
                src = img.get('data-magnifier')  # Use get method with a default value
                if src not in images:  # Check for duplicates before appending
                    images.append('https:'+src)
        
        details_dl = soup.find('dl', class_='product-details')

        if details_dl:
            key_value_string = ""

            for dt, dd in zip(details_dl.find_all('dt'), details_dl.find_all('dd')):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)

                key_value_string += f"{key} {value} <br>"

        tech_spec_data = key_value_string

        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        # İstek başarısızsa
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None