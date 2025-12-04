# -*- coding: utf-8 -*-
import unittest
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class TestEditAccountLevel2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "group_1.csv")
        cls.test_data = []

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append({k: v.strip() for k, v in row.items()})

        if not cls.test_data:
            raise RuntimeError("group_1.csv is empty!")

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(5)
        self.verificationErrors = []

    def tearDown(self):
        try:
            self.driver.quit()
        except:
            pass
        self.assertEqual([], self.verificationErrors)

    # ---------------------------
    def login(self, row):
        driver = self.driver
        driver.get(row["BaseURL"] + "/" + row["LoginURL"])

        driver.find_element(By.CSS_SELECTOR, row["EmailField"]).send_keys(row["EmailLogin"])
        driver.find_element(By.CSS_SELECTOR, row["PasswordField"]).send_keys(row["PasswordLogin"])
        driver.find_element(By.CSS_SELECTOR, row["SubmitLogin"]).click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )

    # ---------------------------
    def go_edit_page(self, row):
        self.driver.get(row["BaseURL"] + "/index.php?route=account/edit")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-firstname"))
        )

    # ---------------------------
    def fill_edit(self, row):
        driver = self.driver

        driver.find_element(By.ID, "input-firstname").clear()
        driver.find_element(By.ID, "input-firstname").send_keys(row["FirstName"])

        driver.find_element(By.ID, "input-lastname").clear()
        driver.find_element(By.ID, "input-lastname").send_keys(row["LastName"])

        driver.find_element(By.ID, "input-email").clear()
        driver.find_element(By.ID, "input-email").send_keys(row["EmailEdit"])

        driver.find_element(By.ID, "input-telephone").clear()
        driver.find_element(By.ID, "input-telephone").send_keys(row["Telephone"])

        driver.find_element(By.CSS_SELECTOR, row["SubmitEdit"]).click()

    # ---------------------------
    def get_message(self):
        driver = self.driver
        try:
            msg = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".alert-success, .alert-danger")
                )
            )
            return msg.text.strip()
        except:
            return driver.find_element(By.TAG_NAME, "body").text

    # ---------------------------
    def restore_email(self, row):
        driver = self.driver
        driver.get(row["BaseURL"] + "/index.php?route=account/edit")

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input-email"))
        )

        email = driver.find_element(By.ID, "input-email")
        email.clear()
        email.send_keys(row["EmailLogin"])

        driver.find_element(By.CSS_SELECTOR, row["SubmitEdit"]).click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )

    # ---------------------------
    def logout(self):
        driver = self.driver
        try:
            logout_link = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
            )
            logout_link.click()
        except:
            pass

    # ---------------------------
    def test_level_2_ddt(self):
        for row in self.test_data:
            with self.subTest(row=row):
                self.login(row)
                self.go_edit_page(row)
                self.fill_edit(row)

                msg = self.get_message()

                if "Success" in msg:
                    self.restore_email(row)

                try:
                    self.assertIn(row["Expected"], msg)
                except AssertionError as e:
                    self.verificationErrors.append(f"Row failed: {row} — {e}")

                self.logout()


if __name__ == "__main__":
    unittest.main()
