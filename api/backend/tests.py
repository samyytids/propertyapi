from django.test import TestCase
import json
from backend.models import *
from backend.data_parser import DataParser


class NoReallyThisTime(TestCase):
    def setUp(self) -> None:
        self.data = []
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
        self.ownership = []
        self.prices = []
        self.statuses = []
        self.accreditations = []
        self.have_accreditations = []
        for i in range(0, 800):
            with open(f"./backend/test_data/propertypal{i}.json") as f:
                self.data.append({"data" : json.load(f), "id_number": i})
    
    def get_update_objects(self, table, id: str|None = None) -> list:
        # objects_to_update = {update[id]: table.objects.get(property = update[id]) for update in self.properties}
        
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
        
        print(f"{key}: {len(table.objects.all())}")
        
    @staticmethod
    def one_to_one_list_no_id(table, property_data, name, ignore=False):
        
        table.objects.bulk_create(
            [table(
                **property
            )
            for property in property_data],
            ignore_conflicts=ignore
        )
        
        print(f"{name}: {len(table.objects.all())}")
        
    @staticmethod
    def one_to_one_no_id(table, property_data, key, ignore=False):
        table.objects.bulk_create(
            [table(
                **property[key]
            )
            for property in property_data],
            ignore_conflicts=ignore
        )
        
        print(f"{key}: {len(table.objects.all())}")

    @staticmethod
    def one_to_many(table, property_data, name, ignore=False):        
        table.objects.bulk_create(
            [table(
                **item
            )
            for item in property_data],
            ignore_conflicts=ignore
        )
        
        print(f"{name}: {len(table.objects.all())}")  
    
    def test_one(self):
        for property in self.data:
            if "props" in property["data"]:
                data = self.parser.parse(property["data"], f"P{property['data']['props']['pageProps']['property']['pathId']}")
            else:
                data = self.parser.parse(property["data"], f"R{property['data']['propertyData']['id']}")
            self.property_data.append(data["single"])
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
            self.properties.append(data["property"])
        
        Property.objects.bulk_create(
            [
                Property(
                    property=property["property_id"]["property_id"],
                    url = "fake",
                )
            for property in self.property_data]
        )
        
        self.one_to_one_no_id(PropertyValue, self.property_data, "property_id", True)
        self.one_to_one(TextElements, self.property_data, "text_elements", True)
        self.one_to_one(OwnershipRetirement, self.property_data, "ownership_retirement", True)
        self.one_to_one(Location, self.property_data, "location", True)
        self.one_to_one(Broadband, self.property_data, "broadband", True)
        self.one_to_one(EPC, self.property_data, "epc", True)
        self.one_to_one(ListingType, self.property_data, "listing_type", True)
        self.one_to_one(Layout, self.property_data, "layout")
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
            ) for accreditation in self.have_accreditations]
        )
        print(f"estate agent accreditation : {len(EstateAgentAccreditation.objects.all())}")    
        
        StationStationDistance.objects.bulk_create(
            [StationStationDistance(
                property_id = PropertyValue(property_id = station["property_id"]),
                station_id = Station(station_name = station["station_name"]),
                station_distance = station["station_distance"],
                station_distance_units = station["station_distance_units"]
            ) for station in self.station_distances]
        )
        print(f"station distances : {len(StationStationDistance.objects.all())}") 
        
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
        
        for property in Property.objects.all():
            property_value = property.property_values
            print(property_value.layout.bedrooms)
            print(property_value.estate_agent)

