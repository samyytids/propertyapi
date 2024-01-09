# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
import django
import os
import sys
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ['DJANGO_SETTINGS_MODULE'] = 'api.api.settings'
django.setup()

from backend.rightmove_parser import RightmoveParser
from backend.models import *

class InsertPipeline:
    def __init__(self):
        self.parser = RightmoveParser()
        self.property_table_data = []
        self.property_data_table_data = []
        self.text_elements_table_data = []
        self.tax_table_data = []
        self.ownership_table_data = []
        self.epc_table_data = []
        self.location_table_data = []
        self.layout_table_data = []
        self.station_table_data = []
        self.station_distance_table_data = []
        self.estate_agent_table_data = []
        self.price_table_data = []
        self.key_feature_table_data = []
        self.status_table_data = []
        self.image_table_data = []
        self.floorplan_table_data = []
        self.room_table_data = []
        self.premium_listing_table_data = []
        self.business_type_table_data = []
        self.lettings_table_data = []
        self.affiliation_table_data = []
        self.agent_affiliation_table_data = []
        self.un_published = []
        self.archived = []
        self.removed = []
        self.bad_data = []
   
    def process_data(self, properties: list[dict]):
        for property in properties:
            id = property.get("id")
            data = self.parser.parse(property, property.get("propertyData", {}).get("id", ""))
            if not data:
                self.removed.append(id)
                continue
            if data.get("property_table").archived:
                self.archived.append(id)
                continue
            if data.get("property_table").un_published:
                self.un_published.append(id)
                continue
            property_data = data.get("property_data_table").get("property")
            if not property_data.get("current_price"):
                self.bad_data.append(id)
                continue
            layout_data: Layout = data.get("layout_table")
            if layout_data.bedrooms is None:
                self.bad_data.append(id)
                continue
            property_data = data.get("property_table")
            self.property_table_data.append(property_data)
            property_data_data = data.get("property_data_table")
            self.property_data_table_data.append(property_data_data)
            
            self.layout_table_data.append(layout_data)
            text_data = data.get("text_elements_table")
            self.text_elements_table_data.append(text_data)
            tax_data = data.get("tax_table")
            self.tax_table_data.append(tax_data)
            ownership_data = data.get("ownership_table")
            self.ownership_table_data.append(ownership_data)
            epc_data = data.get("epc_table")
            if epc_data:
                self.epc_table_data.append(epc_data)
            location_data = data.get("location_table")
            self.location_table_data.append(location_data)
            station_data = data.get("station_table")
            self.station_table_data.extend(station_data)
            station_distance_data = data.get("station_distance_table")
            self.station_distance_table_data.extend(station_distance_data)
            estate_agent_data = data.get("estate_agent_table")
            self.estate_agent_table_data.append(estate_agent_data)
            price_data = data.get("price_table")
            self.price_table_data.append(price_data)
            key_feature_data = data.get("key_feature_table")
            self.key_feature_table_data.extend(key_feature_data)
            status_data = data.get("status_table")
            self.status_table_data.append(status_data)
            image_data = data.get("image_table")
            self.image_table_data.extend(image_data)
            floorplan_data = data.get("floorplan_table")
            self.floorplan_table_data.extend(floorplan_data)
            room_data = data.get("room_table")
            self.room_table_data.extend(room_data)
            premium_data = data.get("premium_listing_table")
            self.premium_listing_table_data.append(premium_data)
            business_type_data = data.get("business_type_table")
            self.business_type_table_data.append(business_type_data)
            lettings_data = data.get("lettings_table")
            if lettings_data:
                self.lettings_table_data.append(lettings_data)
            affiliation_data = data.get("affiliation_table")
            if affiliation_data:
                self.affiliation_table_data.extend(affiliation_data)
                agent_affiliation_data = data.get("agent_affiliation_table")
                self.agent_affiliation_table_data.extend(agent_affiliation_data)
                
    def insert_simple(self, data, model: models.Model):
        model.objects.bulk_create(
            data, 
            ignore_conflicts=True
        )
        
        
    def update_bad_data(self):
        Property.objects.bulk_update(
            [Property.objects.get(
                property_id = un_published
            )
                for un_published in self.un_published],
                ["un_published"]
        )
        
        Property.objects.bulk_update(
            [Property.objects.get(
                property_id = archived
            )
                for archived in self.archived],
                ["archived"]
        )
        
        Property.objects.bulk_update(
            [Property.objects.get(
                property_id = removed
            )
                for removed in self.removed],
                ["removed"]
        )
        
        Property.objects.bulk_update(
            [Property.objects.get(
                property_id = bad_data
            )
                for bad_data in self.bad_data],
                ["bad_data"]
        )
    
    def clear_data(self):
        self.property_table_data.clear()
        self.property_data_table_data.clear()
        self.text_elements_table_data.clear()
        self.tax_table_data.clear()
        self.ownership_table_data.clear()
        self.epc_table_data.clear()
        self.location_table_data.clear()
        self.layout_table_data.clear()
        self.station_table_data.clear()
        self.station_distance_table_data.clear()
        self.estate_agent_table_data.clear()
        self.price_table_data.clear()
        self.key_feature_table_data.clear()
        self.status_table_data.clear()
        self.image_table_data.clear()
        self.floorplan_table_data.clear()
        self.room_table_data.clear()
        self.premium_listing_table_data.clear()
        self.business_type_table_data.clear()
        self.lettings_table_data.clear()
        self.affiliation_table_data.clear()
        self.agent_affiliation_table_data.clear()
        self.un_published.clear()
        self.archived.clear()
        self.removed.clear()
        self.bad_data.clear()
    
    def queries(self):
        self.insert_simple(self.text_elements_table_data, Text)
        self.insert_simple(self.tax_table_data, Tax)
        self.insert_simple(self.ownership_table_data, Ownership)
        self.insert_simple(self.epc_table_data, Epc)
        self.insert_simple(self.location_table_data, Location)
        self.insert_simple(self.layout_table_data, Layout)
        self.insert_simple(self.station_table_data, Station)
        self.insert_simple(self.estate_agent_table_data, EstateAgent)
        self.insert_simple(self.affiliation_table_data, Affiliation)
        self.insert_simple(self.business_type_table_data, BusinessType)
        self.insert_simple(self.lettings_table_data, LettingInfo)
        PropertyData.objects.bulk_create(
            [PropertyData(
                **property["property"],
                text = Text.objects.get(
                    property_id=property["property"]["property_id"]
                    ),
                tax = Tax.objects.get(
                    property_id=property["property"]["property_id"]
                    ),
                epc = Epc.objects.filter(
                    property_id=property["property"]["property_id"])[0] 
                        if len(
                            Epc.objects.filter(
                                property_id=property["property"]["property_id"]
                                )
                        ) == 1 else None,
                location = Location.objects.get(
                    property_id=property["property"]["property_id"]
                    ),
                layout = Layout.objects.get(
                    property_id=property["property"]["property_id"]
                    ),
                agent = EstateAgent.objects.get(
                    agent_name = property.get("agent").agent_name,
                    branch_name = property.get("agent").branch_name
                    ),
                business_type = BusinessType.objects.filter(
                    property_id=property["property"]["property_id"])[0]
                        if len(
                            BusinessType.objects.filter(
                                property_id=property["property"]["property_id"]
                                )
                        ) == 1 else None,            
                ) for property in self.property_data_table_data],
            ignore_conflicts=True
        )
        
        
        for idx, property in enumerate(self.property_table_data):
            property: Property
            property.property_data = PropertyData.objects.get(property_id = property.property_id)
            property.scraped_before = True
            self.property_table_data[idx] = property
        
        Property.objects.bulk_update(
                self.property_table_data,
                ["archived", "un_published", "stc", "property_data", "scraped_before"],
        )
        
        Price.objects.bulk_create(
            [Price(
                property_id = Property.objects.get(property_id = price_data["property_id"]),
                price = price_data["price"],
                price_qualifier = price_data["price_qualifier"],
                original_price = price_data["original_price"],
                price_date = price_data["price_date"],
            )for price_data in self.price_table_data],
            ignore_conflicts=True
        )
        
        Status.objects.bulk_create(
            [Status(
                property_id = Property.objects.get(
                    property_id = status_data["property_id"]
                    ),
                stc = status_data["stc"],
                status_date = status_data["status_date"]
            )for status_data in self.status_table_data],
            ignore_conflicts=True
        )
        
        KeyFeature.objects.bulk_create(
            [KeyFeature(
                property_id = Property.objects.get(property_id = feature_data["property_id"]),
                feature = feature_data["feature"]
            )for feature_data in self.key_feature_table_data],
            ignore_conflicts=True
        )
        
        Image.objects.bulk_create(
            [Image(
                property_id = Property.objects.get(property_id = image_data["property_id"]),
                image_url = image_data["image_url"],
                image_caption = image_data["image_caption"],
            ) for image_data in self.image_table_data],
            ignore_conflicts=True
        )
        
        Floorplan.objects.bulk_create(
            [Floorplan(
                property_id = Property.objects.get(property_id = floorplan_data["property_id"]),
                floorplan_url = floorplan_data["floorplan_url"],
                floorplan_caption = floorplan_data["floorplan_caption"],
            ) for floorplan_data in self.floorplan_table_data],
            ignore_conflicts=True
        )
        
        Room.objects.bulk_create(
            [Room(
                property_id = Property.objects.get(property_id = room_data["property_id"]),
                room_name = room_data["room_name"],
                room_description = room_data["room_description"],
                room_width = room_data["room_width"],
                room_length = room_data["room_length"],
                room_unit = room_data["room_unit"],
                room_dimension = room_data["room_dimension"],
            ) for room_data in self.room_table_data],
            ignore_conflicts=True
        )
        
        PremiumListing.objects.bulk_create(
            [PremiumListing(
                property_id = Property.objects.get(property_id = premium_data["property_id"]),
                featured_property = premium_data["featured_property"],
                premium_listing = premium_data["premium_listing"],
                listing_date = premium_data["listing_date"],
            ) for premium_data in self.premium_listing_table_data],
            ignore_conflicts=True
        )
        
        StationDistance.objects.bulk_create(
            [StationDistance(
                station_id = Station.objects.get(station_name = station.get("station_id")),
                property_id = PropertyData.objects.get(property_id = station.get("property_id")),
                station_distance = station.get("station_distance"),
                station_distance_unit = station.get("station_distance_unit"),
            )for station in self.station_distance_table_data],
            ignore_conflicts=True
        )
        
        AgentAffiliation.objects.bulk_create(
            [AgentAffiliation(
                affiliation_id = Affiliation.objects.get(affiliation_name = affiliation.get("affiliation_id").affiliation_name),
                agent_id = EstateAgent.objects.get(agent_name = affiliation.get("agent_id").agent_name, branch_name = affiliation.get("agent_id").branch_name)
            ) for affiliation in self.agent_affiliation_table_data],
            ignore_conflicts=True
        )
        
    def insert_data(self, data: list[dict]):
        self.process_data(data)
    
        try:
            self.queries()
        except Exception as e:
            print(e)
            
        self.update_bad_data()
        
        self.clear_data()

