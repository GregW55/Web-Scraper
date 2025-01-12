# Price Tracker
# Price Tracker is a web application designed to scrape and track product prices from various e-commerce websites. The application leverages asynchronous scraping with aiohttp and BeautifulSoup to gather product prices from Amazon, eBay, and Newegg. It stores the data in a SQLite database using SQLAlchemy and provides a Django-based interface for managing and viewing the tracked prices.

# Features:

# Asynchronous Scraping:
Utilizes aiohttp for asynchronous HTTP requests to scrape product prices efficiently.

#HTML Parsing: 
Uses BeautifulSoup to parse HTML content and extract product information.

# Database Integration: 
Stores product prices and historical price data in a SQLite database using SQLAlchemy.

# Django Web Interface:
Provides a web interface for managing and viewing tracked prices.

# Requirements:

Python 3.8+

Libraries: aiohttp, asyncio, beautifulsoup4, sqlalchemy, re, logging, Django

# Installation

Clone the Repository:

git clone https://github.com/gregW55/web-scraper

cd price_tracker

# Install Dependencies:

pip install aiohttp beautifulsoup4 sqlalchemy Django

# Set Up Django:

django-admin startproject web_scraper

cd web_scraper

python manage.py migrate

# Database Setup

The application uses SQLite for storing product prices. The database schema is defined using SQLAlchemy ORM.

Create the Database:

python -c "from main import Base, engine; Base.metadata.create_all(engine)"

# Usage

Run the Scraper:

python main.py

View Database Contents:

python main.py

Run Django Server:

python manage.py runserver


# Classes:

ProductPrice: SQLAlchemy model for storing current product prices.
ProductPriceHistory: SQLAlchemy model for storing historical product prices.
Scraper: Contains methods for fetching and parsing product prices from various websites.
Functions:

show_database_contents(): Displays the contents of the product prices database.
manage.py
Django's command-line utility for administrative tasks.

price_tracker/settings.py
Django settings for the project. Make sure to configure your database settings here.

price_tracker/urls.py
URL configuration for the Django project.

# Example Output

Showing database contents...

ID: 1, Website: Amazon, Product: NVIDIA RTX 4080, Price: $699.99

ID: 2, Website: Ebay, Product: NVIDIA RTX 4080, Price: $689.99

ID: 3, Website: Newegg, Product: NVIDIA RTX 4080, Price: $695.00

# Logging
Logs are stored in scraper.log to help with debugging and monitoring the scraping process.

#Notes
Ensure you comply with the terms of service of the websites you are scraping.

The scraper is configured for Amazon, eBay, and Newegg. You can extend it to other websites by adding new parsing functions.

Always test the scraper in a controlled environment to avoid being blocked by the websites.
