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


class TestEditAccountGroup4Level2(unittest.TestCase):

    ORIGINAL_EMAIL = "bangdeptrai13579@gmail.com"
    ORIGINAL_PASSWORD = "123456789"

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "group_4.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("group_4.csv is empty!")

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

    # --------------------------------------------------------------
    def login(self):
        driver = self.driver
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")

        driver.find_element(By.ID, "input-email").send_keys(self.ORIGINAL_EMAIL)
        driver.find_element(By.ID, "input-password").send_keys(self.ORIGINAL_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )

    def fill_form_level2(self, row):
        driver = self.driver

        driver.find_element(By.CSS_SELECTOR, row["FirstNameSelector"]).clear()
        driver.find_element(By.CSS_SELECTOR, row["FirstNameSelector"]).send_keys(row["FirstName"])

        driver.find_element(By.CSS_SELECTOR, row["LastNameSelector"]).clear()
        driver.find_element(By.CSS_SELECTOR, row["LastNameSelector"]).send_keys(row["LastName"])

        driver.find_element(By.CSS_SELECTOR, row["EmailSelector"]).clear()
        driver.find_element(By.CSS_SELECTOR, row["EmailSelector"]).send_keys(row["Email"])

        driver.find_element(By.CSS_SELECTOR, row["TelephoneSelector"]).clear()
        driver.find_element(By.CSS_SELECTOR, row["TelephoneSelector"]).send_keys(row["Telephone"])

        driver.find_element(By.CSS_SELECTOR, row["SubmitSelector"]).click()

    def collect_errors_level2(self, row):
        driver = self.driver
        errors = []

        # inline field-level errors
        inline_errors = driver.find_elements(By.CSS_SELECTOR, row["ErrorSelector"])
        for e in inline_errors:
            txt = e.text.strip()
            if txt:
                errors.append(txt)

        # alert-danger box
        alert_boxes = driver.find_elements(By.CSS_SELECTOR, row["AlertSelector"])
        for a in alert_boxes:
            for line in a.text.split("\n"):
                line = line.strip()
                if line:
                    errors.append(line)

        return errors

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
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Logout')]"))
            )
            logout_btn.click()
        except:
            pass

    # ---------------------------------------------------------------
    def test_group4_level2(self):
        self.login()

        for row in self.test_data:
            with self.subTest(row=row):

                # 1. Navigate to edit page
                self.driver.get(row["URL"])

                # 2. Fill form
                self.fill_form_level2(row)

                # 3. Actual errors
                actual_errors = self.collect_errors_level2(row)

                # 4. Expected messages
                expected_errors = [
                    row[key].strip()
                    for key in row
                    if key.startswith("Expected") and row[key].strip()
                ]

                # 5. Validate
                for expected_msg in expected_errors:
                    if expected_msg not in actual_errors:
                        self.verificationErrors.append(
                            f"Missing: {expected_msg} | Row: {row}"
                        )

                # 6. Logout + login
                self.logout()
                self.login()


if __name__ == "__main__":
    unittest.main()
