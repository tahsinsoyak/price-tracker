from flask import Flask, render_template, request, redirect, url_for
from peewee import SqliteDatabase, Model, CharField, DoesNotExist, TextField, DateTimeField
import schedule
import time
from datetime import datetime 
from scrapers.amazon_scraper import amazon_scraper
from scrapers.trendyol_scraper import trendyol_scraper
import re
import json
import ast
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


# Route to delete a product
@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    try:
        # Try to get the product by ID
        product = Product.get(Product.id == id)
        product.delete_instance()  # Delete the product from the database
        return redirect(url_for('index'))  # Redirect to the main page after deletion
    except DoesNotExist:
        return render_template('error.html', message='Product not found')  # Handle if the product doesn't exist



# Route to view product details
@app.route('/product_detail/<int:id>')
def product_detail(id):
    try:
        # Try to get the product by ID
        product = Product.get(Product.id == id)
        return render_template('product_detail.html', product=product)
    except DoesNotExist:
        return render_template('error.html', message='Product not found')

# Route to update prices for a specific product
@app.route('/update_product_prices/<int:id>', methods=['POST'])
def update_product_prices(id):
    try:
        # Try to get the product by ID
        product = Product.get(Product.id == id)

        # Check the product's company and update prices accordingly
        try:
            if product.product_company == 'trendyol':
                product_data = trendyol_scraper(product.url)
            elif product.product_company == 'amazon':
                product_data = amazon_scraper(product.url)
            else:
                return render_template('error.html', message='Unsupported platform')
        except Exception as e:
            # Handle the scraping error
            print(f"Scraping error: {str(e)}")
            # Show a JavaScript popup toast message
            return render_template('error_popup.html', message='An error occurred while updating prices. Please try again after 15 seconds.')

        # Update the product's fields
        product.price = product_data.get('price', '')
        product.images = str(product_data.get('images', ''))
        product.tech_spec_data = str(product_data.get('tech_spec_data', ''))
        product.updated_at = datetime.now()
        product.save()

        return redirect(url_for('index'))  # Redirect to the main page after updating prices
    except DoesNotExist:
        return render_template('error.html', message='Product not found')  # Handle if the product doesn't exist

# Create a new route for the error popup template
@app.route('/error_popup')
def error_popup():
    return render_template('error_popup.html', message='An error occurred. Please try again after 15 seconds.')

def update_or_create_product(data, company):
    try:
        # Try to get an existing product by URL
        product = Product.get(Product.url == data['url'])

        # If the product exists, update its fields
        product.price = data['price']
        product.images = str(data['images'])
        product.tech_spec_data = str(data['tech_spec_data'])
        product.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product.save()
    except DoesNotExist:
        # If the product doesn't exist, create a new one
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


# Define the route for updating prices
@app.route('/update_prices', methods=['GET', 'POST'])
def update_prices():
    try:    # Get all products from the database
        products = Product.select()

        # Iterate over products and update prices based on the company
        for product in products:
            if product.product_company == 'amazon':
                data = amazon_scraper(product.url)
            elif product.product_company == 'trendyol':
                data = trendyol_scraper(product.url)
            else:
                # Handle other platforms or show an error message
                continue

            # Update or create the product in the database
            update_or_create_product(data, product.product_company)
    except Exception as e:
        # Handle the error and redirect to the error popup route
        print(f"Error: {str(e)}")
        return render_template('error_popup.html', message='An error occurred while updating prices. Please try again after 15 seconds. Some Products may not be updated.')

    return render_template('index.html', products=Product.select())

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            # Get form data
            url = request.form['url']

            # Check the URL for the platform and use the appropriate scraper
            if 'trendyol' in url:
                product_data = trendyol_scraper(url)
                product_company = 'trendyol'
            elif 'amazon' in url:
                product_data = amazon_scraper(url)
                product_company = 'amazon'
            else:
                # Handle unsupported platforms or show an error message
                raise Exception('Unsupported platform')

            # Store scraped data in the database
            new_product = Product.create(
                url=url,
                title=product_data.get('title', ''),  # Replace with the actual key
                price=product_data.get('price', ''),
                images=str(product_data.get('images', '')),
                tech_spec_data=str(product_data.get('tech_spec_data', '')),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                product_company=product_company
            )

            return redirect(url_for('index'))

        except Exception as e:
            # Handle the error and redirect to the error popup route
            print(f"Error: {str(e)}")
            return redirect(url_for('error_popup'))

    return render_template('add_product.html')
# Flask uygulamasını çalıştırdıktan sonra zamanlanmış görevleri başlat
if __name__ == '__main__':
    app.run(debug=True)

    # scrape_data fonksiyonunu her saat başı çalıştır
    schedule.every().hour.do(update_prices)

    while True:
        schedule.run_pending()
        time.sleep(1)
