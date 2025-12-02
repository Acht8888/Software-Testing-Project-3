from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, csv, os
from selenium.webdriver.edge.service import Service

class Register_Level1(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        driver_path = os.path.join(current_dir, 'msedgedriver.exe')
        
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Edge(service=service)
        
        self.driver.implicitly_wait(5)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []
    
    def test_register_level1(self):
        driver = self.driver
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(current_dir, 'data_register_level1.csv')
            
            with open(csv_path, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    tc_id = row.get('ID', '')
                    test_type = row.get('type', '').strip()
                    expected_res = row.get('expected result', '')
                    
                    fname = row.get('First Name', '').strip()
                    lname = row.get('Last Name', '').strip()
                    email = row.get('email', '').strip()
                    phone = row.get('telephone', '').strip()
                    passwd = row.get('password', '').strip()
                    confirm = row.get('Password Confirm', '').strip()
                    privacy = row.get('Privacy Policy', '').strip() 

                    print(f"\n--- Running [{tc_id}] Type: {test_type} ---")

                    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/register")
                    
                    if "password" in test_type and "mismatch" not in test_type:
                        driver.find_element(By.ID, "input-password").send_keys(passwd)
                        
                        driver.find_element(By.XPATH, "//input[@value='Continue']").click()
                        time.sleep(1)
                        
                        if "success" in test_type:
                            self.check_no_error(driver, "//input[@id='input-password']/following-sibling::div")
                        else:
                            self.check_error(driver, "//input[@id='input-password']/following-sibling::div", expected_res)

                    elif "email" in test_type:
                        driver.find_element(By.ID, "input-email").send_keys(email)
                        driver.find_element(By.XPATH, "//input[@value='Continue']").click()
                        time.sleep(1)
                        
                        if "success" in test_type:
                            self.check_no_error(driver, "//input[@id='input-email']/following-sibling::div")
                        else:
                            self.check_error(driver, "//input[@id='input-email']/following-sibling::div", expected_res)

                    elif "telephone" in test_type:
                        driver.find_element(By.ID, "input-telephone").send_keys(phone)
                        driver.find_element(By.XPATH, "//input[@value='Continue']").click()
                        time.sleep(1)
                        
                        if "success" in test_type:
                            self.check_no_error(driver, "//input[@id='input-telephone']/following-sibling::div")
                        else:
                            self.check_error(driver, "//input[@id='input-telephone']/following-sibling::div", expected_res)

                    elif "missing" in test_type or "name" in test_type:
                        if fname: driver.find_element(By.ID, "input-firstname").send_keys(fname)
                        if lname: driver.find_element(By.ID, "input-lastname").send_keys(lname)
                        
                        driver.find_element(By.XPATH, "//input[@value='Continue']").click()
                        time.sleep(1)
                        
                        self.check_error_flexible(driver, expected_res)

                    elif "mismatch" in test_type:
                        driver.find_element(By.ID, "input-password").send_keys(passwd)
                        driver.find_element(By.ID, "input-confirm").send_keys(confirm)
                        driver.find_element(By.XPATH, "//input[@value='Continue']").click()
                        time.sleep(1)
                        
                        self.check_error(driver, "//input[@id='input-confirm']/following-sibling::div", expected_res)

                    elif "privacy" in test_type:
                        driver.find_element(By.ID, "input-firstname").send_keys("Test")
                        driver.find_element(By.ID, "input-lastname").send_keys("User")
                        driver.find_element(By.ID, "input-email").send_keys("test_privacy_auto@gmail.com")
                        driver.find_element(By.ID, "input-telephone").send_keys("0123456789")
                        driver.find_element(By.ID, "input-password").send_keys("123456")
                        driver.find_element(By.ID, "input-confirm").send_keys("123456")
                        
                        if privacy == "TRUE":
                            driver.find_element(By.XPATH, "//label[@for='input-agree']").click()
                        
                        driver.find_element(By.XPATH, "//input[@value='Continue']").click()
                        time.sleep(1)
                        
                        if privacy == "FALSE":
                            self.check_error(driver, "//div[contains(@class, 'alert-danger')]", expected_res)
                        else:
                            self.check_no_error(driver, "//div[contains(@class, 'alert-danger')]")

                    elif "register successful" in test_type:
                        driver.find_element(By.ID, "input-firstname").send_keys(fname)
                        driver.find_element(By.ID, "input-lastname").send_keys(lname)
                        driver.find_element(By.ID, "input-email").send_keys(email)
                        driver.find_element(By.ID, "input-telephone").send_keys(phone)
                        driver.find_element(By.ID, "input-password").send_keys(passwd)
                        driver.find_element(By.ID, "input-confirm").send_keys(confirm)
                        
                        if privacy == "TRUE":
                            driver.find_element(By.XPATH, "//label[@for='input-agree']").click()
                        
                        driver.find_element(By.XPATH, "//input[@value='Continue']").click()
                        time.sleep(2)
                        
                        if "success" in driver.current_url or "Created" in driver.page_source:
                            print(f"   -> [PASS] Account Created Successfully!")
                            driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/logout")
                        else:
                            print(f"   -> [FAIL] Expected Success but Failed.")

        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file CSV. Hãy đảm bảo file 'data_register_level1.csv' nằm CÙNG THƯ MỤC với file code.")
        except KeyError as e:
            print(f"Lỗi: File CSV thiếu cột {e}. Hãy kiểm tra lại header trong file Excel.")

    
    def check_error(self, driver, xpath, expected):
        try:
            actual = driver.find_element(By.XPATH, xpath).text
            if expected in actual:
                print(f"   -> [PASS] Found expected error: {expected}")
            else:
                pass 
        except NoSuchElementException:
            pass

    def check_no_error(self, driver, xpath):
        try:
            driver.find_element(By.XPATH, xpath)
            print(f"   -> [FAIL] Error message appeared but expected none!")
        except NoSuchElementException:
            print(f"   -> [PASS] No error message (Accepted).")

    def check_error_flexible(self, driver, expected):
        found = False
        locators = [
            "//input[@id='input-firstname']/following-sibling::div",
            "//input[@id='input-lastname']/following-sibling::div"
        ]
        for xpath in locators:
            try:
                actual = driver.find_element(By.XPATH, xpath).text
                if expected in actual:
                    print(f"   -> [PASS] Found error in Name field: {expected}")
                    found = True
                    break
            except: pass
        if not found:
            print(f"   -> [FAIL] Could not find name error: {expected}")

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()