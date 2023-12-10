from peewee import Model, SqliteDatabase, CharField, TextField, DateTimeField
from datetime import datetime



# Database
db = SqliteDatabase('products.db')

# Product model
class Product(Model):
    title = CharField()
    price = CharField()
    images = TextField()  # Use TextField instead of JSONField
    tech_spec_data = TextField()  # Use TextField instead of JSONField
    created_at = DateTimeField()
    updated_at = DateTimeField()
    product_company = CharField()

    class Meta:
        database = db

# Connect to the database and create tables
db.connect()

# Drop existing table if it exists
if Product.table_exists():
    db.drop_tables([Product])

# Create a new table
db.create_tables([Product])

# Scraping
from scrapers.amazon_scraper import amazon_scraper

amazon_url = 'https://amzn.eu/d/bqp120C'
amazon_data = amazon_scraper(amazon_url)

from scrapers.trendyol_scraper import trendyol_scraper
# Example usage
trendyol_url = 'https://www.trendyol.com/jbl/tune760btnc-kulaklik-anc-ct-oe-siyah-p-152213494?boutiqueId=61&merchantId=152041'
trendyol_data = trendyol_scraper(trendyol_url)

# Store scraped data in the database
amazon_product = Product.create(
    title=amazon_data['title'],
    price=amazon_data['price'],
    images=str(amazon_data['images']),
    tech_spec_data=str(amazon_data['tech_spec_data']),
    created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    product_company='amazon'  # Specify the product company
)

trendyol_product = Product.create(
    title=trendyol_data['title'],
    price=trendyol_data['price'],
    images=str(trendyol_data['images']),
    tech_spec_data=str(trendyol_data['tech_spec_data']),
    created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    product_company='trendyol'  # Specify the product company
)

# Close the database connection
db.close()
