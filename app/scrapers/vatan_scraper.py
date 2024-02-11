import requests
from bs4 import BeautifulSoup
import random

def vatan_scraper(product_url):
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
        title = soup.find('h1', {'class': lambda x: x and 'product-list__product-name' in x}).get_text().strip()
        print(title)
        price = soup.find('span', {'class': lambda x: x and 'product-list__price' in x}).get_text().strip()       
        price = price + " TL"
        print(price)

        images = []
        img_tag = soup.find('div', {'class': 'product-img-slide'})
        print(img_tag)
        if img_tag:
            img_elements = img_tag.find_all('img')
            for img in img_elements:
                src = img.get('data-srcset')  # Use get method with a default value
                if src not in images:  # Check for duplicates before appending
                    images.append(src)
        print(images[:-1])
        images = images[:-1]
        
        tecdiv_list = soup.find('div', {'class': lambda x: x and 'wrapper-product-detail-info' in x})
        property_list = tecdiv_list.find('ul', {'class':'pdetail-property-list'})

        if property_list:
            key_value_string = ""

            for li_element in property_list.find_all('li'):
                span_elements = li_element.find_all('span')

                if len(span_elements) == 2:
                    key = span_elements[0].get_text(strip=True)
                    value = span_elements[1].get_text(strip=True)

                    key_value_string += f"{key}: {value} <br>"

        tech_spec_data = key_value_string

        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        # İstek başarısızsa
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None
