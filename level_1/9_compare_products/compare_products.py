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
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


class TestProductCompare(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load test data from CSV once"""
        csv_path = os.path.join(os.path.dirname(__file__), "compare_products.csv")
        cls.test_data = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)
        if not cls.test_data:
            raise RuntimeError("No rows found in compare_products.csv")

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []

    def tearDown(self):
        try:
            self.driver.quit()
            print("Browser closed")
        except Exception as e:
            print(f"[Warning] Error quitting browser: {e}")
        self.assertEqual([], self.verificationErrors)

    # ----------------- Helper Methods -----------------
    def login(self):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=account/login")
        driver.find_element(By.ID, "input-email").send_keys("khangnha7@gmail.com")
        driver.find_element(By.ID, "input-password").send_keys("123456")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )
        print("Login successful")

    def select_products(self, row):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=product/category&path=57")
        actions = ActionChains(driver)
        num = int(row["NumProducts"])
        products = driver.find_elements(By.CSS_SELECTOR, "div.product-layout")

        for i in range(num):
            product = products[i]
            try:
                img = product.find_element(By.CSS_SELECTOR, ".image img")
                actions.move_to_element(img).perform()
                time.sleep(0.6)

                action_buttons = product.find_elements(By.CSS_SELECTOR, "div.product-action button")
                if len(action_buttons) < 4:
                    print(f"[Warning] Product {i+1}: action buttons not found (expected 4). Found: {len(action_buttons)}")
                    continue

                compare_btn = action_buttons[3]
                driver.execute_script("arguments[0].click();", compare_btn)
                print(f"Product {i+1} added to Compare")
                time.sleep(1)
            except Exception as e:
                print(f"[Warning] Could not select product {i+1}: {e}")

    def go_to_compare(self):
        driver = self.driver
        driver.get(self.base_url + "index.php?route=product/compare")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        print("Opened Compare Page")

    def remove_products(self, num_products):
        driver = self.driver
        for i in range(num_products):
            try:
                btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Remove"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                driver.execute_script("arguments[0].click();", btn)
                WebDriverWait(driver, 3).until(EC.staleness_of(btn))
                print(f"Removed product {i+1}")
            except Exception as e:
                
                break

    def logout(self):
        driver = self.driver
        try:
            account_menu = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]"))
            )
            ActionChains(driver).move_to_element(account_menu).perform()

            logout_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]/ul/li[6]/a/div/span"))
            )
            logout_btn.click()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "input-email"))
            )
            print("Logout successful")
        except Exception as e:
            pass

    # ----------------- Test Method -----------------
    def test_product_compare_ddt(self):
        driver = self.driver
        self.login()

        for row in self.test_data:
            with self.subTest(data=row):
                num_products = int(row["NumProducts"])
                print(f"\n--- Running subTest for {num_products} products ---")

                # 1. Select products
                print("Selecting products...")
                self.select_products(row)

                # 2. Go to Compare page
                print("Opening Compare Page...")
                self.go_to_compare()

                # 3. Verify Expected results
                print("Verifying expected products...")
                body_text = driver.find_element(By.TAG_NAME, "body").text
                for j in range(1, 5):
                    expected_key = f"Expected{j}"
                    expected = row.get(expected_key, "").strip()
                    if expected:
                        try:
                            self.assertIn(expected, body_text)
                            print(f"Found expected product: {expected}")
                        except AssertionError as e:
                            print(f"Missing expected product: {expected}")
                            self.verificationErrors.append(
                                f"Data row {row} failed for {expected_key}: {str(e)}"
                            )

                # 4. Remove products
                if num_products > 0:
                    print("Removing products...")
                    self.remove_products(num_products)

                # 5. Logout at the end of testcase
                print("Logging out...")
                self.logout()

                # Re-login for next subTest
                print("Logging in again for next subTest...")
                self.login()


if __name__ == "__main__":
    unittest.main()
