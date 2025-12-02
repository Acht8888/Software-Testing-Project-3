# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestGroup2Level1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "level_1.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("No rows found in group2_level_1.csv")

    def setUp(self):
        # WebDriver setup (no executable_path, Selenium 4-style)
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def test_comment_ddt(self):
        driver = self.driver

        for row in self.test_data:
            with self.subTest(test_id=row.get("TestID"), data=row):
                name = row["Name"]
                email = row["Email"]
                comment = row["Comment"]
                expected1 = row["ExpectedResult1"]
                expected2 = row["ExpectedResult2"]

                # 1. Open blog article page (fixed URL for Level 1)
                driver.get(
                    self.base_url
                    + "index.php?route=extension/maza/blog/article&article_id=37"
                )

                # 2. Fill the form (using fixed locators)
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

                # 4. Verify BOTH expected result texts appear
                body_text = driver.find_element(By.TAG_NAME, "body").text
                try:
                    self.assertIn(expected1, body_text)
                    self.assertIn(expected2, body_text)
                except AssertionError as e:
                    # Save failure but continue with other rows
                    self.verificationErrors.append(
                        f"TestID {row.get('TestID')} failed: {str(e)} | Row: {row}"
                    )


if __name__ == "__main__":
    unittest.main()
