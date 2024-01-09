from django.http import JsonResponse
from django.db.models import QuerySet
from django.core import serializers
from backend.models import *
from django.db.models import F
from django.db.models import Q
import json
from time import time

def get_filters(input_dict: dict, prefix="") -> dict:
    filters = {}
    for key, value in input_dict.items():
        current_key = f"{prefix}{key}"
        if isinstance(value, dict):
            nested_filters = get_filters(value, prefix=f"{current_key}__")
            filters.update(nested_filters)
        else:
            filters[current_key] = value
    return filters

def filter_view(request):
    parameters = request.GET.get("params")
    parameters = json.loads(parameters)
    property_parameters: dict = parameters.get("property")
    property_filters = get_filters(property_parameters)
    properties = Property.objects.filter(**property_filters).select_related("property_data").prefetch_related("prices", "keyfeature_set", "status_set", "image_set", "floorplan_set", "room_set", "premiumlisting_set")
    try:
        result = serializers.serialize("json", properties)
        print(result)
    except Exception as e:
        print(e)
       