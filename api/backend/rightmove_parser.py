from datetime import datetime, timedelta
from backend.models import *
import re
# from api.backend.models import PropertyValue

class RightmoveParser:
    def parse_update(self, initial_data: dict, id: str) -> dict:
        if initial_data.get("propertyData", {}).get("id"):
            property_data = initial_data.get("propertyData", {}) or {}
            analytics_info = initial_data.get("analyticsInfo", {}) or {}
            property_data = self.get_property_update_sections(property_data)
            analytics_info = self.get_analytics_property_update_sections(analytics_info.get("analyticsProperty"))
            property_table = self.property_table_data(property_data["published_archived"], analytics_info, id)
            property_data_table = self.property_data_table_update(property_data, analytics_info, id)
            price_table = self.price_table_update(property_data.get("prices"), property_data.get("listing_history"), property_data_table, id)
            status_table = self.status_table_update(property_table, property_data_table, id)
            premium_listing_table = self.premium_listing_table_data(property_data.get("misc_info"), id)

            result = {
                "property_table" : property_table,
                "property_data_table" : property_data_table,
                "price_table" : price_table,
                "status_table" : status_table,
                "premium_listing_table" : premium_listing_table,
            }
            
            return result
            
    def parse(self, initial_data: dict, id: str) -> dict:
        if initial_data.get("propertyData", {}).get("id"):
            property_data = initial_data.get("propertyData", {}) or {}
            analytics_info = initial_data.get("analyticsInfo", {}) or {}
            property_data = self.get_property_data_sections(property_data)
            analytics_info = self.get_analytics_info_sections(analytics_info)
            
            property_table = self.property_table_data(property_data["published_archived"], analytics_info, id)
            property_data_table = self.property_data_table_data(property_data, analytics_info, id)
            text_elements_table  = self.text_elements_table_data(property_data.get("text"), id)
            tax_table = self.tax_table_data(property_data.get("tax"), id)
            ownership_table = self.ownership_table_data(property_data.get("shared_ownership"), id)
            if property_data.get("epc_graphs"):
                epc_table = self.epc_table_data(property_data.get("epc_graphs"), id)
            else:
                epc_table = []
            location_table = self.location_table_data(property_data.get("location"), property_data.get("address"), id)
            layout_table = self.layout_table_data(property_data.get("bedrooms"), property_data.get("bathrooms"), property_data.get("size"), property_data_table.get("property_sub_type"), property_data_table.get("listing_type"), id)
            station_table = self.station_table_data(property_data.get("nearest_stations"))
            station_distance_table = self.station_distance_table_data(property_data.get("nearest_stations"), id)
            estate_agent_table = self.estate_agent_table_data(property_data.get("estate_agent"), analytics_info.get("analytics_branch"))
            if property_data.get("industry_affiliation"):
                affiliation_table = self.affiliation_table_data(property_data.get("industry_affiliation"))
                agent_affiliation_table = self.agent_affiliation_table_data(estate_agent_table, affiliation_table)
            else:
                affiliation_table = None
                agent_affiliation_table = None
                
            price_table = self.price_table_data(property_data.get("prices"), property_data.get("listing_history"), property_data_table, id)
            if property_data.get("key_features"):
                key_feature_table = self.key_feature_table_data(property_data.get("key_features"), id)
            else:
                key_feature_table = []
            status_table = self.status_table_data(property_data_table, id)
            image_table = self.image_table_data(property_data.get("images"), id)
            floorplan_table = self.floorplan_table_data(property_data.get("floorplans"), id)
            room_table = self.room_table_data(property_data.get("rooms"), id)
            premium_listing_table = self.premium_listing_table_data(property_data.get("misc_info"), id)
            business_type_table = self.business_type_table_data(property_data.get("info_reel"), id)
            if property_data.get("lettings"):
                lettings_table = self.lettings_table_data(property_data.get("lettings"), id)
            else:
                lettings_table = []
            
            result = {
                "property_table" : property_table,
                "property_data_table" : {
                        "property":property_data_table,
                        "agent":estate_agent_table,
                    },
                "text_elements_table" : text_elements_table,
                "tax_table" : tax_table,
                "ownership_table" : ownership_table,
                "epc_table" : epc_table,
                "location_table" : location_table,
                "layout_table" : layout_table,
                "station_table" : station_table,
                "station_distance_table" : station_distance_table,
                "estate_agent_table" : estate_agent_table,
                "affiliation_table" : affiliation_table,
                "agent_affiliation_table" : agent_affiliation_table,
                "price_table" : price_table,
                "key_feature_table" : key_feature_table,
                "status_table" : status_table,
                "image_table" : image_table,
                "floorplan_table" : floorplan_table,
                "room_table" : room_table,
                "premium_listing_table" : premium_listing_table,
                "business_type_table" : business_type_table,
                "lettings_table" : lettings_table,
            }
            return result
    
    @staticmethod
    def get_property_update_sections(property_data: dict) -> dict[dict]:
        result = {
            "published_archived" : property_data.get("status"), # done
            "prices" : property_data.get("prices"), # done
            "misc_info" : property_data.get("misInfo"), # done
            "listing_history" : property_data.get("listingHistory"), # done
            "listing_type" : property_data.get("channel"), # done
        }
        
        return result
    
    @staticmethod
    def get_analytics_property_update_sections(analytics_property: dict) -> dict[dict]:
        result = {
            "let_agreed" : analytics_property.get("letAgreed"), # done
            "stc" : analytics_property.get("soldSTC"), # done
        }
        return result
    
    @staticmethod
    def get_property_data_sections(property_data: dict) -> dict[dict]:
        result = {
            "published_archived" : property_data.get("status"), # done
            "text" : property_data.get("text"), # done
            "prices" : property_data.get("prices"), # done
            "address" : property_data.get("address"), # done
            "key_features" : property_data.get("keyFeatures"), # done
            "images" : property_data.get("images"), # done
            "floorplans" : property_data.get("floorplans"), # done
            "virtual_tour" : property_data.get("virtualTours"), # done
            "estate_agent" : property_data.get("customer"), # done
            "industry_affiliation" : property_data.get("industryAffiliations"), # sort of like accreditations
            "rooms" : property_data.get("rooms"), # done
            "location" : property_data.get("location"), # done
            "nearest_stations" : property_data.get("nearestStations"), # done
            "listing_type" : property_data.get("channel"), # done
            "size" : property_data.get("sizings"), # done
            "epc_graphs" : property_data.get("epcGraphs"), # done
            "bedrooms" : property_data.get("bedrooms"), # done
            "bathrooms" : property_data.get("bathrooms"), # done
            "misc_info" : property_data.get("misInfo"), # done
            "additional_info" : property_data.get("dfpAdInfo"), # done
            "listing_history" : property_data.get("listingHistory"), # done
            "tenure" : property_data.get("tenure"), # done
            "property_sub_type" : property_data.get("propertySubType"), # done
            "affordable_buying_scheme" : property_data.get("affordableBuyingScheme"), # done
            "shared_ownership" : property_data.get("sharedOwnership"), # done
            "tax" : property_data.get("livingCosts"), # done
            "info_reel" : property_data.get("infoReelItems"), # done
            "lettings" : property_data.get("lettings"), # done
        }
        
        return result

    @staticmethod
    def property_table_data(published_archived: dict, analytics_property: dict, id: str) -> dict:
        published, archived = published_archived.values()
        un_published = not published
        stc = analytics_property.get("stc") | analytics_property.get("let_agreed")
        property = Property.objects.get(property_id=id)
        property.un_published = un_published
        property.stc = stc
        property.archived = archived
        property.scraped_before = True
        
        result = property
        
        return result
    
    @staticmethod
    def property_data_table_update(property_data: dict, analytics_property: dict, id: str) -> dict:
        transaction_type = None
        if property_data.get("listing_type"):
            _, transaction_type = property_data.get("listing_type").split("_")
        
        current_price = property_data.get("prices", {}).get("primaryPrice", "").replace("£", "").replace(",", "")
        
        if transaction_type == "LET":
            current_price = current_price.split(" ")[0]
        
        if not bool(re.search(r"\d", current_price)):
            current_price = -1
                
        reduced = True if "Reduced" in property_data.get("listing_history", {}).get("listingUpdateReason", "") else False
        
        property_data: PropertyData = PropertyData.objects.get(property_id = id)
        property_data.reduced = reduced
        property_data.current_price = current_price
        
        result = property_data
        
        return result
    
    @staticmethod
    def property_data_table_data(property_data: dict, analytics_property: dict, id: str) -> dict:
        listing_type = transaction_type = None
        virtual_tour = auction = False
        if property_data.get("listing_type"):
            listing_type, transaction_type = property_data.get("listing_type").split("_")
    
        if property_data.get("virtual_tour"):
            virtual_tour = True
        if property_data.get("additional_info"):
            additional_information = property_data.get("additional_info").get("targeting")
            for item in additional_information:
                if not item["key"] == "AUCP":
                    continue
                
                if item["value"][0] == "TRUE":
                    auction = True
                    break
                
        retirement = analytics_property.get("retirement", False)
        affordable = property_data.get("affordable", False)
        property_type = analytics_property.get("property_type")
        property_sub_type = property_data.get("property_sub_type")
        added = analytics_property.get("added")
        added = datetime.strptime(added, "%Y%m%d").date()
        letting_type = analytics_property.get("letting_type")
        pre_owned = analytics_property.get("pre_owned")
        furnished = analytics_property.get("furnished")
        current_price = property_data.get("prices", {}).get("primaryPrice", "").replace("£", "").replace(",", "")
        
        if transaction_type == "LET":
            current_price = current_price.split(" ")[0]
        
        if not bool(re.search(r"\d", current_price)):
            current_price = -1
             
        reduced = True if "Reduced" in property_data.get("listing_history", {}).get("listingUpdateReason", "") else False
        online_viewing = analytics_property.get("online_viewing", False)
        
        result = {
            "property_id":id,
            "property_url" : f"https://www.rightmove.co.uk/properties/{id}",
            "listing_type": listing_type,
            "transaction_type": transaction_type,
            "virtual_tour" : virtual_tour,
            "auction" : auction,
            "retirement" : retirement,
            "affordable_scheme" : affordable, 
            "property_type" : property_type,
            "property_sub_type" : property_sub_type,
            "added_date" : added,
            "letting_type" : letting_type,
            "pre_owned" : pre_owned,
            "furnished" : furnished,
            "current_price" : current_price,
            "reduced" : reduced,
            "online_viewing" : online_viewing,
            "first_scraped" : datetime.now().date(),
        }
        
        return result
    
    def text_elements_table_data(self, text_data: dict, id: str) -> dict:
        description = text_data.get("description")
        disclaimer = text_data.get("disclaimer")
        auction_fees_disclaimer = text_data.get("auctionFeesDisclaimer")
        guide_price_disclaimer = text_data.get("guidePriceDisclaimer")
        reserve_price_disclaimer = text_data.get("reservePriceDisclaimer")
        static_map_disclaimer_text = text_data.get("staticMapDisclaimerText")
        new_homes_brochure_disclaimer = text_data.get("newHomesBrochureDisclaimer")
        share_text = text_data.get("shareText")
        share_description = text_data.get("shareDescription")
        page_title = text_data.get("pageTitle")
        short_description = text_data.get("shortDescription")

        description = self.strip_tags(description) if description else None
        disclaimer = self.strip_tags(disclaimer) if disclaimer else None
        auction_fees_disclaimer = self.strip_tags(auction_fees_disclaimer) if auction_fees_disclaimer else None
        guide_price_disclaimer = self.strip_tags(guide_price_disclaimer) if guide_price_disclaimer else None
        reserve_price_disclaimer = self.strip_tags(reserve_price_disclaimer) if reserve_price_disclaimer else None
        static_map_disclaimer_text = self.strip_tags(static_map_disclaimer_text) if static_map_disclaimer_text else None
        new_homes_brochure_disclaimer = self.strip_tags(new_homes_brochure_disclaimer) if new_homes_brochure_disclaimer else None
        share_text = self.strip_tags(share_text) if share_text else None
        share_description = self.strip_tags(share_description) if share_description else None
        page_title = self.strip_tags(page_title) if page_title else None
        short_description = self.strip_tags(short_description) if short_description else None
        
        result = {
            "property_id" : id,
            "description" : description,
            "disclaimer" : disclaimer,
            "auction_fees_disclaimer" : auction_fees_disclaimer,
            "guide_price_disclaimer" : guide_price_disclaimer,
            "reserve_price_disclaimer" : reserve_price_disclaimer,
            "static_map_disclaimer_text" : static_map_disclaimer_text,
            "new_homes_brochure_disclaimer" : new_homes_brochure_disclaimer,
            "share_text" : share_text,
            "share_description" : share_description,
            "page_title" : page_title,
            "short_description" : short_description,
        }

        result = Text(**result)
        
        return result
    
    @staticmethod
    def tax_table_data(tax_data: dict, id: str) -> dict:
        council_tax_exempt = tax_data.get("councilTaxExempt")
        council_tax_included = tax_data.get("councilTaxIncluded")
        annual_ground_rent = tax_data.get("annualGroundRent")
        ground_rent_review_period_in_years = tax_data.get("groundRentReviewPeriodInYears")
        ground_rent_percentage_increase = tax_data.get("groundRentPercentageIncrease")
        annual_service_charge = tax_data.get("annualServiceCharge")
        council_tax_band = tax_data.get("councilTaxBand")
        domestic_rates = tax_data.get("domesticRates")
        
        result = {
            "property_id" : id,
            "council_tax_exempt" : council_tax_exempt,
            "council_tax_included" : council_tax_included,
            "annual_ground_rent" : annual_ground_rent,
            "ground_rent_review_period_in_years" : ground_rent_review_period_in_years,
            "ground_rent_percentage_increase" : ground_rent_percentage_increase,
            "annual_service_charge" : annual_service_charge,
            "council_tax_band" : council_tax_band,
            "domestic_rates" : domestic_rates,
        }
        
        result = Tax(**result)
        
        return result
    
    @staticmethod
    def ownership_table_data(ownership_data: dict, id: str) -> dict:
        shared_ownership = ownership_data.get("sharedOwnership")
        ownership_percentage = ownership_data.get("ownershipPercentage")
        rent_price = ownership_data.get("rentPrice")
        rent_frequency = ownership_data.get("rentFrequency")
        
        result = {
            "property_id": id,
            "shared_ownership" : shared_ownership,
            "ownership_percentage" : ownership_percentage,
            "rent_price" : rent_price,
            "rent_frequency" : rent_frequency,
        }
        
        result = Ownership(**result)
        
        return result
    
    @staticmethod
    def epc_table_data(epc_data: list, id: str) -> dict:
        if len(epc_data) == 1:
            epc_url = epc_data[0].get("url")
            epc_caption = "EPC"
            result = {
                "property_id": id,
                "epc_url" : epc_url,
                "epc_caption" : epc_caption,
            }
        elif len(epc_data) > 1:
        # else:
            epc_url = epc_data[0].get("url")
            epc_caption = "EPC"
            ei_url = epc_data[1].get("url")
            ei_caption = "EI"
            result = {
                "property_id": id,
                "epc_url" : epc_url,
                "epc_caption" : epc_caption,
                "ei_url" : ei_url,
                "ei_caption" : ei_caption,
            }
        else:
            result = {
                "property_id": id,
                "epc_url" : None,
                "epc_caption" : None,
                "ei_url" : None,
                "ei_caption" : None,
            }
        
        result = Epc(**result)  
        
        return result
            
    @staticmethod
    def location_table_data(location_data: dict, address_data: dict, id: str) -> dict:
        address = address_data.get("displayAddress")
        country = address_data.get("ukCountry")
        out_code = address_data.get("outcode")
        in_code = address_data.get("incode")
        postcode = f"{out_code} {in_code}"
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")
        
        result = {
            "property_id": id,
            "address" : address, 
            "country" : country, 
            "postcode" : postcode, 
            "latitude" : latitude, 
            "longitude" : longitude, 
        }
        
        result = Location(**result)
        
        return result
    
    @staticmethod
    def layout_table_data(bedrooms: int | None, bathrooms: int | None, size: str | None, property_sub_type: str, property_listing_type: str,id: str) -> dict:
        result_size = None
        
        if size:
            for option in size:
                if option.get("unit") == "sqm":
                    result_size = option.get("minimumSize")

        if property_sub_type == "Studio" or property_sub_type == "Mews":
            bedrooms = 0
        elif property_listing_type == "COM":
            bedrooms = 0
        
        result = {
            "property_id" : id,
            "bedrooms" : bedrooms,
            "bathrooms" : bathrooms,
            "size" : result_size
        }

        result = Layout(**result)
        
        return result
                
    @staticmethod
    def station_table_data(station_data: dict) -> dict:
        result = []
        for station in station_data:
            station_name = station.get("name")
            station_type = station.get("types")[0]
            result_data = {
                "station_name" : station_name,
                "station_type" : station_type,
            }
            result_data = Station(**result_data)
            result.append(result_data)
        
        return result
    
    @staticmethod
    def station_distance_table_data(station_data: dict, id: str) -> dict:
        result = []
        for station in station_data:
            station_name = station.get("name")
            station_distance = station.get("distance")
            station_distance_unit = station.get("unit")
            result_data = {
                "property_id" : id,
                "station_id" : station_name,
                "station_distance" : station_distance,
                "station_distance_unit" : station_distance_unit,
            }
            result.append(result_data)
        
        return result
    
    def estate_agent_table_data(self, customer_data: dict, analytics_branch: dict) -> dict:
        agent_type = analytics_branch.get("agentType")
        agent_url = f'https://www.rightmove.co.uk{customer_data.get("customerProfileUrl")}'
        agent_url_type = analytics_branch.get("pageType")
        agent_name = customer_data.get("companyName")
        branch_name = customer_data.get("branchName")
        agent_description = customer_data.get("customerDescription").get("truncatedDescriptionHTML")
        if agent_description:
            agent_description = self.strip_tags(agent_description)
        developer = customer_data.get("isNewHomeDeveloper")
        
        result = {
            "agent_type" : agent_type,
            "agent_url" : agent_url,
            "agent_url_type" : agent_url_type,
            "agent_name" : agent_name,
            "branch_name" : branch_name,
            "agent_description" : agent_description,
            "developer" : developer,
        }
        
        result = EstateAgent(**result)
        
        return result
    
    @staticmethod
    def affiliation_table_data(affiliations_data: list[dict]) -> dict:
        result = []
        for affiliation in affiliations_data:
            result_data = {
                "affiliation_name" : affiliation.get("name")
            }
            
            result_data = Affiliation(**result_data)
            
            result.append(result_data)
        
        return result
        
    @staticmethod
    def agent_affiliation_table_data(estate_agent_table: dict, affiliation_table: list[dict]) -> list[dict]:
        result = []
        for affiliation in affiliation_table:
            result_data = {
                "affiliation_id" : affiliation,
                "agent_id" : estate_agent_table,
            }
            result.append(result_data)
        
        return result
    
    @staticmethod
    def price_table_data(price_data: dict, listing_history: dict, property_data_table: dict, id: str) -> dict:
        price = price_data.get("primaryPrice")
        if "pcm" in price:
            price = price.split(" ")[0]
        
        price = price.replace("£", "").replace(",", "")
        
        if not bool(re.search(r"\d", price)):
            price = -1
            
        price_qualifier: str = price_data.get("displayPriceQualifier")
        price_qualifier = price_qualifier.lower()
        
        if "offers over" == price_qualifier:
            price_qualifier = "from"
        elif "offers in excess of" == price_qualifier:
            price_qualifier = "from"
        elif "offers in region of" == price_qualifier:
            price_qualifier = "guide price"
        
        if price_qualifier == "":
            price_qualifier = None
        history = listing_history.get("listingUpdateReason")
        original_price = False if "Reduced" in history else True
        if not original_price:
            if "yesterday" in history:
                price_date = (datetime.now() - timedelta(1)).date()
            elif "today" in history:
                price_date = datetime.now().date()
            else:
                price_date = datetime.strptime("".join(history.split(" ")[-1].split("/")[::-1]), "%Y%m%d").date()
        else:
            price_date = property_data_table.get("added_date")
        
        result = {
            "property_id": id,
            "price" : price,
            "price_qualifier" : price_qualifier,
            "original_price" : original_price,
            "price_date" : price_date,
        }
        
        return result
    
    @staticmethod
    def price_table_update(price_data: dict, listing_history: dict, property_data_table: dict, id: str) -> dict:
        price: str = price_data.get("primaryPrice")
        if "pcm" in price:
            price = price.split(" ")[0]
            
        price = price.replace("£", "").replace(",", "")
        
        if not bool(re.search(r"\d", price)):
            price = -1
            
        price_qualifier: str = price_data.get("displayPriceQualifier")
        price_qualifier = price_qualifier.lower()
        
        if "offers over" == price_qualifier:
            price_qualifier = "from"
        elif "offers in excess of" == price_qualifier:
            price_qualifier = "from"
        elif "offers in region of" == price_qualifier:
            price_qualifier = "guide price"
        
        if price_qualifier == "":
            price_qualifier = None
        history = listing_history.get("listingUpdateReason")
        original_price = False if "Reduced" in history else True
        if not original_price:
            if "yesterday" in history:
                price_date = (datetime.now() - timedelta(1)).date()
            elif "today" in history:
                price_date = datetime.now().date()
            else:
                price_date = datetime.strptime("".join(history.split(" ")[-1].split("/")[::-1]), "%Y%m%d").date()
        else:
            price_date = property_data_table.added_date
        
        result = {
            "property_id": id,
            "price" : price,
            "price_qualifier" : price_qualifier,
            "original_price" : original_price,
            "price_date" : price_date,
        }
        
        return result
         
    @staticmethod
    def key_feature_table_data(key_feature_data: list[str], id: str) -> list[dict]:
        result = []

        for feature in key_feature_data:
            result_data = {
                "property_id" : id,
                "feature" : feature.lower(),
                "word_count" : len(feature.split(" ")),
            }
            result.append(result_data)
        return result
    
    @staticmethod
    def status_table_data(property_table: dict, id: str) -> dict:
        if property_table.get("stc"):
            status_date = datetime.now().date()
            result = {
                "property_id" : id,
                "stc" : True,
                "status_date" : status_date
            }
        else:
            result = {
                "property_id" : id,
                "stc" : False,
                "status_date" : property_table.get("added_date")
            }
            
        return result
    
    @staticmethod
    def status_table_update(property_table: Property, property_data_table: PropertyData, id: str) -> dict:
        if property_table.stc:
            status_date = datetime.now().date()
            result = {
                "property_id" : id,
                "stc" : True,
                "status_date" : status_date
            }
        else:
            result = {
                "property_id" : id,
                "stc" : False,
                "status_date" : property_data_table.added_date
            }
            
        return result
        
    @staticmethod
    def image_table_data(image_data: list[dict], id: str) -> list[dict]:
        result = []
        for image in image_data:
            result_data = {
                "property_id" : id,
                "image_url" : image.get("url"),
                "image_caption" : image.get("caption")
            }
            result.append(result_data)
        
        return result
    
    @staticmethod
    def floorplan_table_data(floorplan_data: list[dict], id: str) -> list[dict]:
        result = []
        for floorplan in floorplan_data:
            result_data = {
                "property_id" : id,
                "floorplan_url" : floorplan.get("url"),
                "floorplan_caption" : floorplan.get("caption")
            }
            result.append(result_data)
        
        return result
            
    @staticmethod
    def room_table_data(room_data: list[dict], id: str) -> list[dict]:
        result = []
        for room in room_data:
            result_data = {
                "property_id" : id,
                'room_name' :room.get("name"),
                'room_description' : room.get("description"),
                'room_width' : room.get("width"),
                'room_length' : room.get("length"),
                'room_unit' : room.get("unit"),
                'room_dimension' : room.get("dimension"),
            }
            result.append(result_data)
        
        return result
       
    @staticmethod
    def premium_listing_table_data(misc_info: dict, id: str) -> dict:
        featured_property = misc_info.get("featuredProperty")
        premium_listing = misc_info.get("premiumDisplay")
        listing_date = datetime.now().date()
        
        result = {
            "property_id" : id,
            "featured_property" : featured_property,
            "premium_listing" : premium_listing,
            "listing_date" : listing_date,
        }
        
        return result
     
    @staticmethod
    def business_type_table_data(business_type: list[dict], id: str) -> list[dict]:
        result = {
            "property_id" : id,
        }
        for info in business_type:
            item = info.get("title").lower().replace(" ", "_")
            if item == "use_class":
                result["use_class"] = info.get("item_text")
                
            elif item == "sector":
                result["sector"] = info.get("item_text")
        
        result = BusinessType(**result)
        
        return result
    
    @staticmethod
    def lettings_table_data(lettings:dict, id: str) -> dict:
        let_available_date = lettings.get("letAvailableDate")
        if let_available_date:
            if let_available_date == "Now":
                let_available_date = datetime.today().date()
            else:
                let_available_date = datetime.strptime("".join(lettings.get("letAvailableDate").split("/")[::-1]), "%Y%m%d").date()
        result = {
            "property_id" : id,
            "let_available_date" : let_available_date,
            "deposit" : lettings.get("deposit"),
            "minimum_tenancy_length" : lettings.get("minimumTermInMonths"),
            "let_type" : lettings.get("letType"),
            "furnishing_type" : lettings.get("furnishType"),
        }
        
        result = LettingInfo(**result)
        
        return result
    
    def get_analytics_info_sections(self, analytics_info: dict) -> dict[dict]:
        analytics_property = analytics_info.get("analyticsProperty", {})
        result = {
            "analytics_branch" : analytics_info.get("analyticsBranch"),
            **self.get_analytics_property_sections(analytics_property),
        }
        
        return result
        
    @staticmethod
    def get_analytics_property_sections(analytics_property: dict) -> dict[dict]:
        result = {
            "added" : analytics_property.get("added"), # done
            "furnished" : analytics_property.get("furnishedType"), # done
            "online_viewing" : analytics_property.get("hasOnlineViewing"),# done
            "let_agreed" : analytics_property.get("letAgreed"), # done
            "letting_type" : analytics_property.get("lettingType"), # done
            "pre_owned" : analytics_property.get("preOwned"), # done
            "property_type" : analytics_property.get("propertyType"), # done
            "retirement" : analytics_property.get("retirement"), # done
            "stc" : analytics_property.get("soldSTC"), # done
        }
        
        return result
    
    @staticmethod
    def strip_tags(text: str) -> str:
        filtered_text = re.sub("<.*?>", " ", text)
        return filtered_text  
        