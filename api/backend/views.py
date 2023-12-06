from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import QuerySet
from backend.models import *
from django.db.models import F
import json
from time import time

ONE_TO_ONE_TABLES = {
    "text_elements",
    "location",
    "broadband",
    "epc",
    "listing_type",
    "layout",
    "tax",
    "ownership",
    "tenure",
    "added",
    "estate_agent",
    "property"
}

FOREIGN_KEYS = {
    "prices" : {
            "dated" : True,
            "table" : Prices,
            "date_variable" : "price_date"
        },
    "key_feature" : {
            "dated" : True,
            "table" : KeyFeature,
            "date_variable" : None
        },
    "statuses" : {
            "dated" : True,
            "table" : Statuses,
            "date_variable" : "status_date"
        },
    "views" : {
            "dated" : True,
            "table" : Views,
            "date_variable" : "view_date"
        },
    "rooms" : {
            "dated" : True,
            "table" : Rooms,
            "date_variable" : None
        },
    "stationstationdistance" : {
            "dated" : False,
            "table" : StationStationDistance,
            "date_variable" : None
    }
    
}

def get_foreign_key_property_ids(queries: dict[dict]) -> set[str]:
    result_property_ids = set()
    queries_happened = False
    for query_key, query_value in queries.items():
        if not query_key:
            continue
        queries_happened = True
        if not FOREIGN_KEYS[query_key]["dated"]:
            if not result_property_ids:
                result_property_ids = set(list(FOREIGN_KEYS[query_key]["table"].objects.filter(**query_value).values_list("property_id", flat=True).distinct()))
            else:
                result_property_ids &= set(list(FOREIGN_KEYS[query_key]["table"].objects.filter(**query_value).values_list("property_id", flat=True).distinct()))
        else:
            if not result_property_ids:
                result_property_ids = set(list(FOREIGN_KEYS[query_key]["table"].objects.filter(**query_value).order_by("property_id", f'-{FOREIGN_KEYS[query_key]["date_variable"]}').distinct("property_id").values_list("property_id", flat=True)))
            else:
                result_property_ids &= set(list(FOREIGN_KEYS[query_key]["table"].objects.filter(**query_value).order_by("property_id", f'-{FOREIGN_KEYS[query_key]["date_variable"]}').distinct("property_id").values_list("property_id", flat=True)))
    if queries_happened:
        return result_property_ids
    else:
        result_property_ids = set(list(PropertyValue.objects.all().values_list("property_id", flat=True).distinct()))
        return result_property_ids

def get_queries(queries: dict[dict], through: bool=False, foreign_key: bool=False) -> dict[str | dict[str]]:
    result_queries = {}
    for query_key, query_value in queries.items():
        query_value: dict | None
        
        if not query_value:
            continue        
        
        for sub_query_key, sub_query_value in query_value.items():
            
            if through:
                result_queries[f"{sub_query_key}"] = sub_query_value
                
            elif foreign_key: 
                if query_key not in result_queries:
                    result_queries[query_key] = {}
                result_queries[query_key][f"{sub_query_key}"] = sub_query_value
                
            else:
                result_queries[f"{query_key}__{sub_query_key}"] = sub_query_value
    return result_queries

def get_fields(fields: dict[dict]) -> [dict[F], dict[str]]:
    one_to_one_fields = {}
    other_fields = {}
    for field_key, field_value in fields.items():
        if not field_value:
            continue
        for field in field_value:
            if field_key in ONE_TO_ONE_TABLES:
                one_to_one_fields[field] = F(f"{field_key}__{field}")
            else:
                if field_key not in other_fields:
                    other_fields[field_key]  = []
                other_fields[field_key].append(field)
                
                
    return one_to_one_fields, other_fields

def serialized_result(property_ids: set[str], one_to_one_fields: dict[F], other_fields: dict[str]) -> QuerySet[dict]:
    extra_data = {}
    for table, fields in other_fields.items():
        data = FOREIGN_KEYS[table]["table"].objects.filter(property_id__in=property_ids).values("property_id", *fields)
        for instance in data:
            if instance["property_id"] not in extra_data:
                extra_data[instance["property_id"]] = {}
            if table not in extra_data[instance["property_id"]]:
                extra_data[instance["property_id"]][table] = []
            extra_data[instance["property_id"]][table].append(
                {
                    str(key) : value for key, value in instance.items() if key != "property_id"
                }
            )
    final_query = PropertyValue.objects.filter(property_id__in=property_ids).values("property_id").annotate(
            **one_to_one_fields
        )
    result = {}
    for item in final_query:
        id = item.get("property_id")
        if extra_data.get(id):
            item.update(extra_data[id])    
            result[id] = item
    return result

def filter_view(request):
    serialized_params = request.GET.get('params')
    if not serialized_params:
        return JsonResponse({"Error" : "No parameters provided"})
    params = json.loads(serialized_params)
    one_to_one_queries = get_queries(queries=params["queries"]["one_to_one"])
    through_queries = get_queries(queries=params["queries"]["through"], through=True)
    foreign_key_queries = get_queries(queries=params["queries"]["foreign_key"], foreign_key=True)
    property_ids = set(list(PropertyValue.objects.filter(**one_to_one_queries).values_list("property_id", flat=True)))
    if params["queries"]["through"]["stations"]:
        property_ids &= set(list(PropertyValue.stations.through.objects.filter(**through_queries).values_list("property_id", flat=True)))
    property_ids &= get_foreign_key_property_ids(foreign_key_queries)
    one_to_one_fields, other_fields = get_fields(params["fields"])
    result = serialized_result(property_ids=property_ids, one_to_one_fields=one_to_one_fields, other_fields=other_fields)
    return JsonResponse(result)