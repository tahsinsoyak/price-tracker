from flask import Flask, render_template
from peewee import SqliteDatabase, Model, CharField, IntegerField, TextField, DateTimeField
import schedule
import time
from datetime import datetime
from peewee import DoesNotExist
from flask import request
from flask import redirect
from flask import url_for


app = Flask(__name__)

# SQLite veritabanı bağlantısı
db = SqliteDatabase('products.db')

class Product(Model):
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
    products = Product.select()

    # Ürünleri HTML şablonuna gönder
    return render_template('index.html', products=products)

@app.route('/compare_prices/<product_id>')
def compare_prices(product_id):
    # Fiyatları karşılaştırma sorgusu
    product = Product.get_by_id(product_id)
    same_product_prices = Product.select().where(
        (Product.title == product.title) & 
        (Product.product_company != product.product_company)
    )

    # Fiyat karşılaştırma sonuçlarını HTML şablonuna gönder
    return render_template('compare_prices.html', product=product, same_product_prices=same_product_prices)


@app.route('/search', methods=['POST'])
def search_products():
    search_term = request.form['search']
    products = Product.select().where(Product.title.contains(search_term))
    return render_template('index.html', products=products)

from scrapers.amazon_scraper import amazon_scraper
from scrapers.trendyol_scraper import trendyol_scraper
def scrape_data():
    # Example URLs
    amazon_url = 'https://amzn.eu/d/bqp120C'
    trendyol_url = 'https://www.trendyol.com/jbl/tune760btnc-kulaklik-anc-ct-oe-siyah-p-152213494?boutiqueId=61&merchantId=152041'

    # Scrape data from Amazon
    amazon_data = amazon_scraper(amazon_url)
    update_or_create_product(amazon_data, 'amazon')

    # Scrape data from Trendyol
    trendyol_data = trendyol_scraper(trendyol_url)
    update_or_create_product(trendyol_data, 'trendyol')


def update_or_create_product(data, company):
    try:
        # Try to get an existing product by title
        product = Product.get(Product.title == data['title'])

        # If the product exists, update its fields
        product.price = data['price']
        product.images = str(data['images'])
        product.tech_spec_data = str(data['tech_spec_data'])
        product.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product.save()
    except DoesNotExist:
        # If the product doesn't exist, create a new one
        Product.create(
            title=data['title'],
            price=data['price'],
            images=str(data['images']),
            tech_spec_data=str(data['tech_spec_data']),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            product_company=company
        )

# Define the route for updating prices
@app.route('/update_prices', methods=['POST'])
def update_prices():
    scrape_data()  # Call the function to update prices
    return render_template('index.html', products=Product.select())


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        # Get form data
        url = request.form['url']

        # Scrape data using the appropriate scraper function
        product_data = trendyol_scraper(url)  # Replace with the actual scraper function

        # Store scraped data in the database
        new_product = Product.create(
            title=product_data['title'],  # If available, adjust accordingly
            price=product_data['price'],
            images=str(product_data['images']),
            tech_spec_data=str(product_data['tech_spec_data']),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            product_company='amazon'  # Specify the product company
        )

        return redirect(url_for('index'))

    return render_template('add_product.html')


# Flask uygulamasını çalıştırdıktan sonra zamanlanmış görevleri başlat
if __name__ == '__main__':
    app.run(debug=True)

    # scrape_data fonksiyonunu her saat başı çalıştır
    schedule.every().hour.do(scrape_data)

    while True:
        schedule.run_pending()
        time.sleep(1)
