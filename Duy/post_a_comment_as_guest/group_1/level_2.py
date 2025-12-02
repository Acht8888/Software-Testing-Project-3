# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestPostCommentDDTLevel2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "level_2.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("No rows found in level_2.csv")

    def setUp(self):
        # WebDriver setup (Selenium 4 style)
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.verificationErrors = []

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def test_comment_ddt(self):
        driver = self.driver

        for row in self.test_data:
            with self.subTest(test_id=row.get("TestID", ""), data=row):
                url = row["URL"]

                name_selector = row["NameSelector"]
                email_selector = row["EmailSelector"]
                comment_selector = row["CommentSelector"]
                submit_selector = row["SubmitSelector"]
                result_selector = row["ResultSelector"]

                name_value = row["Name"]
                email_value = row["Email"]
                comment_value = row["Comment"]
                expected = row["ExpectedResult"]

                # 1. Open URL from data file (dynamic site URL)
                driver.get(url)

                # 2. Fill the form using dynamic selectors from CSV
                name_input = driver.find_element(By.CSS_SELECTOR, name_selector)
                name_input.clear()
                name_input.send_keys(name_value)

                email_input = driver.find_element(By.CSS_SELECTOR, email_selector)
                email_input.clear()
                email_input.send_keys(email_value)

                comment_input = driver.find_element(By.CSS_SELECTOR, comment_selector)
                comment_input.clear()
                comment_input.send_keys(comment_value)

                # 3. Submit comment with dynamic selector
                driver.find_element(By.CSS_SELECTOR, submit_selector).click()
                time.sleep(2)  # could be replaced by WebDriverWait

                # 4. Verify expected result text appears in element
                result_element = driver.find_element(By.CSS_SELECTOR, result_selector)
                result_text = result_element.text

                try:
                    self.assertIn(expected, result_text)
                except AssertionError as e:
                    # Save failure but continue with other rows
                    self.verificationErrors.append(
                        f"TestID {row.get('TestID')} failed: {str(e)}"
                    )


if __name__ == "__main__":
    unittest.main()
