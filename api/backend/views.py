from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, Avg, Count, ExpressionWrapper, Sum, F, IntegerField, Max
from django.db.models.functions import Length, Cast
from backend.models import *
import json
import time 

FUNCTIONS = {
    "ArrayAgg" : ArrayAgg,
    "Avg" : Avg,
    "Count" : Count, 
    "Sum" : Sum,
    "Max" : Max,
}

FIELDS = {
    "IntegerField" : IntegerField()
}

def get_fields(input_dict: dict, prefix="") -> list:
    fields = []
    for key, value in input_dict.items():
        if key != "property": 
            fields.extend([f"{key}__{field}" for field in value])
        else:
            fields.extend([field for field in value])
    return fields

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

def get_annotated(input_dict: dict, prefix="") -> dict:
    annotated = {}
    for key, value in input_dict.items():
        value["args"]["filter"] = Q(**value["filter"])
        
        if "Cast" in value:
            annotated[key] = FUNCTIONS[value["function"]](
                Cast(value["field"], output_field=FIELDS[value["Cast"]]),
                **value["args"],
            )
        else:
            annotated[key] = FUNCTIONS[value["function"]](
                value["field"],
                **value["args"],
            )
            
    return annotated

class YourModelPagination(PageNumberPagination):
    page_size = 100 
    
class FilterView(APIView):
    pagination_class = YourModelPagination
    def get(self, request, *args, **kwargs):
        try:
            parameters = request.GET.get("params")
            page_size = int(request.GET.get("page_size"))
            sample_size = int(request.GET.get("sample_size"))
            parameters = json.loads(parameters)
            
            annotated_fields = parameters["fields"]["annotated"]
            annotated_fields = get_annotated(annotated_fields)
            
            direct_fields = parameters["fields"]["direct"]
            direct_fields = get_fields(direct_fields)
            
            filters = parameters["filters"]
            
            select_related = parameters["select_related"]
            prefetch_related = parameters["prefetch_related"]
            
            start = time.time()
            properties = Property.objects\
                .select_related(*select_related)\
                .prefetch_related(*prefetch_related)\
                .values(*direct_fields)\
                .annotate(
                        **annotated_fields
                        )\
                .filter(
                        **filters
                    )
            
            if sample_size:
                properties = properties.order_by("?")[0:sample_size]
            
            paginator = self.pagination_class()
            paginator.page_size = page_size
            paginator.page_query_param = "page"
            p = paginator.paginate_queryset(queryset=properties, request=request)
            return paginator.get_paginated_response(p)
                
        except Exception as e:
            print(e)
        
        print("time take: ", time.time() - start)
        
        return Response(list(p), status=status.HTTP_200_OK)
    
class KeyFeatureView(APIView):
    def get(self, request, *args, **kwargs):
        properties = KeyFeature.objects.values_list("feature", flat=True).distinct()
        return Response(properties, status=status.HTTP_200_OK)