from flask import Flask, render_template, request, redirect, url_for # Import Flask, render_template, and request, redirect, and url_for functions
from peewee import SqliteDatabase, Model, CharField, DoesNotExist, TextField, DateTimeField # Import the database and model fields
import schedule # Import the schedule library for scheduling tasks
import time
from datetime import datetime 
from scrapers.amazon_scraper import amazon_scraper
from scrapers.trendyol_scraper import trendyol_scraper
from scrapers.hepsiburada_scraper import hepsiburada_scraper
from scrapers.defacto_scraper import defacto_scraper
from scrapers.lcwaikiki_scraper import lcwaikiki_scraper
from scrapers.koton_scraper import koton_scraper
from scrapers.boyner_scraper import boyner_scraper
from scrapers.mavi_scraper import mavi_scraper
from scrapers.teknosa_scraper import teknosa_scraper
from scrapers.vatan_scraper import vatan_scraper
from scrapers.mediamarkt_scraper import mediamarkt_scraper

app = Flask(__name__)

# SQLite veritabanı bağlantısı
db = SqliteDatabase('products.db')

class Product(Model):
    url = TextField()
    title = CharField()
    price = CharField()
    images = TextField()  
    tech_spec_data = TextField()  
    created_at = DateTimeField()
    updated_at = DateTimeField()
    product_company = CharField()

    class Meta:
        database = db

# Tabloyu oluştur
db.connect()
db.create_tables([Product], safe=True)

@app.route('/')
def index():
    # Veritabanından ürünleri çek
    products = Product.select().order_by(Product.updated_at.desc())
    # Ürünleri HTML şablonuna gönder
    return render_template('index.html', products=products)


@app.route('/compare')
def compare_products():
    # Fiyat karşılaştırması yapılacak ürünlerin ID'lerini al
    product_ids = request.args.get('ids').split(',')
    products = [Product.get_by_id(id) for id in product_ids]
    return render_template('compare_prices.html', products=products)


@app.route('/search', methods=['POST'])
def search_products():
    # Arama kelimesini al ve ürünleri bul
    
    search_term = request.form['search']
    products = Product.select().where(Product.title.contains(search_term))
    return render_template('index.html', products=products)


#  Ürünü sil
@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    try:
        product = Product.get(Product.id == id)
        product.delete_instance()  # Sil
        return redirect(url_for('index'))  #    Ana sayfaya yönlendir
    except DoesNotExist:
        return render_template('error.html', message='Ürün bulunamadı!')  #  Ürün bulunamadı hatası ver



#  Ürün detay sayfası
@app.route('/product_detail/<int:id>')
def product_detail(id):
    try:
        #  Ürünü ID'ye göre bul
        product = Product.get(Product.id == id)
        return render_template('product_detail.html', product=product)
    except DoesNotExist:
        return render_template('error.html', message='Ürün bulunamadı!')

#  Ürünü güncelleme sayfası
@app.route('/update_product_prices/<int:id>', methods=['POST'])
def update_product_prices(id):
    try:
        #   Ürünü ID'ye göre bul
        product = Product.get(Product.id == id)

        #  Ürünü güncelle
        try:
            if product.product_company == 'trendyol':
                product_data = trendyol_scraper(product.url)
            elif product.product_company == 'amazon':
                product_data = amazon_scraper(product.url)
            elif product.product_company == 'hepsiburada':
                product_data = hepsiburada_scraper(product.url)
            elif product.product_company == 'defacto':
                product_data = defacto_scraper(product.url)
            elif product.product_company == 'lcwaikiki':
                product_data = lcwaikiki_scraper(product.url)
            elif product.product_company == 'koton':
                product_data = koton_scraper(product.url)
            elif product.product_company == 'boyner':
                product_data = boyner_scraper(product.url)
            elif product.product_company == 'mavi':
                product_data = mavi_scraper(product.url)
            elif product.product_company == 'teknosa':
                product_data = teknosa_scraper(product.url)
            elif product.product_company == 'vatan':
                product_data = vatan_scraper(product.url)
            elif product.product_company == 'mediamarkt':
                product_data = mediamarkt_scraper(product.url)
            else:
                return render_template('error.html', message=' Ürün bulunamadı!')
        except Exception as e:
            #   Hata mesajı göster
            print(f"Scraping error: {str(e)}")
            #  Hata mesajı göster
            return render_template('error_popup.html', message='Bir hata oluştu. Lütfen 15 saniye sonra tekrar deneyin.')

        # Ürünü güncelle
        product.price = product_data.get('price', '')
        product.images = str(product_data.get('images', ''))
        product.tech_spec_data = str(product_data.get('tech_spec_data', ''))
        product.updated_at = datetime.now()
        product.save()

        return redirect(url_for('index'))  #  Ana sayfaya yönlendir
    except DoesNotExist:
        return render_template('error.html', message=' Ürün Bulunamadı!')  #  Ürün bulunamadı hatası ver