# These are tests where the database starts with no data in it. 
class FinalTests(TestCase):
    def setUp(self) -> None:
        self.data = []
        for i in range(0, 800):
            with open(f"./backend/test_data/propertypal{i}.json") as f:
                self.data.append({"data" : json.load(f), "id_number": i})
            with open(f"./backend/test_data/rightmove{i}.json") as f:
                self.data.append({"data" : json.load(f), "id_number": i})  
        
    @staticmethod
    def one_to_one(table, property_data, key, ignore=False):
        table.objects.bulk_create(
            [table(
                property_id = property["property_id"],
                **property[key]
            )
            for property in property_data],
            ignore_conflicts=ignore
        )
        
        print(f"{key}: {len(table.objects.all())}")
        
    @staticmethod
    def one_to_one_list_no_id(table, property_data, name, ignore=False):
        
        table.objects.bulk_create(
            [table(
                **property
            )
            for property in property_data],
            ignore_conflicts=ignore
        )
        
        print(f"{name}: {len(table.objects.all())}")
        
    @staticmethod
    def one_to_one_no_id(table, property_data, key, ignore=False):
        table.objects.bulk_create(
            [table(
                **property[key]
            )
            for property in property_data],
            ignore_conflicts=ignore
        )
        
        print(f"{key}: {len(table.objects.all())}")

    @staticmethod
    def one_to_many(table, property_data, name, ignore=False):        
        table.objects.bulk_create(
            [table(
                **item
            )
            for item in property_data],
            ignore_conflicts=ignore
        )
        
        print(f"{name}: {len(table.objects.all())}")    
    
    def test_parsing(self):
        parser = DataParser()
        property_data = []
        properties = []
        views = []
        key_features = []
        images = []
        floorplans = []
        rooms = []
        stations = []
        station_distances = []
        prices = []
        statuses = []
        accreditations = []
        have_accreditations = []
        
        for property in self.data:
            if "props" in property["data"]:
                data = parser.parse(property["data"], f"P{property['data']['props']['pageProps']['property']['pathId']}")
            else:
                data = parser.parse(property["data"], f"R{property['data']['propertyData']['id']}")
            property_data.append(data["single"])
            views.extend(data["views"])
            key_features.extend(data["key_features"])
            images.extend(data["images"])
            floorplans.extend(data["floorplans"])
            rooms.extend(data["rooms"])
            stations.extend(data["stations"])
            station_distances.extend(data["station_distances"])
            prices.extend(data["prices"])
            statuses.extend(data["statuses"])    
            accreditations.extend(data["accreditations"])
            have_accreditations.extend(data["have_accreditations"])

        self.one_to_one_no_id(PropertyValue, property_data, "property_id", True)
        self.one_to_one(TextElements, property_data, "text_elements", True)
        self.one_to_one(Location, property_data, "location", True)
        self.one_to_one(Broadband, property_data, "broadband", True)
        self.one_to_one(EPC, property_data, "epc", True)
        self.one_to_one(ListingType, property_data, "listing_type", True)
        self.one_to_one(Layout, property_data, "layout")
        self.one_to_one(Tax, property_data, "tax", True)
        self.one_to_one(Tenure, property_data, "tenure", True)
        self.one_to_one_list_no_id(Station, stations, "stations", True)
        self.one_to_one_list_no_id(Accreditation, accreditations, "accreditations", True)
        self.one_to_many(ImageProperty, images, "images", True)
        self.one_to_many(FloorplanProperty, floorplans, "floorplans", True)
        self.one_to_one_no_id(EstateAgent, property_data, "estate_agent", True)
        self.one_to_many(KeyFeature, key_features, "key_features", True)
        self.one_to_many(Views, views, "views", True)
        self.one_to_many(Rooms, rooms, "rooms", True)
        self.one_to_many(Prices, prices, "prices", True)
        self.one_to_many(Statuses, statuses, "statuses", True)
        
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
            ) for accreditation in have_accreditations]
        )
        print(f"estate agent accreditation : {len(EstateAgentAccreditation.objects.all())}")    
        
        StationStationDistance.objects.bulk_create(
            [StationStationDistance(
                property_id = PropertyValue(property_id = station["property_id"]),
                station_id = Station(station_name = station["station_name"]),
                station_distance = station["station_distance"],
                station_distance_units = station["station_distance_units"]
            ) for station in station_distances]
        )
        print(f"station distances : {len(StationStationDistance.objects.all())}")    
        
        for property in PropertyValue.objects.all():
            print(property.tenure.tenure_type)
        
        
        
        




