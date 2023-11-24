from datetime import datetime, timedelta
import json

class DataParser:
    def parse(self, initial_data: dict, id: str) -> dict:
        if id[0] == "R":
            property_data = initial_data.get("propertyData") or {}
            analytics_info = initial_data.get("analyticsInfo") or {}
            
            analytics_property = analytics_info.get("analyticsProperty", {}) or {}
            text_elements = property_data.get("text", {}) or {}
            location = {
                "address" : property_data.get("address", {}) or {},
                "location" : property_data.get("location", {}) or {}
            }
            broadband = {}
            epc = property_data.get("epcGraphs", []) or []
            listing_type = {
                "property_data" : property_data,
                "analytics_property" : analytics_property
            }
            layout = {
                "bedrooms" : property_data.get("bedrooms"),
                "bathrooms" : property_data.get("bathrooms"),
                "property_type": analytics_property
            }
            tax = property_data.get("livingCosts", {}) or {}
            ownership = property_data.get("sharedOwnership", {}) or {}
            retirement = analytics_property
            tenure = property_data.get("tenure", {}) or {}
            estate_agent = property_data.get("customer", {}) or {}
            accreditations_list = []
            
            views = [{}]
            key_features = property_data.get("keyFeatures", []) or []
            images = {
                "images" : property_data.get("images", []) or [],
                "floorplans" : property_data.get("floorplans", []) or []
                }
            rooms = property_data.get("rooms", []) or []
            stations = property_data.get("nearestStations", []) or []
            prices = {
                "listing_history" : property_data.get("listingHistory", {}) or {},
                "analytics_property" : analytics_property
            }
            statuses = analytics_property
                
            property_updates = {
                "property_id": id,
                "un_published": not property_data.get("status", {}).get("published"),
                "scraped_before": True
            }
            
        else:
            property_data = initial_data["props"]["pageProps"]["property"] or {}
            text_elements = property_data.get("description", "") or ""
            location = property_data
            broadband = property_data.get("ofcomBroadband", {}) or {}
            epc = {
                "epc": property_data.get("epc", {}) or {},
                "key_features": property_data.get("keyInfo", []) or []
            }
            listing_type = property_data.get("saleType", {}) or {}
            layout = property_data
            tax = {}
            ownership = property_data
            retirement = {}
            tenure = property_data.get("keyInfo", []) or []
            estate_agent = property_data.get("agents", []) or [{}]
            accreditations = estate_agent[0] or {}
            accreditations = accreditations.get("accreditations", []) or []
            missing_accreditations = estate_agent[0] or {}
            missing_accreditations = missing_accreditations.get("missingAccredidataions", []) or []
            accreditations_list = {
                "have": accreditations,
                "dont_have": missing_accreditations,
                "estate_agent": estate_agent[0] or {}
            }
            
            views = property_data.get("stats", {}) or {}
            key_features = property_data.get("keyInfo", []) or []
            images = property_data.get("images", []) or []
            rooms = []
            stations = []
            prices = property_data.get("history", []) or []
            statuses = property_data.get("history", []) or []
            property_updates = {
                "property_id": id,
                "un_published": not property_data.get("published"),
                "scraped_before": True
            }
        data = {}
        data["single"] = {}
        data["single"]["property_id"] = {"property_id":id}
        data["single"]["text_elements"] = self.extract_text(text_elements, id)
        data["single"]["location"] = self.extract_location(location, id)
        data["single"]["broadband"]  = self.extract_broadband(broadband, id)
        data["single"]["epc"] = self.extract_epc(epc, id)
        data["single"]["listing_type"] = self.extract_listing_type(listing_type, id)
        data["single"]["layout"] = self.extract_layout(layout, id)
        data["single"]["tax"] = self.extract_tax(tax, id)
        data["single"]["ownership_retirement"] = {
                "ownership_type": self.extract_ownership(ownership, id),
                "retirement_home": self.extract_retirement(retirement, id)
            } 
        data["single"]["tenure"] = self.extract_tenure(tenure, id)
        data["single"]["estate_agent"] = self.extract_estate_agent(estate_agent, id)
        data["views"] = self.extract_views(views, id)
        data["key_features"]  = self.extract_key_features(key_features, id)
        data["images"], data["floorplans"] = self.extract_images(images, id)
        data["rooms"] = self.extract_rooms(rooms, id)
        data["stations"] = self.extract_stations(stations, id)
        data["station_distances"] = self.extract_station_distances(stations, id)
        data["prices"] = self.extract_prices(prices, id)
        data["statuses"] = self.extract_statuses(statuses, id)
        data["accreditations"], data["have_accreditations"] = self.extract_accreditations(accreditations_list, id)
        data["property"] = property_updates
        data["property"]["stc"] = False
        for status in data["statuses"]:
            if status["status"]: 
                data["property"]["stc"] = True
                break
        data["property"]["scraped_before"] = True
        
        return data
       
    def parse_update(self, initial_data: dict, id: str) -> dict:
        if id[0] == "R":
            property_data = initial_data["propertyData"] or {}
            analytics_info = initial_data["analyticsInfo"] or {}
            analytics_property = analytics_info.get("analyticsProperty", {}) or {}
            prices = {
                "listing_history" : property_data.get("listingHistory", {}) or {},
                "analytics_property" : analytics_property
            }
            statuses = analytics_property
            property_updates = {
                "property_id": id,
                "un_published": not property_data.get("status", {}).get("published"),
                "scraped_before": True
            }
            
        else:
            property_data = initial_data["props"]["pageProps"]["property"] or {}
            prices = property_data.get("history", []) or []
            statuses = property_data.get("history", []) or []
            property_updates = {
                "property_id": id,
                "un_published": not property_data.get("published"),
                "scraped_before": True
            }
            
        data = {}
        data["prices"] = self.extract_prices(prices, id)
        data["statuses"] = self.extract_statuses(statuses, id)
        data["property"] = property_updates
        data["property"]["stc"] = False
        for status in data["statuses"]:
            if status["status"]: 
                data["property"]["stc"] = True
                break
        data["property"]["scraped_before"] = True
        
        return data
     
    @staticmethod
    def extract_text(data: dict | str, id: str) -> dict:
        description = None
        share_description = None
        share_text = None
        if id[0] == "R":
            description = data.get("description")
            share_description = data.get("shareDescription")
            share_text = data.get("shareText")
        else:
            description = data
            
        return {
            "description" : description,
            "share_description" : share_description,
            "share_text" : share_text
        }
        
    @staticmethod
    def extract_location(data: dict, id: str) -> dict:
        country = None
        town = None
        postcode = None
        street = None
        display_address = None
        lat = None
        long = None
        
        if id[0] == "R":
            country = data.get("address", {}).get("ukCountry")
            display_address = data.get("address", {}).get("displayAddress")
            postcode = f"{data.get('address', {}).get('outcode')} {data.get('address', {}).get('incode')}"
            lat = data.get("location", {}).get("latitude")
            long = data.get("location", {}).get("longitude")
        else:
            country = data.get("country", {}).get("name")
            town = data.get("town")
            postcode = data.get("postcode")
            street = data.get("street")
            display_address = data.get("displayAddress")
            lat = data.get("coordinate", {}).get("latitude")
            long = data.get("coordinate", {}).get("longitude")
        
        return {
            "country" : country,
            "town" : town,
            "postcode" : postcode,
            "street" : street,
            "display_address" : display_address,
            "lat" : lat,
            "long" : long,
        }
            
    @staticmethod
    def extract_broadband(data: dict, id: str) -> dict:
        standard_upload = None
        standard_download = None
        super_fast_upload = None
        super_fast_download = None
        ultra_fast_upload = None
        ultra_fast_download = None
        
        if id[0] == "R":
            pass
        else:
            standard_upload: str = data.get("maxBbPredictedUp") or ""
            standard_upload = standard_upload.replace(",", "")
            if standard_upload == "":
                standard_upload = None

            standard_download: str = data.get("maxBbPredictedDown") or ""
            standard_download = standard_download.replace(",", "")
            if standard_download == "":
                standard_download = None

            super_fast_upload: str = data.get("maxSfbbPredictedUp") or ""
            super_fast_upload = super_fast_upload.replace(",", "")
            if super_fast_upload == "":
                super_fast_upload = None

            super_fast_download: str = data.get("maxSfbbPredictedDown") or ""
            super_fast_download = super_fast_download.replace(",", "")
            if super_fast_download == "":
                super_fast_download = None

            ultra_fast_upload: str = data.get("maxUfbbPredictedUp") or ""
            ultra_fast_upload = ultra_fast_upload.replace(",", "")
            if ultra_fast_upload == "":
                ultra_fast_upload = None

            ultra_fast_download: str = data.get("maxUfbbPredictedDown") or ""
            ultra_fast_download = ultra_fast_download.replace(",", "")
            if ultra_fast_download == "":
                ultra_fast_download = None

        
        return {
            "standard_upload" : standard_upload,
            "standard_download" : standard_download,
            "super_fast_upload" : super_fast_upload,
            "super_fast_download" : super_fast_download,
            "ultra_fast_upload" : ultra_fast_upload,
            "ultra_fast_download" : ultra_fast_download,
        }
        
    @staticmethod
    def extract_epc(data: dict, id: str) -> dict:
        epc_url = None
        epc_current = None
        epc_potential = None
        epc_scraped = False
        
        if id[0] == "R":
            if len(data) > 0:
                epc_url = data[0]["url"]
        
        else:
            key_info = {
                item["name"] : item for item in data.get("key_features")
            }
            if "EPC Rating" in key_info:
                if key_info["EPC Rating"].get("image"):
                    epc_url = key_info["EPC Rating"].get("image")
                else:
                    epc_url = key_info["EPC Rating"].get("link")
                
                if "/" in key_info["EPC Rating"].get("text"):
                    epc_current, epc_potential = key_info["EPC Rating"].get("text").split("/")
                    epc_current = epc_current[1:]
                    epc_potential = epc_potential[1:]
                    epc_scraped = True

            if epc_current == "":
                epc_current = None
            if epc_potential == "":
                epc_potential = None
            if epc_url == "":
                epc_url = None
        
        return {
            "epc_current" : epc_current,
            "epc_potential" : epc_potential,
            "epc_url" : epc_url,
            "epc_scraped" : epc_scraped
        }
            
    @staticmethod
    def extract_listing_type(data: dict, id: str) -> dict:
        listing_type = None
        letting_type = None
        
        if id[0] == "R":
            listing_type = data["property_data"].get("transactionType")
            if listing_type[0] == "B":
                listing_type = "SALE"

            letting_type = data["analytics_property"].get("lettingType")
        else:
            listing_type = data.get("text", "").upper()
            if listing_type == "":
                listing_type = None
            
        return {
            "listing_type": listing_type,
            "letting_type": letting_type
        }
    
    @staticmethod
    def extract_layout(data: dict, id: str) -> dict:
        bathrooms = None
        bedrooms = None
        receptions = None
        property_type = None
        min_size = None
        max_size = None
        
        if id[0] == "R":
            bedrooms = data["bedrooms"]
            bathrooms = data["bathrooms"]
            property_type = f"{data['property_type'].get('propertyType')} {data['property_type'].get('propertySubType')}"
            min_size = data.get("minSizeFt")
            max_size = data.get("maxSizeFt") 
        else:
            property_type = data.get('propertyType', {}) or {}
            property_style = data.get("style", {}) or {}
            
            property_type = f"{property_type.get('text')} {property_style.get('text')}"
            bedrooms = data.get("numBedrooms")
            bathrooms = data.get("numBathrooms")
            receptions = data.get("numReceptionRooms")
        
        return {
            "bathrooms" : bathrooms,
            "bedrooms" : bedrooms,
            "receptions" : receptions,
            "property_type" : property_type,
            "min_size" : min_size,
            "max_size" : max_size,
        }
        
    @staticmethod
    def extract_tax(data: dict, id: str) -> dict:
        tax_band = None
        tax_exempt = None
        tax_included = None
        annual_ground_rent = None
        annual_ground_rent_review_period = None
        annual_ground_rent_percentage_increase = None
        annual_service_charge = None
        domestic_rates = None
        
        if id[0] == "R":
            tax_band = data.get("councilTaxBand")
            tax_exempt = data.get("councilTaxExempt")
            tax_included = data.get("councilTaxIncluded")
            annual_ground_rent = data.get("annualGroundRent")
            annual_ground_rent_review_period = data.get("groundRentReviewPeriodInYears")
            annual_ground_rent_percentage_increase = data.get("groundRentPercentageIncrease")
            annual_service_charge = data.get("annualServiceCharge")
            domestic_rates = data.get("domesticRates")
            
        
        return {
            "tax_band" : tax_band,
            "tax_exempt" : tax_exempt,
            "tax_included" : tax_included,
            "annual_ground_rent" : annual_ground_rent,
            "annual_ground_rent_review_period" : annual_ground_rent_review_period,
            "annual_ground_rent_percentage_increase" : annual_ground_rent_percentage_increase,
            "annual_service_charge" : annual_service_charge,
            "domestic_rates" : domestic_rates,
        }
    
    @staticmethod
    def extract_ownership(data: dict, id: str) -> dict:
        ownership = None
        
        if id[0] == "R":
            ownership = data.get("sharedOwnership")
            
        else:
            ownership = data.get("coOwnershipEligible")
        
        return ownership
        
    @staticmethod
    def extract_retirement(data: dict, id: str) -> dict:
        retirement = None
        
        if id[0] == "R":
            retirement = data.get("retirement")
        
        return retirement
        
    @staticmethod
    def extract_tenure(data: dict, id: str) -> dict: 
        tenure_type = None
        tenure_lease_years = None
        tenure_text = None
        
        if id[0] == "R":
            tenure_type = data.get("tenureType")
            tenure_lease_years = data.get("yearsRemainingOnLease")
            tenure_text = data.get("message")
            
        else:
            key_info = {
                item["name"] : item for item in data
            }
            tenure_type: str = key_info.get("Tenure", {}).get("name", "")
            if tenure_type == "":
                tenure_type = None
            elif tenure_type[0] == "N":
                tenure_type = None
            else:
                tenure_type = tenure_type.upper()
        
        return {
            "tenure_type" : tenure_type, 
            "tenure_lease_years" : tenure_lease_years, 
            "tenure_text" : tenure_text, 
        }

    @staticmethod
    def extract_estate_agent(data: dict | list[dict], id: str) -> dict:
        name = None
        branch_name = None
        branch_display_address = None
        branch_url = None
        branch_description = None
        
        if id[0] == "R":
            name = data.get("companyName", "")
            branch_name = data.get("branchName", "")
            branch_display_address: data.get("displayAddress")
            branch_url = data.get(f"https://rightmove.co.uk{'customerProfileUrl'}")
            branch_description = data.get("customerDescription", {}).get("truncatedDescriptionHTML")
            
        else:
            if len(data) > 0:
                agent: dict = data[0]
                name = agent.get("organisation")
                branch_name = agent.get("organisationBranch")
                branch_display_address = agent.get("displayAddress")
                branch_url = agent.get("websiteUrl")

        return {
            "name" : name, 
            "branch_name" : branch_name, 
            "branch_display_address" : branch_display_address, 
            "branch_url" : branch_url, 
            "branch_description" : branch_description, 
        }
        
    @staticmethod
    def extract_views(data: list[dict], id: str) -> list[dict]:
        views_list = []
        
        if id[0] == "R":
            pass
            
        else:   
            history = data.get("history", []) or []
            for view_data in history:
                views = {}
                views["view_id"] = id
                views["view_date"] = view_data["date"].split("T")[0]
                views["unique_views"] = view_data["totalUniqueViews"]
                views["views"] = view_data["totalViews"]
                views["featured"] = view_data["featured"]
                views["bumped"] = view_data["bumped"]
                views["published"] = view_data["published"]
                views_list.append(views)
        
        return views_list
    
    @staticmethod
    def extract_key_features(data: list[dict], id: str) -> list[dict]:
        key_features = []
        
        if id[0] == "R": 
            for feature in data:
                key_features.append(
                    {
                        "key_feature_id" : id,
                        "key_feature": feature
                    }
                )
        
        else:
            for feature in data:
                key_features.append(
                    {
                        "key_feature_id" : id,
                        "key_feature" : feature["name"],
                        "key_feature_text" : feature["text"]
                    }
                )
        
        return key_features
                    
    @staticmethod
    def extract_images(data: list[dict], id: str) -> list[dict]:
        images = []
        floorplans = []
        
        if id[0] == "R":
            for idx, floorplan_data in enumerate(data["floorplans"]):
                floorplan = {}
                floorplan["property_id"] = id
                floorplan["floorplan_url"] = floorplan_data["url"]
                floorplan["floorplan_url_resized"] = floorplan_data.get("resizedFloorplanUrls", {}).get("size296x197") if floorplan.get("resizedFloorplanUrls") is not None else None
                floorplan["floorplan_caption"] = floorplan_data["caption"]
                floorplan["floorplan_id"] = idx
                floorplans.append(floorplan)
            for idx, image_data in enumerate(data["images"]):
                image = {}
                image["property_id"] = id
                image["image_url"] =  image_data["url"]
                image["image_url_resized"] =  image_data.get("resizedImageUrls", {}).get("size656x437")
                image["image_caption"] =  image_data["caption"]
                image["image_id"] =  idx
                images.append(image)
                
        else:
            for image_data in data:
                image = {}
                if image_data["imageType"][0] == "F":
                    image["property_id"] = id
                    image["floorplan_id"] = image_data["displayOrder"]
                    image["floorplan_url"] = image_data["url"]
                    image["floorplan_url_resized"] = image_data["urls"].get("580x425:FILL_CROP")
                    image["floorplan_caption"] = None
                    floorplans.append(image)
                else:
                    image["property_id"] = id
                    image["image_id"] = image_data["displayOrder"]
                    image["image_url"] = image_data["url"]
                    image["image_url_resized"] = image_data["urls"].get("580x425:FILL_CROP")
                    image["image_caption"] =  None
                    images.append(image)
        
        return images, floorplans
            
    @staticmethod
    def extract_rooms(data: list[dict], id: str) -> list[dict]:
        rooms_list = []
        room_name = None
        room_description = None
        room_width = None
        room_length = None
        room_unit = None
        room = None
        
        if id[0] == "R":             
            for idx, room_data in enumerate(data): 
                room_name =  room_data["name"]
                room_description =  room_data["description"]
                room_width =  room_data["width"]
                room_length =  room_data["length"]
                room_unit =  room_data["unit"]
                room =  idx
                
                rooms_list.append(
                        {
                            "room_id" : id,
                            "room_name" : room_name,
                            "room_description" : room_description,
                            "room_width" : room_width,
                            "room_length" : room_length,
                            "room_unit" : room_unit,
                            "room" : room,
                        }
                )
        
        return rooms_list
    
    @staticmethod
    def extract_stations(data: list[dict], id: str) -> list[dict]:
        stations_list = []
        
        if id[0] == "R":
            for station in data:
                station_name = station.get("name")
                station_type = station.get("types")[0]
                stations_list.append(
                    {
                        "station_name": station_name,
                        "station_type": station_type,
                    }
                )
        
        return stations_list

    @staticmethod
    def extract_station_distances(data: list[dict], id: str) -> list[dict]:
        station_distances_list = []
        
        if id[0] == "R":
            for station in data:
                station_name = station.get("name")
                station_type = station.get("types")[0]
                distance = station.get("distance")
                units = station.get("unit")
                station_distances_list.append(
                    {
                        "property_id": id,
                        "station_name": station_name,
                        "station_type": station_type,
                        "station_distance": distance,
                        "station_distance_units": units
                    }
                )
        
        return station_distances_list
    
    @staticmethod
    def extract_prices(data: dict | list[dict], id: str) -> list[dict]:
        price = None
        price_date = None
        price_qualifier = None
        price_type = None
        prices = []
        
        if id[0] == "R":
            price_date = None
            if len(data["listing_history"]) > 0:
                update_reason = data["listing_history"].get("listingUpdateReason")
                
                if "today" in update_reason:
                    price_date = datetime.now().strftime("%Y-%m-%d")
                elif "yesterday" in update_reason:
                    price_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    price_date = "-".join(update_reason.split(" ")[-1].split("/")[::-1])
                
                price_type = update_reason.split(" ")[0]
                
            else:
                price_type = "Added"
                price_date = data["analytics_property"].get("added")
                
                if price_date:
                    price_date = f"{price_date[0:4]}-{price_date[4:6]}-{price_date[6:]}"
            
            if price_date == "":
                price_date = None
            
            price = data["analytics_property"].get("price")
            price_qualifier = data["analytics_property"].get("priceQualifier")
            
            prices.append(
                    {
                        "price_id" : id,
                        "price" : price,
                        "price_date" : price_date,
                        "price_qualifier" : price_qualifier,
                        "price_type" : price_type
                    }
            )
                
        else:
            for idx, history_data in enumerate(data):
                price_difference = history_data.get("difference", 0) or 0
                
                if price_difference < 0:
                    price_type = "Reduced"
                    
                elif idx == len(data) -1:
                    price_type = "Added"
                
                price = history_data["price"]
                price_date = history_data.get("timeModified").split("T")[0]
                price_qualifier = history_data.get("pricePrefix")
                
                prices.append(
                    {
                        "price_id" : id,
                        "price" : price,
                        "price_date" : price_date,
                        "price_qualifier" : price_qualifier,
                        "price_type" : price_type
                    }
                )
        
        return prices
                    
    @staticmethod
    def extract_statuses(data: dict | list[dict], id: str) -> list[dict]:
        status = None
        status_date = None
        statuses = []
        
        if id[0] == "R":            
            status = data.get("soldSTC")
            
            if status:
                status_date = datetime.now().strftime("%Y-%m-%d")
            else:
                status_date = data.get("added")
                if not status_date:
                    status_date = datetime.now().strftime("%Y-%m-%d")
                else:
                    status_date = f"{status_date[0:4]}-{status_date[4:6]}-{status_date[6:]}"

                statuses.append(
                    {
                        "status_id" : id,
                        "status" : status,
                        "status_date" : status_date,
                    }
                )
                
        else:   
            for idx, history_data in enumerate(data):
                if history_data.get("statusChange") and idx != len(data) - 1:
                    status = True
                    status_date = history_data.get("timeModified").split("T")[0]
                
                elif idx == len(data) - 1:
                    status = False
                    status_date = history_data.get("timeModified").split("T")[0]
                
                statuses.append(
                    {
                        "status_id" : id,
                        "status" : status,
                        "status_date" : status_date,
                    }
                )
                    
        return statuses
    
    @staticmethod
    def extract_accreditations(data: list[dict], id: str) -> list[dict]:
        accreditations_list = []
        have_accreditations_list = []
        
        if id[0] == "R":
            pass
        else:
            for accreditation_data in data["have"]:
                accreditation = {}
                have_accreditation = {}
                
                accreditation["accreditation_label"] = have_accreditation["accreditation_label"] = accreditation_data["label"]
                have_accreditation["have"] = True
                have_accreditation["estate_agent"] = data["estate_agent"]
                accreditation["accreditation_url"] = accreditation_data["url"]
                accreditation["accreditation_key"] = accreditation_data["textKey"]
                accreditation["accreditation_type"] = accreditation_data["type"]
                accreditations_list.append(accreditation)
                have_accreditations_list.append(have_accreditation)
            
            for accreditation_data in data["dont_have"]:
                accreditation = {}
                accreditation["accreditation_label"] = have_accreditation["accreditation_label"] = accreditation_data["label"]
                have_accreditation["have"] = False
                have_accreditation["estate_agent"] = data["estate_agent"]
                accreditation["accreditation_url"] = accreditation_data["url"]
                accreditation["accreditation_key"] = accreditation_data["textKey"]
                accreditation["accreditation_type"] = accreditation_data["type"]
                accreditations_list.append(accreditation)
                have_accreditations_list.append(have_accreditation)
                
        return accreditations_list, have_accreditations_list
        