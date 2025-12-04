# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, csv, os, random, string
from selenium.webdriver.edge.service import Service

class TC_Login_Level1(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        driver_path = os.path.join(current_dir, 'msedgedriver.exe')
        
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Edge(service=service)
        
        self.driver.implicitly_wait(5)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
    
    def test_login_level1(self):
        driver = self.driver
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(current_dir, 'group_1.csv')
            
            # --- BƯỚC 1: ĐỌC DỮ LIỆU VÀO BỘ NHỚ ---
            rows = []
            with open(csv_path, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for row in reader:
                    rows.append(row)

            for row in rows:
                tc_id = row['ID'] 
                test_type = row['type']
                expected_res = row['expected result'] 

                if test_type == "fail":
                    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                    new_email = f"{random_str}@gmail.com"
                    row['email'] = new_email
                    print(f"   -> [INFO] Generated NEW random email for {tc_id}: {new_email}")
                
                email_data = row['email'] if row['email'] else ""
                password_data = row['password'] if row['password'] else ""
                
                if not email_data and not password_data: continue

                print(f"\n--- Running [{tc_id}] Type: {test_type} | Email: {email_data} ---")

                driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")
                
                if test_type == "locked":
                    print(f"   -> [{tc_id}] Dang thu dang nhap nhieu lan de khoa tai khoan...")
                    actual_text = ""
                    
                    for i in range(6):
                        driver.find_element(By.ID, "input-email").clear()
                        driver.find_element(By.ID, "input-email").send_keys(email_data)
                        driver.find_element(By.ID, "input-password").clear()
                        
                        if i < 5:
                            driver.find_element(By.ID, "input-password").send_keys("wrong_pass_123")
                        else:
                            driver.find_element(By.ID, "input-password").send_keys(password_data)

                        driver.find_element(By.XPATH, "//input[@value='Login']").click()
                        time.sleep(1) 
                        
                        try:
                            msg = driver.find_element(By.XPATH, "//div[contains(@class, 'alert-danger')]").text
                            if "exceeded" in msg:
                                actual_text = msg
                                print(f"   -> [{tc_id}] Da xuat hien thong bao khoa o lan thu {i+1}")
                                break 
                        except:
                            pass 
                    
                    try:
                        self.assertIn(expected_res, actual_text)
                        print(f"   -> [{tc_id}] [PASS] Account Locked message found.")
                    except AssertionError as e:
                        self.verificationErrors.append(str(e))
                        print(f"   -> [{tc_id}] [FAIL] Expected Lock message but got: '{actual_text}'")

                elif test_type == "success":
                    driver.find_element(By.ID, "input-email").clear()
                    driver.find_element(By.ID, "input-email").send_keys(email_data)
                    driver.find_element(By.ID, "input-password").clear()
                    driver.find_element(By.ID, "input-password").send_keys(password_data)
                    driver.find_element(By.XPATH, "//input[@value='Login']").click()
                    time.sleep(1)

                    try: 
                        self.assertTrue(self.is_element_present(By.XPATH, "//aside[@id='column-right']//a[contains(@href, 'route=account/logout')]"))
                        print(f"   -> [{tc_id}] [PASS] Login Success (Logout button found)")
                    except AssertionError as e: 
                        self.verificationErrors.append(str(e))
                        print(f"   -> [{tc_id}] [FAIL] Expected Success but Logout button NOT found")
                    
                    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/logout")
                    
                elif test_type == "fail":
                    driver.find_element(By.ID, "input-email").clear()
                    driver.find_element(By.ID, "input-email").send_keys(email_data)
                    driver.find_element(By.ID, "input-password").clear()
                    driver.find_element(By.ID, "input-password").send_keys(password_data)
                    driver.find_element(By.XPATH, "//input[@value='Login']").click()
                    time.sleep(1)

                    try: 
                        actual_text = driver.find_element(By.XPATH, "//div[contains(@class, 'alert-danger')]").text
                        self.assertIn(expected_res, actual_text)
                        print(f"   -> [{tc_id}] [PASS] Error message matches.")
                    except AssertionError as e: 
                        self.verificationErrors.append(str(e))
                        print(f"   -> [{tc_id}] [FAIL] Message mismatch. Got: {actual_text}")
                    except NoSuchElementException:
                         print(f"   -> [{tc_id}] [FAIL] No error message found.")

            with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print("\n[INFO] CSV File Updated with new random emails.")

        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file CSV. Hãy đảm bảo file 'group_1.csv' nằm CÙNG THƯ MỤC với file code.")
        except KeyError:
            print("Lỗi: File CSV thiếu cột 'ID'. Hãy kiểm tra lại header trong Excel.")
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()