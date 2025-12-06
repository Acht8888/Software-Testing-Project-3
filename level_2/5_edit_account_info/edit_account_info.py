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
        csv_path = os.path.join(os.path.dirname(__file__), "edit_account_info.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("edit_account_info.csv is empty!")

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
            hover = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]")
                )
            )
            ActionChains(driver).move_to_element(hover).perform()

            logout_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Logout')]"))
            )
            logout_btn.click()
        except:
            pass

    # -------------------------------------------------------------
    def restore_email(self):
        driver = self.driver
        driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/edit")

        email_field = driver.find_element(By.ID, "input-email")
        email_field.clear()
        email_field.send_keys(self.ORIGINAL_EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )

    # -------------------------------------------------------------
    def test_group2_level2(self):

        self.login()

        for row in self.test_data:
            with self.subTest(row=row):

                driver = self.driver
                driver.get(row["URL"])

                # Fill form
                driver.find_element(By.CSS_SELECTOR, row["FirstNameSelector"]).clear()
                driver.find_element(By.CSS_SELECTOR, row["FirstNameSelector"]).send_keys(row["FirstName"])

                driver.find_element(By.CSS_SELECTOR, row["LastNameSelector"]).clear()
                driver.find_element(By.CSS_SELECTOR, row["LastNameSelector"]).send_keys(row["LastName"])

                driver.find_element(By.CSS_SELECTOR, row["EmailSelector"]).clear()
                driver.find_element(By.CSS_SELECTOR, row["EmailSelector"]).send_keys(row["Email"])

                driver.find_element(By.CSS_SELECTOR, row["TelephoneSelector"]).clear()
                driver.find_element(By.CSS_SELECTOR, row["TelephoneSelector"]).send_keys(row["Telephone"])

                driver.find_element(By.CSS_SELECTOR, row["SubmitSelector"]).click()

                # Collect errors
                errors = []

                # Inline field errors
                for e in driver.find_elements(By.CSS_SELECTOR, row["ErrorSelector"]):
                    t = e.text.strip()
                    if t:
                        errors.append(t)

                # Alert errors
                for a in driver.find_elements(By.CSS_SELECTOR, row["AlertSelector"]):
                    for line in a.text.strip().split("\n"):
                        if line.strip():
                            errors.append(line.strip())

                # Read success alert
                success = False
                for a in driver.find_elements(By.CSS_SELECTOR, ".alert-success"):
                    if "Success" in a.text:
                        success = True

                # Expected list
                expected_errors = []
                for k, v in row.items():
                    if not k:
                        continue
                    if k.startswith("Expected") and v and v.strip():
                        expected_errors.append(v.strip())

                # Validate
                for msg in expected_errors:
                    if msg not in errors:
                        self.verificationErrors.append(f"Row failed: {row}\nMissing: {msg}")

                # Reset email if updated
                if success:
                    self.restore_email()

                self.logout()
                self.login()


if __name__ == "__main__":
    unittest.main()
