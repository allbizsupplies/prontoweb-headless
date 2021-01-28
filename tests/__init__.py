
import logging
import os
import settings
import unittest
from prontoweb.driver import ProntoWebDriver

logging.disable()


class DriverTestBase(unittest.TestCase):

    def setUp(self):
        self.driver = self.start_session()
        self.driver.select_company("TEST-Allbiz")

    def tearDown(self):
        self.driver.close()

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
