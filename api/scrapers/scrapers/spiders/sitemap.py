from scrapy.spiders import XMLFeedSpider
from scrapy.selector import Selector
from scrapy import Request
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from backend.models import Property


class SitemapSpider(XMLFeedSpider):
    name = "sitemap"
    start_urls = [
            "https://www.rightmove.co.uk/sitemap.xml",
            "https://www.propertypal.com/sitemaps/town/property-for-sale/index",
            "https://www.propertypal.com/sitemaps/town/property-to-rent/index"
        ]
    iterator = "iternodes"  # you can change this; see the docs
    itertag = "sitemap"  # change it accordingly
    urls = []

    def parse_node(self, response, selector: Selector):
        if response.url[12] == "r":
            yield from self.parse_rightmove(response, selector)
        elif response.url[12] == "p":
            yield from self.parse_propertypal(response, selector)
    
    def parse_rightmove(self, response, selector: Selector):
        item = {}
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        item["url"] = selector.xpath("ns:loc/text()", namespaces=namespace).get()
        if "sitemap-properties" in item["url"]:
            yield Request(
                item["url"],
                callback=self.parse_rightmove_layer2,
                meta={"ns": namespace}
            )
            
    def parse_propertypal(self, response, selector: Selector):
        item = {}
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        item["url"] = selector.xpath("ns:loc/text()", namespaces=namespace).get()
        yield Request(
            item["url"],
            callback=self.parse_propertypal_layer2,
            meta={"ns": namespace}
        )   
    
    def parse_propertypal_layer2(self, response):
        selector = Selector(response)
        namespace = response.meta["ns"]
        item = {}
        item["url"] = selector.xpath(".//ns:loc/text()", namespaces=namespace).getall()
        for idx, thing in enumerate(item["url"]):
            item["url"][idx] = (thing, f"P{thing.split('/')[-1]}")
        # item["id"] = f"P{item['url'].split('/')[-1]}"
        self.urls.extend(item["url"])
        print(len(self.urls), end="\r")
    
    def parse_rightmove_layer2(self, response):
        selector = Selector(response)
        namespace = response.meta["ns"]
        item = {}
        item["url"] = selector.xpath(".//ns:loc/text()", namespaces=namespace).getall()
        for idx, url in enumerate(item["url"]):
            item["url"][idx] = (url, f'R{url.split("/")[-1].split(".")[0].split("-")[-1]}')
        self.urls.extend(item["url"])
        print(len(self.urls), end="\r")
        
    def closed(self, reason):
        self.close_spider(reason)
    
    def close_spider(self, reason):
        Property.objects.bulk_create(
            [Property(
                property = item[-1],
                url = item[0]
            ) for item in self.urls],
            ignore_conflicts=True
        )
