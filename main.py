import aiohttp
import asyncio
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import re
import logging

logging.basicConfig(filename='scraper.log', level=logging.INFO)

Base = declarative_base()

class ProductPrice(Base):
    __tablename__ = 'product_prices'
    id = Column(Integer, primary_key=True)
    website = Column(String)
    product_name = Column(String)
    price = Column(Float)

class ProductPriceHistory(Base):
    __tablename__ = 'product_price_history'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    website = Column(String)
    product_name = Column(String)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Set up the database
engine = create_engine('sqlite:///product_prices.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class Scraper:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    async def fetch(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            return await response.text()

    async def scrape_site(self, site, search_url, parse_function):
        async with aiohttp.ClientSession() as session:
            response = await self.fetch(session, search_url)
            return parse_function(response, site)

    def parse_amazon(self, html, site):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for item in soup.select('.s-main-slot .s-result-item'):
            title = item.select_one('h2 .a-link-normal')
            price = item.select_one('.a-price .a-offscreen')
            if title and price:
                product_title = title.get_text().strip()
                product_price = float(price.get_text().strip().replace('$', '').replace(',', ''))
                products.append(ProductPrice(website=site, product_name=product_title, price=product_price))
        return products

    def parse_ebay(self, html, site):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for item in soup.select('.s-item'):
            title = item.select_one('.s-item__title')
            price = item.select_one('.s-item__price')
            if title and price:
                product_title = title.get_text().strip()
                product_price = float(re.findall(r'\d+\.\d+', price.get_text().strip().replace(',', ''))[0])
                products.append(ProductPrice(website=site, product_name=product_title, price=product_price))
        return products

    def parse_newegg(self, html, site):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for item in soup.select('.item-cell'):
            title = item.select_one('.item-title')
            price = item.select_one('.price .price-current')
            if title and price:
                product_title = title.get_text().strip()
                price_numeric_part = re.search(r'\d+\.\d+', price.get_text().strip())
                if price_numeric_part:
                    product_price = float(price_numeric_part.group())
                    products.append(ProductPrice(website=site, product_name=product_title, price=product_price))
        return products

    async def scrape_all(self, product_name):
        sites = {
            'Amazon': (f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}", self.parse_amazon),
            'Ebay': (f"https://www.ebay.com/sch/i.html?_nkw={product_name.replace(' ', '+')}", self.parse_ebay),
            'Newegg': (f"https://www.newegg.com/p/pl?d={product_name.replace(' ', '+')}", self.parse_newegg)
        }
        tasks = [self.scrape_site(site, url, parser) for site, (url, parser) in sites.items()]
        results = await asyncio.gather(*tasks)
        for products in results:
            if products:
                session.bulk_save_objects(products)
                session.commit()


def show_database_contents():
    print("Showing database contents...")
    products = session.query(ProductPrice).order_by(ProductPrice.price).all()
    for product in products:
        print(f"ID: {product.id}, Website: {product.website}, Product: {product.product_name}, Price: ${product.price}")


bot = Scraper()
# Example usage
asyncio.run(bot.scrape_all('RTX 4080 Graphics card'))
show_database_contents()
