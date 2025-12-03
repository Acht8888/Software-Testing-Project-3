# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class TestAddressBookLevel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load CSV one time"""
        csv_path = os.path.join(os.path.dirname(__file__), "group_2.csv")
        cls.test_data = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                cls.test_data.append(row)
        if not cls.test_data:
            raise RuntimeError("No rows found in group_2.csv")

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.verificationErrors = []

    def tearDown(self):
        try:
            self.driver.quit()
        except:
            pass
        self.assertEqual([], self.verificationErrors)

    # ---------------------- Helper: Safe URL join ----------------------
    @staticmethod
    def join_url(base, path):
        return base.rstrip("/") + "/" + path.lstrip("/")

    # ---------------------- LOGIN ----------------------
    def dynamic_login(self, row):
        driver = self.driver
        driver.get(self.join_url(row["BaseURL"], row["LoginURL"]))

        # Điền email + password + submit
        driver.find_element(By.CSS_SELECTOR, row["EmailField"]).send_keys(row["Email"])
        driver.find_element(By.CSS_SELECTOR, row["PasswordField"]).send_keys(row["Password"])
        driver.find_element(By.CSS_SELECTOR, row["SubmitLogin"]).click()

        time.sleep(0.3)  # chờ page load

        # Kiểm tra login có lỗi không
        try:
            error_text = driver.find_element(By.CSS_SELECTOR, ".alert-danger").text
            if "No match" in error_text:
                print("❌ Login failed")
                return False
        except NoSuchElementException:
            pass
        
        return True

    # ---------------------- GO TO ADDRESSBOOK ----------------------
    def go_to_addressbook(self, row):
        driver = self.driver
        driver.get(self.join_url(row["BaseURL"], row["AddressBookURL"]))
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "New Address"))
        )

    # ---------------------- CLICK NEW ADDRESS ----------------------
    def click_new_address(self):
        driver = self.driver
        btn = driver.find_element(By.LINK_TEXT, "New Address")
        btn.click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-firstname"))
        )

    # ---------------------- FILL ADDRESS FORM ----------------------
    def fill_address_form(self, row):
        driver = self.driver
        driver.find_element(By.ID, "input-firstname").clear()
        driver.find_element(By.ID, "input-firstname").send_keys(row.get("FirstName", "").strip())

        driver.find_element(By.ID, "input-lastname").clear()
        driver.find_element(By.ID, "input-lastname").send_keys(row.get("LastName", "").strip())

        driver.find_element(By.ID, "input-address-1").clear()
        driver.find_element(By.ID, "input-address-1").send_keys(row.get("Address1", "").strip())

        driver.find_element(By.ID, "input-city").clear()
        driver.find_element(By.ID, "input-city").send_keys(row.get("City", "").strip())

        driver.find_element(By.ID, "input-postcode").clear()
        driver.find_element(By.ID, "input-postcode").send_keys(row.get("PostCode", "").strip())

        country_val = row.get("Country", "").strip()
        if country_val and country_val != "(not selected)":
            Select(driver.find_element(By.ID, "input-country")).select_by_visible_text(country_val)
            time.sleep(0.5)

        region_val = row.get("Region/State", "").strip()
        if region_val and region_val != "(not selected)":
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "input-zone"))
            )
            Select(driver.find_element(By.ID, "input-zone")).select_by_visible_text(region_val)
            time.sleep(0.5)

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    # ---------------------- LOGOUT ----------------------
    def logout(self, row):
        driver = self.driver
        try:
            account_menu = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]"))
            )
            ActionChains(driver).move_to_element(account_menu).perform()

            logout_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]/ul/li[6]/a/div/span"))
            )
            logout_btn.click()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, row["EmailField"]))
            )
        except Exception:
            pass

    # ---------------------- TEST CASE ----------------------
    def test_add_addressbook_ddt_level2(self):
        for row in self.test_data:
            with self.subTest(data=row):
                ok = self.dynamic_login(row)
                if not ok:
                    continue

                self.go_to_addressbook(row)
                self.click_new_address()
                self.fill_address_form(row)
                time.sleep(0.5)

                body_text = self.driver.find_element(By.TAG_NAME, "body").text

                # ---------------------- Check all Expected fields dynamically ----------------------
                for i in range(1, 7):  # tối đa 6 expected (Group 1 → 6)
                    expected = row.get(f"Expected{i}", "").strip()
                    if expected:
                        try:
                            self.assertIn(expected, body_text)
                        except AssertionError:
                            self.verificationErrors.append(f"[{row.get('Email','NoEmail')}] Missing {expected}")

                self.logout(row)


if __name__ == "__main__":
    unittest.main()
