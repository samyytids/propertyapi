# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import django
import os
import sys
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ['DJANGO_SETTINGS_MODULE'] = 'api.api.settings'
django.setup()

from backend.data_parser import DataParser
from backend.models import *


class ScrapersPipeline:
    def __init__(self):
        self.parser = DataParser()
        self.property_data = []
        self.properties = []
        self.views = []
        self.key_features = []
        self.images = []
        self.floorplans = []
        self.rooms = []
        self.stations = []
        self.station_distances = []
        self.prices = []
        self.statuses = []
        self.accreditations = []
        self.have_accreditations = []
        self.epcs = []
        self.property_updates = []
        self.removed = []
    
    def store_data(self, data: dict):
        self.property_data.append(data["single"])
        self.properties.append(data["property"])
        self.views.extend(data["views"])
        self.key_features.extend(data["key_features"])
        self.images.extend(data["images"])
        self.floorplans.extend(data["floorplans"])
        self.rooms.extend(data["rooms"])
        self.stations.extend(data["stations"])
        self.station_distances.extend(data["station_distances"])
        self.prices.extend(data["prices"])
        self.statuses.extend(data["statuses"])    
        self.accreditations.extend(data["accreditations"])
        self.have_accreditations.extend(data["have_accreditations"])
        
    def store_update_data(self, data: dict):
        self.properties.append(data["property"])
        self.prices.extend(data["prices"])
        self.statuses.extend(data["statuses"])    
    
    def clear_data(self):
        self.property_data.clear()
        self.properties.clear()
        self.views.clear()
        self.key_features.clear()
        self.images.clear()
        self.floorplans.clear()
        self.rooms.clear()
        self.stations.clear()
        self.station_distances.clear()
        self.prices.clear()
        self.statuses.clear()
        self.accreditations.clear()
        self.have_accreditations.clear()
        self.removed.clear()
    
    def process_items_manually(self, item):
        for property in item:
            if not property.get("analyticsInfo"):
                self.removed.append(property["id"])
                continue
            if property["scraped_before"]:
                data = self.parser.parse_update(property, property["id"])
                self.store_update_data(data)
            else:
                data = self.parser.parse(property, property["id"])
                self.store_data(data)
        try:
            self.insert_test()
            self.update_removed()
            self.clear_data()
        except:
            self.clear_data()
    
    def process_epcs(self, item):
        self.epcs = item
        try:
            self.insert_epcs()
            self.epcs.clear()
        except:
            self.epcs.clear()
    
    def process_image(self, item):
        self.images = item
        try:
            self.insert_images()
            self.images.clear()
        except:
            self.images.clear()
    
    def insert_images(self):
        updates = []
        for image in self.images:
            image_property = ImageProperty.objects.get(property=image["property"], image_id=image["image_id"])
            image_property.image_scraped = True
            updates.append(image_property)            
        
        Images.objects.bulk_create(
            [Images(
                composite_id = image["composite_id"],
                image_file = SimpleUploadedFile(f"{image['composite_id']}.png", ContentFile(image["image_binary"]).read(), content_type="image/png")
            ) for image in self.images]
        )
        
        ImageProperty.objects.bulk_update(
            updates,
            [
                "image_scraped"
            ]
        )
        
    def insert_epcs(self):
        updates = []
        for epc_data in self.epcs:
            epc = EPC.objects.get(property_id = epc_data["property_id"])
            epc.epc_image = epc_data["scraped_info"].get("epc_image")
            epc.epc_current = epc_data["scraped_info"].get("epc_current")
            epc.epc_potential = epc_data["scraped_info"].get("epc_potential")
            epc.epc_scraped = epc_data["scraped_info"].get("epc_scraped")
            updates.append(epc)
        
        EPC.objects.bulk_update(
            updates,
            [
                "epc_image",
                "epc_current",
                "epc_potential",
                "epc_scraped",
            ]
        )
            
    def update_removed(self):
        properties = []
        for item in self.removed:
            property = Property.objects.get(property=item)
            property.scraped_before = True
            property.un_published = True
            properties.append(property)
        
        Property.objects.bulk_update(
            properties,
            [
                "un_published",
                "scraped_before",
            ]
        )
    
    @staticmethod
    def one_to_one_no_id(table, property_data, key, ignore=False):
        table.objects.bulk_create(
            [table(
                **property[key]
            )
            for property in property_data],
            ignore_conflicts=ignore
        )
    
    @staticmethod
    def one_to_one_list_no_id(table, property_data, name, ignore=False):
        
        table.objects.bulk_create(
            [table(
                **property
            )
            for property in property_data],
            ignore_conflicts=ignore
        )
    
    @staticmethod
    def one_to_one(table, property_data, key, ignore=False):
        table.objects.bulk_create(
            [table(
                property_id = property["property_id"]["property_id"],
                **property[key]
            )
            for property in property_data],
            ignore_conflicts=ignore
        )
        
    
    
    @staticmethod
    def one_to_many(table, property_data, name, ignore=False):        
        table.objects.bulk_create(
            [table(
                **item
            )
            for item in property_data],
            ignore_conflicts=ignore
        )
        
    
    def get_update_objects(self, table, id: str|None = None) -> list:
        if table == Property:
            things_to_update = []
            for idx, property in enumerate(self.properties):
                property_obj: Property = table.objects.get(property = property["property_id"])
                
                property_obj.un_published = property["un_published"]
                property_obj.scraped_before = property["scraped_before"]
                property_obj.stc = property["stc"]
                property_obj.property_values = PropertyValue.objects.get(property_id = property["property_id"])
                things_to_update.append(property_obj)
                
        else:
            things_to_update = [
                {
                    "property": table.objects.get(property_id = property[id][id]),
                    "estate_agent": {
                        "name": property["estate_agent"]["name"],
                        "branch_name": property["estate_agent"]["branch_name"]
                        }
                } 
                for property in self.property_data
            ]
            for idx, update in enumerate(things_to_update):
                update["property"]: PropertyValue
                update["property"].text_elements = TextElements.objects.get(property_id=update["property"].property_id)
                update["property"].location = Location.objects.get(property_id = update["property"].property_id)
                update["property"].broadband = Broadband.objects.get(property_id = update["property"].property_id)
                update["property"].epc = EPC.objects.get(property_id = update["property"].property_id)
                update["property"].listing_type = ListingType.objects.get(property_id = update["property"].property_id)
                update["property"].layout = Layout.objects.get(property_id = update["property"].property_id)
                update["property"].tax = Tax.objects.get(property_id = update["property"].property_id)
                update["property"].ownership = OwnershipRetirement.objects.get(property_id = update["property"].property_id)
                update["property"].tenure = Tenure.objects.get(property_id = update["property"].property_id)
                if update["estate_agent"]["name"] is not None:
                    update["property"].estate_agent = EstateAgent.objects.get(**update["estate_agent"])
                things_to_update[idx] = update["property"]

        return things_to_update
    
    def insert_test(self):
        self.one_to_one_no_id(PropertyValue, self.property_data, "property_id", True)
        self.one_to_one(TextElements, self.property_data, "text_elements", True)
        self.one_to_one(OwnershipRetirement, self.property_data, "ownership_retirement", True)
        self.one_to_one(Location, self.property_data, "location", True)
        self.one_to_one(Broadband, self.property_data, "broadband", True)
        self.one_to_one(EPC, self.property_data, "epc", True)
        self.one_to_one(ListingType, self.property_data, "listing_type", True)
        self.one_to_one(Layout, self.property_data, "layout", True)
        self.one_to_one(Tax, self.property_data, "tax", True)
        self.one_to_one(Tenure, self.property_data, "tenure", True)
        self.one_to_one_list_no_id(Station, self.stations, "stations", True)
        self.one_to_one_list_no_id(Accreditation, self.accreditations, "accreditations", True)
        self.one_to_many(ImageProperty, self.images, "images", True)
        self.one_to_many(FloorplanProperty, self.floorplans, "floorplans", True)
        self.one_to_one_no_id(EstateAgent, self.property_data, "estate_agent", True)
        self.one_to_many(KeyFeature, self.key_features, "key_features", True)
        self.one_to_many(Views, self.views, "views", True)
        self.one_to_many(Rooms, self.rooms, "rooms", True)
        self.one_to_many(Prices, self.prices, "prices", True)
        self.one_to_many(Statuses, self.statuses, "statuses", True)
        
        EstateAgentAccreditation.objects.bulk_create(
            [EstateAgentAccreditation(
                estate_agent_id = EstateAgent.objects.get(
                    name = accreditation["estate_agent"].get("organisation"),
                    branch_name = accreditation["estate_agent"].get("organisationBranch")
                ),
                accreditation_id = Accreditation.objects.get(
                    accreditation_label = accreditation["accreditation_label"]
                ),
                have_accreditation = accreditation["have"] 
            ) for accreditation in self.have_accreditations],
            ignore_conflicts=True
        )
        
        StationStationDistance.objects.bulk_create(
            [StationStationDistance(
                property_id = PropertyValue(property_id = station["property_id"]),
                station_id = Station(station_name = station["station_name"]),
                station_distance = station["station_distance"],
                station_distance_units = station["station_distance_units"]
            ) for station in self.station_distances],
            ignore_conflicts=True
        )
        
        property_values = self.get_update_objects(PropertyValue, "property_id")
        PropertyValue.objects.bulk_update(
            property_values,
            [
                "text_elements",
                "location",
                "broadband",
                "epc",
                "listing_type",
                "layout",
                "tax",
                "ownership",
                "tenure",
                "estate_agent",
            ]
        )
        properties = self.get_update_objects(Property)
        Property.objects.bulk_update(
            properties,
            [
                "un_published",
                "scraped_before",
                "stc",
                "property_values",
            ]
        )
