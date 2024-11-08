from django.test import TestCase
from django.contrib.auth.models import User
from .models import SubColumn, Column, Refrigerator, Cut, Tupper, Order
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


class TestReorderOnLowStock(TestCase):
    def setUp(self):
        self.refrigerator = Refrigerator.objects.create(name="TestRefrigerator")
        self.column = Column.objects.create(refrigerator=self.refrigerator)

        self.cut_carne = Cut.objects.create(
            name='Carne',
            milas_per_tupper=10,
            reorder_threshold=5,
            reorder_tuppers=10,
            is_order_pending=False
        )

        SubColumn.objects.create(
            column=self.column,
            cut=self.cut_carne,
            total_tuppers=3,
            milas_tupper_in_use=4
        )

        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_sell_milas_and_trigger_reorder(self):
        milas_to_sell = 24

        self.cut_carne.sell_milas(milas_to_sell, self.user)
        self.cut_carne.refresh_from_db()
        print("Venta de milanesas realizada, stock actualizado.")

        self.assertTrue(self.cut_carne.is_order_pending, "The reorder should be marked as pending when stock is low.")
        print("Estado de reorden verificado: is_order_pending está en True.")

        order = Order.objects.filter(cut=self.cut_carne).first()
        self.assertIsNotNone(order, "An order should have been created when stock reached reorder threshold.")
        print("Creación de pedido verificada: se generó un pedido al alcanzar el umbral de reorden.")

        self.assertEqual(order.tuppers_requested, self.cut_carne.reorder_tuppers, "The order should request the correct number of tuppers.")
        print(f"Cantidad de tuppers en el pedido verificada: se solicitaron {order.tuppers_requested} tuppers, como se esperaba.")