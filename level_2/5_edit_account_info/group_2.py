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


class TestEditAccountGroup2Level2(unittest.TestCase):

    ORIGINAL_EMAIL = "bangdeptrai13579@gmail.com"
    ORIGINAL_PASSWORD = "123456789"

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "group_2.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("group_2.csv is empty!")

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.verificationErrors = []

    def tearDown(self):
        try:
            self.driver.quit()
        finally:
            self.assertEqual([], self.verificationErrors)

    # -------------------------------------------------------------
    def login(self):
        driver = self.driver
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")

        driver.find_element(By.ID, "input-email").send_keys(self.ORIGINAL_EMAIL)
        driver.find_element(By.ID, "input-password").send_keys(self.ORIGINAL_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )

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

    # -------------------------------------------------------------
    def test_group2_level2(self):

        self.login()

        for row in self.test_data:
            with self.subTest(row=row):

                driver = self.driver

                # Open edit page from CSV
                driver.get(row["URL"])

                # Fill form using CSV selectors
                driver.find_element(By.CSS_SELECTOR, row["FirstNameSelector"]).clear()
                driver.find_element(By.CSS_SELECTOR, row["FirstNameSelector"]).send_keys(row["FirstName"])

                driver.find_element(By.CSS_SELECTOR, row["LastNameSelector"]).clear()
                driver.find_element(By.CSS_SELECTOR, row["LastNameSelector"]).send_keys(row["LastName"])

                driver.find_element(By.CSS_SELECTOR, row["EmailSelector"]).clear()
                driver.find_element(By.CSS_SELECTOR, row["EmailSelector"]).send_keys(row["Email"])

                driver.find_element(By.CSS_SELECTOR, row["TelephoneSelector"]).clear()
                driver.find_element(By.CSS_SELECTOR, row["TelephoneSelector"]).send_keys(row["Telephone"])

                driver.find_element(By.CSS_SELECTOR, row["SubmitSelector"]).click()

                # Read errors
                errors = []

                for e in driver.find_elements(By.CSS_SELECTOR, row["ErrorSelector"]):
                    t = e.text.strip()
                    if t:
                        errors.append(t)

                for a in driver.find_elements(By.CSS_SELECTOR, row["AlertSelector"]):
                    for line in a.text.strip().split("\n"):
                        if line.strip():
                            errors.append(line.strip())

                # Collect Expected
                expected_errors = [
                    row[k].strip()
                    for k in row
                    if k.startswith("Expected") and row[k].strip()
                ]

                # Validate
                for msg in expected_errors:
                    try:
                        self.assertIn(msg, errors)
                    except AssertionError:
                        self.verificationErrors.append(f"Row failed: {row}\nMissing: {msg}")

                self.logout()
                self.login()


if __name__ == "__main__":
    unittest.main()
