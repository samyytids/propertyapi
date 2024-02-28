import django
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'api.settings'
django.setup()

from backend.models import *
from statistics import mean
from collections import defaultdict
from operator import itemgetter
from random import sample

def divide_chunks(l, n=10_000): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def total_pixels():
    ids = list(divide_chunks(Image.objects.filter(image_scraped=True, image_dimension__isnull=False).values_list("property_id", flat=True).distinct()))
    for idx, chunk in enumerate(ids):
        print(f"Image chunk: {idx+1}/{len(ids)} begun")
        images = Image.objects.filter(property_id__in = chunk, image_scraped=True, image_dimension__isnull=False)
        already_created = ImageDimensions.objects.all().values_list("property_id", flat=True).distinct()
        create_images = {}
        update_images = {}
        for idx, image in enumerate(images):
            if image.property_id.property_id in already_created or image.property_id.property_id in update_images:
                needed_dict = update_images
            else:
                needed_dict = create_images
            
            # Check if the property_id is already in the dictionary
            if image.property_id.property_id not in needed_dict:
                needed_dict[image.property_id.property_id] = {
                    "image_height": [],
                    "image_width": [],
                    "image_dimension": [],
                }

            # Append image attributes to the dictionary
            needed_dict[image.property_id.property_id]["image_dimension"].append(image.image_dimension)
            needed_dict[image.property_id.property_id]["image_height"].append(image.image_height)
            needed_dict[image.property_id.property_id]["image_width"].append(image.image_width)

        property_ids = list(update_images.keys())
        image_dimensions_to_update = ImageDimensions.objects.filter(property_id__in=property_ids)
        
        for image_dimensions in image_dimensions_to_update:
            update_data = update_images.get(image_dimensions.property_id)
            image_dimensions.avg_image_height = mean(update_data.get("image_height"))
            image_dimensions.avg_image_width = mean(update_data.get("image_width"))
            image_dimensions.total_pixels = sum(update_data.get("image_dimension"))
            image_dimensions.num_images = len(update_data.get("image_dimension"))
        
        ImageDimensions.objects.bulk_update(
            image_dimensions_to_update,
            [
                "avg_image_height",
                "avg_image_width",
                "total_pixels",
                "num_images",
            ],
            batch_size=5000
        )
        
        images_to_create = [
            ImageDimensions(
                property_id = property_id,
                total_pixels = sum(values["image_dimension"]),
                avg_image_height = mean(values["image_height"]),
                avg_image_width = mean(values["image_width"]),
                num_images = len(values["image_dimension"]),
            ) for property_id, values in create_images.items()
        ]
        
        ImageDimensions.objects.bulk_create(
            images_to_create,
            batch_size=5000,
            ignore_conflicts=True
        )
        
        property_ids = list(create_images.keys())
        properties_to_update = PropertyData.objects.filter(property_id__in=property_ids)
        
        for property_data in properties_to_update:
            total_pixels_obj = ImageDimensions.objects.get(property_id = property_data.property_id)
            property_data.total_pixels = total_pixels_obj

        PropertyData.objects.bulk_update(
            properties_to_update,
            ["total_pixels"],
            batch_size=5000
        )

def station_distances():
    ids = list(divide_chunks(StationDistance.objects.all().values_list("property_id", flat=True).distinct()))
    for idx, chunk in enumerate(ids):
        map = defaultdict(list)
        print(f"Station distance chunk: {idx+1}/{len(ids)} begun")
        elements = StationDistance.objects.filter(property_id__in=chunk)    
        for item in elements:
            map[item.property_id.property_id].append(item.station_distance)
        
        stations_to_create = []
        for property_id, stations in map.items():
            instance = AverageDistanceFromStation(
                property_id = property_id,
                avg_distance = mean(stations),
                number_of_stations = len(stations)
            )
            
            stations_to_create.append(instance)
        
        AverageDistanceFromStation.objects.bulk_create(
            stations_to_create,
            batch_size=5000,
            ignore_conflicts=True,
        )
        
        properties_to_update = PropertyData.objects.filter(property_id__in=chunk)
        
        for property_data in properties_to_update:
            avg_distance_obj = AverageDistanceFromStation.objects.get(property_id = property_data.property_id)
            property_data.avg_station_distance = avg_distance_obj

        PropertyData.objects.bulk_update(
            properties_to_update,
            ["avg_station_distance"],
            batch_size=5000
        )

def ever_premium():
    ids = list(divide_chunks(PremiumListing.objects.all().values_list("property_id", flat=True).distinct()))
    for idx, chunk in enumerate(ids):
        print(f"Ever premium chunk: {idx+1}/{len(ids)} begun")
        elements = PremiumListing.objects.filter(property_id__in=chunk)
        already_created = EverPremium.objects.all().values_list("property_id", flat=True).distinct()
        
        create_ever_premium = {}
        update_ever_premium = {}
        for element in elements:
            if element.property_id.property_id in already_created or element.property_id.property_id in update_ever_premium:
                needed_dict = update_ever_premium
            else:
                needed_dict = create_ever_premium
            
            # Check if the property_id is already in the dictionary
            if element.property_id.property_id not in needed_dict:
                needed_dict[element.property_id.property_id] = {
                    "ever_premium" : [],
                    "ever_featured" : [],
                }

            # Append element attributes to the dictionary
            needed_dict[element.property_id.property_id]["ever_premium"].append(element.premium_listing)
            needed_dict[element.property_id.property_id]["ever_featured"].append(element.featured_property)
        
        property_ids = list(update_ever_premium.keys())
        
        ever_premium_to_update = EverPremium.objects.filter(property_id__in=property_ids)
        
        for ever_premium in ever_premium_to_update:
            update_data = update_ever_premium.get(ever_premium.property_id)
            ever_premium.ever_featured = max(update_data.get("ever_featured"))
            ever_premium.ever_premium = max(update_data.get("ever_premium"))
        
        EverPremium.objects.bulk_update(
            ever_premium_to_update,
            [
                "ever_featured",
                "ever_premium",
            ],
            batch_size=5000
        )
        
        ever_premiums_to_create = [
            EverPremium(
                property_id = property_id,
                ever_premium = max(values["ever_premium"]),
                ever_featured = max(values["ever_featured"]),
            ) for property_id, values in create_ever_premium.items()
        ]
        
        EverPremium.objects.bulk_create(
            ever_premiums_to_create,
            batch_size=5000,
            ignore_conflicts=True
        )
        
        
        property_ids = list(create_ever_premium.keys())
        
        properties_to_update = PropertyData.objects.filter(property_id__in=property_ids)
        
        for property_data in properties_to_update:
            ever_premium_obj = EverPremium.objects.get(property_id = property_data.property_id)
            property_data.ever_premium = ever_premium_obj

        PropertyData.objects.bulk_update(
            properties_to_update,
            ["ever_premium"],
            batch_size=5000
        )
    
def test():
    ...