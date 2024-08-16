from django.test import TestCase
from .models import SubColumn, Column, Refrigerator, Cut
# Create your tests here.

class TestDB(TestCase):
    def setUp(self):
        SubColumn.objects.create(
            column=Column.objects.create(
                refrigerator=Refrigerator.objects.create(name="TestRefrigerator")
                ),
            cut=Cut.objects.create(milas_per_tupper=10),
            total_tuppers=18,
            milas_tupper_in_use=10
        )
    
    def test(self):
        subcolumn = SubColumn.objects.get(id=1)
        print(subcolumn)