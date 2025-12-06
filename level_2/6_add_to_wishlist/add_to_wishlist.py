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


class TestWishlistLevel2(unittest.TestCase):

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
        self.verificationErrors = []

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    # ------------------ Helper ------------------

    @staticmethod
    def join(base, path):
        return base.rstrip("/") + "/" + path.lstrip("/")

    def dynamic_login(self, row):
        d = self.driver
        d.get(self.join(row["BaseURL"], row["LoginURL"]))

        d.find_element(By.CSS_SELECTOR, row["EmailField"]).send_keys(row["Email"])
        d.find_element(By.CSS_SELECTOR, row["PasswordField"]).send_keys(row["Password"])
        d.find_element(By.CSS_SELECTOR, row["SubmitLogin"]).click()

        WebDriverWait(d, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='logout']")
            )
        )

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
        time.sleep(0.5)

        # wishlist button index = 1
        buttons = tile.find_elements(By.CSS_SELECTOR, "div.product-action button")
        wishlist_btn = buttons[1]

        d.execute_script("arguments[0].click();", wishlist_btn)
        time.sleep(1)

    def go_to_wishlist(self, row):
        self.driver.get(self.join(row["BaseURL"], row["WishlistURL"]))
        time.sleep(1)

    def clear_wishlist(self):
        d = self.driver
        try:
            buttons = d.find_elements(By.CSS_SELECTOR, "a.btn-light.btn-sm.text-danger")
            for btn in buttons:
                d.execute_script("arguments[0].click();", btn)
                time.sleep(0.7)
            time.sleep(1)
        except:
            pass

    def logout(self):
        driver = self.driver
        try:
            hover = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[6]")
                )
            )
            ActionChains(driver).move_to_element(hover).perform()

            logout_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Logout')]"))
            )
            logout_btn.click()
        except:
            pass


    # ------------------ Test ------------------

    def test_wishlist_level2(self):
        d = self.driver

        for row in self.test_data:
            with self.subTest(row=row):

                self.dynamic_login(row)

                product = row["ProductName"].strip()
                expected = row["Expected"].strip()

                self.go_to_wishlist(row)

                # Case 1: no product added
                if product == "":
                    self.go_to_wishlist(row)
                    body = d.find_element(By.TAG_NAME, "body").text

                    if expected not in body:
                        self.verificationErrors.append(
                            f"FAILED: expected '{expected}' but not found"
                        )

                    self.logout()
                    continue

                # Case 2: add product
                self.add_to_wishlist(row)
                self.go_to_wishlist(row)

                body = d.find_element(By.TAG_NAME, "body").text
                if expected not in body:
                    self.verificationErrors.append(
                        f"FAILED: expected '{expected}' but not found"
                    )

                # Cleanup
                time.sleep(3)
                self.clear_wishlist()
                self.logout()


if __name__ == "__main__":
    unittest.main()
