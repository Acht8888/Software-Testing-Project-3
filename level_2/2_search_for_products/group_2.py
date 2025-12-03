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
        csv_path = os.path.join(os.path.dirname(__file__), "group_2.csv")
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

    def test_search_ddt(self):
        driver = self.driver

        for row in self.test_data:
            with self.subTest(test_id=row.get("TestID", ""), data=row):
                url = row["URL"]
                search_box_selector = row["SearchBoxSelector"]
                search_button_selector = row["SearchButtonSelector"]
                result_selector = row["ResultSelector"]

                keyword = row["SearchKeyword"]
                unwanted_message = row["UnwantedMessage"]

                driver.get(url)

                search_input = driver.find_element(By.CSS_SELECTOR, search_box_selector)
                search_input.click()
                search_input.clear()
                search_input.send_keys(keyword)

                driver.find_element(By.CSS_SELECTOR, search_button_selector).click()
                time.sleep(2)

                result_element = driver.find_element(By.CSS_SELECTOR, result_selector)
                result_text = result_element.text

                try:
                    self.assertNotIn(unwanted_message, result_text)
                except AssertionError as e:
                    self.verificationErrors.append(
                        f"TestID {row.get('TestID')} failed: {str(e)} | Row: {row}"
                    )


if __name__ == "__main__":
    unittest.main()
