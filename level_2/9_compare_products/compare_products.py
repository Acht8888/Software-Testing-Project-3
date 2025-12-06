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
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class TestCompareProductsLevel2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load CSV one time"""
        csv_path = os.path.join(os.path.dirname(__file__), "compare_products.csv")
        cls.test_data = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                cls.test_data.append(row)
        if not cls.test_data:
            raise RuntimeError("No rows found in compare_products.csv")

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.verificationErrors = []

    def tearDown(self):
        try:
            self.driver.quit()
        except:
            pass
        self.assertEqual([], self.verificationErrors)

    # ---------------------- Helper: Safe URL join ----------------------
    @staticmethod
    def join_url(base, path):
        return base.rstrip("/") + "/" + path.lstrip("/")

    # ---------------------- LOGIN ----------------------
    def dynamic_login(self, row):
        driver = self.driver
        driver.get(self.join_url(row["BaseURL"], row["LoginURL"]))

        # Điền email + password + submit
        driver.find_element(By.CSS_SELECTOR, row["EmailField"]).send_keys(row["Email"])
        driver.find_element(By.CSS_SELECTOR, row["PasswordField"]).send_keys(row["Password"])
        driver.find_element(By.CSS_SELECTOR, row["SubmitLogin"]).click()

        time.sleep(0.3)  # chờ page load

        # Kiểm tra xem có lỗi login không
        try:
            error_text = driver.find_element(By.CSS_SELECTOR, ".alert-danger").text
            if "No match" in error_text:
                print("❌ Login failed")
                return False
        except NoSuchElementException:
            # Không tìm thấy alert-danger → coi là login thành công
            pass

        
        return True

    # ---------------------- SELECT PRODUCTS ----------------------
    def select_products(self, row):
        driver = self.driver
        driver.get(self.join_url(row["BaseURL"], row["CategoryURL"]))

        actions = ActionChains(driver)
        num = int(row["NumProducts"])
        products = driver.find_elements(By.CSS_SELECTOR, "div.product-layout")

        for i in range(num):
            try:
                item = products[i]
                img = item.find_element(By.CSS_SELECTOR, ".image img")
                actions.move_to_element(img).perform()
                time.sleep(0.5)

                compare_btn = item.find_elements(By.CSS_SELECTOR, "div.product-action button")[3]
                driver.execute_script("arguments[0].click();", compare_btn)
                time.sleep(0.5)
            except Exception:
                pass

    # ---------------------- GO TO COMPARE PAGE ----------------------
    def go_to_compare(self, row):
        driver = self.driver
        driver.get(self.join_url(row["BaseURL"], row["CompareURL"]))
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    # ---------------------- REMOVE PRODUCTS ----------------------
    def remove_products(self):
        driver = self.driver
        while True:
            try:
                btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Remove"))
                )
                driver.execute_script("arguments[0].click();", btn)
                WebDriverWait(driver, 3).until(EC.staleness_of(btn))
            except:
                break

    # ---------------------- LOGOUT ----------------------
    def logout(self, row):
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
                EC.presence_of_element_located((By.CSS_SELECTOR, row["EmailField"]))
            )
        except Exception:
            pass

    # ---------------------- TEST CASE ----------------------
    def test_compare_products_L2(self):
        for row in self.test_data:
            with self.subTest(data=row):
                # 1. Login
                ok = self.dynamic_login(row)
                if not ok:
                    continue

                # 2. Select products
                self.select_products(row)

                # 3. Go to compare page
                self.go_to_compare(row)

                # 4. Verify expected result
                page = self.driver.find_element(By.TAG_NAME, "body").text
                for i in range(1, 6):
                    key = f"Expected{i}"
                    expected = row.get(key, "").strip()
                    if expected:
                        try:
                            self.assertIn(expected, page)
                        except AssertionError:
                            self.verificationErrors.append(f"[{row['Email']}] Missing {expected}")

                # 5. Remove products
                self.remove_products()

                # 6. Logout
                self.logout(row)


if __name__ == "__main__":
    unittest.main()

