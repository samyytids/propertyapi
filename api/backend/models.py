from django.db import models

class Property(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    property_url = models.URLField(max_length=300)
    scraped_before = models.BooleanField(default=False)
    un_published = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    bad_data = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)
    stc = models.BooleanField(default=False)
    property_data = models.OneToOneField("PropertyData", on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "property"
        ordering = ["property_id"]
class PropertyData(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    property_url = models.URLField(max_length=300)
    listing_type = models.CharField(max_length=3)
    transaction_type = models.CharField(max_length=3)
    virtual_tour = models.BooleanField()
    auction = models.BooleanField()
    retirement = models.BooleanField()
    affordable_scheme = models.BooleanField()
    property_type = models.CharField(max_length=35, null=True)
    property_sub_type = models.CharField(max_length=35)
    added_date = models.DateField()
    letting_type = models.CharField(max_length=30)
    pre_owned = models.CharField(max_length=30)
    furnished = models.CharField(max_length=100)
    current_price = models.IntegerField()
    reduced = models.BooleanField()
    online_viewing = models.BooleanField()
    text = models.OneToOneField("Text", on_delete=models.CASCADE)
    tax = models.OneToOneField("Tax", on_delete=models.CASCADE)
    epc = models.OneToOneField("Epc", on_delete=models.CASCADE, null=True)
    location = models.OneToOneField("Location", on_delete=models.CASCADE)
    layout = models.OneToOneField("Layout", on_delete=models.CASCADE)
    station = models.ManyToManyField(
        "Station", 
        through="StationDistance",
        through_fields=("property_id", "station_id")
    )
    agent = models.ForeignKey("EstateAgent", on_delete=models.CASCADE)
    business_type = models.ForeignKey("BusinessType", on_delete=models.CASCADE, null=True)
    letting_info = models.OneToOneField("LettingInfo", on_delete=models.CASCADE, null=True)
    first_scraped = models.DateField()
    class Meta:
        db_table = "property_data"

class Text(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    description = models.TextField(null=True)
    disclaimer = models.TextField()
    auction_fees_disclaimer = models.TextField(null=True)
    guide_price_disclaimer = models.TextField(null=True)
    reserve_price_disclaimer = models.TextField(null=True)
    static_map_disclaimer_text = models.TextField(null=True)
    new_homes_brochure_disclaimer = models.TextField()
    share_text = models.TextField()
    share_description = models.TextField()
    page_title = models.TextField()
    short_description = models.TextField()
    
    class Meta:
        db_table = "text"
    
class Tax(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    council_tax_exempt = models.BooleanField()
    council_tax_included = models.BooleanField()
    annual_ground_rent = models.IntegerField(null=True)
    ground_rent_review_period_in_years = models.IntegerField(null=True)
    ground_rent_percentage_increase = models.IntegerField(null=True)
    annual_service_charge = models.IntegerField(null=True)
    council_tax_band = models.CharField(max_length=100, null=True)
    domestic_rates = models.IntegerField(null=True)
    class Meta:
        db_table = "tax"

class Ownership(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    shared_ownership = models.BooleanField(null=True)
    ownership_percentage = models.IntegerField(null=True)
    rent_price = models.IntegerField(null=True)
    rent_frequency = models.CharField(max_length=30, null=True)

    class Meta:
        db_table = "ownership"
        
class Epc(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    epc_url = models.URLField(null=True)
    epc_caption = models.CharField(max_length=255, null=True)
    epc_current = models.IntegerField(null=True)
    epc_potential = models.IntegerField(null=True)
    epc_image = models.ImageField(upload_to="epc_image/", null=True)
    ei_url = models.URLField(null=True)
    ei_caption = models.CharField(max_length=255, null=True)
    ei_current = models.IntegerField(null=True)
    ei_potential = models.IntegerField(null=True)
    ei_image = models.ImageField(upload_to="ei_image/", null=True)
    epc_scraped = models.BooleanField(default=False)
    
    class Meta:
        db_table = "epc"
        
class Location(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=100, null=True)
    postcode = models.CharField(max_length=9)
    latitude = models.DecimalField(max_digits=50, decimal_places=10, null=True)
    longitude = models.DecimalField(max_digits=50, decimal_places=10, null=True)
    
    class Meta:
        db_table = "location"
        
class Layout(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField(null=True)
    size = models.IntegerField(null=True)
    
    class Meta:
        db_table = "layout"
        
class Station(models.Model):
    station_name = models.CharField(max_length=255, unique=True)
    station_type = models.CharField(max_length=100)
    
    class Meta:
        db_table = "station"

class StationDistance(models.Model):
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE)
    property_id = models.ForeignKey(PropertyData, on_delete=models.CASCADE)
    station_distance = models.DecimalField(max_digits=20, decimal_places=10)
    station_distance_unit = models.CharField(max_length = 10)
    class Meta:
        db_table = "station_distance"
        unique_together = [["station_id", "property_id"]]

class EstateAgent(models.Model):
    agent_type = models.CharField(max_length=255)
    agent_url = models.URLField(max_length=300)
    agent_url_type = models.CharField(max_length=255)
    agent_name = models.CharField(max_length=255)
    branch_name = models.CharField(max_length=255, null=True)
    agent_description = models.TextField()
    developer = models.BooleanField()
    affiliation = models.ManyToManyField(
        "Affiliation", 
        through="AgentAffiliation",
        through_fields=("agent_id", "affiliation_id")
    )
    
    class Meta:
        db_table = "estate_agent"
        unique_together = [["agent_name", "branch_name"]]
        
class Affiliation(models.Model):
    affiliation_name = models.CharField(max_length=255, unique=True)
    
    class Meta:
        db_table = "affiliation"

class AgentAffiliation(models.Model):
    affiliation_id = models.ForeignKey(Affiliation, on_delete=models.CASCADE)
    agent_id = models.ForeignKey(EstateAgent, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "agent_affiliation"
        unique_together = [["affiliation_id", "agent_id"]]

class Price(models.Model):
    property_id = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="prices")
    price = models.IntegerField()
    price_qualifier = models.CharField(max_length=100, null=True)
    original_price = models.BooleanField()
    price_date = models.DateField()
    
    class Meta:
        db_table = "price"
        unique_together = [["price", "property_id"]]
        
class KeyFeature(models.Model):
    property_id = models.ForeignKey(Property, on_delete=models.CASCADE)
    feature = models.TextField()
    
    class Meta:
        db_table = "key_feature"
        unique_together = [["feature", "property_id"]]
        
class Status(models.Model):
    property_id = models.ForeignKey(Property, on_delete=models.CASCADE)
    stc = models.BooleanField()
    status_date = models.DateField()
    
    class Meta:
        db_table = "status"
        unique_together = [["stc", "property_id"]]
        
class Image(models.Model):
    property_id = models.ForeignKey(Property, on_delete=models.CASCADE)
    image_url = models.URLField(max_length=300)
    image_caption = models.CharField(max_length=255, null=True)
    image_file = models.ImageField(upload_to="image/", null=True)
    image_scraped = models.BooleanField(default=False)
    
    class Meta:
        db_table = "image"
        unique_together = [["property_id", "image_url"]]
        
class Floorplan(models.Model):
    property_id = models.ForeignKey(Property, on_delete=models.CASCADE)
    floorplan_url = models.URLField(max_length=300)
    floorplan_caption = models.CharField(max_length=255, null=True)
    floorplan_file = models.ImageField(upload_to="floorplan/", null=True)
    
    class Meta:
        db_table = "floorplan"
        unique_together = [["property_id", "floorplan_url"]]
        
class Room(models.Model):
    property_id = models.ForeignKey(Property, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255, null=True)
    room_description = models.TextField(null=True)
    room_width = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    room_length = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    room_unit = models.CharField(max_length=4, null=True)
    room_dimension = models.CharField(max_length=100, null=True)
    
    class Meta:
        db_table = "room"
        unique_together = [["property_id", "room_name", "room_description"]]

class PremiumListing(models.Model):
    property_id = models.ForeignKey(Property, on_delete=models.CASCADE)
    featured_property = models.BooleanField()
    premium_listing = models.BooleanField()
    listing_date = models.DateField()
    
    class Meta:
        db_table = "premium_listing"
        unique_together = [["property_id", "listing_date"]]

class BusinessType(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    use_class = models.CharField(max_length=255, null=True)
    sector = models.CharField(max_length=255, null=True)
    
    class Meta:
        db_table = "business type"
        
class LettingInfo(models.Model):
    property_id = models.CharField(max_length=15, unique=True)
    let_available_date = models.DateField(null=True)
    deposit = models.IntegerField(null=True)
    minimum_tenancy_length = models.IntegerField(null=True)
    let_type = models.CharField(max_length=30, null=True)
    furnishing_type = models.CharField(max_length=100, null=True)
    
    class Meta:
        db_table = "letting info"