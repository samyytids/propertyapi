import django
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'api.settings'
django.setup()

from scrapy.spiders import XMLFeedSpider
from scrapy.selector import Selector
from scrapy import Request
from backend.models import *
from scrapers.scrapers.spiders.sitemap import SitemapSpider
from scrapers.scrapers.spiders.property_pal import PropertyPalSpider
from scrapers.scrapers.spiders.rightmove import RightmoveSpider
from scrapers.scrapers.spiders.image import ImageSpider
from scrapers.scrapers.spiders.epc import EpcSpider
from scrapy.crawler import CrawlerProcess
from django.db.models import Q

process = CrawlerProcess(settings={
        "LOG_LEVEL":"INFO",
        "HTTPCACHE_ENABLED":False,
        "HTTPERROR_ALLOWED_CODES": [410,404],
        "CONCURRENT_REQUESTS" : 16,
    })

if sys.argv[1][0] == "s":
    
    process.crawl(SitemapSpider)
    
elif sys.argv[1][0] == "p":
    filter = (Q(property__icontains="P") & Q(stc = False)) & Q(un_published = False)
    properties = Property.objects.filter(filter).values_list("property", "url", "scraped_before")
    properties = sorted(properties, key=lambda x: x[2])
    mapper = {}
    urls = []
    
    for property in properties:
        mapper[property[1]] = {
            "property_id": property[0],
            "scraped_before": property[2],
        }
        urls.append(property[1])
    
    process.settings["ITEM_PIPELINES"] = {
        "scrapers.scrapers.pipelines.ScrapersPipeline": 100
    }
    
    num_urls = len(urls)
    process.crawl(PropertyPalSpider, mapper=mapper, start_urls=urls, num_urls=num_urls)

elif sys.argv[1][0] == "r":
    filter = (Q(property__icontains="R") & Q(stc = False)) & Q(un_published = False)
    properties = Property.objects.filter(filter).values_list("property", "url", "scraped_before")
    properties = sorted(properties, key=lambda x: x[2])
    mapper = {}
    urls = []
    
    for property in properties:
        mapper[property[1]] = {
            "property_id": property[0],
            "scraped_before": property[2],
        }
        urls.append(property[1])
    
    process.settings["ITEM_PIPELINES"] = {
        "scrapers.scrapers.pipelines.ScrapersPipeline": 100,
    }
    
    num_urls = len(urls)
    process.crawl(RightmoveSpider, mapper=mapper, start_urls=urls, num_urls=num_urls)

elif sys.argv[1][0] == "i":
    filter = Q(image_scraped = False)
    images = ImageProperty.objects.filter(filter).values_list("image_url", "image_id", "property")
    mapper = {}
    urls = [
        
    ]
    for image in images:
        mapper[image[0]] = {"property": image[2], "image_id": image[1], "composite_id": f'{image[2]}_{image[1]}'}
        urls.append(image[0])
        
    process.settings["ITEM_PIPELINES"] = {
        "scrapers.scrapers.pipelines.ScrapersPipeline": 100
    }
    
    num_urls = len(urls)
    process.crawl(ImageSpider, mapper=mapper, start_urls=urls, num_urls=num_urls)

elif sys.argv[1][0] == "e":
    filter = Q(epc_scraped=False) & Q(epc_url__isnull=False)
    epcs = EPC.objects.filter(filter).values_list("property_id", "epc_url")
    mapper = {}
    urls = []
    
    for epc in epcs:
        mapper[epc[1]] = {"property_id": epc[0]}
        if ".co.uk" in epc[1]:
            continue
        urls.append(epc[1])
    
    process.settings["ITEM_PIPELINES"] = {
        "scrapers.scrapers.pipelines.ScrapersPipeline": 100
    }
    
    num_urls = len(urls)
    process.crawl(EpcSpider, mapper=mapper, start_urls=urls, num_urls=num_urls)
    

elif sys.argv[1][0] == "T":
    filter = Q(un_published = True)
    for item in Property.objects.filter(filter):
        print(item.property)

process.start()