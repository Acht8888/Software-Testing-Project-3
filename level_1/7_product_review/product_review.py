# -*- coding: utf-8 -*-
import unittest
import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class TestProductReview(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load CSV once and open browser ONCE (very fast)."""
        print("🚀 Starting Product Review Test Suite...")
        
        # Load CSV data
        csv_path = os.path.join(os.path.dirname(__file__), "product_review.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError("CSV not found")

        cls.test_data = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                cls.test_data.append(row)

        print(f"✅ Loaded {len(cls.test_data)} test cases")

        # Start browser only once
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.maximize_window()

        cls.wait = WebDriverWait(cls.driver, 15)
        cls.product_url = "https://ecommerce-playground.lambdatest.io/index.php?route=product/product&product_id=104"

        # Load product page once
        print("📄 Loading product page...")
        cls.driver.get(cls.product_url)
        cls.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)  # Wait for full page load including scripts
        
        # Close any popups
        try:
            close_buttons = cls.driver.find_elements(By.CSS_SELECTOR, ".close, .modal .btn-close, .popup-close")
            for btn in close_buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(0.3)
        except:
            pass

        # Scroll to review form
        cls.scroll_to_review_form()

    @classmethod
    def tearDownClass(cls):
        print("\n🛑 Closing browser...")
        cls.driver.quit()

    # ---------------------------------------------------------
    # Helper Functions
    # ---------------------------------------------------------

    @classmethod
    def scroll_to_review_form(cls):
        """Scroll to the review form on the product page."""
        print("📜 Scrolling to review form...")
        
        try:
            # Wait for form to be present
            review_form = cls.wait.until(
                EC.presence_of_element_located((By.ID, "form-review"))
            )
            
            # Scroll to form
            cls.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", 
                review_form
            )
            time.sleep(0.5)
            
            print("✅ Review form is now visible")
        except Exception as e:
            raise Exception(f"Could not find review form: {e}")

    def reset_form(self):
        """Clear form fields and any alerts before each test."""
        try:
            # Close any existing alerts first
            try:
                alerts = self.driver.find_elements(By.CSS_SELECTOR, ".alert-dismissible .close, .alert .close")
                for alert_close in alerts:
                    if alert_close.is_displayed():
                        alert_close.click()
                        time.sleep(0.2)
            except:
                pass
            
            # Scroll to form first
            review_form = self.driver.find_element(By.ID, "form-review")
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", 
                review_form
            )
            time.sleep(0.2)
            
            # Clear name field
            name_field = self.driver.find_element(By.ID, "input-name")
            self.driver.execute_script("arguments[0].value = '';", name_field)
            
            # Clear review field
            review_field = self.driver.find_element(By.ID, "input-review")
            self.driver.execute_script("arguments[0].value = '';", review_field)
            
            # Uncheck all ratings using JavaScript
            self.driver.execute_script("""
                var radios = document.querySelectorAll('input[name="rating"]');
                radios.forEach(function(radio) { radio.checked = false; });
            """)
        except Exception as e:
            print(f"⚠️ Warning: Could not reset form: {e}")

    def fill_field(self, locator, text):
        """Clear field + type text fast."""
        element = self.wait.until(EC.presence_of_element_located(locator))
        
        # Clear using JavaScript for reliability
        self.driver.execute_script("arguments[0].value = '';", element)
        
        if text:
            element.send_keys(text)

    def select_rating(self, rating_value):
        """Select star rating."""
        if not rating_value.strip():
            print("⏭️ Skipping rating (testing validation)")
            return
        
        try:
            # Use direct JavaScript to set the rating
            self.driver.execute_script(
                f"document.querySelector('input[name=\"rating\"][value=\"{rating_value}\"]').checked = true;"
            )
            print(f"⭐ Selected rating: {rating_value}")
        except Exception as e:
            print(f"⚠️ Could not select rating {rating_value}: {e}")

    def submit_review(self):
        """Submit the review form."""
        btn = self.wait.until(EC.element_to_be_clickable((By.ID, "button-review")))
        self.driver.execute_script("arguments[0].click();", btn)
        print("🚀 Form submitted")

    def get_alert_text(self):
        """Return success/error message text from alert that appears on same page."""
        try:
            # Wait for alert to appear - it shows up on the same page
            # Alert appears as: <div class="alert alert-danger alert-dismissible"> or alert-success
            alert_wait = WebDriverWait(self.driver, 5)
            
            # Try to find the alert (could be success or danger)
            alert = alert_wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger, .alert-success, .alert-warning"))
            )
            
            # Scroll to alert to make sure it's visible
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", alert)
            time.sleep(0.3)
            
            # Get the text (skip the icon)
            text = alert.text.strip()
            
            # Remove the "×" close button text if present
            text = text.replace("×", "").strip()
            
            print(f"📋 Alert found: {text[:100]}...")
            return text
            
        except Exception as e:
            print(f"⚠️ No alert found after 5 seconds: {e}")
            
            # Fallback: check if text is somewhere in the page
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                
                if "Thank you for your review" in page_text:
                    print("📋 Found success message in page text")
                    return "Thank you for your review. It has been submitted to the webmaster for approval."
                
                if "Warning:" in page_text:
                    print("📋 Found warning in page text")
                    # Try to extract the warning message
                    lines = page_text.split("\n")
                    for line in lines:
                        if "Warning:" in line:
                            return line.strip()
                
            except Exception as e2:
                print(f"⚠️ Fallback check failed: {e2}")
            
            return ""

    # ---------------------------------------------------------
    # Main Test Method
    # ---------------------------------------------------------

    def test_product_review_fast(self):
        """Ultra-fast DDT test execution."""
        for row in self.test_data:
            with self.subTest(TestCaseID=row["TestCaseID"]):
                print("\n" + "="*70)
                print(f"🧪 Running {row['TestCaseID']}")
                print(f"📋 Rating: {row['Rating'] or '(empty)'}")
                print(f"📋 Name: {len(row['Name'])} chars")
                print(f"📋 Review: {len(row['Review'])} chars")
                print(f"📋 Expected: {row['ExpectedResult'][:50]}...")
                print("="*70)

                # Reset form before each test (clear fields AND close any alerts)
                self.reset_form()
                time.sleep(0.3)

                # Fields
                name = row["Name"]
                review = row["Review"]
                rating = row["Rating"]
                expected = row["ExpectedResult"]

                # Fill form (rating first for speed)
                self.select_rating(rating)
                self.fill_field((By.ID, "input-name"), name)
                self.fill_field((By.ID, "input-review"), review)

                # Submit
                self.submit_review()
                
                # Wait for alert to appear on the same page
                time.sleep(2)

                # Get the alert message
                actual_message = self.get_alert_text()

                # Verify the result
                if "Thank you for your review" in expected:
                    # Success case
                    self.assertIn("Thank you for your review", actual_message,
                                f"❌ Expected success message but got: {actual_message}")
                    print("✅ Success message verified")
                    
                elif "Warning:" in expected:
                    # Error case - check for exact or partial match
                    if expected in actual_message:
                        print("✅ Exact error match found")
                    else:
                        # Check partial match (70% of significant words)
                        expected_words = [w.strip().lower() for w in expected.split() if len(w) > 3]
                        matches = sum(1 for word in expected_words if word in actual_message.lower())
                        match_ratio = matches / len(expected_words) if expected_words else 0
                        
                        self.assertGreaterEqual(match_ratio, 0.7,
                                              f"❌ Expected error not found.\nExpected: {expected}\nActual: {actual_message}\nMatch ratio: {match_ratio:.2f}")
                        print(f"✅ Partial error match found ({match_ratio*100:.0f}%)")
                else:
                    # Generic check
                    self.assertIn(expected, actual_message,
                                f"❌ Expected '{expected}' but got: {actual_message}")
                    print("✅ Message verified")

                print(f"✅ {row['TestCaseID']} PASSED\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)