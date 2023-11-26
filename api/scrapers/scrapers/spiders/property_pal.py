from spiders.basespider import BasespiderSpider
import time
from bs4 import BeautifulSoup
import json
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)


class PropertyPalSpider(BasespiderSpider):
    name = "property_pal"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def parse(self, response):        
        soup = BeautifulSoup(response.text, "html.parser")
        db_data = response.meta.get("db_data")
        data = soup.find("script", attrs={"id": "__NEXT_DATA__"})
        json_data = json.loads(data.text)
        
        property_id = db_data["property_id"]
        
        json_data["id"] = property_id 
        json_data["scraped_before"] = db_data["scraped_before"]
        self.count += 1
        print(f"Number of properties scraped: {self.count}, progress % {(self.count/self.num_urls)*100:.2f}", end="\r")
        self.data.append(json_data)
        self.check_time_limit()
        
        if len(self.data) % 100 == 0:
            try:
                print("processing")
                self.pipeline.process_items_manually(self.data)
                self.data.clear()
            except Exception as e:                
                print(e)
                self.data.clear()
            
    def property_removed(self, response):
        if response.status == 410 or response.status == 404:
            return True
        return False