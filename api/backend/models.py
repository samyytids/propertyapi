from django.db import models
import json
# Data tables

## One to one

class TextElements(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    description = models.TextField(null=True)
    share_text = models.TextField(null=True)
    share_description = models.TextField(null=True)

class Broadband(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    standard_upload = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    standard_download = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    super_fast_upload = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    super_fast_download = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    ultra_fast_upload = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    ultra_fast_download = models.DecimalField(max_digits=6, decimal_places=2, null=True)

class Tax(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    tax_band = models.CharField(max_length=20,null=True)
    tax_exempt = models.BooleanField(null=True)
    tax_included = models.BooleanField(null=True)
    annual_ground_rent = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    annual_ground_rent_review_period = models.IntegerField(null=True)
    annual_ground_rent_percentage_increase = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    annual_service_charge = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    domestic_rates = models.DecimalField(max_digits=20, decimal_places=10, null=True)

class OwnershipRetirement(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    ownership_type = models.BooleanField(null=True)
    retirement_home = models.BooleanField(null=True)

class Tenure(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    tenure_type = models.CharField(max_length=20,null=True)
    tenure_lease_years = models.IntegerField(null=True)
    tenure_text = models.TextField(null=True)
    
class EPC(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    epc_url = models.URLField(max_length=255, null=True)
    epc_scraped = models.BooleanField(default=False)
    epc_current = models.IntegerField(null=True)
    epc_potential = models.IntegerField(null=True)
    epc_image = models.ImageField(upload_to="epc_image/", null=True)

class Location(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    country = models.CharField(max_length=255, null=True)
    town = models.CharField(max_length=255, null=True)
    postcode = models.CharField(max_length=8, null=True)
    street = models.CharField(max_length=255, null=True)
    display_address = models.CharField(max_length=255)
    lat = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    long = models.DecimalField(max_digits=20, decimal_places=10, null=True)

class Layout(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    bathrooms = models.IntegerField(null=True)
    bedrooms = models.IntegerField(null=True)
    receptions = models.IntegerField(null=True)
    property_type = models.CharField(max_length=255, null=True)
    min_size = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    max_size = models.DecimalField(max_digits=20, decimal_places=10, null=True)

class ListingType(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    listing_type = models.CharField(max_length=30, null=True)
    letting_type = models.CharField(max_length=50, null=True)

class Added(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    added_date = models.DateField(null=True)

## Many to one

class Station(models.Model):
    station_name = models.CharField(max_length=200, primary_key=True)
    station_type = models.CharField(max_length=200, null=True)
        
class Accreditation(models.Model):
    accreditation_url = models.URLField(max_length=255)
    accreditation_label = models.CharField(max_length=255, primary_key=True)
    accreditation_key = models.CharField(max_length=255)
    accreditation_type = models.CharField(max_length=255)

class EstateAgent(models.Model):
    name = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200, null=True)
    branch_display_address = models.CharField(max_length=200, null=True)
    branch_url = models.CharField(max_length=200, null=True)
    branch_description = models.TextField(null=True)
    accreditations = models.ManyToManyField(Accreditation, through="EstateAgentAccreditation")

    class Meta:
        unique_together = [["name", "branch_name"]]
        
        
# Link tables

class PropertyValue(models.Model):
    property_id = models.CharField(max_length=20, primary_key=True)
    text_elements = models.OneToOneField(TextElements, on_delete=models.CASCADE, related_name="text_elements_id", null=True)
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name="location_id", null=True)
    broadband = models.OneToOneField(Broadband, on_delete=models.CASCADE, related_name="broadband_id", null=True)
    epc = models.OneToOneField(EPC, on_delete=models.CASCADE, related_name="epc_id", null=True)
    listing_type = models.OneToOneField(ListingType, on_delete=models.CASCADE, related_name="listing_type_id", null=True)
    layout = models.OneToOneField(Layout, on_delete=models.CASCADE, related_name="layout_id", null=True)
    tax = models.OneToOneField(Tax, on_delete=models.CASCADE, related_name="tax_id", null=True)
    ownership = models.OneToOneField(OwnershipRetirement, on_delete=models.CASCADE, related_name="ownership_id", null=True)
    tenure = models.OneToOneField(Tenure, on_delete=models.CASCADE, related_name="tenure_id", null=True)
    added = models.OneToOneField(Added, on_delete=models.CASCADE, related_name="added_id", null=True)
    estate_agent = models.ForeignKey(EstateAgent, on_delete=models.CASCADE, related_name="estate_agent", null=True)
    stations = models.ManyToManyField(Station, through="StationStationDistance")


## One to Many

class Prices(models.Model):
    property_id = models.ForeignKey(PropertyValue, on_delete=models.CASCADE, max_length=20, to_field="property_id")
    price = models.IntegerField(null=True)
    price_date = models.DateField(null=True)
    price_qualifier = models.CharField(max_length = 255, null=True)
    price_type = models.CharField(max_length = 255, null=True)
    
    class Meta:
        unique_together = [["property_id", "price"]]

class KeyFeature(models.Model):
    property_id = models.ForeignKey(PropertyValue, on_delete=models.CASCADE,max_length=20, to_field="property_id")
    key_feature = models.CharField(max_length=255, null=True)
    key_feature_text = models.CharField(max_length=255, null=True)
    
    class Meta:
        unique_together = [["property_id", "key_feature"]]

class Statuses(models.Model):
    property_id = models.ForeignKey(PropertyValue, on_delete=models.CASCADE,max_length=20, to_field="property_id")
    status = models.BooleanField(default = False, null=True)
    status_date = models.DateField(null=True)
    
    class Meta:
        unique_together = [["property_id", "status", "status_date"]]

class Views(models.Model):
    property_id = models.ForeignKey(PropertyValue, on_delete=models.CASCADE,max_length=20, to_field="property_id")
    views = models.IntegerField(null=True)
    unique_views = models.IntegerField(null=True)
    view_date = models.DateField(null=True)
    featured = models.BooleanField(null=True)
    bumped = models.BooleanField(null=True)
    published = models.BooleanField(null=True)
    
    class Meta:
        unique_together = [["property_id", "view_date"]]

class Images(models.Model):
    composite_id = models.CharField(max_length=25, primary_key=True)
    image_file = models.ImageField(upload_to="image/", null=True) # think about using imagefield
    image_file_resized = models.ImageField(upload_to="image/", null=True) # think about using imagefield]

class Floorplans(models.Model):
    composite_id = models.CharField(max_length=25, primary_key=True)
    floorplan_file = models.ImageField(upload_to="floorplan/", null=True) # think about using floorplanfield
    floorplan_file_resized = models.ImageField(upload_to="floorplan/", null=True) # think about using floorplanfield

class Rooms(models.Model):
    property_id = models.ForeignKey(PropertyValue, on_delete=models.CASCADE)
    room = models.IntegerField(null=True) # derived from the idx in the property floorplan list
    room_name = models.CharField(max_length=255, null=True)
    room_description = models.TextField(null=True)
    room_width = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    room_length = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    room_unit = models.CharField(max_length=10, null=True)
    
    class Meta:
        unique_together = [["property_id", "room"]]

# class TestManager(models.Manager):
    
    
#     def append_new_items(self, new_list):
#         for item in new_list:
#             if item not in 
        
# class TestModel(models.Model):
#     id = models.CharField(max_length=100, primary_key=True)
#     list_field = models.JSONField()
    
#     objects = TestManager()
    
#     @classmethod
#     def update(cls, id, new_list):
#         test_model = cls(id=id, list_field=new_list)
#         return test_model




## Link tables


class EstateAgentAccreditation(models.Model):
    estate_agent_id = models.ForeignKey(EstateAgent, on_delete=models.CASCADE, related_name="estate_agent_id")
    accreditation_id = models.ForeignKey(Accreditation, on_delete=models.CASCADE, related_name="accreditation_id")
    have_accreditation = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [["estate_agent_id", "accreditation_id"]]
   
class StationStationDistance(models.Model):
    property_id = models.ForeignKey(PropertyValue, on_delete=models.CASCADE)
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="station_id")
    station_distance = models.DecimalField(max_digits=20, decimal_places=16)
    station_distance_units = models.CharField(max_length=20, null=True)
    
    class Meta:
        unique_together = [["property_id", "station_id"]]
 
class ImageProperty(models.Model):
    property = models.ForeignKey(PropertyValue, on_delete=models.CASCADE)
    image_id = models.IntegerField()
    image_data = models.OneToOneField(Images, on_delete=models.CASCADE, related_name="image_id", null=True) # derived from the idx in the property image list
    image_url = models.URLField()
    image_caption = models.CharField(max_length=100, null=True)
    image_url_resized = models.URLField(null=True)
    image_scraped = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [["property", "image_id"]]
        
class FloorplanProperty(models.Model):
    property = models.ForeignKey(PropertyValue, on_delete=models.CASCADE)
    floorplan_id = models.IntegerField()
    floorplan_data = models.OneToOneField(Floorplans, on_delete=models.CASCADE, related_name="floorplan_id", null=True) # derived from the idx in the property floorplan list
    floorplan_url = models.URLField()
    floorplan_caption = models.CharField(max_length=100, null=True)
    floorplan_url_resized = models.URLField(null=True)
    floorplan_scraped = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [["property", "floorplan_id"]]



# Main table

class Property(models.Model):
    property = models.CharField(max_length=20, primary_key=True)
    url = models.URLField(max_length=200)
    un_published = models.BooleanField(default = False)
    scraped_before = models.BooleanField(default = False)
    stc = models.BooleanField(default = False)
    property_values = models.OneToOneField(PropertyValue, on_delete=models.CASCADE, null=True)