#  Hata sayfası
@app.route('/error_popup')
def error_popup():
    return render_template('error_popup.html', message='Bir hata oluştu. Lütfen 15 saniye sonra tekrar deneyin.')

def update_or_create_product(data, company):
    try:
        #  ürünün url'i ile ürün bul varmı yokmu kontrol et
        product = Product.get(Product.url == data['url'])

        #  ürünü güncelle
        product.price = data['price']
        product.images = str(data['images'])
        product.tech_spec_data = str(data['tech_spec_data'])
        product.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product.save()
    except DoesNotExist:
        #  ürünü oluştur
        Product.create(
            url=data['url'],
            title=data['title'],
            price=data['price'],
            images=str(data['images']),
            tech_spec_data=str(data['tech_spec_data']),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            product_company=company
        )


#  Ürünleri güncelleme fonksiyonu
@app.route('/update_prices', methods=['GET', 'POST'])
def update_prices():
    try:    # Ürünleri çek
        products = Product.select()

        #  Her ürün için scraper'ı çalıştır
        for product in products:
            if product.product_company == 'amazon':
                data = amazon_scraper(product.url)
            elif product.product_company == 'trendyol':
                data = trendyol_scraper(product.url)
            elif product.product_company == 'hepsiburada':
                data = hepsiburada_scraper(product.url)
            elif product.product_company == 'defacto':
                data = defacto_scraper(product.url)
            elif product.product_company == 'lcwaikiki':
                data = lcwaikiki_scraper(product.url)
            elif product.product_company == 'koton':
                data = koton_scraper(product.url)
            elif product.product_company == 'boyner':
                data = boyner_scraper(product.url)
            elif product.product_company == 'mavi':
                data = mavi_scraper(product.url)
            elif product.product_company == 'teknosa':
                data = teknosa_scraper(product.url)
            elif product.product_company == 'vatan':
                data = vatan_scraper(product.url)
            elif product.product_company == 'mediamarkt':
                data = mediamarkt_scraper(product.url)
            else:
                continue

            #  Ürünü güncelle veya oluştur
            update_or_create_product(data, product.product_company)
    except Exception as e:
        #  Hata mesajı göster
        print(f"Error: {str(e)}")
        return render_template('error_popup.html', message=' Bir hata oluştu. Lütfen 15 saniye sonra tekrar deneyin. Ürünlerin bazıları güncellenmeyebilir.')

    return render_template('index.html', products=Product.select())

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            url2 = request.form['url']

            try:
                # Check if product already exists
                
                existing_product = Product.get(url=url2)

                if existing_product:
                    return render_template('error_popup.html', message=' Ürün zaten mevcut!')

            except DoesNotExist:
                # Product doesn't exist, continue with scraping and storing
                if 'trendyol' in url2:
                    product_data = trendyol_scraper(url2)
                    product_company = 'trendyol'
                elif 'amazon' in url2:
                    product_data = amazon_scraper(url2)
                    product_company = 'amazon'
                elif 'hepsiburada' in url2:
                    product_data = hepsiburada_scraper(url2)
                    product_company = 'hepsiburada'
                elif 'defacto' in url2:
                    product_data = defacto_scraper(url2)
                    product_company = 'defacto'
                elif 'lcwaikiki' in url2:
                    product_data = lcwaikiki_scraper(url2)
                    product_company = 'lcwaikiki'
                elif 'koton' in url2:
                    product_data = koton_scraper(url2)
                    product_company = 'koton'
                elif 'boyner' in url2:
                    product_data = boyner_scraper(url2)
                    product_company = 'boyner'
                elif 'mavi' in url2:
                    product_data = mavi_scraper(url2)
                    product_company = 'mavi'
                elif 'teknosa' in url2:
                    product_data = teknosa_scraper(url2)
                    product_company = 'teknosa'
                elif 'vatan' in url2:
                    product_data = vatan_scraper(url2)
                    product_company = 'vatan'
                elif 'mediamarkt' in url2:
                    product_data = mediamarkt_scraper(url2)
                    product_company = 'mediamarkt'
                else:
                    raise Exception(' Ürün bulunamadı!')

                new_product = Product.create(
                    url=url2,
                    title=product_data.get('title', ''),
                    price=product_data.get('price', ''),
                    images=str(product_data.get('images', '')),
                    tech_spec_data=str(product_data.get('tech_spec_data', '')),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    product_company=product_company
                )

                return redirect(url_for('index'))

        except Exception as e:
            print(f"Error: {str(e)}")
            return redirect(url_for('error_popup'))

    return render_template('add_product.html', message='')


# Flask uygulamasını çalıştırdıktan sonra zamanlanmış görevleri başlat
if __name__ == '__main__':
    app.run(debug=True)

    # scrape_data fonksiyonunu her saat başı çalıştır
    schedule.every().hour.do(update_prices)

    while True:
        schedule.run_pending()
        time.sleep(1)
