# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Load test data from CSV once for all tests.
        CSV file must be in the same folder as this Test.py
        and have headers: Name,Email,Comment,ExpectedResult
        """
        csv_path = os.path.join(os.path.dirname(__file__), "data_input.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("No rows found in data_input.csv")

    def setUp(self):
        # WebDriver setup (no executable_path, Selenium 4-style)
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def test_comment_ddt(self):
        """
        Data-driven test:
        - For each row in data_input.csv:
          + Open article page
          + Fill Name, Email, Comment from CSV
          + Submit
          + Check ExpectedResult from CSV appears on page
        """
        driver = self.driver

        for row in self.test_data:
            with self.subTest(data=row):
                name = row["Name"]
                email = row["Email"]
                comment = row["Comment"]
                expected = row["ExpectedResult"]

                # 1. Open blog article page
                driver.get(
                    self.base_url
                    + "index.php?route=extension/maza/blog/article&article_id=37"
                )

                # 2. Fill the form (new Selenium 4 style)
                name_input = driver.find_element(By.ID, "input-name")
                name_input.clear()
                name_input.send_keys(name)

                email_input = driver.find_element(By.ID, "input-email")
                email_input.clear()
                email_input.send_keys(email)

                comment_input = driver.find_element(By.ID, "input-comment")
                comment_input.clear()
                comment_input.send_keys(comment)

                # 3. Submit comment
                driver.find_element(By.ID, "button-comment").click()
                time.sleep(2)  # simple wait; can be improved with WebDriverWait

                # 4. Verify expected result text appears
                body_text = driver.find_element(By.TAG_NAME, "body").text
                try:
                    self.assertIn(expected, body_text)
                except AssertionError as e:
                    # Save failure but continue with other rows
                    self.verificationErrors.append(
                        f"Data row {row} failed: {str(e)}"
                    )

    # === Helper methods (updated for Selenium 4) ===
    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to.alert
        except NoAlertPresentException:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True


if __name__ == "__main__":
    unittest.main()
