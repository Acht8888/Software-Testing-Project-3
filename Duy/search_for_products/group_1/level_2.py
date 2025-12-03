# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestGroup1Level2(unittest.TestCase):

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
        # WebDriver setup (Selenium 4-style)
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
                # Dynamic items (Level 2)
                url = row["URL"]
                search_box_selector = row["SearchBoxSelector"]
                search_button_selector = row["SearchButtonSelector"]
                result_selector = row["ResultSelector"]

                # Test data
                keyword = row["SearchKeyword"]
                expected = row["ExpectedResult"]

                # 1. Open page from data file
                driver.get(url)

                # 2. Locate and fill the search box using dynamic selector
                search_input = driver.find_element(By.CSS_SELECTOR, search_box_selector)
                search_input.click()
                search_input.clear()
                search_input.send_keys(keyword)

                # 3. Click the SEARCH button using dynamic selector
                driver.find_element(By.CSS_SELECTOR, search_button_selector).click()
                time.sleep(2)  # simple wait; can be improved with WebDriverWait

                # 4. Verify expected result text appears in the result area
                result_element = driver.find_element(By.CSS_SELECTOR, result_selector)
                result_text = result_element.text

                try:
                    self.assertIn(expected, result_text)
                except AssertionError as e:
                    # Save failure but continue with other rows
                    self.verificationErrors.append(
                        f"TestID {row.get('TestID')} failed: {str(e)} | Row: {row}"
                    )


if __name__ == "__main__":
    unittest.main()
