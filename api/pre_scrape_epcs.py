import django
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'api.settings'
django.setup()

from backend.models import Epc
from django.db.models import Q
import re

def get_epcs() -> list[dict]:
    filter = Q(epc_scraped=False) & Q(epc_url__isnull=False) & Q(epc_url__icontains=",") & Q(epc_url__icontains="png")
    epcs = Epc.objects.filter(filter).values("epc_url", "property_id")
    print(len(epcs))
    return epcs

def get_epc_data(epcs: list[dict]) -> list[dict]:
    pattern = re.compile('[a-zA-Z]')
    result = []
    for epc in epcs:
        split_item = epc["epc_url"].split(",")
        if split_item[-1] == "M" or split_item[-1] == "S":
            split_item[0] = split_item[0].split("?")
            split_item[0] = split_item[0][1]
            if "." in split_item[0]:
                if pattern.search(split_item[0]):
                    split_item[0], split_item[1] = split_item[0].split(".")
                    split_item[0] = split_item[0][:-1]
                    split_item[1] = split_item[1][:-1]
                else:
                    split_item[0], split_item[1] = split_item[0].split(".")
                    split_item[0] = split_item[0]
                    split_item[1] = split_item[1]
                
            elif "/" in split_item[0]:
                split_item[0], split_item[1] = split_item[0].split("/")
            
            try:
                epc_current=int(split_item[0])
            except:
               epc_current=None
                
            try:
                epc_potential=int(split_item[1])
            except: 
                epc_potential = None
            
            result.append(
                {
                    "property_id" : {
                        "property_id": epc["property_id"],
                    },
                    "epc" : {
                        "epc_scraped" : True,
                        "epc_potential" : epc_potential,
                        "epc_current" : epc_current,
                    }
                }
            )
    return result

def update_epcs(epcs: list[dict]) -> None:
    things_to_update = []
    for epc_data in epcs:
        epc = Epc.objects.get(property_id = epc_data["property_id"]["property_id"])
        epc.epc_current = epc_data["epc"].get("epc_current")
        epc.epc_potential = epc_data["epc"].get("epc_potential")
        epc.epc_scraped = epc_data["epc"].get("epc_scraped")
        things_to_update.append(epc)
    
    Epc.objects.bulk_update(
        things_to_update,
        [
            "epc_current",
            "epc_potential",
            "epc_scraped",
        ]
    )
    
def pre_scrape_epcs():
    epcs = get_epcs()
    epcs = get_epc_data(epcs)
    update_epcs(epcs)
    
if __name__ == "__main__":
    pre_scrape_epcs()
