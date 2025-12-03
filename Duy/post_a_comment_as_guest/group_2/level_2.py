# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestGroup2Level2(unittest.TestCase):

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
            with self.subTest(test_id=row.get("TestID"), data=row):
                url = row["URL"]
                name_selector = row["NameSelector"]
                email_selector = row["EmailSelector"]
                comment_selector = row["CommentSelector"]
                submit_selector = row["SubmitSelector"]
                result_selector = row["ResultSelector"]

                name = row["Name"]
                email = row["Email"]
                comment = row["Comment"]
                expected1 = row["ExpectedResult1"]
                expected2 = row["ExpectedResult2"]

                driver.get(url)

                name_input = driver.find_element(By.CSS_SELECTOR, name_selector)
                name_input.clear()
                name_input.send_keys(name)

                email_input = driver.find_element(By.CSS_SELECTOR, email_selector)
                email_input.clear()
                email_input.send_keys(email)

                comment_input = driver.find_element(By.CSS_SELECTOR, comment_selector)
                comment_input.clear()
                comment_input.send_keys(comment)

                driver.find_element(By.CSS_SELECTOR, submit_selector).click()
                time.sleep(2)

                result_element = driver.find_element(By.CSS_SELECTOR, result_selector)
                result_text = result_element.text

                try:
                    self.assertIn(expected1, result_text)
                    self.assertIn(expected2, result_text)
                except AssertionError as e:
                    self.verificationErrors.append(
                        f"TestID {row.get('TestID')} failed: {str(e)} | Row: {row}"
                    )


if __name__ == "__main__":
    unittest.main()
