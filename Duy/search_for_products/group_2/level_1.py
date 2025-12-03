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
            raise RuntimeError("No rows found in level_1.csv")

    def setUp(self):
        # WebDriver setup (Selenium 4-style)
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def test_search_default_list_ddt(self):
        driver = self.driver

        for row in self.test_data:
            with self.subTest(test_id=row.get("TestID", ""), data=row):
                keyword = row["SearchKeyword"]
                unwanted_message = row["UnwantedMessage"]

                # 1. Open home page (fixed URL for Level 1)
                driver.get(self.base_url)

                # 2. Focus and fill the search box (using fixed locator)
                search_input = driver.find_element(By.NAME, "search")
                search_input.click()
                search_input.clear()
                search_input.send_keys(keyword)

                # 3. Click the SEARCH button
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(2)  # simple wait; can be improved with WebDriverWait

                # 4. Verify the unwanted message is NOT shown
                body_text = driver.find_element(By.TAG_NAME, "body").text
                try:
                    self.assertNotIn(unwanted_message, body_text)
                except AssertionError as e:
                    # Save failure but continue with other rows
                    self.verificationErrors.append(
                        f"TestID {row.get('TestID')} failed: {str(e)} | Row: {row}"
                    )


if __name__ == "__main__":
    unittest.main()
