from django.test import TestCase
from backend.models import *
from backend.rightmove_parser import RightmoveParser
import json
from django.db.models import Prefetch

class NoReallyThisTime(TestCase):
    def setUp(self) -> None:
        self.data = []
        for i in range(100):
            with open(f"./data/{i}.json", "r") as f:
                self.data.append(
                    json.load(f)
                )
                
        Property.objects.bulk_create(
            [Property(
                property_id=data.get("propertyData", {}).get("id"),
                property_url="https://www.cum.com",
            ) for data in self.data],
            ignore_conflicts=True
        )
        
    def test0(self) -> None:
        parser = RightmoveParser()
        property_data_table_data = []
        property_table_data = []
        text_elements_table_data = []
        tax_table_data = []
        ownership_table_data = []
        epc_table_data = []
        location_table_data = []
        layout_table_data = []
        station_table_data = []
        station_distance_table_data = []
        estate_agent_table_data = []
        price_table_data = []
        key_feature_table_data = []
        status_table_data = []
        image_table_data = []
        floorplan_table_data = []
        room_table_data = []
        premium_listing_table_data = []
        business_type_table_data = []
        lettings_table_data = []
        affiliation_table_data = []
        agent_affiliation_table_data = []
        
        for item in self.data:
            data = parser.parse(item, item.get("propertyData", {}).get("id", ""))
            if not data:
                continue
            
            property_data = data.get("property_data_table").get("property")
            if not property_data.get("current_price"):
                continue
            
            layout_data: Layout = data.get("layout_table")
            if layout_data.bedrooms is None:
                continue
            
            property_data = data.get("property_table")
            property_table_data.append(property_data)
            
            property_value_data = data.get("property_data_table")
            property_data_table_data.append(property_value_data)
            
            layout_table_data.append(layout_data)
            text_data = data.get("text_elements_table")
            text_elements_table_data.append(text_data)
            tax_data = data.get("tax_table")
            tax_table_data.append(tax_data)
            ownership_data = data.get("ownership_table")
            ownership_table_data.append(ownership_data)
            epc_data = data.get("epc_table")
            if epc_data:
                epc_table_data.append(epc_data)
                
            location_data = data.get("location_table")
            location_table_data.append(location_data)
            station_data = data.get("station_table")
            station_table_data.extend(station_data)
            station_distance_data = data.get("station_distance_table")
            station_distance_table_data.extend(station_distance_data)
            estate_agent_data = data.get("estate_agent_table")
            estate_agent_table_data.append(estate_agent_data)
            price_data = data.get("price_table")
            price_table_data.append(price_data)
            key_feature_data = data.get("key_feature_table")
            key_feature_table_data.extend(key_feature_data)
            status_data = data.get("status_table")
            status_table_data.append(status_data)
            image_data = data.get("image_table")
            image_table_data.extend(image_data)
            floorplan_data = data.get("floorplan_table")
            floorplan_table_data.extend(floorplan_data)
            room_data = data.get("room_table")
            room_table_data.extend(room_data)
            premium_data = data.get("premium_listing_table")
            premium_listing_table_data.append(premium_data)
            business_type_data = data.get("business_type_table")
            business_type_table_data.append(business_type_data)
            lettings_data = data.get("lettings_table")
            if lettings_data:
                lettings_table_data.append(lettings_data)
              
            affiliation_data = data.get("affiliation_table")
            if affiliation_data:
                affiliation_table_data.extend(affiliation_data)
                agent_affiliation_data = data.get("agent_affiliation_table")
                agent_affiliation_table_data.extend(agent_affiliation_data)
             
        Text.objects.bulk_create(
            text_elements_table_data,
            ignore_conflicts=True
        )
        
        Tax.objects.bulk_create(
            tax_table_data,
            ignore_conflicts=True
        )
        
        Ownership.objects.bulk_create(
            ownership_table_data,
            ignore_conflicts=True
        )
        
        Epc.objects.bulk_create(
            epc_table_data,
            ignore_conflicts=True
        )
        
        Location.objects.bulk_create(
            location_table_data,
            ignore_conflicts=True
        )
        
        Layout.objects.bulk_create(
            layout_table_data,
            ignore_conflicts=True
        )
        
        Station.objects.bulk_create(
            station_table_data,
            ignore_conflicts=True
        )
        
        EstateAgent.objects.bulk_create(
            estate_agent_table_data,
            ignore_conflicts=True
        )
        
        Affiliation.objects.bulk_create(
            affiliation_table_data, 
            ignore_conflicts=True
        )
        
        
        
        BusinessType.objects.bulk_create(
            business_type_table_data,
            ignore_conflicts=True
        )
        
        LettingInfo.objects.bulk_create(
            lettings_table_data,
            ignore_conflicts=True
        )
        
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
                ) for property in property_data_table_data],
            ignore_conflicts=True
        )
        
        for idx, property in enumerate(property_table_data):
            property.property_data = PropertyData.objects.get(property_id = property.property_id)
            property_table_data[idx] = property
        
        Property.objects.bulk_update(
                property_table_data,
                ["archived", "un_published", "stc", "property_data"],
        )
        
        Price.objects.bulk_create(
            [Price(
                property_id = Property.objects.get(property_id = price_data["property_id"]),
                price = price_data["price"],
                price_qualifier = price_data["price_qualifier"],
                original_price = price_data["original_price"],
                price_date = price_data["price_date"],
            )for price_data in price_table_data],
            ignore_conflicts=True
        )
        
        Status.objects.bulk_create(
            [Status(
                property_id = Property.objects.get(
                    property_id = status_data["property_id"]
                    ),
                stc = status_data["stc"],
                status_date = status_data["status_date"]
            )for status_data in status_table_data],
            ignore_conflicts=True
        )
        
        KeyFeature.objects.bulk_create(
            [KeyFeature(
                property_id = Property.objects.get(property_id = feature_data["property_id"]),
                feature = feature_data["feature"]
            )for feature_data in key_feature_table_data],
            ignore_conflicts=True
        )
        
        Image.objects.bulk_create(
            [Image(
                property_id = Property.objects.get(property_id = image_data["property_id"]),
                image_url = image_data["image_url"],
                image_caption = image_data["image_caption"],
            ) for image_data in image_table_data],
            ignore_conflicts=True
        )
        
        Floorplan.objects.bulk_create(
            [Floorplan(
                property_id = Property.objects.get(property_id = floorplan_data["property_id"]),
                floorplan_url = floorplan_data["floorplan_url"],
                floorplan_caption = floorplan_data["floorplan_caption"],
            ) for floorplan_data in floorplan_table_data],
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
            ) for room_data in room_table_data],
            ignore_conflicts=True
        )
        
        PremiumListing.objects.bulk_create(
            [PremiumListing(
                property_id = Property.objects.get(property_id = premium_data["property_id"]),
                featured_property = premium_data["featured_property"],
                premium_listing = premium_data["premium_listing"],
                listing_date = premium_data["listing_date"],
            ) for premium_data in premium_listing_table_data],
            ignore_conflicts=True
        )
        
        StationDistance.objects.bulk_create(
            [StationDistance(
                station_id = Station.objects.get(station_name = station.get("station_id")),
                property_id = PropertyData.objects.get(property_id = station.get("property_id")),
                station_distance = station.get("station_distance"),
                station_distance_unit = station.get("station_distance_unit"),
            )for station in station_distance_table_data],
            ignore_conflicts=True
        )
        
        AgentAffiliation.objects.bulk_create(
            [AgentAffiliation(
                affiliation_id = Affiliation.objects.get(affiliation_name = affiliation.get("affiliation_id").affiliation_name),
                agent_id = EstateAgent.objects.get(agent_name = affiliation.get("agent_id").agent_name, branch_name = affiliation.get("agent_id").branch_name)
            ) for affiliation in agent_affiliation_table_data],
            ignore_conflicts=True
        )
        
        self.assertEqual(len(Text.objects.all()), len(PropertyData.objects.all()))
        self.assertEqual(len(Tax.objects.all()), len(PropertyData.objects.all()))
        self.assertEqual(len(Ownership.objects.all()), len(PropertyData.objects.all()))
        self.assertLess(len(Epc.objects.all()), len(PropertyData.objects.all()))
        self.assertEqual(len(Location.objects.all()), len(PropertyData.objects.all()))
        self.assertEqual(len(Location.objects.all()), len(PropertyData.objects.all()))
        self.assertLess(len(Station.objects.all()), len(StationDistance.objects.all()))
        
        # This will be stored as a keyfeature_set
        # item = Property.objects.prefetch_related("keyfeature_set").first()
        
    def test1(self) -> None:
        instances = PropertyData.objects.all().prefetch_related(
            Prefetch("price_set", to_attr="price_history")).select_related(
                "text"
            )
        
        for instance in instances:
            print(instance.text)
    
    def test2(self) -> None:
        instances = PropertyData.objects.all().values_list("property_id", "current_price")
        raw_instance = PropertyData.objects.all()
        for instance in raw_instance:
            instance.current_price = 1
            
        PropertyData.objects.bulk_update(
            raw_instance, ["current_price"]
        )
        
        new_instances = PropertyData.objects.all().values_list("property_id", "current_price")
        
        success = True
        
        for idx, instance in enumerate(new_instances):
            if instance[1] != instances[idx][1]:
                success = False
        
        self.assertTrue(success)
    
    def test3(self) -> None:
        instances = PropertyData.objects.all().select_related("agent")
        for item in instances:
            print(item.agent.affiliation.all())
        
    def test4(self) -> None:
        instances = Property.objects.all().values()
        for instance in instances:
            print(instance)