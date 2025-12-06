# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, csv, os, random, string
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
            csv_path = os.path.join(current_dir, 'group_1.csv')
            
            # --- BƯỚC 1: ĐỌC DỮ LIỆU ---
            rows = []
            with open(csv_path, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for row in reader:
                    rows.append(row)

            # --- BƯỚC 2: CHẠY TEST ---
            for row in rows:
                tc_id = row.get('ID', '')
                test_type = row.get('type', '').strip()
                expected_res = row.get('expected result', '')
                
                # Logic sinh email random (giữ nguyên)
                if "register successful" in test_type:
                    allowed_chars = string.ascii_lowercase + string.digits
                    random_str = ''.join(random.choices(allowed_chars, k=10))
                    new_email = f"{random_str}@gmail.com"
                    row['email'] = new_email

                fname = row.get('First Name', '').strip()
                lname = row.get('Last Name', '').strip()
                email = row.get('email', '').strip()
                phone = row.get('telephone', '').strip()
                passwd = row.get('password', '').strip()
                confirm = row.get('Password Confirm', '').strip()
                privacy = row.get('Privacy Policy', '').strip()

                print(f"\n--- Running [{tc_id}] Type: {test_type} ---")

                driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/register")
                
                # --- ĐIỀN FORM ---
                if fname:
                    driver.find_element(By.ID, "input-firstname").clear()
                    driver.find_element(By.ID, "input-firstname").send_keys(fname)
                if lname:
                    driver.find_element(By.ID, "input-lastname").clear()
                    driver.find_element(By.ID, "input-lastname").send_keys(lname)
                if email:
                    driver.find_element(By.ID, "input-email").clear()
                    driver.find_element(By.ID, "input-email").send_keys(email)
                if phone:
                    driver.find_element(By.ID, "input-telephone").clear()
                    driver.find_element(By.ID, "input-telephone").send_keys(phone)
                if passwd:
                    driver.find_element(By.ID, "input-password").clear()
                    driver.find_element(By.ID, "input-password").send_keys(passwd)
                if confirm:
                    driver.find_element(By.ID, "input-confirm").clear()
                    driver.find_element(By.ID, "input-confirm").send_keys(confirm)
                
                # [SỬA ĐỔI 1] Logic tick Privacy:
                # Tick nếu CSV = TRUE HOẶC nếu là case "email fail 3" (để check trùng email)
                should_tick_privacy = False
                if privacy == "TRUE": 
                    should_tick_privacy = True
                elif "email fail 3" in test_type: # Bắt buộc tick để hiện lỗi trùng email
                    should_tick_privacy = True
                
                if should_tick_privacy:
                    try:
                        driver.find_element(By.XPATH, "//label[@for='input-agree']").click()
                    except: pass
                
                # Bấm Continue
                driver.find_element(By.XPATH, "//input[@value='Continue']").click()
                time.sleep(2)
                
                # --- VERIFY KẾT QUẢ ---
                if "register successful" in test_type:
                    try:
                        if "success" in driver.current_url or "Created" in driver.page_source:
                            print(f"   -> [{tc_id}] [PASS] Account Created Successfully!")
                            driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/logout")
                        else:
                            print(f"   -> [{tc_id}] [FAIL] Expected Success but Failed.")
                    except: pass

                elif "password" in test_type:
                    if expected_res == "Accepted":
                        self.check_no_error(driver, "//input[@id='input-password']/following-sibling::div", tc_id)
                    else:
                        found_pass = self.check_error_message(driver, "//input[@id='input-password']/following-sibling::div", expected_res, tc_id)
                        # [SỬA ĐỔI 2] Nếu tìm lỗi password mà không thấy -> Tức là web chấp nhận -> FAIL
                        if not found_pass:
                             # Thử check bên ô confirm
                             found_confirm = self.check_error_message(driver, "//input[@id='input-confirm']/following-sibling::div", expected_res, tc_id)
                             if not found_confirm:
                                 print(f"   -> [{tc_id}] [FAIL] Expected error '{expected_res}' but NO error appeared (Web accepted it!).")

                elif "email" in test_type:
                    if "email fail 1" in test_type:
                        is_valid = driver.execute_script("return document.getElementById('input-email').checkValidity()")
                        if is_valid == False:
                            print(f"   -> [{tc_id}] [PASS] HTML5 Validation blocked invalid email correctly.")
                        else:
                            print(f"   -> [{tc_id}] [FAIL] HTML5 Validation PASSED but expected FAIL.")
                    
                    elif "email fail 3" in test_type:
                        self.check_error_message(driver, "//div[contains(@class, 'alert-danger')]", expected_res, tc_id)
                    
                    else: 
                        if expected_res == "Accepted":
                            self.check_no_error(driver, "//input[@id='input-email']/following-sibling::div", tc_id)
                        else:
                            self.check_error_message(driver, "//input[@id='input-email']/following-sibling::div", expected_res, tc_id)

                elif "telephone" in test_type:
                    if expected_res == "Accepted":
                        self.check_no_error(driver, "//input[@id='input-telephone']/following-sibling::div", tc_id)
                    else:
                        self.check_error_message(driver, "//input[@id='input-telephone']/following-sibling::div", expected_res, tc_id)

                elif "missing" in test_type or "name" in test_type:
                    self.check_error_flexible(driver, expected_res, tc_id)

                elif "privacy" in test_type:
                    self.check_error_message(driver, "//div[contains(@class, 'alert-danger')]", expected_res, tc_id)

                elif "mismatch" in test_type:
                    self.check_error_message(driver, "//input[@id='input-confirm']/following-sibling::div", expected_res, tc_id)

            # --- GHI LẠI FILE CSV ---
            with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            print("\n[INFO] Da cap nhat email moi vao file CSV (San sang cho lan chay sau).")

        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file CSV.")
        except KeyError as e:
            print(f"Lỗi: File CSV thiếu cột {e}.")

    # --- HÀM PHỤ TRỢ ---
    def check_error_message(self, driver, xpath, expected, tc_id):
        try:
            actual = driver.find_element(By.XPATH, xpath).text
            if expected in actual:
                print(f"   -> [{tc_id}] [PASS] Error match found: {expected}")
                return True
            else:
                # Có lỗi hiện ra, nhưng nội dung sai
                print(f"   -> [{tc_id}] [FAIL] Mismatch! Expected: '{expected}' - Actual: '{actual}'")
                return True
        except NoSuchElementException:
            # Không thấy lỗi nào cả
            return False

    def check_no_error(self, driver, xpath, tc_id):
        try:
            driver.find_element(By.XPATH, xpath)
            print(f"   -> [{tc_id}] [FAIL] Error message appeared but expected none!")
        except NoSuchElementException:
            print(f"   -> [{tc_id}] [PASS] No error message (Accepted).")

    def check_error_flexible(self, driver, expected, tc_id):
        found = False
        locators = ["//input[@id='input-firstname']/following-sibling::div", 
                    "//input[@id='input-lastname']/following-sibling::div", 
                    "//input[@id='input-email']/following-sibling::div"]
        for xpath in locators:
            try:
                actual = driver.find_element(By.XPATH, xpath).text
                if expected in actual:
                    print(f"   -> [{tc_id}] [PASS] Error match found: {expected}")
                    found = True
                    break
            except: pass
        if not found: 
            print(f"   -> [{tc_id}] [FAIL] Could not find error message: '{expected}'")

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()