import requests
from bs4 import BeautifulSoup
import random

def hepsiburada_scraper(product_url):
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
        title = soup.find('h1', {'id': 'product-name'}).get_text().strip()
        price_wrapper = soup.find('div', {'class': 'product-price-wrapper'})
        price = price_wrapper.find('span', {'class': 'price'}).get_text().strip()
        price = f"{price.split()[0]} TL"
        images = []
        img_div = soup.find('div', {'id': 'productDetailsCarousel'})
        img_tags = img_div.find_all('img')
        for img_tag in img_tags:
            # Check if 'data-src' attribute exists before accessing it
            if 'data-src' in img_tag.attrs:
                image_url = img_tag['data-src']
                images.append(image_url)

        tech_spec_data = ''
        # Ürünün teknik özelliklerini içeren tabloyu bul
        tech_spec_table = soup.find('div', {'id': 'productTechSpecContainer'})
        # find tables
        tables = tech_spec_table.find_all('table')
        for table in tables:
            # Tablodaki her satır için
            for row in table.find_all('tr'):
                key = row.find(['th']).get_text().strip()
                value = row.find(['td']).get_text().strip()
                tech_spec_data += f"{key}: {value}<br>"
        # Elde edilen verileri sözlük olarak döndür
        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        # İstek başarısızsa
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None
