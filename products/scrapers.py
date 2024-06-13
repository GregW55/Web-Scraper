import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from django.db import models
from .models import ProductPrice  # Assuming your ProductPrice model is already defined in models.py

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

    def parse_price(self, price_str):
        # Remove any currency symbols and commas, then convert to float
        price_str = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(price_str)
        except ValueError:
            return None

    def parse_amazon(self, html, site):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for item in soup.select('.s-main-slot .s-result-item'):
            title = item.select_one('h2 .a-link-normal')
            price = item.select_one('.a-price .a-offscreen')
            image = item.select_one('.s-image')
            if title and price and image:
                product_title = title.get_text().strip()
                product_price = self.parse_price(price.get_text().strip())
                image_url = image['src']
                if product_price is not None:
                    products.append(ProductPrice(product_name=product_title, price=product_price, url=title['href'], image_url=image_url, source=site))
        return products

    def parse_ebay(self, html, site):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for item in soup.select('.s-item'):
            title = item.select_one('.s-item__title')
            price = item.select_one('.s-item__price')
            image = item.select_one('.s-item__image-img')
            if title and price and image:
                product_title = title.get_text().strip()
                product_price = self.parse_price(price.get_text().strip())
                image_url = image['src']
                if product_price is not None:
                    products.append(ProductPrice(product_name=product_title, price=product_price, url=item.select_one('.s-item__link')['href'], image_url=image_url, source=site))
        return products

    def parse_newegg(self, html, site):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for item in soup.select('.item-cell'):
            title = item.select_one('.item-title')
            price = item.select_one('.price .price-current')
            image = item.select_one('.item-img img')
            if title and price and image:
                product_title = title.get_text().strip()
                price_text = price.get_text().strip()
                product_price = self.parse_price(price_text)
                image_url = image['src']
                if product_price is not None:
                    products.append(ProductPrice(product_name=product_title, price=product_price, url=title['href'], image_url=image_url, source=site))
        return products

    def parse_target(self, html, site):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for item in soup.select('.h-padding-a-tight'):
            title = item.select_one('.Link__StyledLink')
            price = item.select_one('.h-text-bs')
            image = item.select_one('.h-padding-a-none img')
            if title and price and image:
                product_title = title.get_text().strip()
                product_price = self.parse_price(price.get_text().strip())
                image_url = image['src']
                if product_price is not None:
                    products.append(ProductPrice(product_name=product_title, price=product_price, url='https://target.com' + title['href'], image_url=image_url, source=site))
        return products

    def parse_bestbuy(self, html, site):
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for item in soup.select('.sku-item'):
            title = item.select_one('.sku-header a')
            price = item.select_one('.priceView-customer-price span')
            image = item.select_one('.product-image img')
            if title and price and image:
                product_title = title.get_text().strip()
                product_price = self.parse_price(price.get_text().strip())
                image_url = image['src']
                if product_price is not None:
                    products.append(ProductPrice(product_name=product_title, price=product_price, url='https://bestbuy.com' + title['href'], image_url=image_url, source=site))
        return products

    async def scrape_all(self, product_name):
        sites = {
            'Amazon': (f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}", self.parse_amazon),
            'Ebay': (f"https://www.ebay.com/sch/i.html?_nkw={product_name.replace(' ', '+')}", self.parse_ebay),
            'Newegg': (f"https://www.newegg.com/p/pl?d={product_name.replace(' ', '+')}", self.parse_newegg),
            'Target': (f"https://www.target.com/s?searchTerm={product_name.replace(' ', '+')}", self.parse_target),
            'BestBuy': (f"https://www.bestbuy.com/site/searchpage.jsp?st={product_name.replace(' ', '+')}", self.parse_bestbuy)
        }
        tasks = [self.scrape_site(site, url, parser) for site, (url, parser) in sites.items()]
        results = await asyncio.gather(*tasks)
        products = [product for result in results for product in result]
        return products
