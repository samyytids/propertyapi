from spiders.basespider import BasespiderSpider
from bs4 import BeautifulSoup
import json
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)


class RightmoveSpider(BasespiderSpider):
    name = "rightmove"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def parse(self, response): 
        # getting necessary data and meta data       
        db_data = response.meta.get("db_data")
        json_data = self.get_json(response)
        property_id = db_data["property_id"]
        
        # Adding in id and scraped before from meta data. 
        json_data["id"] = property_id 
        json_data["scraped_before"] = db_data["scraped_before"]      
        self.count += 1
        
        print(f"Number of properties scraped: {self.count}, progress % {(self.count/self.num_urls)*100:.2f}", end="\r")
        
        # Appending to lists for export at length threshold. 
        if json_data["scraped_before"]:
            self.update_data.append(json_data)
        else:
            self.insert_data.append(json_data)
        
        # Checking to see if the scraper has been running for 20 hours. 
        self.check_time_limit()
        
        # Insert or update data once either list is too long. 
        if len(self.insert_data) % 100 == 0 and len(self.insert_data) != 0:
            self.insert_or_update("insert_data")
                        
        if len(self.update_data) % 100 == 0  and len(self.update_data) != 0:
            self.insert_or_update("update_data")
    
    
    def get_json(self, response) -> dict:
        soup = BeautifulSoup(response.text, "html.parser")
        data = soup.find('script', text=lambda t: t and "window.PAGE_MODEL" in t).text
        start_index = 24
        end_index = -1
        json_string = data[start_index:end_index]
        json_data = json.loads(json_string)
        return json_data
    
    def insert_or_update(self, list_to_check: str):
        submission_list: list = self.__getattribute__(list_to_check)
        try:
            if list_to_check == "update_data":
                self.update_pipeline.update_data(submission_list)
            else:
                self.insert_pipeline.insert_data(submission_list)
            submission_list.clear()
        except Exception as e:                
            print(e)
            submission_list.clear()
    
    def property_removed(self, response):
        if response.status == 410 or response.status == 404:
            return True
        return False