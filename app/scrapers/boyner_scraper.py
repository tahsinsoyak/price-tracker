import requests
from bs4 import BeautifulSoup
import random

def boyner_scraper(product_url):
    # Kullanıcı ajanları dosyasını aç ve rastgele bir kullanıcı ajanı seç
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
        title = soup.find('h1', {'class': lambda x: x and 'title_headingContainer' in x}).get_text().strip()
        price = soup.find('div', {'class': lambda x: x and 'product-price_checkPrice' in x}).get_text().strip()

        images = []
        img_tag = soup.find('div', {'class': lambda x: x and 'grid_productDetailGallery' in x})
        if img_tag:
            img_elements = img_tag.find_all('img')
            for img in img_elements:
                src = img.get('src')  # Use get method with a default value
                if src not in images and src.startswith('https:'):  # Check for duplicates before appending
                    images.append(src)


        tecdiv_list = soup.find('div', {'class': lambda x: x and 'product-information-card_infoText' in x})
        tech_spec_data = ""
        product_info_rows = tecdiv_list.find_all('span', {'class': lambda x: x and 'product-information-card_value' in x})
        for row in product_info_rows:
            strong_tag = row.find('strong')
            if strong_tag:
                key = strong_tag.get_text(strip=True)
                value = row.get_text(strip=True).replace(key, '').strip()
                tech_spec_data += f"{key} {value}<br>"


        # Elde edilen verileri sözlük olarak döndür
        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        # İstek başarısızsa
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None

