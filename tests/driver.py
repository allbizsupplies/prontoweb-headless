
from nose.tools import assert_equal, assert_in
import logging
import os
import settings
from time import sleep
import unittest
from prontoweb.driver import ProntoWebDriver, FormException

logging.disable()


class DriverTest(unittest.TestCase):

    def setUp(self):
        self.driver = self.start_session()

    def tearDown(self):
        self.driver.close()
        download_dir = os.path.join(os.getcwd(), "downloads")
        existing_files = os.listdir(download_dir)
        for file in existing_files:
            os.unlink(os.path.join(download_dir, file))

    def start_session(self):
        download_dir = os.path.join(os.getcwd(), "downloads")
        driver = ProntoWebDriver(
            headless=(not settings.DEBUG),
            download_dir=download_dir
        )
        driver.login(
            settings.PRONTOWEB_URL,
            settings.PRONTO_USERNAME,
            settings.PRONTO_PASSWORD)
        return driver

    def test_download_datagrid(self):
        self.driver.select_menu_item(
            ["Inventory Reports", "DI Price Algorithm Rules"])
        filename = self.driver.export_datagrid()
        self.driver.close_function()
        self.assertEqual("tempFileName.ods", filename)

    def test_open_function(self):
        self.driver.open_function("INV.M138")

    def test_select_function_mode(self):
        self.driver.open_function("INV.M138")
        self.driver.select_function_mode("&Find")

    def test_select_nested_function_mode(self):
        self.driver.open_function("INV.M138")
        self.driver.select_function_mode("&Whse")
        self.driver.select_function_mode("&Correct")

    def test_fill_form(self):
        self.driver.open_function("INV.M138")
        self.driver.select_function_mode("&Find")
        seen_inputs = self.driver.fill_form({
            "stock-code": "BIC-10206"
        })
        self.assertIn("stock-code", seen_inputs)

    def test_fill_datagrid_row(self):
        self.driver.select_menu_item([
            "Office Choice Main Menu",
            "Web Site Category / Product Maintenance",
            "Stockcode Review",
        ])
        self.driver.select_function_mode("&Find")
        self.driver.fill_datagrid_row({
            "1": "BIC-10206"
        })

    def test_detect_form_error(self):
        self.driver.open_function("INV.M138")
        self.driver.select_function_mode("&Find")
        # with self.assertRaises(FormException):
        with self.assertRaises(FormException):
            self.driver.fill_form({
                "stock-code": "SLARTIBARTFAST"
            })