class CleanTests(TestCase):
    def setUp(self) -> None:
        self.data = []
        for i in range(0, 500):
            with open(f"./backend/test_data/propertypal{i}.json") as f:
                self.data.append({"data" : json.load(f), "id_number": i})
            with open(f"./backend/test_data/rightmove{i}.json") as f:
                self.data.append({"data" : json.load(f), "id_number": i})        
        
    @staticmethod
    def extract_text_data(data: dict) -> dict:
        description = {}
        if "props" in data:
            # Property pal
            property_data = data["props"]["pageProps"]["property"]
            description = {
                "description" : property_data.get("description", "")
            }
            
        else:
            # Rightmove
            property_data = data["propertyData"]
            description_section = property_data.get("text", {})
            description = {
                "description" : description_section.get("description", None),
                "share_text" : description_section.get("shareText", None),
                "share_description" : description_section.get("shareDescription", None)
            }
        return description
    
    @staticmethod
    def extract_images(data: dict, id: str) -> list[dict]:
        images = []
        if "props" in data:
            image_data = data["props"]["pageProps"]["property"].get("images", {})
            for idx, image in enumerate(image_data):
                image_dict = {
                    "composite_id": f"{id}_{idx}",
                    "image_url": image["url"],
                    "image_caption": image["imageType"],
                    "image_url_resized": image["urls"]["580x425:FILL_CROP"]
                }
                images.append(image_dict)
        else:
            image_data = data["propertyData"]["images"]
            for idx, image in enumerate(image_data):
                image_dict = {
                    "composite_id": f"{id}_{idx}",
                    "image_url": image["url"],
                    "image_caption": image["caption"],
                    "image_url_resized": image["resizedImageUrls"]["size656x437"]
                }
                images.append(image_dict)
        
        return images
    
    @staticmethod
    def extract_fake_id(data: dict, id_num: int) -> str:
        if "props" in data:
            return f"p{id_num}"
        else:
            return f"r{id_num}"
    
    def test_basic(self):
        self.assertEqual(len(self.data), 1000)
        text_elements = []
        properties = []
        for property in self.data:
            text_element = self.extract_text_data(property["data"])
            id = self.extract_fake_id(property["data"], property["id_number"])
            url = "fake"
            property = {
                "property" : id,
                "url": url
            }
            
            text_elements.append(text_element)
            properties.append(property)
        
        TextElements.objects.bulk_create(
            [TextElements(**text_element, property_id = properties[idx]["property"]) for idx, text_element in enumerate(text_elements)],
            ignore_conflicts=True
        )
        
        PropertyValue.objects.bulk_create(
            [PropertyValue(property_id = properties[idx]["property"], text_elements=TextElements.objects.get(property_id=properties[idx]["property"]))
            for idx, _ in enumerate(properties)]
        )
        
        Property.objects.bulk_create(
            [Property(**property, property_values=PropertyValue.objects.get(property_id=property["property"])) for property in properties],
            ignore_conflicts=True
        )
        
        self.assertEqual(len(Property.objects.all()), 1000)
        self.assertEqual(len(TextElements.objects.all()), 1000)
        self.assertEqual(len(PropertyValue.objects.all()), 1000)
    
    def test_one_to_many(self):
        images = []
        properties = []
        for property in self.data:
            id = self.extract_fake_id(property["data"], property["id_number"])
            image = self.extract_images(property["data"], id)
            url = "fake"
            property = {
                "property" : id,
                "url": url
            }
            
            images.extend(image)
            properties.append(property)
        
        Image.objects.bulk_create(
            [Image(composite_id = image["composite_id"]) for image in images]
        )
        
        PropertyValue.objects.bulk_create(
            [PropertyValue(property_id = property["property"])
            for idx, property in enumerate(properties)]
        )
        
        ImageProperty.objects.bulk_create(
            [ImageProperty(
                property = PropertyValue.objects.get(property_id = image["composite_id"].split("_")[0]),
                image_id = Image.objects.get(composite_id = image["composite_id"]),
                image_caption = image["image_caption"],
                image_url_resized = image["image_url_resized"],
                image_url = image["image_url"]
                ) for image in images]
        )
        
        Property.objects.bulk_create(
            [Property(**property,
                      property_values = PropertyValue.objects.get(property_id = property["property"])) for property in properties]
        )
    
