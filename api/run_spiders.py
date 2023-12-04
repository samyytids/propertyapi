import django
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'api.settings'
django.setup()

from backend.models import *
from scrapers.scrapers.spiders.sitemap import SitemapSpider
from scrapers.scrapers.spiders.property_pal import PropertyPalSpider
from scrapers.scrapers.spiders.rightmove import RightmoveSpider
from scrapers.scrapers.spiders.image import ImageSpider
from scrapers.scrapers.spiders.epc import EpcSpider
from scrapy.crawler import CrawlerProcess
from django.db.models import Q
from pre_scrape_epcs import pre_scrape_epcs

process = CrawlerProcess(settings={
        "LOG_LEVEL":"INFO",
        "HTTPCACHE_ENABLED":False,
        "HTTPERROR_ALLOWED_CODES": [410,404],
        "CONCURRENT_REQUESTS" : 16,
    })

def images_test():
    filter = Q(image_scraped = False)
    images = ImageProperty.objects.filter(filter).values_list("image_url", "image_id", "property")
    mapper = {}
    urls = []
    
    for image in images:
        mapper[image[0]] = {"property": image[2], "image_id": image[1], "composite_id": f'{image[2]}_{image[1]}'}
        urls.append(image[0])
        
    process.settings["ITEM_PIPELINES"] = {
        "scrapers.scrapers.pipelines.ImagePipeline": 100
    }
    num_urls = len(urls)
    process.crawl(ImageSpider, mapper=mapper, start_urls=urls, num_urls=num_urls)
    list(images).clear()
    
    
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
        "scrapers.scrapers.pipelines.InsertPipeline": 100,
        "scrapers.scrapers.pipelines.UpdatePipeline": 200,
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
        "scrapers.scrapers.pipelines.InsertPipeline": 100,
        "scrapers.scrapers.pipelines.UpdatePipeline": 200,
    }
    
    num_urls = len(urls)
    process.crawl(RightmoveSpider, mapper=mapper, start_urls=urls, num_urls=num_urls)

elif sys.argv[1][0] == "i":
    images_test()

elif sys.argv[1][0] == "e":
    pre_scrape_epcs()
    
    filter = Q(epc_scraped=False) & Q(epc_url__isnull=False)
    epcs = EPC.objects.filter(filter).values_list("property_id", "epc_url")
    mapper = {}
    urls = []
    for epc in epcs:
        mapper[epc[1]] = {"property_id": epc[0]}
        if any(
            substring in epc[1] for substring in [
                    "jupix", "Document", "kea.pmp",
                    "ewemove", ".pdf", ".gov.uk",
                    ".png", ".jpeg", ".jpg",
                    ".JPG", ".PNG", ".JPEG"
                ]
            ):
            
            urls.append(epc[1])
            
        elif ".co.uk" in epc[1]:
            continue
    
    process.settings["ITEM_PIPELINES"] = {
        "scrapers.scrapers.pipelines.EpcPipeline": 100
    }
    
    num_urls = len(urls)
    process.crawl(EpcSpider, mapper=mapper, start_urls=urls, num_urls=num_urls)
    

elif sys.argv[1][0] == "T":
    filter = (Q(property__icontains="R") & Q(scraped_before = True))
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
        "scrapers.scrapers.pipelines.InsertPipeline": 100,
        "scrapers.scrapers.pipelines.UpdatePipeline": 200,
    }
    
    num_urls = len(urls)
    process.crawl(RightmoveSpider, mapper=mapper, start_urls=urls, num_urls=num_urls)

process.start()