class UpdatePipeline:
    def __init__(self):
        self.parser = RightmoveParser()
        self.property_table_data = []
        self.property_data_table_data = []
        self.price_table_data = []
        self.status_table_data = []
        self.premium_listing_table_data = []
        self.un_published = []
        self.archived = []
        self.removed = []
        self.bad_data = []

    def process_data(self, properties):
        for property in properties:
            property: dict
            id = property.get("id")
            data = self.parser.parse_update(property, property.get("propertyData", {}).get("id", ""))
            if not data:
                self.removed.append(id)
                continue
            elif data.get("property_table").archived:
                self.archived.append(id)
                continue
            elif data.get("property_table").un_published:
                self.un_published.append(id)
                continue
            
            property_data = data.get("property_table")
            self.property_table_data.append(property_data)
            
            property_data_data = data.get("property_data_table")
            self.property_data_table_data.append(property_data_data)
            
            price_data = data.get("price_table")
            self.price_table_data.append(price_data)
            status_data = data.get("status_table")
            self.status_table_data.append(status_data)
            premium_data = data.get("premium_listing_table")
            self.premium_listing_table_data.append(premium_data)
    
    def update_bad_data(self):
        Property.objects.bulk_update(
            [Property.objects.get(
                property_id = un_published
            )
                for un_published in self.un_published],
                ["un_published"]
        )
        
        Property.objects.bulk_update(
            [Property.objects.get(
                property_id = archived
            )
                for archived in self.archived],
                ["archived"]
        )
        
        Property.objects.bulk_update(
            [Property.objects.get(
                property_id = removed
            )
                for removed in self.removed],
                ["removed"]
        )
        
        Property.objects.bulk_update(
            [Property.objects.get(
                property_id = bad_data
            )
                for bad_data in self.bad_data],
                ["bad_data"]
        )
    
    def clear_data(self):
        self.property_table_data.clear()
        self.property_data_table_data.clear()
        self.price_table_data.clear()
        self.status_table_data.clear()
        self.premium_listing_table_data.clear()
        self.un_published.clear()
        self.archived.clear()
        self.removed.clear()
        self.bad_data.clear()
        
    def queries(self):
        PropertyData.objects.bulk_update(
        self.property_data_table_data,
            ["current_price", "reduced"]
        )
        
        Property.objects.bulk_update(
                self.property_table_data,
                ["stc"]
        )
        
        Price.objects.bulk_create(
            [Price(
                property_id = Property.objects.get(property_id = price_data["property_id"]),
                price = price_data["price"],
                price_qualifier = price_data["price_qualifier"],
                original_price = price_data["original_price"],
                price_date = price_data["price_date"],
            )for price_data in self.price_table_data],
            ignore_conflicts=True
        )
        
        Status.objects.bulk_create(
            [Status(
                property_id = Property.objects.get(
                    property_id = status_data["property_id"]
                    ),
                stc = status_data["stc"],
                status_date = status_data["status_date"]
            )for status_data in self.status_table_data],
            ignore_conflicts=True
        )    
        
        PremiumListing.objects.bulk_create(
            [PremiumListing(
                property_id = Property.objects.get(
                    property_id = premium_listing_data["property_id"]
                    ),
                featured_property = premium_listing_data["featured_property"],
                premium_listing = premium_listing_data["premium_listing"],
                listing_data = premium_listing_data["listing_date"]
            )for premium_listing_data in self.premium_listing_table_data],
            ignore_conflicts=True
        )    
        
        
    def update_data(self, data: list[dict]):
        self.process_data(data)
        try:
            self.queries()
        except Exception as e:
            print(e)
            
        self.update_bad_data()
        
        self.clear_data()
        
