# Gerekli kütüphaneleri içe aktarın
import requests
from bs4 import BeautifulSoup
import random

# Trendyol ürün bilgileri çıkartma fonksiyonu
def trendyol_scraper(product_url):
    # Kullanıcı agent'ları dosyasından oku
    with open('user_agents/user-agents.txt', 'r') as file:
        user_agents = file.readlines()

    # Rastgele bir kullanıcı agent seç
    random_user_agent = random.choice(user_agents)
    headers = {'User-Agent': random_user_agent.strip()}  # Rastgele agent ile başlık oluştur
    response = requests.get(product_url, headers=headers)  # Sayfayı isteğini gerçekleştir

    # Sayfa başarıyla çekildiyse
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')  # BeautifulSoup nesnesi oluştur

        # Başlık elementini bul
        title_element = soup.find('h1', {'class': 'pr-new-br'})
        title = title_element.text.strip() if title_element else 'Başlık bulunamadı'

        # Fiyat elementini bul
        price_element = soup.find('span', {'class': 'prc-dsc'})
        price = price_element.text.strip() if price_element else 'Fiyat bulunamadı'



        # Resim elementlerini bul ve temizle
        image_elements = soup.find('div', {'class': 'gallery-container'}).find_all('img', {'loading': 'lazy'})
        images = [img['src'] for img in image_elements if 'stamp' not in img['src'].lower()]

        for i in range(len(images)):
            images[i] = images[i].replace('mnresize/1200/1800/', '')

        # Teknik özellikleri veya diğer bilgileri çıkartmak için
        tech_spec_data = ""
        tech_spec_section = soup.find('ul', {'class': 'detail-desc-list'})

        if tech_spec_section:
            for li_element in tech_spec_section.find_all('li'):
                if li_element:
                    text_content = li_element.get_text(strip=True)
                    tech_spec_data += f"{text_content}<br>"
        else:
            tech_spec_data = None
            print("Teknik özellik bölümü sayfada bulunamadı.")

            
        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None
