import django, os, sys, joblib, json, io
from django.db.models import Avg, Count, Sum, IntegerField, Max, Q
from django.db.models.functions import Cast
from collections import defaultdict
from backend.models import *

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'api.settings'
django.setup()

def divide_chunks(l, n=10_000): 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def total_pixels():
    image_ids = set(Image.objects.filter(image_scraped=True, image_dimension__isnull=False).values_list("property_id__property_id", flat=True).distinct())
    image_dimension_ids = set(ImageDimensions.objects.values_list("property_id", flat=True))
    ids = list(divide_chunks(list(image_ids-image_dimension_ids)))
    for idx, chunk in enumerate(ids):
        print(f"Image chunk: {idx+1}/{len(ids)} begun")
        images = Image.objects\
            .values("property_id__property_id")\
            .annotate(
                total_pixels=Sum("image_dimension"),
                avg_height=Avg("image_height"),
                avg_width=Avg("image_width"),
                num_images=Count("id"),
                null_count=Count("id", filter = Q(image_binary__isnull=True))
            )\
            .filter(property_id__property_id__in = chunk, null_count__lt=1)
            
        values = defaultdict(ImageDimensions)
        for idx, image in enumerate(images):
            property_id = image["property_id__property_id"]
            values[property_id].property_id = property_id
            values[property_id].total_pixels = image["total_pixels"]
            values[property_id].avg_image_height = image["avg_height"]
            values[property_id].avg_image_width = image["avg_width"]
            values[property_id].num_images = image["num_images"]
        
        ImageDimensions.objects.bulk_create(
            list(values.values()),
            batch_size=5000,
            ignore_conflicts=True
        )
        
        property_ids = list(values.keys())
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
    ids = list(
        divide_chunks(
            StationDistance.objects.filter(
                property_id__avg_station_distance__isnull=True
            )\
            .values_list(
                "property_id__property_id", flat=True
            )\
            .distinct()
        )
    )
    
    for idx, chunk in enumerate(ids):
        print(f"Station distance chunk: {idx+1}/{len(ids)} begun")
        elements = StationDistance.objects.filter(property_id__property_id__in=chunk)\
            .values("property_id__property_id")\
            .annotate(
                avg_distance = Avg("station_distance"),
                number_of_stations = Count("station_distance"),
            )
        stations_to_create = [
            AverageDistanceFromStation(property_id = property.get("property_id__property_id"),
            avg_distance = property.get("avg_distance"),
            number_of_stations = property.get("number_of_stations"))
            for property in elements
        ]
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
        elements = PremiumListing.objects.filter(property_id__in=chunk)\
            .values("property_id__property_id")\
            .annotate(
                ever_premium = Max(Cast("premium_listing", output_field=IntegerField())),
                ever_featured = Max(Cast("featured_property", output_field=IntegerField())),
            )
        already_created = EverPremium.objects.all().values_list("property_id", flat=True).distinct()
        
        create_ever_premium = defaultdict(EverPremium)
        update_ever_premium = defaultdict(EverPremium)
        for element in elements:
            if element.get("property_id") in already_created or element.get("property_id") in update_ever_premium:
                needed_dict = update_ever_premium
            else:
                needed_dict = create_ever_premium
            
            property_id = element.get("property_id__property_id")

            needed_dict[property_id].property_id = property_id
            needed_dict[property_id].ever_featured = element.get("every_featured")
            needed_dict[property_id].ever_premium = element.get("ever_premium")
            
        property_ids = list(update_ever_premium.keys())
        
        ever_premium_to_update = EverPremium.objects.filter(property_id__in=property_ids)
        
        for ever_premium in ever_premium_to_update:
            update_data = update_ever_premium.get(ever_premium.property_id)
            ever_premium.ever_featured = update_data.ever_featured
            ever_premium.ever_premium = update_data.ever_premium
        
        EverPremium.objects.bulk_update(
            ever_premium_to_update,
            [
                "ever_featured",
                "ever_premium",
            ],
            batch_size=5000
        )
        
        EverPremium.objects.bulk_create(
            list(create_ever_premium.values()),
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
    
def reduce_keyfeatures():
    ids = list(divide_chunks(KeyFeature.objects.all().values_list("property_id", flat=True).distinct()))
    for idx, chunk in enumerate(ids):
        print(f"Key feature chunk: {idx+1}/{len(ids)} begun")
        model = joblib.load("model.joblib")
        vectorizer = joblib.load("vectorizer.joblib")
        data = KeyFeature.objects.filter(property_id__property_data__reduced_features__isnull=True, property_id__in=chunk).values_list("feature", "property_id__property_id")
        if len(data) == 0:
            continue
    
        data, ids = [list(x) for x in zip(*data)]
        X = vectorizer.transform(data)
        new_cluster_labels = model.predict(X)
        values = defaultdict(ReducedFeatures)
        for idx, label in enumerate(new_cluster_labels):
            
            values[ids[idx]].property_id = ids[idx]
            if values[ids[idx]].reduced_feature_list is None:
                values[ids[idx]].reduced_feature_list = []
            values[ids[idx]].reduced_feature_list.append(int(label+1))

        ReducedFeatures.objects.bulk_create(
            values.values(),
            ignore_conflicts=True
        )
        
        properties_to_update = PropertyData.objects.filter(property_id__in=ids)
        for property_data in properties_to_update:
            reduced_features_obj = ReducedFeatures.objects.get(property_id = property_data.property_id)
            property_data.reduced_features = reduced_features_obj

        PropertyData.objects.bulk_update(
            properties_to_update,
            ["reduced_features"],
            batch_size=5000
        )

def test():
    ...