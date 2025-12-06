# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class TestWishlistLevel1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "add_to_wishlist.csv")
        cls.test_data = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    # ------------------ Helper ------------------

    def login(self):
        d = self.driver
        d.get(self.base_url + "index.php?route=account/login")
        d.find_element(By.ID, "input-email").send_keys("bangdeptrai13579@gmail.com")
        d.find_element(By.ID, "input-password").send_keys("123456789")
        d.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(d, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))

    def add_to_wishlist(self, product_name):
        d = self.driver
        d.get(self.base_url + "index.php?route=product/category&path=57")

        actions = ActionChains(d)

        tile = WebDriverWait(d, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//a[contains(text(), '{product_name}')]/ancestor::div[contains(@class,'product-thumb')]")
            )
        )

        img = tile.find_element(By.CSS_SELECTOR, ".image img")

        actions.move_to_element(img).perform()
        time.sleep(0.5)

        # IMPORTANT → wishlist button is index 1
        buttons = tile.find_elements(By.CSS_SELECTOR, "div.product-action button")
        wishlist_btn = buttons[1]

        d.execute_script("arguments[0].click();", wishlist_btn)
        time.sleep(1)

    def go_to_wishlist(self):
        self.driver.get(self.base_url + "index.php?route=account/wishlist")
        time.sleep(1)

    def clear_wishlist(self):
        d = self.driver
        try:
            # correct selector for remove button on wishlist page
            remove_buttons = d.find_elements(
                By.CSS_SELECTOR,
                "a.btn-light.btn-sm.text-danger"
            )
            for btn in remove_buttons:
                d.execute_script("arguments[0].click();", btn)
                time.sleep(0.7)

            # small wait so page refreshes
            time.sleep(1)

        except Exception as e:
            print("Clear wishlist error:", e)


    # ------------------ Test ------------------

    def test_wishlist_level1(self):
        d = self.driver
        self.login()

        for row in self.test_data:
            with self.subTest(row=row):
                product = row["ProductName"].strip()
                expected = row["Expected"].strip()

                self.go_to_wishlist()

                # Case 1: No product added
                if product == "":
                    self.go_to_wishlist()
                    body = d.find_element(By.TAG_NAME, "body").text

                    if expected not in body:
                        self.verificationErrors.append(
                            f"FAILED: expected '{expected}' but not found"
                        )

                    # Logout after each test case
                    self.driver.get(self.base_url + "index.php?route=account/logout")
                    self.login()
                    continue

                # Case 2: Add 1 product
                self.add_to_wishlist(product)
                self.go_to_wishlist()

                body = d.find_element(By.TAG_NAME, "body").text
                if expected not in body:
                    self.verificationErrors.append(
                        f"FAILED: expected '{expected}' but not found"
                    )

                # Cleanup
                time.sleep(4)
                self.clear_wishlist()

                # Logout after each test case
                self.driver.get(self.base_url + "index.php?route=account/logout")
                self.login()




if __name__ == "__main__":
    unittest.main()
