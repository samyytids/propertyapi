import json 
import django
import os
import sys
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ['DJANGO_SETTINGS_MODULE'] = 'api.api.settings'
django.setup()

from api.backend.rightmove_parser import RightmoveParser
from time import time
from datetime import datetime, timedelta


def set_up() -> list[dict]:
    result = []
    for i in range(7883):
        with open(f"./api/data/{i}.json", "r") as f:
            result.append(
                json.load(f)
            )
    
    return result

def get_type(channel: str|None) -> tuple[str,str]:
    result = None
    if channel:
        property_type, listing_type = channel.split("_")
        result = [property_type, listing_type]
        
    return result
    
def get_auction(targeting: list[dict]):
    result = None
    for item in targeting:
        if item.get("key") == "AUCP":
            value = item.get("value")[0]
            if value == "TRUE":
                result = "auction"
            else:
                result = "normal"
                
    return result
        

def split_into_types(data: list[dict]):
    result = []
    for item in data:
        property_data = item.get("propertyData", {}).get("dfpAdInfo", {})
        property_id = item.get("propertyData", {}).get("id")
        result_item = {property_id:
                {
                    "type":get_type(property_data.get("channel", None)),
                    "auction":get_auction(property_data.get("targeting", []))
                }
            }
        if not result_item[property_id]["type"]:
            print(item)
            
        result.append(result_item)

class test:
    def __init__(self) -> None:
        self.list = [1,2,3]

if __name__ == "__main__":
    data = set_up()
    parser = RightmoveParser()
    start = time()
    property_data = []
    feature_set = set()
    for idx, item in enumerate(data):
        data = parser.parse(item, item.get("propertyData", {}).get("id", ""))