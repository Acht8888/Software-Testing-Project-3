# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.edge.service import Service 
import unittest, time, csv, os, random, string

class Register_Level2(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        driver_path = os.path.join(current_dir, 'msedgedriver.exe')
        
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Edge(service=service)
        
        self.driver.implicitly_wait(3)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []
    
    def test_register_level2(self):
        driver = self.driver
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(current_dir, 'register.csv')
            
            rows = []
            with open(csv_path, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for row in reader:
                    rows.append(row)

            for row in rows:
                tc_id = row.get('ID', '')
                test_type = row.get('type', '').strip()
                expected_res = row.get('expected result', '').strip()
                
                if "register successful" in test_type:
                    allowed_chars = string.ascii_lowercase + string.digits
                    random_str = ''.join(random.choices(allowed_chars, k=10))
                    new_email = f"{random_str}@gmail.com"
                    row['email'] = new_email
                    print(f"   -> [INFO] Generated NEW Email: {new_email}")

                fname = row.get('First Name', '').strip()
                lname = row.get('Last Name', '').strip()
                email = row.get('email', '').strip()
                phone = row.get('telephone', '').strip()
                passwd = row.get('password', '').strip()
                confirm = row.get('Password Confirm', '').strip()
                privacy = row.get('Privacy Policy', '').strip().upper()

                url_web = row.get('url')
                id_fn = row.get('fn_id')
                id_ln = row.get('ln_id')
                id_email = row.get('email_id')
                id_phone = row.get('phone_id')
                id_pass = row.get('pass_id')
                id_confirm = row.get('confirm_id')
                xp_privacy = row.get('privacy_xpath')
                xp_submit = row.get('submit_xpath')
                
                xp_error = row.get('error_xpath')

                print(f"\n--- Running [{tc_id}] Type: {test_type} ---")

                driver.get(url_web)
                
                if fname:
                    driver.find_element(By.ID, id_fn).clear()
                    driver.find_element(By.ID, id_fn).send_keys(fname)
                if lname:
                    driver.find_element(By.ID, id_ln).clear()
                    driver.find_element(By.ID, id_ln).send_keys(lname)
                if email:
                    driver.find_element(By.ID, id_email).clear()
                    driver.find_element(By.ID, id_email).send_keys(email)
                if phone:
                    driver.find_element(By.ID, id_phone).clear()
                    driver.find_element(By.ID, id_phone).send_keys(phone)
                if passwd:
                    driver.find_element(By.ID, id_pass).clear()
                    driver.find_element(By.ID, id_pass).send_keys(passwd)
                if confirm:
                    driver.find_element(By.ID, id_confirm).clear()
                    driver.find_element(By.ID, id_confirm).send_keys(confirm)
                
                should_click = False
                if privacy == "TRUE": should_click = True
                if "email fail 3" in test_type: should_click = True 
                
                if should_click:
                    try:
                        element = driver.find_element(By.XPATH, xp_privacy)
                        driver.execute_script("arguments[0].click();", element)
                    except: pass
                
                try:
                    driver.find_element(By.XPATH, xp_submit).click()
                except:
                    print(f"   -> [FAIL] Could not click Continue button!")
                
                time.sleep(2)
                
                
                if "register successful" in test_type:
                    try:
                        if "success" in driver.current_url or "Created" in driver.page_source:
                            print(f"   -> [{tc_id}] [PASS] Account Created Successfully!")
                            driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/logout")
                        else:
                            print(f"   -> [{tc_id}] [FAIL] Expected Success but Failed.")
                    except: 
                        print(f"   -> [{tc_id}] [FAIL] Error checking success condition.")

                elif xp_error == "HTML5_CHECK":
                    is_valid = driver.execute_script(f"return document.getElementById('{id_email}').checkValidity()")
                    if is_valid == False:
                        print(f"   -> [{tc_id}] [PASS] HTML5 Validation blocked invalid data.")
                    else:
                        print(f"   -> [{tc_id}] [FAIL] HTML5 Validation PASSED but expected FAIL.")

                elif expected_res == "Accepted":
                    if xp_error:
                        self.check_no_error(driver, xp_error, tc_id)
                    else:
                        self.check_no_error(driver, "//div[contains(@class, 'text-danger')]", tc_id)

                else:
                    if xp_error: 
                        self.check_error(driver, xp_error, expected_res, tc_id)
                    else:
                        print(f"   -> [{tc_id}] [FAIL] Missing 'error_xpath' in CSV for this Fail case.")

            with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print("\n[INFO] CSV File Updated.")

        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file CSV register.csv.")
        except KeyError as e:
            print(f"Lỗi: File CSV thiếu cột {e}.")

    def check_error(self, driver, xpath, expected, tc_id):
        try:
            actual = driver.find_element(By.XPATH, xpath).text
            if expected.strip() in actual.strip():
                print(f"   -> [{tc_id}] [PASS] Error match found: '{expected}'")
            else:
                print(f"   -> [{tc_id}] [FAIL] Mismatch! Expected: '{expected}' - Actual: '{actual}'")
        except NoSuchElementException:
            print(f"   -> [{tc_id}] [FAIL] Expected error '{expected}' but NO error message appeared.")

    def check_no_error(self, driver, xpath, tc_id):
        try:
            element = driver.find_element(By.XPATH, xpath)
            if element.is_displayed():
                 print(f"   -> [{tc_id}] [FAIL] Error message appeared: '{element.text}'")
            else:
                 print(f"   -> [{tc_id}] [PASS] No error message (Accepted).")
        except NoSuchElementException:
            print(f"   -> [{tc_id}] [PASS] No error message (Accepted).")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()