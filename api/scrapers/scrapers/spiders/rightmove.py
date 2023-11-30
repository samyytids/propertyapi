from spiders.basespider import BasespiderSpider
import time
from bs4 import BeautifulSoup
import json
import os
import sys
from scrapy import signals
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)


class RightmoveSpider(BasespiderSpider):
    name = "rightmove"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def parse(self, response):        
        soup = BeautifulSoup(response.text, "html.parser")
        db_data = response.meta.get("db_data")
        data = soup.find('script', text=lambda t: t and "window.PAGE_MODEL" in t).text
        start_index = 24
        end_index = -1
        json_string = data[start_index:end_index]
        json_data = json.loads(json_string)
        
        property_id = db_data["property_id"]
        
        json_data["id"] = property_id 
        json_data["scraped_before"] = db_data["scraped_before"]      
        self.count += 1
        print(f"Number of properties scraped: {self.count}, progress % {(self.count/self.num_urls)*100:.2f}", end="\r")
        self.data.append(json_data)
        self.check_time_limit()
        
        if len(self.data) % 100 == 0:
            try:
                self.pipeline.process_items_manually(self.data)
                self.data.clear()
            except Exception as e:                
                print(e)
                self.data.clear()
        
    def property_removed(self, response):
        if response.status == 410 or response.status == 404:
            return True
        return False