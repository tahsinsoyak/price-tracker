import requests
from bs4 import BeautifulSoup
import random

def mavi_scraper(product_url):
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
        title = soup.find('h1', {'class': 'product__title'}).get_text().strip()
        price = soup.find('div', {'class': 'product__product-pricing'})
        price = price.find('span', {'class': 'price'}).get_text().strip()

        images = []  # Use a different variable name
        img_tag = soup.find('div', {'class': 'product__gallery-slider'})
        if img_tag:
            img_elements = img_tag.find_all('img')
            for img in img_elements:
                src = img.get('src')  # Use get method with a default value
                if src not in images:  # Check for duplicates before appending
                    images.append('https:'+src)

        tecdiv_list = soup.find('div', {'class': 'product__features--content'})

        if tecdiv_list:
            # Extracting product description
            product_description = tecdiv_list.find('span', {'class': 'product-features-description'}).get_text(strip=True)

            # Extracting product code
            product_code_element = tecdiv_list.find('div', {'class': 'product__features__product-code'})
            if product_code_element:
                product_code = product_code_element.find('p').get_text(strip=True)

            # Extracting fabric information
            fabric_element = tecdiv_list.find('div', {'class': 'product__features__detay'})
            if fabric_element:
                fabric_info = fabric_element.find('ul').get_text(strip=True)
            # Extracting model measurements
            model_measurements_element = tecdiv_list.find('div', {'class': 'product__features__detay'})
            if model_measurements_element:
                model_measurements = model_measurements_element.find_all('p')
        else:
            print("Product details not found.")

        # teknik özellikleri her birine <br> ile ayrılmış bir şekilde alıyoruz
        tech_spec_data = product_description + '<br>' + product_code + '<br>' + fabric_info + '<br>' + '<br>'.join([measurement.get_text(strip=True) for measurement in model_measurements])
        # Elde edilen verileri sözlük olarak döndür
        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        # İstek başarısızsa
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None

