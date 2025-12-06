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


class TestWishlistLevel2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "add_to_wishlist.csv")
        cls.test_data = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("CSV is empty!")

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

    # ---------- Helper: Combine URLs ----------
    @staticmethod
    def join(base, path):
        return base.rstrip("/") + "/" + path.lstrip("/")

    # ---------- LOGIN ----------
    def dynamic_login(self, row):
        d = self.driver
        d.get(self.join(row["BaseURL"], row["LoginURL"]))

        d.find_element(By.CSS_SELECTOR, row["EmailField"]).send_keys(row["Email"])
        d.find_element(By.CSS_SELECTOR, row["PasswordField"]).send_keys(row["Password"])
        d.find_element(By.CSS_SELECTOR, row["SubmitLogin"]).click()

        # Detect login failure
        try:
            alert = d.find_element(By.CSS_SELECTOR, ".alert-danger").text
            if "No match" in alert:
                print("❌ Login failed")
                return False
        except:
            pass

        return True

    # ---------- ADD TO WISHLIST ----------
    def add_to_wishlist(self, row):
        product = row["ProductName"].strip()
        d = self.driver

        d.get(self.join(row["BaseURL"], row["CategoryURL"]))
        actions = ActionChains(d)

        tile = WebDriverWait(d, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//a[contains(text(), '{product}')]/ancestor::div[contains(@class,'product-thumb')]")
            )
        )

        img = tile.find_element(By.CSS_SELECTOR, ".image img")
        actions.move_to_element(img).perform()

        # wishlist button = index 1
        buttons = tile.find_elements(By.CSS_SELECTOR, "div.product-action button")
        wishlist_btn = buttons[1]

        d.execute_script("arguments[0].click();", wishlist_btn)

    # ---------- OPEN WISHLIST ----------
    def open_wishlist(self, row):
        self.driver.get(self.join(row["BaseURL"], row["WishlistURL"]))

    # ---------- REMOVE ALL ITEMS ----------
    def clear_wishlist(self):
        d = self.driver
        try:
            while True:
                btn = d.find_element(By.CSS_SELECTOR, "a.btn-light.btn-sm.text-danger")
                d.execute_script("arguments[0].click();", btn)
        except:
            pass

    # ---------- LOGOUT ----------
    def logout(self, row):
        d = self.driver
        try:
            menu = WebDriverWait(d, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]"))
            )
            ActionChains(d).move_to_element(menu).perform()

            logout = WebDriverWait(d, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]/ul/li[6]/a/div/span"))
            )
            logout.click()

            WebDriverWait(d, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, row["EmailField"]))
            )
        except:
            pass

    # ---------- TEST CASE ----------
    def test_wishlist_L2(self):
        for row in self.test_data:
            with self.subTest(row=row):
                ok = self.dynamic_login(row)
                if not ok:
                    continue

                product = row["ProductName"].strip()
                expected = row["Expected"].strip()

                self.open_wishlist(row)

                # Case 1: no product added
                if product == "":
                    self.open_wishlist(row)
                    body = self.driver.find_element(By.TAG_NAME, "body").text

                    if expected not in body:
                        self.verificationErrors.append(f"Missing expected: {expected}")

                else:
                    # Case 2: add product
                    self.add_to_wishlist(row)
                    self.open_wishlist(row)

                    body = self.driver.find_element(By.TAG_NAME, "body").text
                    if expected not in body:
                        self.verificationErrors.append(f"Missing expected: {expected}")

                # After each row: cleanup + logout
                time.sleep(4)
                self.clear_wishlist()
                self.logout(row)


if __name__ == "__main__":
    unittest.main()
