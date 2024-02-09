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
from django.db.models.base import ModelState

process = CrawlerProcess(settings={
        "LOG_LEVEL":"INFO",
        "HTTPCACHE_ENABLED":False,
        "HTTPERROR_ALLOWED_CODES": [410,404],
        "CONCURRENT_REQUESTS" : 16,
    })
    
def crawl_sequentially(process: CrawlerProcess, crawlers: list):
    if crawlers[0] == SitemapSpider:
        deferred = process.crawl(crawlers[0])

    elif crawlers[0] == EpcSpider:
        pre_scrape_epcs()
    
        filter = Q(epc_scraped=False) & Q(epc_url__isnull=False)
        epcs = Epc.objects.filter(filter).values_list("property_id", "epc_url")
        mapper = {}
        urls = []
        for epc in epcs:
            mapper[epc[1]] = {"property_id": epc[0]}
            if any(
                substring in epc[1] for substring in [
                        "jupix", "Document", "kea.pmp",
                        "ewemove", ".pdf",
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
        deferred = process.crawl(crawlers[0], mapper=mapper, start_urls=urls, num_urls=num_urls)
    
    elif crawlers[0] == ImageSpider:
        filter = Q(image_scraped = False)
        images = Image.objects.filter(filter).values_list("image_url", "pk")
        mapper = {}
        urls = []
        
        for image in images:
            mapper[image[0]] = {"pk": image[1]}
            urls.append(image[0])
            
        process.settings["ITEM_PIPELINES"] = {
            "scrapers.scrapers.pipelines.ImagePipeline": 100
        }
        num_urls = len(urls)
        deferred = process.crawl(crawlers[0], mapper=mapper, start_urls=urls, num_urls=num_urls)
        
    else:
        filter = (Q(stc = False) & Q(un_published = False) & Q(archived = False) & Q(removed=False) & Q(bad_data = False))
        properties = Property.objects.filter(filter).values_list("property_id", "property_url", "scraped_before")
        properties = sorted(properties, key=lambda x: x[2])
        # properties = properties[:500]
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
        deferred = process.crawl(crawlers[0], mapper=mapper, start_urls=urls, num_urls=num_urls)

    print(crawlers)

    if len(crawlers) > 1:
        deferred.addCallback(lambda _: crawl_sequentially(process, crawlers[1:]))
    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        crawlers = [SitemapSpider, RightmoveSpider, ImageSpider, EpcSpider]
    else:
        crawlers = [ImageSpider]
    
        
    process = CrawlerProcess(settings={
        "LOG_LEVEL":"INFO",
        "HTTPCACHE_ENABLED":False,
        "HTTPERROR_ALLOWED_CODES": [410,404],
        "CONCURRENT_REQUESTS" : 16,
    })
    
    crawl_sequentially(process=process, crawlers=crawlers)
    process.start()