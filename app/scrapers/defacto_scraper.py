import requests
from bs4 import BeautifulSoup
import random

def defacto_scraper(product_url):
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
        title = soup.find('h1', {'class': 'product-card__name'}).get_text().strip()
        print(title)
        price_wrapper = soup.find('div', {'class': 'product-card__price-list'})
        
        if price_wrapper.find('div', {'class': 'sale'}):
            price = price_wrapper.find('div', {'class': 'sale'}).get_text().strip()
        else:
            price = price_wrapper.find('div', {'class': 'product-card__price--new'}).get_text().strip()
        print(price)   

        images = []  # Use a different variable name
        img_tag = soup.find('div', {'class': 'product-card__image-slider'})

        if img_tag:
            img_elements = img_tag.find_all('img')
            for img in img_elements:
                src = img.get('data-src', '')  # Use get method with a default value
                if src and not src.startswith('https:'):
                    src = 'https:' + src
                    images.append(src)


        print(images)



        tecdiv_list = soup.find_all('div', {'class': 'sideMenu__box'})
        tech_spec_data = ""
        for tecdiv in tecdiv_list:
            li_elements = tecdiv.find_all('li')
            for li_element in li_elements:
                key = "*"
                value = li_element.get_text().strip()
                tech_spec_data += f"{key} {value}<br>"

        print(tech_spec_data)

        # Elde edilen verileri sözlük olarak döndür
        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        # İstek başarısızsa
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None
