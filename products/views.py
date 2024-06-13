from django.shortcuts import render
from .scrapers import Scraper

async def product_list(request):
    query = request.GET.get('query', '')
    scraper = Scraper()
    products = await scraper.scrape_all(query)
    return render(request, 'products/product_list.html', {'products': products, 'query': query})
