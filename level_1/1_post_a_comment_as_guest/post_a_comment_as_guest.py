# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "post_a_comment_as_guest.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("No rows found in data_input.csv")

    def setUp(self):
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
            with self.subTest(test_id=row.get("TestID", ""), data=row):
                name = row["Name"]
                email = row["Email"]
                comment = row["Comment"]

                expected_cell = row["ExpectedResult"].strip()
                expected_messages = [
                    msg.strip()
                    for msg in expected_cell.split("||")
                    if msg.strip()
                ]

                driver.get(self.base_url + "index.php?route=extension/maza/blog/article&article_id=37")

                name_input = driver.find_element(By.ID, "input-name")
                name_input.clear()
                name_input.send_keys(name)

                email_input = driver.find_element(By.ID, "input-email")
                email_input.clear()
                email_input.send_keys(email)

                comment_input = driver.find_element(By.ID, "input-comment")
                comment_input.clear()
                comment_input.send_keys(comment)

                driver.find_element(By.ID, "button-comment").click()
                time.sleep(2)

                body_text = driver.find_element(By.TAG_NAME, "body").text
                
                for msg in expected_messages:
                    try:
                        self.assertIn(
                            msg,
                            body_text,
                            f"Expected message not found: '{msg}'",
                        )
                    except AssertionError as e:
                        self.verificationErrors.append(
                            f"TestID {row.get('TestID')} failed for expected '{msg}': {str(e)}"
                        )

if __name__ == "__main__":
    unittest.main()
