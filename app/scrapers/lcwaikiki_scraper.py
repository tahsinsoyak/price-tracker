import requests
from bs4 import BeautifulSoup
import random

def lcwaikiki_scraper(product_url):
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
        title = soup.find('div', {'class': 'product-title'}).get_text().strip()
        price = soup.find('div', {'class': 'basket-discount'})
        if price == None:
            price = soup.find('span', {'class': 'advanced-price'}).get_text().strip()
        else:
            price = price.get_text().strip()

        images = []
        img_tag = soup.find('div', {'id': 'productSliderPhotos'})
        if img_tag:
            img_elements = img_tag.find_all('img')
            for img in img_elements:
                images = [img['data-src'] for img in soup.find_all('img') if 'data-src' in img.attrs and img['data-src'].startswith('https://img-lcwaikiki.mncdn.com/mnresize/1020/1360/')]

        tech_spec_data = ""
        tecdiv_list = soup.find_all('div', {'id': 'collapseOne'})
        for tecdiv in tecdiv_list:
            panel_body = tecdiv.find('div', class_='panel-body')
            if panel_body is not None:
                for col_div in panel_body.find_all('div', class_='col-xs-12'):
                    key_element = col_div.find('h5')
                    value_elements = col_div.find_all(['li', 'p', 'b'])
                    if key_element is not None and value_elements:
                        key = key_element.get_text().strip()
                        values = '<br>'.join(value.get_text().strip() for value in value_elements)
                        tech_spec_data += f"{key}: {values}<br>"

                    elif not key_element and value_elements:
                        values = '<br>'.join(value.get_text().strip() for value in value_elements)
                        tech_spec_data += f"No Key: {values}<br>"
                    else:
                        continue
        # Elde edilen verileri sözlük olarak döndür
        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        # İstek başarısızsa
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None

