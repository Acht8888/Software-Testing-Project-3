# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


class TestEditAccount(unittest.TestCase):

    ORIGINAL_EMAIL = "bangdeptrai13579@gmail.com"
    ORIGINAL_PASSWORD = "123456789"

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "group_1.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("group_1.csv is empty!")

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

    # ---------------------------
    # Login
    # ---------------------------
    def login(self, email=None):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=account/login")

        driver.find_element(By.ID, "input-email").send_keys(email or self.ORIGINAL_EMAIL)
        driver.find_element(By.ID, "input-password").send_keys(self.ORIGINAL_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )

    # ---------------------------
    # Go to Edit Account
    # ---------------------------
    def go_to_edit_account(self):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=account/edit")

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-firstname"))
        )

    # ---------------------------
    # Fill Edit Form
    # ---------------------------
    def fill_edit_form(self, row):
        driver = self.driver

        driver.find_element(By.ID, "input-firstname").clear()
        driver.find_element(By.ID, "input-firstname").send_keys(row["FirstName"])

        driver.find_element(By.ID, "input-lastname").clear()
        driver.find_element(By.ID, "input-lastname").send_keys(row["LastName"])

        driver.find_element(By.ID, "input-email").clear()
        driver.find_element(By.ID, "input-email").send_keys(row["Email"])

        driver.find_element(By.ID, "input-telephone").clear()
        driver.find_element(By.ID, "input-telephone").send_keys(row["Telephone"])

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    # ---------------------------
    # Get success or error text clearly
    # ---------------------------
    def get_message(self):
        driver = self.driver
        try:
            alert = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".alert-success, .alert-danger")
                )
            )
            return alert.text.strip()
        except:
            return driver.find_element(By.TAG_NAME, "body").text

    # ---------------------------
    # Restore Email (only if update succeeded)
    # ---------------------------
    def restore_email(self):
        driver = self.driver

        # Navigate back to edit page
        driver.get(self.base_url + "index.php?route=account/edit")

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-email"))
        )

        email = driver.find_element(By.ID, "input-email")
        email.clear()
        email.send_keys(self.ORIGINAL_EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Ensure restore actually succeeded
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )

    # ---------------------------
    # Logout
    # ---------------------------
    def logout(self):
        driver = self.driver
        try:
            account_hover = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]")
                )
            )
            ActionChains(driver).move_to_element(account_hover).perform()

            logout_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(., 'Logout')]")
                )
            )
            logout_btn.click()
        except:
            pass

    # ---------------------------
    # MAIN TEST
    # ---------------------------
    def test_edit_account_ddt(self):
        self.login()

        for row in self.test_data:
            with self.subTest(data=row):
                self.go_to_edit_account()
                self.fill_edit_form(row)

                msg = self.get_message()
                expected = row["Expected"]

                # Restore email ONLY when success happens
                if "Success" in msg:
                    self.restore_email()

                try:
                    self.assertIn(expected, msg)
                except AssertionError as e:
                    self.verificationErrors.append(f"Failed row: {row} — {e}")

                self.logout()
                self.login()


if __name__ == "__main__":
    unittest.main()
