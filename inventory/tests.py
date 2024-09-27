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
            total_tuppers=3,
            milas_tupper_in_use=4
        )

        SubColumn.objects.create(
            column=Column.objects.get(pk=1),
            cut=Cut.objects.create(name='Pollo',milas_per_tupper=30),
            total_tuppers=2,
            milas_tupper_in_use=15
        )

        SubColumn.objects.create(
            column=Column.objects.get(pk=1),
            cut=Cut.objects.create(name='Soja',milas_per_tupper=60),
            total_tuppers=2,
            milas_tupper_in_use=30
        )

    def test(self):
        column=Column.objects.get(pk=1)
        subcolumn1 = column.subcolumn_set.get(id=1)

        subcolumn1.sell_milas(2)
        subcolumn1.sell_milas(2)
        print(subcolumn1.total_tuppers, subcolumn1.milas_tupper_in_use)
        print(list(column.column_generator()))
  
    def test_sell_milas(self):
        user_cut_to_sell = 1
        milas_to_sell = 10

        valid_subcolumn = SubColumn.search_cut(user_cut_to_sell)

        column = Column.objects.get(pk=1)
        print(list(column.column_generator()))
        print(valid_subcolumn.total_tuppers, valid_subcolumn.milas_tupper_in_use)

        valid_subcolumn.sell_milas(milas_to_sell)
        print(list(column.column_generator()))
        print(valid_subcolumn.total_tuppers, valid_subcolumn.milas_tupper_in_use)

    def test_add_milas(self):
        cut_incoming_tuppers = 1
        tuppers_num = 12
        selected_column = 1
        column = Column.objects.get(pk=selected_column)

        valid_subcolumn = SubColumn.search_column_cut(cut_incoming_tuppers, selected_column)

        if valid_subcolumn:
            valid_subcolumn.add_tuppers(tuppers_num)
        
        print(list(column.column_generator()))
        print(valid_subcolumn.total_tuppers, valid_subcolumn.milas_tupper_in_use)


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
