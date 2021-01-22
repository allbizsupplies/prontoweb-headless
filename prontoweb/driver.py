
import os
import re
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import urllib3


DEFAULT_WAIT_TIME = 10
DEFAULT_FUNCTION = "EMS.X001"
DEFAULT_INTERVAL = 0.1


class ProntoWebDriver(webdriver.Chrome):

    def __init__(self, headless="True", download_dir="downloads"):
        self.download_dir = download_dir
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        options = Options()
        options.headless = headless
        options.add_argument("user-data-dir=chromedriver_profile")
        options.add_argument("start-maximized")
        options.add_argument('log-level=3')
        options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
        })
        options.add_experimental_option("excludeSwitches", [
            "enable-logging"
        ])
        super().__init__(options=options, service_log_path="chromedriver.log")

    def login(self, url, username, password):
        self.get(url)
        self.wait_for_element_by_id("loginForm")
        self.wait_for_element_by_id("login-username").send_keys(username)
        self.wait_for_element_by_id("login-password").send_keys(password)
        self.wait_for_clickable_element_by_id("login-button").click()
        self.wait_for_input_value(
            (By.ID, "header-shortcut"), DEFAULT_FUNCTION.replace(".", " "),
            wait_time=60)

    def open_function(self, code):
        element = self.wait_for_clickable_element_by_id(
            "header-shortcut")
        element.click()
        element.send_keys(code)
        element.send_keys(Keys.RETURN)
        self.wait_for_input_value(
            (By.ID, "header-shortcut"),
            code.replace(".", " "),
            wait_time=30)

    def select_function_mode(self, name):
        self.wait_for_clickable_element_by_name(name).click()
        self.wait_until(element_has_any_css_class((By.NAME, name), ["hidden", "disabled"]))

    def select_menu_item(self, values):
        for value in values:
            self.wait_for_clickable_element_by_text(value).click()

    def fill_form(self, values):
        self.wait_for_clickable_element_by_class_name("mode-ok")
        seen_inputs = []
        while(True):
            element = self.wait_for_next_form_field(seen_inputs)
            if element:
                self.fill_form_field(element, values)
            else:
                break
        return seen_inputs

    def fill_datagrid_row(self, values):
        seen_inputs = []
        while(True):
            column_index, element = self.wait_for_next_datagrid_field(seen_inputs)
            if element:
                self.fill_datagrid_field(element, column_index, values)
            else:
                return

    def export_datagrid(self, wait_time=DEFAULT_WAIT_TIME):
        self.wait_for_clickable_element_by_id("export-view").click()
        return self.wait_for_download(wait_time)

    def wait_for_next_form_field(self, seen_inputs, wait_time=DEFAULT_WAIT_TIME):
        elapsed_time = 0.0
        while(self.form_is_open()):
            self.detect_error_dialog(seen_inputs)
            element = self.detect_active_input(seen_inputs)
            if element:
                name = element.get_attribute("name")
                seen_inputs.append(name)
                return element
            # Check for the presence of an error dialog.
            sleep(0.1)
            if elapsed_time >= wait_time:
                raise TimeoutError()
            elapsed_time += DEFAULT_INTERVAL

    def wait_for_next_datagrid_field(self, seen_inputs, wait_time=DEFAULT_WAIT_TIME):
        elapsed_time = 0.0
        while(self.datagrid_is_open()):
            self.detect_error_dialog(seen_inputs)
            element = self.detect_active_input(seen_inputs)
            if element:
                name = element.get_attribute("name")
                matches = re.match("^C:(\d+),R:\d+$", name)
                if matches:
                    seen_inputs.append(name)
                    column_index = matches[1]
                    return column_index, element
            # Check for the presence of an error dialog.
            sleep(0.1)
            if elapsed_time >= wait_time:
                raise TimeoutError()
            elapsed_time += DEFAULT_INTERVAL
        return None, None

    def fill_form_field(self, element, values):
        name = element.get_attribute("name")
        if name in values.keys():
            element.send_keys(values[name])
        element.send_keys(Keys.RETURN)

    def fill_datagrid_field(self, element, column_index, values):
        name = element.get_attribute("name")
        if column_index in values.keys():
            element.send_keys(values[column_index])
        element.send_keys(Keys.RETURN)

    def form_is_open(self):
        try:
            self.find_element_by_class_name("mode-ok")
            return True
        except NoSuchElementException:
            return False

    def datagrid_is_open(self):
        try:
            self.find_element_by_class_name("data-tbody input")
            return True
        except NoSuchElementException:
            return False

    def detect_active_input(self, seen_inputs):
        element = self.switch_to.active_element
        name = element.get_attribute("name")
        classes = element.get_attribute("class")
        if name and classes and name not in seen_inputs and "screen-field" in classes:
            return element

    def detect_error_dialog(self, seen_inputs):
        element = self.switch_to.active_element
        name = element.get_attribute("name")
        if name == "OK":
            error_message = self.wait_for_element_by_css_selector(
                ".pro-card-dialog.ui-draggable label",
                wait_time=1
            ).get_attribute("title")
            raise FormException(
                "{}: {}".format(seen_inputs[-1], error_message))

    def wait_for_clickable_element_by_class_name(self, value, wait_time=DEFAULT_WAIT_TIME):
        try:
            return WebDriverWait(self, wait_time).until(
                EC.element_to_be_clickable((By.CLASS_NAME, value)))
        except TimeoutException:
            raise TimeoutException("ID: " + value)

    def wait_for_clickable_element_by_id(self, value, wait_time=DEFAULT_WAIT_TIME):
        try:
            return WebDriverWait(self, wait_time).until(
                EC.element_to_be_clickable((By.ID, value)))
        except TimeoutException:
            raise TimeoutException("ID: " + value)

    def wait_for_clickable_element_by_name(self, value, wait_time=DEFAULT_WAIT_TIME):
        try:
            return WebDriverWait(self, wait_time).until(
                EC.element_to_be_clickable((By.NAME, value)))
        except TimeoutException:
            raise TimeoutException("Name: " + value)

    def wait_for_clickable_element_by_text(self, value, wait_time=DEFAULT_WAIT_TIME):
        locator = (By.XPATH, "//*[text()='{}']".format(value))
        try:
            return WebDriverWait(self, wait_time).until(
                EC.element_to_be_clickable(locator))
        except TimeoutException:
            raise TimeoutException("Text: " + value)

    def wait_for_element_by_css_selector(self, value, wait_time=DEFAULT_WAIT_TIME):
        try:
            return WebDriverWait(self, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, value)))
        except TimeoutException:
            raise TimeoutException("CSS selector: " + value)

    def wait_for_element_by_id(self, value, wait_time=DEFAULT_WAIT_TIME):
        try:
            return WebDriverWait(self, wait_time).until(
                EC.presence_of_element_located((By.ID, value)))
        except TimeoutException:
            raise TimeoutException("ID: " + value)

    def wait_for_element_by_name(self, value, wait_time=DEFAULT_WAIT_TIME):
        try:
            return WebDriverWait(self, wait_time).until(
                EC.presence_of_element_located((By.NAME, value)))
        except TimeoutException:
            raise TimeoutException("Name: " + value)

    def wait_for_element_by_text(self, value, wait_time=DEFAULT_WAIT_TIME):
        locator = (By.XPATH, "//[text()='{}']".format(value))
        try:
            return WebDriverWait(self, wait_time).until(
                EC.presence_of_element_located(locator))
        except TimeoutException:
            raise TimeoutException("Text: " + value)

    def wait_for_element_by_xpath(self, value, wait_time=DEFAULT_WAIT_TIME):
        try:
            return WebDriverWait(self, wait_time).until(
                EC.presence_of_element_located((By.XPATH, value)))
        except TimeoutException:
            raise TimeoutException("XPath: " + value)

    def wait_for_input_value(self, locator, value, wait_time=DEFAULT_WAIT_TIME):
        try:
            return WebDriverWait(self, wait_time).until(
                EC.text_to_be_present_in_element_value(locator, value))
        except TimeoutException:
            print("wait_time:", wait_time)
            raise TimeoutException(
                "Element: \"{}\", value: \"{}\"".format(locator, value))

    def wait_for_download(self, wait_time=DEFAULT_WAIT_TIME):
        existing_files = os.listdir(self.download_dir)
        for file in existing_files:
            os.unlink(os.path.join(self.download_dir, file))
        time_elapsed = 0
        while (time_elapsed < wait_time):
            files = os.listdir(self.download_dir)
            if files:
                if "tempFileName.ods" in files or "tempFileName.xlsx" in files:
                    return files[0]
            sleep(1)
            time_elapsed += 1
        raise Exception("Did not receive downloaded file")

    def wait_until(self, expected_condition, wait_time=DEFAULT_WAIT_TIME):
        return WebDriverWait(self, wait_time).until(expected_condition)

    def close_function(self):
        webdriver.ActionChains(self).send_keys(Keys.ESCAPE).perform()


class element_has_css_class(object):
    """An expectation for checking that an element has a particular CSS class.

    locator - used to find the element
    returns the WebElement once it has the particular CSS class
    """

    def __init__(self, element, css_class):
        self.element = element
        self.css_class = css_class

    def __call__(self, driver):
        # Finding the referenced element
        if self.css_class in self.element.get_attribute("class"):
            return self.element
        return False


class element_has_any_css_class(object):
    """An expectation for checking that an element has any of a given list of CSS classes.

    locator - used to find the element
    returns the WebElement once it has one of the given CSS classes
    """

    def __init__(self, locator, css_classes):
        self.locator = locator
        self.css_classes = css_classes

    def __call__(self, driver):
        # Finding the referenced element
        element = driver.find_element(*self.locator)
        # TDOD this intermittently triggers a StaleElementReferenceException
        element_css_classes = element.get_attribute("class")
        for css_class in self.css_classes:
            if css_class in element_css_classes:
                return element
        return False


class FormException(BaseException):
    pass