class DirtyTests(TestCase):
    def setUp(self) -> None:
        setup_text_elements = []
        setup_properties = []
        images = []
        self.data = []
        
        for i in range(0, 500):
            with open(f"./backend/test_data/propertypal{i}.json") as f:
                self.data.append({"data" : json.load(f), "id_number": i})
            with open(f"./backend/test_data/rightmove{i}.json") as f:
                self.data.append({"data" : json.load(f), "id_number": i})
        
        for i in range(0, 200):
            with open(f"./backend/test_data/propertypal{i}.json") as f:
                property = json.load(f)
            with open(f"./backend/test_data/rightmove{i}.json") as f:
                property = json.load(f)
                
            text_element = self.extract_text_data(property)
            id = self.extract_fake_id(property, i)
            image = self.extract_images(property, id)
            url = "fake"
            text_element["property_id"] = id
            property = {
                "property" : id,
                "url": url
            }
            
            images.extend(image)
            setup_text_elements.append(text_element)
            setup_properties.append(property)
        
        TextElements.objects.bulk_create(
            [TextElements(**text_element) for idx, text_element in enumerate(setup_text_elements)],
            ignore_conflicts=True
        )
        
        Image.objects.bulk_create(
            [Image(composite_id = image["composite_id"]) for image in images],
            ignore_conflicts=True
        )
        
        PropertyValue.objects.bulk_create(
            [PropertyValue(property_id = property["property"], text_elements=TextElements.objects.get(property_id=property["property"]))
            for idx, property in enumerate(setup_properties)],
            ignore_conflicts=True
        )
        
        ImageProperty.objects.bulk_create(
            [ImageProperty(
                property = PropertyValue.objects.get(property_id = image["composite_id"].split("_")[0]),
                image_id = Image.objects.get(composite_id = image["composite_id"]),
                image_caption = image["image_caption"],
                image_url_resized = image["image_url_resized"],
                image_url = image["image_url"]
                ) for image in images],
            ignore_conflicts=True
        )
        
        Property.objects.bulk_create(
            [Property(**property, property_values=PropertyValue.objects.get(property_id=property["property"])) for property in setup_properties],
            ignore_conflicts=True
        )
    
    @staticmethod
    def extract_images(data: dict, id: str) -> list[dict]:
        images = []
        if "props" in data:
            image_data = data["props"]["pageProps"]["property"].get("images", {})
            for idx, image in enumerate(image_data):
                image_dict = {
                    "composite_id": f"{id}_{idx}",
                    "image_url": image["url"],
                    "image_caption": image["imageType"],
                    "image_url_resized": image["urls"]["580x425:FILL_CROP"]
                }
                images.append(image_dict)
        else:
            image_data = data["propertyData"]["images"]
            for idx, image in enumerate(image_data):
                image_dict = {
                    "composite_id": f"{id}_{idx}",
                    "image_url": image["url"],
                    "image_caption": image["caption"],
                    "image_url_resized": image["resizedImageUrls"]["size656x437"]
                }
                images.append(image_dict)
        
        return images    
    
    @staticmethod
    def extract_text_data(data: dict) -> dict:
        description = {}
        if "props" in data:
            # Property pal
            property_data = data["props"]["pageProps"]["property"]
            description = {
                "description" : property_data.get("description", "")
            }
            
        else:
            # Rightmove
            property_data = data["propertyData"]
            description_section = property_data.get("text", {})
            description = {
                "description" : description_section.get("description", None),
                "share_text" : description_section.get("shareText", None),
                "share_description" : description_section.get("shareDescription", None)
            }
        return description
    
    @staticmethod
    def extract_fake_id(data: dict, id_num: int) -> str:
        if "props" in data:
            return f"p{id_num}"
        else:
            return f"r{id_num}"
        
    def test_basic(self):
        self.assertEqual(len(self.data), 1000)
        text_elements = []
        properties = []
        for property in self.data:
            text_element = self.extract_text_data(property["data"])
            id = self.extract_fake_id(property["data"], property["id_number"])
            url = "fake"
            property = {
                "property" : id,
                "url": url
            }
            
            text_elements.append(text_element)
            properties.append(property)
        
        TextElements.objects.bulk_create(
            [TextElements(**text_element, property_id = properties[idx]["property"]) for idx, text_element in enumerate(text_elements)],
            ignore_conflicts=True
        )
        
        PropertyValue.objects.bulk_create(
            [PropertyValue(property_id = properties[idx]["property"], text_elements=TextElements.objects.get(property_id=properties[idx]["property"]))
            for idx, _ in enumerate(properties)],
            ignore_conflicts=True
        )
        
        Property.objects.bulk_create(
            [Property(**property, property_values=PropertyValue.objects.get(property_id=property["property"])) for property in properties],
            ignore_conflicts=True
        )
        
        self.assertEqual(len(Property.objects.all()), 1000)
        self.assertEqual(len(TextElements.objects.all()), 1000)
        self.assertEqual(len(PropertyValue.objects.all()), 1000)
        
        
    def test_one_to_many(self):
        images = []
        properties = []
        for property in self.data:
            id = self.extract_fake_id(property["data"], property["id_number"])
            image = self.extract_images(property["data"], id)
            url = "fake"
            property = {
                "property" : id,
                "url": url
            }
            
            images.extend(image)
            properties.append(property)
        
        Image.objects.bulk_create(
            [Image(composite_id = image["composite_id"]) for image in images],
            ignore_conflicts=True
        )
        
        PropertyValue.objects.bulk_create(
            [PropertyValue(property_id = property["property"])
            for idx, property in enumerate(properties)],
            ignore_conflicts=True
        )
        
        ImageProperty.objects.bulk_create(
            [ImageProperty(
                property = PropertyValue.objects.get(property_id = image["composite_id"].split("_")[0]),
                image_id = Image.objects.get(composite_id = image["composite_id"]),
                image_caption = image["image_caption"],
                image_url_resized = image["image_url_resized"],
                image_url = image["image_url"]
                ) for image in images],
            ignore_conflicts=True
        )
        
        Property.objects.bulk_create(
            [Property(**property,
                      property_values = PropertyValue.objects.get(property_id = property["property"])) for property in properties],
            ignore_conflicts=True
        )    

