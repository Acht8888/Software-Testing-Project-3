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


class TestAddressBook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load test data from CSV once"""
        csv_path = os.path.join(os.path.dirname(__file__), "add_edit_address_book.csv")
        cls.test_data = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)
        if not cls.test_data:
            raise RuntimeError("No rows found in add_edit_address_book.csv")

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []

    def tearDown(self):
        try:
            self.driver.quit()
        except:
            pass
        self.assertEqual([], self.verificationErrors)

    # ----------------- Helper Methods -----------------
    def login(self):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=account/login")
        driver.find_element(By.ID, "input-email").send_keys("khangnha7@gmail.com")
        driver.find_element(By.ID, "input-password").send_keys("123456")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )

    def go_to_addressbook(self):
        driver = self.driver
        addr_link = driver.find_element(By.LINK_TEXT, "Address Book")
        addr_link.click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "New Address"))
        )

    def click_new_address(self):
        driver = self.driver
        new_addr_btn = driver.find_element(By.LINK_TEXT, "New Address")
        new_addr_btn.click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-firstname"))
        )

    def fill_address_form(self, row):
        driver = self.driver
        # Chỉ bỏ qua company, address_2, default address
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

        # Select Country
        country_val = row.get("Country", "").strip()
        country_selected = False
        if country_val and country_val != "(not selected)":
            try:
                Select(driver.find_element(By.ID, "input-country")).select_by_visible_text(country_val)
                time.sleep(0.5)
                country_selected = True
            except:
                # Nếu country không tồn tại trên dropdown, bỏ qua
                country_selected = False

        # Select Region/State chỉ khi country hợp lệ
        region_val = row.get("Region/State", "").strip()
        if region_val and region_val != "(not selected)" and country_selected:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "input-zone"))
                )
                Select(driver.find_element(By.ID, "input-zone")).select_by_visible_text(region_val)
                time.sleep(0.5)
            except:
                pass  # Nếu region không tồn tại, bỏ qua

        # Click Continue
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    def logout(self):
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
                EC.presence_of_element_located((By.ID, "input-email"))
            )
        except Exception:
            pass

    # ----------------- Test Method -----------------
    def test_add_addressbook_ddt(self):
        driver = self.driver
        self.login()

        for row in self.test_data:
            with self.subTest(data=row):
                self.go_to_addressbook()
                self.click_new_address()
                self.fill_address_form(row)
                time.sleep(1)

                body_text = driver.find_element(By.TAG_NAME, "body").text

                # Lặp qua tất cả cột Expected* để assert nhiều lỗi cùng lúc
                for key in row:
                    if key.startswith("Expected") and row[key].strip():
                        expected = row[key].strip()
                        try:
                            self.assertIn(expected, body_text)
                        except AssertionError as e:
                            self.verificationErrors.append(
                                f"Data row {row} failed for {key}: {str(e)}"
                            )

                self.logout()
                self.login()


if __name__ == "__main__":
    unittest.main()