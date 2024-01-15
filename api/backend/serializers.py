from rest_framework import serializers
from rest_framework.fields import empty
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
        exclude = ["property_id", "id", "floorplan_file"]

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        exclude = ["property_id", "id", "image_file"]

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
    class Meta:
        model = PremiumListing
        # fields = "__all__"
        exclude = ["property_id", "id"]

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
    price_history = PriceSerializer(many=True, read_only=True, source="prices")
    premium_listing_history = PremiumListingSerializer(many=True, read_only=True, source="premiumlisting")
    key_features = KeyFeatureSerializer(many=True, read_only=True, source="keyfeature")
    images = ImageSerializer(many=True, read_only=True, source="image")
    floorplans = FloorplanSerializer(many=True, read_only=True, source="floorplan")
    property_data = PropertyDataSerializer()
   
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
            "property_data",
            "price_history",
            "premium_listing_history",
            "key_features",
            "images",
            "floorplans",
        ]
        
    def __init__(self, *args, **kwargs):
        submitted_fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
                
        if submitted_fields is not None:
            allowed = [list(item.keys())[0] if isinstance(item, dict) else item for item in submitted_fields["property"]]
            allowed = set(allowed)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        
        def get_fields(all_fields: dict, submitted_fields: dict):
            for key, value in all_fields.items():
                if not key in submitted_fields:
                    all_fields.pop(key)
        
        def get_fields(input: dict, result: dict) -> dict:
            result = {}
            for key, value in input.items():
                for field in value:
                    if isinstance(field, dict):
                        result[key] = get_fields(field, result[key])
                    else:
                        result[key][field] = ""
            return result

        
        
                
        
    
        
        