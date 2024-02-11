import requests
from bs4 import BeautifulSoup
import random

def teknosa_scraper(product_url):
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
        title = soup.find('span', {'class': lambda x: x and 'replaceName' in x}).get_text().strip()
        price = soup.find('span', {'class': lambda x: x and 'prc-last' in x}).get_text().strip()

        images = []
        img_tag = soup.find('div', {'class': lambda x: x and 'pdp-gallery' in x})
        if img_tag:
            img_elements = img_tag.find_all('img')
            for img in img_elements:
                src = img.get('data-srcset')  # Use get method with a default value
                if src not in images:  # Check for duplicates before appending
                    images.append(src)
        tecdiv_list = soup.find('div', {'class': lambda x: x and 'pdp-acc-body' in x})
        tech_spec_data = []

        # Find the div with class 'ptf-body'
        ptf_body_div = tecdiv_list.find('div', {'class': 'ptf-body'})

        # Find all tables within the 'ptf-body' div
        tables = ptf_body_div.find_all('table')

        # Iterate through each table to extract key-value pairs
        for table in tables:
            # Find all rows within the table
            rows = table.find_all('tr')

            for row in rows:
                # Extract the cells from the row
                cells = row.find_all(['th', 'td'])

                # Extract key-value pairs
                for i in range(0, len(cells), 2):
                    key = cells[i].get_text(strip=True)
                    value = cells[i + 1].get_text(strip=True)
                    tech_spec_data.append(f"{key}: {value}")

        # Join the key-value pairs with '<br>'
        formatted_tech_spec_data = '<br>'.join(tech_spec_data)
        tech_spec_data = formatted_tech_spec_data

        # Elde edilen verileri sözlük olarak döndür
        return {'url': product_url,'title': title, 'price': price, 'images': images, 'tech_spec_data': tech_spec_data}
    else:
        # İstek başarısızsa
        print(f"Hata: Sayfa çekilemedi. Durum Kodu: {response.status_code}")
        return None
