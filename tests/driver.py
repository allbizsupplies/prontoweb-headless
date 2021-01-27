
from nose.tools import assert_equal, assert_in
import logging
import os
from random import randint
import settings
from time import sleep
import unittest
from prontoweb.driver import ProntoWebDriver, FormException

logging.disable()


class DriverTest(unittest.TestCase):

    def setUp(self):
        self.driver = self.start_session()
        self.driver.select_company("TEST-Allbiz")

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

    def test_select_company(self):
        self.driver.select_company("Allbiz Supplies Pty. Ltd.")
        self.driver.select_company("TEST-Allbiz")

    def test_download_datagrid(self):
        self.driver.select_menu_item([
            "Inventory Reports", 
            "DI Price Algorithm Rules",
        ])
        filename = self.driver.export_datagrid()
        self.driver.close_function()
        self.assertEqual("tempFileName.ods", filename)

    def test_open_function(self):
        self.driver.open_function("INV.M138")

    def test_select_function_mode(self):
        self.driver.open_function("INV.M138")
        self.driver.select_function_mode("&Find")

    def test_select_extra_function_mode(self):
        self.driver.open_function("INV.M138")
        self.driver.select_extra_function_mode("GTIN/&Multi UOM")

    def test_select_nested_function_mode(self):
        self.driver.open_function("INV.M138")
        self.driver.select_function_mode("&Whse")
        self.driver.select_function_mode("&Correct")

    def test_fill_form(self):
        self.driver.open_function("INV.M138")
        self.driver.select_function_mode("&Find")
        self.driver.fill_form({
            "stock-code": "BIC-10206"
        })

    def test_fill_datagrid_row(self):
        self.driver.select_menu_item([
            "Inventory Reports",
            "Stock Control datagrid",
        ])
        self.driver.select_function_mode("&Find")
        self.driver.fill_datagrid_row({
            "0": "BIC-10206"
        })

    def test_fill_multiple_datagrid_rows(self):
        self.driver.open_function("INV.M138")
        self.driver.select_extra_function_mode("GTIN/&Multi UOM")
        fake_gtin_codes = []
        for i in range(2):
            fake_gtin_codes.append(
                "".join([str(randint(1, 9)) for j in range(10)]))
        for fake_gtin_code in fake_gtin_codes:
            self.driver.select_function_mode("&Entry")
            self.driver.fill_datagrid_row({
                "0": fake_gtin_code,
                "1": "TIN",
                "2": "1",
                "9": "N",
            })

    def test_detect_form_error(self):
        self.driver.open_function("INV.M138")
        self.driver.select_function_mode("&Find")
        # with self.assertRaises(FormException):
        with self.assertRaises(FormException):
            self.driver.fill_form({
                "stock-code": "SLARTIBARTFAST"
            })
