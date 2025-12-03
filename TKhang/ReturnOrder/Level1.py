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
from webdriver_manager.chrome import ChromeDriverManager


class TestReturnOrder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Load test data once """
        csv_path = os.path.join(os.path.dirname(__file__), "return_order.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("CSV empty — no test data found")

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

    # --------------------------------------------------
    # Helper methods
    # --------------------------------------------------

    def login(self):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=account/login")

        driver.find_element(By.ID, "input-email").send_keys("khang@gmail.com")
        driver.find_element(By.ID, "input-password").send_keys("watdiw-boRnij-0cypsi")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )

    def open_return_form(self):
        """Direct link to return form"""
        self.driver.get(self.base_url + "index.php?route=account/return/add")

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-firstname"))
        )

    def fill_form(self, row):
        d = self.driver

        d.find_element(By.ID, "input-firstname").clear()
        d.find_element(By.ID, "input-firstname").send_keys(row["FirstName"])

        d.find_element(By.ID, "input-lastname").clear()
        d.find_element(By.ID, "input-lastname").send_keys(row["LastName"])

        d.find_element(By.ID, "input-email").clear()
        d.find_element(By.ID, "input-email").send_keys(row["Email"])

        d.find_element(By.ID, "input-telephone").clear()
        d.find_element(By.ID, "input-telephone").send_keys(row["Telephone"])

        d.find_element(By.ID, "input-order-id").clear()
        d.find_element(By.ID, "input-order-id").send_keys(row["OrderId"])

        d.find_element(By.ID, "input-product").clear()
        d.find_element(By.ID, "input-product").send_keys(row["ProductName"])

        d.find_element(By.ID, "input-model").clear()
        d.find_element(By.ID, "input-model").send_keys(row["ProductCode"])

        # Always select a reason (required)
        try:
            d.find_element(By.CSS_SELECTOR, "input[name='return_reason_id']").click()
        except:
            pass

        d.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    # --------------------------------------------------
    # Test method with robust ExpectedResult handling
    # --------------------------------------------------

    def test_return_order_ddt(self):
        self.login()

        VALID_SUCCESS_MESSAGES = [
            "Your return request",
            "return request has been",
            "Thank you for submitting your return request",
            "Your return has been submitted",
            "success",
        ]

        for row in self.test_data:
            with self.subTest(TestCase=row["TestCaseID"]):

                self.open_return_form()
                self.fill_form(row)

                time.sleep(1)

                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                expected = row["ExpectedResult"].strip()

                try:
                    if "must" in expected or "required" in expected or "valid" in expected:
                        # Error case → must match EXACT text
                        self.assertIn(expected, page_text)

                    else:
                        # Success case → allow multiple possible success messages
                        matched = any(success_msg.lower() in page_text.lower()
                                      for success_msg in VALID_SUCCESS_MESSAGES)

                        self.assertTrue(
                            matched,
                            f"Expected success but none of the known success messages appeared.\n\nPage:\n{page_text}"
                        )

                except AssertionError as e:
                    self.verificationErrors.append(
                        f"[{row['TestCaseID']}] FAILED → {expected}"
                    )


if __name__ == "__main__":
    unittest.main()
