# -*- coding: utf-8 -*-
import unittest
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


class TestEditAccountAll(unittest.TestCase):

    ORIGINAL_EMAIL = "bangdeptrai13579@gmail.com"
    ORIGINAL_PASSWORD = "123456789"

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "edit_account_info.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("edit_account_all.csv is empty!")

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.errors = []

    def tearDown(self):
        try:
            self.driver.quit()
        except:
            pass
        self.assertEqual([], self.errors)

    # ----------------------------------
    # LOGIN
    # ----------------------------------
    def login(self, email=None):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=account/login")

        driver.find_element(By.ID, "input-email").send_keys(email or self.ORIGINAL_EMAIL)
        driver.find_element(By.ID, "input-password").send_keys(self.ORIGINAL_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )

    # ----------------------------------
    # OPEN EDIT ACCOUNT PAGE
    # ----------------------------------
    def go_to_edit(self):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=account/edit")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-firstname"))
        )

    # ----------------------------------
    # FILL EDIT FORM
    # ----------------------------------
    def fill_edit_form(self, row):
        d = self.driver

        d.find_element(By.ID, "input-firstname").clear()
        d.find_element(By.ID, "input-firstname").send_keys(row["FirstName"])

        d.find_element(By.ID, "input-lastname").clear()
        d.find_element(By.ID, "input-lastname").send_keys(row["LastName"])

        d.find_element(By.ID, "input-email").clear()
        d.find_element(By.ID, "input-email").send_keys(row["Email"])

        d.find_element(By.ID, "input-telephone").clear()
        d.find_element(By.ID, "input-telephone").send_keys(row["Telephone"])

        d.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    # ----------------------------------
    # CAPTURE SUCCESS OR ERROR MESSAGE
    # ----------------------------------
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

    # ----------------------------------
    # RESTORE ORIGINAL EMAIL
    # ----------------------------------
    def restore_email(self):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=account/edit")

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-email"))
        )

        email_field = driver.find_element(By.ID, "input-email")
        email_field.clear()
        email_field.send_keys(self.ORIGINAL_EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )

    # ----------------------------------
    # LOGOUT
    # ----------------------------------
    def logout(self):
        driver = self.driver
        try:
            account = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]")
                )
            )
            ActionChains(driver).move_to_element(account).perform()

            logout_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
            )
            logout_btn.click()
        except:
            pass

    # ----------------------------------
    # MAIN TEST
    # ----------------------------------
    def test_edit_account_all(self):
        self.login()

        for row in self.test_data:
            with self.subTest(row=row):

                self.go_to_edit()
                self.fill_edit_form(row)

                msg = self.get_message()

                # Collect all expected messages in CSV row
                expected_list = [
                    row.get("Expected", "").strip(),
                    row.get("Expected1", "").strip(),
                    row.get("Expected2", "").strip(),
                    row.get("Expected3", "").strip(),
                    row.get("Expected4", "").strip()
                ]

                # Filter out empty expected fields
                expected_list = [e for e in expected_list if e]

                # Validate all expected messages
                for expected in expected_list:
                    if expected not in msg:
                        self.errors.append(f"❌ Missing expected '{expected}' for row: {row}")

                # Restore email after SUCCESS
                if "Success" in msg:
                    self.restore_email()

                self.logout()
                self.login()


if __name__ == "__main__":
    unittest.main()
