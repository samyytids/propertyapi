from rest_framework import serializers
from backend.models import *

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class FloorplanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floorplan
        exclude = ["property_id", "id"]

class ImageSerializer(serializers.ModelSerializer):
    pixel_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        exclude = ["property_id", "id"]
    
    def get_pixel_count(self, obj: Image):
        height = obj.image_file.height
        width = obj.image_file.width
        
        return width * height
                
class AffiliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliation
        exclude = ["id"]

class EstateAgentSerializer(serializers.ModelSerializer):
    affiliation = AffiliationSerializer(many=True)
    class Meta:
        model = EstateAgent
        fields = "__all__"
        
class OwnershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ownership
        exclude = ["property_id", "id"]
        
class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ["station_name", "station_type"]

class StationDistanceSerializer(serializers.ModelSerializer):
    station_data = StationSerializer(read_only=True, source="station_id")
    class Meta:
        model = StationDistance
        exclude = ["station_id", "id", "property_id"]
        
class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        # fields = "__all__"
        exclude = ["property_id", "id"]

class LettingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LettingInfo
        # fields = "__all__"
        exclude = ["property_id", "id"]

class LayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layout
        # fields = "__all__"
        exclude = ["property_id", "id"]

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        # fields = "__all__"
        exclude = ["property_id", "id"]

class EpcSerializer(serializers.ModelSerializer):
    class Meta:
        model = Epc
        # fields = "__all__"
        exclude = ["property_id", "id", "epc_image", "ei_image"]

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        # fields = "__all__"
        exclude = ["property_id", "id"]

class KeyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyFeature
        # fields = "__all__"
        exclude = ["property_id", "id"]
class PremiumListingSerializer(serializers.ModelSerializer):
    premium_listing_ever = serializers.SerializerMethodField()
    featured_property_ever = serializers.SerializerMethodField()
    class Meta:
        model = PremiumListing
        # fields = "__all__"
        exclude = ["property_id", "id"]
    
    def get_premium_listing_ever(self, obj: PremiumListing): 
        return PremiumListing.objects.filter(property_id=obj.property_id, premium_listing=True).exists()
    
    def get_featured_property_ever(self, obj: PremiumListing): 
        return PremiumListing.objects.filter(property_id=obj.property_id, featured_property=True).exists()

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        # fields = "__all__"
        exclude = ["property_id", "id"]

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        # fields = "__all__"
        exclude = ["property_id", "id"]

class PropertyDataSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    text = TextSerializer()
    tax = TaxSerializer()
    epc = EpcSerializer()
    location = LocationSerializer()
    layout = LayoutSerializer()
    business_type = BusinessTypeSerializer()
    letting_info = LettingInfoSerializer()
    station = StationDistanceSerializer(many=True, read_only=True, source="stationdistance_set")
    agent = EstateAgentSerializer()
    class Meta:
        model = PropertyData
        fields = [
            "property_id",
            "property_url",
            "listing_type",
            "transaction_type",
            "virtual_tour",
            "auction",
            "retirement",
            "affordable_scheme",
            "property_type",
            "property_sub_type",
            "added_date",
            "letting_type",
            "pre_owned",
            "furnished",
            "current_price",
            "reduced",
            "online_viewing",
            "text",
            "tax",
            "epc",
            "location",
            "layout",
            "station",
            "agent",
            "business_type",
            "letting_info",
            "first_scraped",
        ]

class PropertySerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    # price_history = PriceSerializer(many=True, read_only=True)
    # premium_listing_history = PremiumListingSerializer(many=True, read_only=True)
    # premium_listing = serializers.SerializerMethodField()
    # featured_property = serializers.SerializerMethodField()
    # pixel_count = serializers.SerializerMethodField()
    # key_features = serializers.SerializerMethodField()
    # images = ImageSerializer(many=True, read_only=True)
    # floorplans = FloorplanSerializer(many=True, read_only=True)
    # property_data = PropertyDataSerializer()
   
    class Meta:
        model = Property
        # exclude = ["id"]
        fields = [
            "property_id",
            "property_url",
            "scraped_before",
            "un_published",
            "archived",
            "bad_data",
            "removed",
            "stc",
            # "property_id",
            # "property_url",
            # "scraped_before",
            # "un_published",
            # "archived",
            # "bad_data",
            # "removed",
            # "stc",
            # "property_data",
            # "price_history",
            # "premium_listing",
            # "featured_property",
            # "premium_listing_history",
            # "key_features",
            # "pixel_count",
            # "images",
            # "floorplans",
        ]
        
    def __init__(self, *args, **kwargs):
        submitted_fields: dict = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        def get_fields(submitted_fields: dict, self: PropertySerializer, result: dict):
            for key, value in submitted_fields.items():
                if isinstance(value, dict):
                    sub_serializer = self.fields[key]
                    result[key] = {}
                    sub_serializer.fields = get_fields(submitted_fields[key], self.fields[key], result[key])
                    result[key] = sub_serializer
                else:
                    if hasattr(self.fields[key], "many"):
                        _fields = {sub_key: self.fields[key].child.fields[sub_key] for sub_key in value}
                        self.fields[key].child.fields = _fields
                        result[key] = self.fields[key]
                    else:
                        result[key] = self.fields[key]
            return result
        
        try:
            self.fields = get_fields(submitted_fields, self, {})
        except Exception as e:
            print(e)
    
    # def get_premium_listing(self, obj: Property):
    #     return PremiumListing.objects.filter(property_id=obj.property_id, premium_listing=True).exists()

    # def get_featured_property(self, obj: Property):
    #     return PremiumListing.objects.filter(property_id=obj.property_id, featured_property=True).exists()
    
    # def get_pixel_count(self, obj: Property): 
    #     pixel_count = 0
    #     image: Image

    #     for image in Image.objects.filter(property_id=obj):
    #         pixel_count += image.image_file.height * image.image_file.width
    #     return pixel_count

    # def get_key_features(self, instance: Property):
    #     filter_condition = self.context.get("key_features")
    #     filter_condition["property_id"] = instance
    #     key_features = KeyFeature.objects.filter(**filter_condition)
    #     return KeyFeatureSerializer(key_features, many=True).data
        
    
        
        