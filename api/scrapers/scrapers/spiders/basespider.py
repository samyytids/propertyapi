import scrapy
from abc import ABC, abstractmethod
from pipelines import InsertPipeline, UpdatePipeline, EpcPipeline, ImagePipeline
import time
from scrapy.exceptions import CloseSpider



class BasespiderSpider(ABC, scrapy.Spider):
    name = "basespider"
    allowed_domains = ["fake.com"]
    start_urls = ["https://fake.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = kwargs.get("start_urls", set())
        self.mapper = kwargs.get("mapper", {})
        self.num_urls = kwargs.get("num_urls", 0)
        self.count = 0
        self.insert_data = []
        self.update_data = []
        self.insert_pipeline = InsertPipeline()
        self.update_pipeline = UpdatePipeline()
        self.epc_pipeline = EpcPipeline()
        self.image_pipeline = ImagePipeline()
        self.start_time = time.time()
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta = {"db_data":self.mapper[url]})
    
    def check_time_limit(self):
        if (time.time() - self.start_time)/3600 > 20:
            self.close_spider("Time limit exceeded")
    
    @abstractmethod
    def parse(self, response):
        pass
    
    def closed(self, reason):
        self.close_spider(reason)
    
    def close_spider(self, reason):
        self.insert_pipeline.insert_data(self.insert_data)
        self.update_pipeline.update_data(self.update_data)
        self.insert_data.clear()
        self.update_data.clear()
        if (time.time() - self.start_time)/60 > 0.25:
            raise CloseSpider(f"It's fucked mate: {reason}")
        
