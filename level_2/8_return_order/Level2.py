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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class TestReturnOrderLevel2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load test data once"""
        csv_path = os.path.join(os.path.dirname(__file__), "return_order_2.csv")
        cls.test_data = []

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.test_data.append(row)

        if not cls.test_data:
            raise RuntimeError("CSV empty — no test data found")

        print(f"✅ Loaded {len(cls.test_data)} test cases")
        
        # Initialize test results tracking
        cls.test_results = {
            'passed': [],
            'failed': [],
           # 'errors': []
        }
        cls.start_time = datetime.now()

    def setUp(self):
        """Initialize browser for each test"""
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 15)

    def tearDown(self):
        """Clean up after each test"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Browser closed")
            except Exception as e:
                print(f"⚠️ Warning: Error quitting browser: {e}")

    @classmethod
    def tearDownClass(cls):
        """Generate test report after all tests complete"""
        cls.end_time = datetime.now()
        cls.generate_report()

    # --------------------------------------------------
    # Helper methods
    # --------------------------------------------------

    def login(self, row):
        """Log in to the account using data from CSV"""
        try:
            base_url = row['BaseURL']
            login_url = row['LoginURL']
            
            self.driver.get(f"{base_url}/{login_url}")

            email_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, row['EmailField']))
            )
            email_field.clear()
            email_field.send_keys(row['LoginEmail'])

            password_field = self.driver.find_element(By.CSS_SELECTOR, row['PasswordField'])
            password_field.clear()
            password_field.send_keys(row['LoginPassword'])

            submit_btn = self.driver.find_element(By.CSS_SELECTOR, row['SubmitLogin'])
            submit_btn.click()

            self.wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
            )

            print("✅ Login successful")
            return True

        except TimeoutException:
            self.fail("Login failed: Timeout waiting for page elements")
            return False
        except Exception as e:
            self.fail(f"Login failed: {str(e)}")
            return False

    def open_return_form(self, row):
        """Navigate to return form with retry logic"""
        max_retries = 3
        base_url = row['BaseURL']
        return_url = row['ReturnFormURL']
        
        for attempt in range(max_retries):
            try:
                print(f"📄 Loading return form (attempt {attempt + 1}/{max_retries})...")
                
                self.driver.get(f"{base_url}/{return_url}")
                
                self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                firstname_selector = row['FirstNameField']
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, firstname_selector))
                )
                
                firstname_field = self.driver.find_element(By.CSS_SELECTOR, firstname_selector)
                if firstname_field.is_displayed() and firstname_field.is_enabled():
                    print("✅ Return form loaded successfully")
                    return True
                    
            except TimeoutException as e:
                print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    print(f"❌ Current URL: {self.driver.current_url}")
                    print(f"❌ Page title: {self.driver.title}")
                    self.fail(f"Failed to load return form after {max_retries} attempts")
                    return False
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                self.fail(f"Failed to load return form: {str(e)}")
                return False
        
        return False

    def fill_form(self, row):
        """Fill the return form with test data from CSV"""
        try:
            test_case_id = row["TestCaseID"]
            select_return_reason = row['SelectReturnReason'].lower() == 'yes'

            # Map CSV columns to form fields
            fields = {
                row['FirstNameField']: row['FirstName'],
                row['LastNameField']: row['LastName'],
                row['EmailInputField']: row['Email'],
                row['TelephoneField']: row['Telephone'],
                row['OrderIdField']: row['OrderId'],
                row['ProductNameField']: row['ProductName'],
                row['ProductCodeField']: row['ProductCode']
            }

            # Fill all text fields
            for selector, value in fields.items():
                try:
                    element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    element.clear()
                    time.sleep(0.2)
                    if value:  # Only send keys if value is not empty
                        element.send_keys(value)
                        time.sleep(0.2)
                except Exception as e:
                    print(f"⚠️ Warning: Could not fill {selector}: {e}")

            # Select return reason if required
            if select_return_reason:
                try:
                    reason_selector = row['ReturnReasonField']
                    reason_radio = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, reason_selector))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", reason_radio)
                    time.sleep(0.3)
                    
                    try:
                        reason_radio.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", reason_radio)
                    
                    print(f"✅ Return reason selected for {test_case_id}")
                except (TimeoutException, NoSuchElementException) as e:
                    print(f"⚠️ Warning: Could not select return reason: {e}")
            else:
                print(f"⏭️ Skipping return reason selection for {test_case_id}")

            # Submit form
            try:
                submit_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                time.sleep(0.3)
                submit_btn.click()
            except:
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                self.driver.execute_script("arguments[0].click();", submit_btn)

            # Wait for page response
            time.sleep(2)
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

        except Exception as e:
            print(f"❌ Error in fill_form: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            self.fail(f"Failed to fill form: {str(e)}")

    def verify_result(self, expected_result, test_case_id):
        """Verify the result on the page"""
        try:
            time.sleep(1)
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            expected = expected_result.strip()

            error_keywords = [
                "must be between",
                "must be greater",
                "does not appear to be valid",
                "required!",
                "You must select"
            ]

            SUCCESS_MESSAGES = [
                "Your return request has been submitted",
                "Thank you for submitting your return request",
                "Your request has been sent to the relevant department",
                "successfully submitted"
            ]

            is_error_case = any(keyword.lower() in expected.lower() for keyword in error_keywords)
            has_success_message = any(
                success_msg.lower() in page_text.lower()
                for success_msg in SUCCESS_MESSAGES
            )

            if is_error_case:
                # Check if form was submitted when it shouldn't have been
                if has_success_message:
                    self.fail(
                        f"❌ VALIDATION BUG DETECTED!\n"
                        f"Expected validation error: {expected}\n"
                        f"But form was submitted successfully.\n"
                        f"The website failed to validate the input properly."
                    )
                
                if expected in page_text:
                    print(f"✅ Error validation passed for {test_case_id}: {expected}")
                else:
                    expected_words = [word for word in expected.split() if len(word) > 3]
                    partial_match = all(word in page_text for word in expected_words)
                    
                    if partial_match:
                        print(f"✅ Partial error match found for {test_case_id}")
                    else:
                        self.fail(
                            f"Expected error message not found.\n"
                            f"Expected: {expected}\n"
                            f"Page text snippet: {page_text[:500]}"
                        )

            else:
                self.assertTrue(
                    has_success_message,
                    f"Expected success message not found for {test_case_id}.\n"
                    f"Expected indicators: {SUCCESS_MESSAGES}\n"
                    f"Page content snippet: {page_text[:500]}"
                )
                print(f"✅ Success validation passed for {test_case_id}")

        except AssertionError:
            raise
        except Exception as e:
            self.fail(f"Failed to verify result: {str(e)}")

    # --------------------------------------------------
    # Main test method
    # --------------------------------------------------

    def test_return_order_level2(self):
        """Data-driven test for return order functionality - Level 2"""
        # Login once at the start
        if self.test_data:
            self.login(self.test_data[0])

        for row in self.test_data:
            with self.subTest(TestCase=row["TestCaseID"]):
                print(f"\n{'='*60}")
                print(f"Running: {row['TestCaseID']}")
                print(f"Expected: {row['Expected'][:50]}...")
                print(f"{'='*60}")

                try:
                    self.open_return_form(row)
                    self.fill_form(row)
                    self.verify_result(row['Expected'], row['TestCaseID'])
                    
                    # Record passed test
                    TestReturnOrderLevel2.test_results['passed'].append({
                        'test_case_id': row['TestCaseID'],
                        'expected': row['Expected']
                    })
                    
                    print(f"✅ {row['TestCaseID']} PASSED\n")

                except AssertionError as e:
                    # Record failed test
                    TestReturnOrderLevel2.test_results['failed'].append({
                        'test_case_id': row['TestCaseID'],
                        'expected': row['Expected'],
                        'reason': str(e)
                    })
                    
                    print(f"❌ {row['TestCaseID']} FAILED")
                    print(f"Reason: {str(e)}\n")
                    raise

                except Exception as e:
                    # Record error
                    TestReturnOrderLevel2.test_results['errors'].append({
                        'test_case_id': row['TestCaseID'],
                        'expected': row['Expected'],
                        'reason': str(e)
                    })
                    
                    print(f"❌ {row['TestCaseID']} ERROR")
                    print(f"Reason: {str(e)}\n")
                    raise

    # --------------------------------------------------
    # Report generation
    # --------------------------------------------------

    @classmethod
    def generate_report(cls):
        """Generate comprehensive test report"""
        duration = cls.end_time - cls.start_time
        total_tests = len(cls.test_data)
        passed = len(cls.test_results['passed'])
        failed = len(cls.test_results['failed'])
       # errors = len(cls.test_results['errors'])
        
        # Console report
        print("\n" + "="*80)
        print("🔍 TEST EXECUTION REPORT - LEVEL 2")
        print("="*80)
        print(f"Test Suite: Return Order Functionality (Level 2)")
        print(f"Start Time: {cls.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time: {cls.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        print(f"\nTotal Test Cases: {total_tests}")
        print(f"✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
       # print(f"⚠️  Errors: {errors} ({errors/total_tests*100:.1f}%)")
        
        # Passed tests summary
        if cls.test_results['passed']:
            print(f"\n{'='*80}")
            print(f"✅ PASSED TEST CASES ({passed})")
            print(f"{'='*80}")
            for i, test in enumerate(cls.test_results['passed'], 1):
                print(f"{i}. {test['test_case_id']}")
                print(f"   Expected: {test['expected'][:60]}...")
        
        # Failed tests summary
        if cls.test_results['failed']:
            print(f"\n{'='*80}")
            print(f"❌ FAILED TEST CASES ({failed})")
            print(f"{'='*80}")
            for i, test in enumerate(cls.test_results['failed'], 1):
                print(f"{i}. {test['test_case_id']}")
                print(f"   Expected: {test['expected'][:60]}...")
                print(f"   Reason: {test['reason'][:100]}...")
        
        # Error tests summary
        if cls.test_results['errors']:
            print(f"\n{'='*80}")
           # print(f"⚠️  ERROR TEST CASES ({errors})")
            print(f"{'='*80}")
            for i, test in enumerate(cls.test_results['errors'], 1):
                print(f"{i}. {test['test_case_id']}")
                print(f"   Expected: {test['expected'][:60]}...")
                print(f"   Reason: {test['reason'][:100]}...")
        
        print(f"\n{'='*80}")
        print("END OF REPORT")
        print("="*80 + "\n")
        
        # Save report to file
        cls.save_report_to_file(duration, total_tests, passed, failed, )
    
    @classmethod
    def save_report_to_file(cls, duration, total_tests, passed, failed, errors):
        """Save detailed report to file"""
        report_path = os.path.join(os.path.dirname(__file__), "test_report_level2.txt")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("TEST EXECUTION REPORT - LEVEL 2\n")
            f.write("="*80 + "\n")
            f.write(f"Test Suite: Return Order Functionality (Level 2)\n")
            f.write(f"Start Time: {cls.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End Time: {cls.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration}\n")
            f.write(f"\nTotal Test Cases: {total_tests}\n")
            f.write(f"Passed: {passed} ({passed/total_tests*100:.1f}%)\n")
            f.write(f"Failed: {failed} ({failed/total_tests*100:.1f}%)\n")
            f.write(f"Errors: {errors} ({errors/total_tests*100:.1f}%)\n")
            
            if cls.test_results['passed']:
                f.write(f"\n{'='*80}\n")
                f.write(f"PASSED TEST CASES ({passed})\n")
                f.write(f"{'='*80}\n")
                for i, test in enumerate(cls.test_results['passed'], 1):
                    f.write(f"{i}. {test['test_case_id']}\n")
                    f.write(f"   Expected: {test['expected']}\n\n")
            
            if cls.test_results['failed']:
                f.write(f"\n{'='*80}\n")
                f.write(f"FAILED TEST CASES ({failed})\n")
                f.write(f"{'='*80}\n")
                for i, test in enumerate(cls.test_results['failed'], 1):
                    f.write(f"{i}. {test['test_case_id']}\n")
                    f.write(f"   Expected: {test['expected']}\n")
                    f.write(f"   Reason: {test['reason']}\n\n")
            
            if cls.test_results['errors']:
                f.write(f"\n{'='*80}\n")
                f.write(f"ERROR TEST CASES ({errors})\n")
                f.write(f"{'='*80}\n")
                for i, test in enumerate(cls.test_results['errors'], 1):
                    f.write(f"{i}. {test['test_case_id']}\n")
                    f.write(f"   Expected: {test['expected']}\n")
                    f.write(f"   Reason: {test['reason']}\n\n")
            
            f.write(f"\n{'='*80}\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"📄 Detailed report saved to: {report_path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)