class EpcPipeline:
    def __init__(self) -> None:
        self.epcs = []
    
    def process_items_manually(self, epcs: dict):
        self.epcs = epcs
        try:
            self.insert()
            self.epcs.clear()
        except Exception as e:
            print(e)
            self.epcs.clear()
        
    def insert(self):
        updates = []
        for epc_data in self.epcs:
            epc = Epc.objects.get(property_id = epc_data["property_id"])
            epc.epc_image = epc_data["scraped_info"].get("epc_image")
            epc.epc_current = epc_data["scraped_info"].get("epc_current")
            epc.epc_potential = epc_data["scraped_info"].get("epc_potential")
            epc.epc_scraped = epc_data["scraped_info"].get("epc_scraped")
            updates.append(epc)
        
        Epc.objects.bulk_update(
            updates,
            [
                "epc_image",
                "epc_current",
                "epc_potential",
                "epc_scraped",
            ]
        )

class ImagePipeline:
    def __init__(self) -> None:
        self.images = []
        
    def process_items_manually(self, images: list[dict]):
        self.images = images
        try:
            self.insert()
            self.images.clear()
        except Exception as e:
            print(e)
            self.images.clear()
    
    def insert(self):
        primary_keys = [image for image in self.images]
        images = Image.objects.filter(pk__in=primary_keys)
        for image in images:
            image.image_file = self.images[image.pk]["image_file"]
            image.image_scraped = True
        # for image in self.images:
        #     image_property = Image.objects.get(pk=image["pk"])
        #     image_property.image_scraped = True
        #     updates.append(image_property)         
        
        Image.objects.bulk_update(
            images,
            ["image_file", "image_scraped"]
        )
        
        # Images.objects.bulk_create(
        #     [Images(
        #         composite_id = image["composite_id"],
        #         image_file = SimpleUploadedFile(f"{image['composite_id']}.png", ContentFile(image["image_binary"]).read(), content_type="image/png")
        #     ) for image in self.images]
        # )
        
        # ImageProperty.objects.bulk_update(
        #     updates,
        #     [
        #         "image_scraped"
        #     ]
        # )