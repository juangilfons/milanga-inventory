from django.test import TestCase
from .models import SubColumn, Column, Refrigerator, Cut, Tupper
# Create your tests here.

class TestDB(TestCase):
    def setUp(self):
        SubColumn.objects.create(
            column=Column.objects.create(
                refrigerator=Refrigerator.objects.create(name="TestRefrigerator")
                ),
            cut=Cut.objects.create(name='Carne',milas_per_tupper=10),
            total_tuppers=2,
            milas_tupper_in_use=4
        )

        SubColumn.objects.create(
            column=Column.objects.get(pk=1),
            cut=Cut.objects.create(name='Pollo',milas_per_tupper=30),
            total_tuppers=3,
            milas_tupper_in_use=15
        )

        SubColumn.objects.create(
            column=Column.objects.get(pk=1),
            cut=Cut.objects.create(name='Soja',milas_per_tupper=60),
            total_tuppers=4,
            milas_tupper_in_use=30
        )

    
    def test(self):
        column=Column.objects.get(pk=1)
        print(list(column.subcolumn_generator()))


class CutModelTest(TestCase):
    def setUp(self):
        self.cut = Cut.objects.create(name="Carne", milas_per_tupper=10)

    def test_create_cut(self):
        self.assertEqual(self.cut.name, "Carne")

    def test_read_cut(self):
        cut = Cut.objects.get(id=self.cut.id)
        self.assertEqual(cut.name, "Carne")

    def test_update_cut(self):
        self.cut.name = "Pollo"
        self.cut.save()
        updated_cut = Cut.objects.get(id=self.cut.id)
        self.assertEqual(updated_cut.name, "Pollo")

    def test_delete_cut(self):
        self.cut.delete()
        with self.assertRaises(Cut.DoesNotExist):
            Cut.objects.get(id=self.cut.id)