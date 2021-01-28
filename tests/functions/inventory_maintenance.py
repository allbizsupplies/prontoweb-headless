
from nose.tools import assert_equal, assert_in
from random import randint
from time import sleep
from tests import DriverTestBase
from prontoweb.driver import FormException
from prontoweb.functions.inventory_maintenance import InventoryMaintenanceFunction


class InvMaintTest(DriverTestBase):

    def setUp(self):
        super().setUp()
        self.function = InventoryMaintenanceFunction(self.driver)

    def test_open(self):
        self.function.open()

    def test_find_record(self):
        item_code = "BIC-10206"
        self.function.open()
        self.function.find_record(item_code)
    
    def test_update_record(self):
        item_code = "BIC-10206"
        values = {
            "stk-apn-number": str(randint(00000,99999)),
        }
        self.function.open()
        self.function.update_record(item_code, values)

    def test_find_warehouse_stock_record(self):
        item_code = "BIC-10206"
        warehouse_code = "ALB"
        self.function.open()
        self.function.find_record(item_code)
        self.function.open_warehouse_stock_mode()
        self.function.find_warehouse_stock_record(warehouse_code)
