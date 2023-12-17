import requests
from bs4 import BeautifulSoup
import random

def amazon_scraper(product_url):
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
        title = soup.find('span', {'id': 'productTitle'}).get_text().strip()
        price = soup.find('span', {'class': 'a-offscreen'}).get_text().strip()
        images = []

        # Sayfadaki tüm ürün resimlerini bul ve listeye ekle
        li_elements = soup.find_all('li', {'class': 'image'})
        for li_element in li_elements:
            # li öğesi içinde img etiketini bul
            img = li_element.find('img')

            # Eğer img etiketi bulunduysa ve 'src' özelliği varsa
            if img and 'src' in img.attrs:
                src = img['src']
                images.append(src)

        # Ürünün teknik özelliklerini içeren tabloyu bul
        tech_spec_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})

        # Eğer tablo bulunduysa
        if tech_spec_table:
            tech_spec_data = ""

            # Tablodaki her satır için
            for row in tech_spec_table.find_all('tr'):
                key = row.find(['th']).get_text().strip()
                value = row.find(['td']).get_text().strip()
                tech_spec_data += f"{key}: {value}<br>"
        else:
            # Eğer tablo bulunamazsa
            tech_spec_data = None
            print("Teknik özellik bölümü sayfada bulunamadı.")

        # Elde edilen verileri sözlük olarak döndür
        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        # İstek başarısızsa
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None