class PropertyPalTests(TestCase):
    def setUp(self) -> None:
        self.accreds = []
        self.data = []
        for i in range(0,500):
            with open(f"./backend/test_data/propertypal{i}.json") as f:
                self.data.append({"data" : json.load(f), "id_number": i})
    
    @staticmethod
    def extract_fake_id(data: dict, id_num: int) -> str:
        if "props" in data:
            return f"p{id_num}"
        else:
            return f"r{id_num}"
    
    @staticmethod
    def extract_estate_agent(data: dict) -> dict:
        property_data: dict = data["props"]["pageProps"]["property"]
        estate_agent_section = property_data.get("agents", []) or [{}]
        estate_agent_section = estate_agent_section[0]
        name = estate_agent_section.get("organisation", "")
        branch_name = estate_agent_section.get("organisationBranch", "")
        branch_url = estate_agent_section.get("websiteUrl")
        branch_display_address = estate_agent_section.get("displayAddress")
        
        return {
            "name" : name,
            "branch_name" : branch_name,
            "branch_display_address" : branch_display_address,
            "branch_url" : branch_url,
        }
        
    # @staticmethod
    def extract_accreditations(self, data: dict, id: str) -> dict: 
        property_data: dict = data["props"]["pageProps"]["property"]
        estate_agent_section: list[dict] = property_data.get("agents", []) or [{}]
        accreditations = estate_agent_section[0].get("accreditations", []) or []
        missing_accreditations = estate_agent_section[0].get("missingAccreditations", []) or []
        name = estate_agent_section[0].get("organisation", "")
        branch_name = estate_agent_section[0].get("organisationBranch", "")
        
        
        for accreditation in accreditations:
            accreditation["have_accreditation"]  = True
            accreditation["estate_agent"] = {
                "name": name,
                "branch_name": branch_name
            }
            self.accreds.append(accreditation)
        
        for accreditation in missing_accreditations:
            accreditation["have_accreditation"]  = False
            accreditation["estate_agent"] = {
                "name": name,
                "branch_name": branch_name
            }
            self.accreds.append(accreditation)
            
        
    def test_mini_agent(self):
        EstateAgent.objects.create(
            name = "piss",
            branch_name = ""
        )
        EstateAgent.objects.create(
            name = "off",
            branch_name = ""
        )
    
    def test_estate_agent(self): 
        estate_agents = []
        properties = []
        for property in self.data:
            estate_agent = self.extract_estate_agent(property["data"])
            id = self.extract_fake_id(property["data"], property["id_number"])
            estate_agent["property_id"] = id
            self.extract_accreditations(property["data"], property["id_number"])
            properties.append(id)
            estate_agents.append(estate_agent)
            
        EstateAgent.objects.bulk_create(
            [EstateAgent(name = estate_agent["name"],
                        branch_name = estate_agent["branch_name"],
                        branch_display_address = estate_agent["branch_display_address"],
                        branch_url = estate_agent["branch_url"]) for estate_agent in estate_agents],
            ignore_conflicts=True
        )
        
        Accreditation.objects.bulk_create(
            [Accreditation(
                accreditation_url = accreditation["url"],
                accreditation_label = accreditation["label"],
                accreditation_key = accreditation["textKey"],
                accreditation_type = accreditation["type"],
            )for accreditation in self.accreds],
            ignore_conflicts=True
        )

        EstateAgentAccreditation.objects.bulk_create(
            [EstateAgentAccreditation(
                estate_agent_id = EstateAgent.objects.get(name = accreditation["estate_agent"]["name"], branch_name = accreditation["estate_agent"]["branch_name"]),
                accreditation_id = Accreditation.objects.get(accreditation_label = accreditation["label"]),
                have_accreditation = accreditation["have_accreditation"]
            ) for accreditation in self.accreds]
        )
        
        insert_values = []
        for property in properties:
            for agent in estate_agents:
                if agent["property_id"] == property:
                    insert_values.append(
                        PropertyValue(
                            property_id = property,
                            estate_agent = EstateAgent.objects.get(
                                name = agent["name"],
                                branch_name = agent["branch_name"]
                            )
                        )
                    )  
        
        PropertyValue.objects.bulk_create(
            insert_values
        )
        
        Property.objects.bulk_create(
            [Property(
                property = property,
                property_values = PropertyValue.objects.get(property_id=property))
                for property in properties],
            ignore_conflicts=True
        )
        
        
        
