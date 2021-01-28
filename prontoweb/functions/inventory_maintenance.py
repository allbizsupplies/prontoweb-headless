
from prontoweb.functions.base import FunctionBase


class InventoryMaintenanceFunction(FunctionBase):

    def open(self):
        self.driver.open_function("INV.M138")

    def close(self):
        self.driver.close_function()

    def update_record(self, item_code, values):
        self.find_record(item_code)
        self.driver.select_function_mode("&Correct")
        filled_fields = self.driver.fill_form(values)
        return filled_fields

    def find_record(self, item_code):
        self.driver.select_function_mode("&Find")
        self.driver.fill_form({
            "stock-code": item_code
        })
    
    def find_warehouse_stock_record(self, warehouse_code):
        self.driver.select_function_mode("&Find")
        self.driver.fill_form({
            "whse-code": warehouse_code
        })
    
    def open_warehouse_stock_mode(self):
        self.driver.select_function_mode("&Whse", opens_new_card=True)
