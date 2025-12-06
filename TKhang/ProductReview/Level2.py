# -*- coding: utf-8 -*-
import unittest
import csv
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


class TestProductReviewLevel2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("🚀 Starting Product Review Level 2 Test Suite...")

        # Load CSV
        csv_path = os.path.join(os.path.dirname(__file__), "product_review_2.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        cls.test_data = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                cls.test_data.append(row)

        print(f"✅ Loaded {len(cls.test_data)} test cases")

        # Initialize result tracking
        cls.test_results = {'passed': [], 'failed': [], 'errors': []}
        cls.start_time = datetime.now()

        # Start browser once
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)

        # Grab settings from CSV
        first = cls.test_data[0]
        cls.base_url = first['BaseURL']
        cls.product_url = f"{cls.base_url}/{first['ProductURL']}"
        cls.form_id = first['FormID']
        cls.name_field_id = first['NameFieldID']
        cls.review_field_id = first['ReviewFieldID']
        cls.submit_button_id = first['SubmitButtonID']

        print(f"🌐 URL: {cls.product_url}")

        # Load product page
        cls.load_product_page()

    @classmethod
    def tearDownClass(cls):
        cls.end_time = datetime.now()
        cls.generate_report()
        print("🛑 Closing browser...")
        cls.driver.quit()

    # ---------------------------------------------------------
    # PAGE LOAD
    # ---------------------------------------------------------

    @classmethod
    def load_product_page(cls):
        print("📄 Loading product page...")
        cls.driver.get(cls.product_url)

        # Wait for body
        cls.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)

        # Scroll to review form
        review_form = cls.wait.until(
            EC.visibility_of_element_located((By.ID, cls.form_id))
        )
        cls.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", review_form)
        print("✅ Form ready")

    # ---------------------------------------------------------
    # FORM RESET
    # ---------------------------------------------------------

    def reset_form(self):
        """Clear all fields + alerts"""
        try:
            # Remove alerts if visible
            alerts = self.driver.find_elements(By.CSS_SELECTOR, ".alert")
            for a in alerts:
                self.driver.execute_script("arguments[0].remove();", a)

        except Exception:
            pass

        # Clear fields
        self.driver.execute_script(f"document.getElementById('{self.name_field_id}').value = ''")
        self.driver.execute_script(f"document.getElementById('{self.review_field_id}').value = ''")

        # Uncheck all rating inputs
        self.driver.execute_script("""
            document.querySelectorAll("input[name='rating']").forEach(r => r.checked = false);
        """)

    # ---------------------------------------------------------
    # FIELD FILLING
    # ---------------------------------------------------------

    def fill_field(self, field_id, value):
        field = self.driver.find_element(By.ID, field_id)
        field.clear()
        if value:
            field.send_keys(value)

    # ---------------------------------------------------------
    # ⭐ RATING SELECTION (FIXED)
    # ---------------------------------------------------------

    def select_rating(self, rating_value):
        """Select star rating using label[for^='rating-{value}-']"""
        if not rating_value.strip():
            print("⏭️ Rating empty → skip")
            return

        selector = f"label[for^='rating-{rating_value}-']"

        try:
            label = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", label
            )
            self.driver.execute_script("arguments[0].click();", label)
            print(f"⭐ Rating selected = {rating_value}")

        except Exception as e:
            raise AssertionError(f"Could not select rating {rating_value}: {e}")

    # ---------------------------------------------------------
    # SUBMISSION
    # ---------------------------------------------------------

    def submit_review(self):
        btn = self.driver.find_element(By.ID, self.submit_button_id)
        self.driver.execute_script("arguments[0].click();", btn)

    # ---------------------------------------------------------
    # ALERT EXTRACTION
    # ---------------------------------------------------------

    def get_alert_text(self):
        """Return visible alert text"""
        try:
            alert = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert"))
            )
            text = alert.text.replace("×", "").strip()
            print(f"📢 Alert → {text}")
            return text

        except TimeoutException:
            print("⚠️ No alert found")
            return ""

    # ---------------------------------------------------------
    # RESULT VERIFICATION
    # ---------------------------------------------------------

    def verify_result(self, expected):
        actual = self.get_alert_text()

        # Success case
        if "Thank you for your review" in expected:
            assert "Thank you for your review" in actual, f"Expected success, got: {actual}"
            return

        # Error case
        assert expected in actual, f"Expected: {expected}\nActual: {actual}"

    # ---------------------------------------------------------
    # MAIN TEST LOOP
    # ---------------------------------------------------------

    def test_product_review_level2(self):
        for row in self.test_data:
            with self.subTest(row["TestCaseID"]):

                print("\n" + "="*65)
                print(f"🧪 TestCase → {row['TestCaseID']}")
                print("="*65)

                try:
                    self.reset_form()
                    time.sleep(0.2)

                    # Fill fields
                    self.select_rating(row["Rating"])
                    self.fill_field(self.name_field_id, row["Name"])
                    self.fill_field(self.review_field_id, row["Review"])

                    # Submit
                    self.submit_review()
                    time.sleep(1)

                    # Validate
                    self.verify_result(row["ExpectedResult"])

                    # Mark passed
                    TestProductReviewLevel2.test_results["passed"].append(row["TestCaseID"])
                    print(f"✅ {row['TestCaseID']} PASSED")

                except AssertionError as e:
                    TestProductReviewLevel2.test_results["failed"].append(f"{row['TestCaseID']} → {e}")
                    print(f"❌ FAIL: {e}")
                    raise

                except Exception as e:
                    TestProductReviewLevel2.test_results["errors"].append(f"{row['TestCaseID']} → {e}")
                    print(f"❌ ERROR: {e}")
                    raise

    # ---------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------

    @classmethod
    def generate_report(cls):
        print("\n" + "="*80)
        print("📊 FINAL REPORT - LEVEL 2")
        print("="*80)

        print("Passed:", cls.test_results["passed"])
        print("Failed:", cls.test_results["failed"])
        print("Errors:", cls.test_results["errors"])

        print("="*80)
        print("END OF REPORT\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)