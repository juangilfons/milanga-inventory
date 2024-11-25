from django.test import TestCase
from django.contrib.auth.models import User
from .models import SubColumn, Column, Refrigerator, Cut, Order, ActionLog, OrderAllocation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from selenium.webdriver.edge.service import Service

class InventoryUnitTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print('Pruebas Unitarias\n')

    def setUp(self):
        self.user = User.objects.create(username="test_user", is_superuser=True)
        self.refrigerator = Refrigerator.objects.create(name="Test Refrigerator")
        self.column = Column.objects.create(refrigerator=self.refrigerator, capacity=10)
        self.cut = Cut.objects.create(
            name="Test Cut",
            milas_per_tupper=5,
            reorder_threshold=10,
            reorder_tuppers=20,
            days_until_expiration=10
        )

    def test_add_tuppers_to_cut(self):
        self.cut.add_tuppers(tuppers_num=15, column_id=self.column.id)
        
        subcolumn = SubColumn.objects.get(column=self.column, cut=self.cut)
        self.assertEqual(subcolumn.total_tuppers, 15, "El total de tuppers en el subcolumna debería ser 15")
        print("Prueba 1: Tuppers añadidos correctamente al corte.")

    def test_sell_milas_from_cut(self):
        self.cut.add_tuppers(5, self.column.id)
        self.cut.sell_milas(milas_num=8, user=self.user)
        
        action_log = ActionLog.objects.filter(user=self.user, action_type="SALE").first()
        self.assertIsNotNone(action_log, "Debería existir un registro de venta en ActionLog")
        self.assertIn("Sold 8 milanesas", action_log.action_description, "El log debería indicar la cantidad correcta de milanesas vendidas")
        print("Prueba 2: Venta de milanesas registrada correctamente y cantidad actualizada en subcolumnas.")


    def test_order_allocation(self):
        order = Order.objects.create(cut=self.cut, tuppers_requested=20)
        order.allocate_tuppers(column_id=self.column.id, tuppers_to_add=10, user=self.user)
        
        allocation = OrderAllocation.objects.get(order=order, column=self.column)
        self.assertEqual(allocation.tuppers_allocated, 10, "Debería haber una asignación de 10 tuppers en OrderAllocation")
        self.assertEqual(order.tuppers_remaining, 10, "El pedido debería tener 10 tuppers restantes después de la asignación")
        print("Prueba 3: Asignación de tuppers realizada correctamente y tuppers restantes actualizados.")


class TestReorderOnLowStock(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print('Prueba de Integracion\n')

    def setUp(self):
        self.refrigerator = Refrigerator.objects.create(name="TestRefrigerator")
        self.column = Column.objects.create(refrigerator=self.refrigerator, capacity=10)

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


class SellMilasTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print('Prueba de Aceptacion\n')
        
    def setUp(self):
        driver_path = getattr(settings, "EDGE_DRIVER_PATH")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.cut_name = "Test Cut"
        self.cut = Cut.objects.create(
            name=self.cut_name,
            milas_per_tupper=5,
            reorder_threshold=10,
            reorder_tuppers=20,
            days_until_expiration=10
        )
        self.refrigerator = Refrigerator.objects.create(name="Test Refrigerator")
        self.column = Column.objects.create(refrigerator=self.refrigerator, capacity=10)
        self.cut.add_tuppers(5, self.column.id)
        service = Service(driver_path)
        self.browser = webdriver.Edge(service=service)
    
    def tearDown(self):
        self.browser.quit()

    def test_sell_milas(self):
        # Open the login page
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        # Log in as the test user
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("testuser")
        password_input.send_keys("testpassword")
        password_input.send_keys(Keys.RETURN)

        # Navigate to the sell_milas page
        self.browser.get(f"{self.live_server_url}/sell_milas/")

        #  Wait for the page to load and form to appear
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        # Fill in the form fields
        cut_select = self.browser.find_element(By.NAME, "cut")
        cut_select.send_keys(self.cut_name)
        
        milas_input = self.browser.find_element(By.NAME, "milas_to_sell")
        milas_input.send_keys("10")
        
        #  Submit the form
        submit_button = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        #  Wait for the success message
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success"))
        )

        #  Check that the success message is displayed
        messages = self.browser.find_element(By.CLASS_NAME, "mensaje-lista").text
        self.assertIn("Venta exitosa!", messages)
        print(f"Venta realizada con exito.")
