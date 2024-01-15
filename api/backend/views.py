from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from backend.serializers import PropertySerializer
from backend.models import *
import json


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

class YourModelPagination(PageNumberPagination):
    page_size = 100  # Set the number of items per page

# class FilterView(APIView):
#     pagination_class = YourModelPagination
#     def get(self, request, *args, **kwargs):
#         try:
#             parameters = request.GET.get("params")
#             parameters = json.loads(parameters)
#             property_parameters: dict = parameters.get("property")
#             property_filters = get_filters(property_parameters)
#             properties = Property.objects.filter(**property_filters)#.select_related("property_data").prefetch_related("prices", "keyfeature_set", "status_set", "image_set", "floorplan_set", "room_set", "premiumlisting_set")
#             properties = properties[0:500]
#             page = self.pagination_class().paginate_queryset(properties, request, view=self)
#             serializer = PropertySerializer(properties, many=True)
#             if page:
#                 return self.pagination_class().get_paginated_response(serializer.data)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             print(e)

class FilterView(APIView):
    pagination_class = YourModelPagination
    def get(self, request, *args, **kwargs):
        try:
            parameters = request.GET.get("params")
            page_size = int(request.GET.get("page_size"))
            parameters = json.loads(parameters)
            property_parameters: dict = parameters.get("property")
            property_filters = get_filters(property_parameters)
            properties = Property.objects.filter(**property_filters)#.select_related("property_data").prefetch_related("prices", "keyfeature_set", "status_set", "image_set", "floorplan_set", "room_set", "premiumlisting_set")
            properties = properties[0:10]
            paginator = self.pagination_class()
            paginator.page_size = page_size
            paginator.page_query_param = "page"
            p = paginator.paginate_queryset(queryset=properties, request=request)
            serializer = PropertySerializer(p, many=True, fields=parameters["fields"])
            if p:
                return paginator.get_paginated_response(serializer.data)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)