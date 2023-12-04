import scrapy
from time import time
from spiders.basespider import BasespiderSpider

class ImageSpider(BasespiderSpider):
    name = "image"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def parse(self, response):
        data = response.meta.get("db_data")
        data["image_binary"] = response.body
        self.insert_data.append(data)
        self.count += 1
        print(f"Number of imagess scraped: {self.count}, progress % {(self.count/self.num_urls)*100:.2f}", end="\r")
        self.check_time_limit()
        
        if self.count % 100 == 0:
            try:
                self.image_pipeline.process_items_manually(self.insert_data)
                self.insert_data.clear()
            except Exception as e:                
                print(e)
                self.insert_data.clear()
        
    def closed(self, reason):
        self.close_spider(reason)
    
    def close_spider(self, reason):
        try:
            self.image_pipeline.process_items_manually(self.insert_data)
            self.insert_data.clear()
        except Exception as e:                
            print(e)
            self.insert_data.clear()
        