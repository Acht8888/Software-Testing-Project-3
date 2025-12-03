# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestGroup1Level1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "level_1.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("No rows found in level_1.csv")

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def test_search_ddt(self):
        driver = self.driver

        for row in self.test_data:
            with self.subTest(test_id=row.get("TestID", ""), data=row):
                keyword = row["SearchKeyword"]
                expected = row["ExpectedResult"]

                driver.get(self.base_url)

                search_input = driver.find_element(By.NAME, "search")
                search_input.click()
                search_input.clear()
                search_input.send_keys(keyword)

                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(2)

                body_text = driver.find_element(By.TAG_NAME, "body").text
                try:
                    self.assertIn(expected, body_text)
                except AssertionError as e:
                    self.verificationErrors.append(
                        f"TestID {row.get('TestID')} failed: {str(e)} | Row: {row}"
                    )


if __name__ == "__main__":
    unittest.main()
