from django.test import TestCase
import json
from backend.models import *
from backend.data_parser import DataParser


class NoReallyThisTime(TestCase):
    def setUp(self) -> None:
        pass
    
    def test_list(self):
        TestModel.objects.create(id = "I am an id", list_field = ["this", "is", "a" , "list"])
        
        TestModel.objects.set_list_field(list_field = ["this", "is", "a", "new", "list"])
        print(TestModel.objects.all().values("list_field"))
        