# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class TestReturnOrder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load test data from CSV once"""
        csv_path = os.path.join(os.path.dirname(__file__), "return_order.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("No rows found in return_order.csv")

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

    # ---------------- Helper Methods ----------------

    def login(self):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=account/login")
        driver.find_element(By.ID, "input-email").send_keys("khang@gmail.com")
        driver.find_element(By.ID, "input-password").send_keys("watdiw-boRnij-0cypsi")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )

    def go_to_return_form(self):
        """Navigate to Return Request form"""
        driver = self.driver

        driver.get(self.base_url + "index.php?route=account/return/add")

        # Wait until the First Name field is visible
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-firstname"))
        )

    def fill_return_form(self, row):
        driver = self.driver
        
        # Fill text inputs
        driver.find_element(By.ID, "input-firstname").clear()
        driver.find_element(By.ID, "input-firstname").send_keys(row["FirstName"])

        driver.find_element(By.ID, "input-lastname").clear()
        driver.find_element(By.ID, "input-lastname").send_keys(row["LastName"])

        driver.find_element(By.ID, "input-email").clear()
        driver.find_element(By.ID, "input-email").send_keys(row["Email"])

        driver.find_element(By.ID, "input-telephone").clear()
        driver.find_element(By.ID, "input-telephone").send_keys(row["Telephone"])

        driver.find_element(By.ID, "input-order-id").clear()
        driver.find_element(By.ID, "input-order-id").send_keys(row["OrderId"])

        driver.find_element(By.ID, "input-product").clear()
        driver.find_element(By.ID, "input-product").send_keys(row["ProductName"])

        driver.find_element(By.ID, "input-model").clear()
        driver.find_element(By.ID, "input-model").send_keys(row["ProductCode"])

        # Always choose a reason since we removed Reason column
        driver.find_element(By.CSS_SELECTOR, "input[value='1']").click()

        # Submit
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    # ---------------- Test Method ----------------

    def test_return_order_ddt(self):
        self.login()

        for row in self.test_data:
            with self.subTest(TestCase=row["TestCaseID"]):
                self.go_to_return_form()
                self.fill_return_form(row)

                time.sleep(1)

                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                expected = row["ExpectedResult"]

                try:
                    self.assertIn(expected, body_text)
                except AssertionError as e:
                    self.verificationErrors.append(
                        f"TestCase {row['TestCaseID']} FAILED → Expected: {expected}"
                    )


if __name__ == "__main__":
    unittest.main()