class RightmoveTests(TestCase):
    def setUp(self) -> None:
        self.data = []
        for i in range(0,500):
            with open(f"./backend/test_data/rightmove{i}.json") as f:
                self.data.append({"data" : json.load(f), "id_number": i})
                
    @staticmethod
    def extract_station(data: dict, id: int) -> list[dict]:
        data = data["propertyData"]
        stations = data.get("nearestStations", []) or []
        station_list = []
        for station_data in stations:
            station = {
                "station_name": station_data["name"],
                "station_type": station_data["types"][0],
                "station_distance": station_data["distance"],
                "distance_unit": station_data["unit"],
                "property_id": id
            }
            station_list.append(station)
            
        return station_list
    
    @staticmethod
    def extract_fake_id(data: dict, id_num: int) -> str:
        if "props" in data:
            return f"p{id_num}"
        else:
            return f"r{id_num}"
    
    def test_station(self):
        stations = []
        properties = []
        for property in self.data:
            id = self.extract_fake_id(property["data"], property["id_number"])
            
            stations.extend(self.extract_station(property["data"], id))
            url = "fake"
            property = {
                "property" : id,
                "url": url
            }
            properties.append(property)
        
        Station.objects.bulk_create(
            [Station(
                station_name = station["station_name"],
                station_type = station["station_type"])
            for station in stations],
            ignore_conflicts=True
        )
        
        PropertyValue.objects.bulk_create(
            [PropertyValue(
                property_id = property["property"])
             for property in properties]
        )
        
        StationStationDistance.objects.bulk_create(
            [StationStationDistance(
                property_id = PropertyValue.objects.get(property_id = station["property_id"]),
                station_id = Station.objects.get(station_name = station["station_name"]),
                station_distance = station["station_distance"]
                ) 
            for station in stations]
        )
        
        
        Property.objects.bulk_create(
            [Property(**property, property_values = PropertyValue(property_id = property["property"])) for property in properties]
        )
        
        properties = Property.objects.all()
        for property in properties:
            stations = property.property_values.stations.all()
            for station in stations:
                station: Station
                print(station.station_name, station.station_type)
        
            
        

        
            
        
        
