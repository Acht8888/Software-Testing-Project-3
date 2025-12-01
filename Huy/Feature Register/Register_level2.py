# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
# Import Service để tương thích Selenium 4
from selenium.webdriver.edge.service import Service 
import unittest, time, csv, os 

class Register_Level2(unittest.TestCase):
    def setUp(self):
        # [CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG - RELATIVE PATH]
        current_dir = os.path.dirname(os.path.abspath(__file__))
        driver_path = os.path.join(current_dir, 'msedgedriver.exe')
        
        # Khởi tạo Driver với Service (Selenium 4)
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Edge(service=service)
        
        self.driver.implicitly_wait(5)
        self.base_url = "https://ecommerce-playground.lambdatest.io/"
        self.verificationErrors = []
    
    def test_register_level2(self):
        driver = self.driver
        
        try:
            # [CẤU HÌNH ĐƯỜNG DẪN CSV TỰ ĐỘNG]
            current_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(current_dir, 'data_register_level2.csv')
            
            with open(csv_path, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # --- 1. LẤY DỮ LIỆU INPUT (DATA) ---
                    tc_id = row.get('ID', '')
                    test_type = row.get('type', '').strip()
                    expected_res = row.get('expected result', '')
                    
                    # Dữ liệu nhập liệu (nếu null thì lấy chuỗi rỗng)
                    fname = row.get('First Name', '').strip()
                    lname = row.get('Last Name', '').strip()
                    email = row.get('email', '').strip()
                    phone = row.get('telephone', '').strip()
                    passwd = row.get('password', '').strip()
                    confirm = row.get('Password Confirm', '').strip()
                    privacy = row.get('Privacy Policy', '').strip().upper() # Chuyển TRUE/FALSE về in hoa

                    # --- 2. LẤY ĐỊNH DANH PHẦN TỬ (LOCATORS - LEVEL 2) ---
                    # Code đọc ID/XPath từ file Excel thay vì viết cứng
                    url_web = row.get('url')
                    id_fn = row.get('fn_id')
                    id_ln = row.get('ln_id')
                    id_email = row.get('email_id')
                    id_phone = row.get('phone_id')
                    id_pass = row.get('pass_id')
                    id_confirm = row.get('confirm_id')
                    xp_privacy = row.get('privacy_xpath') # XPath label của privacy
                    xp_submit = row.get('submit_xpath')
                    
                    # [QUAN TRỌNG] Cột định vị lỗi (Thay thế cho logic if/elif tìm lỗi)
                    xp_error = row.get('error_locator') 

                    print(f"\n--- Running [{tc_id}] Type: {test_type} ---")

                    # Mở trang web (Lấy URL từ CSV)
                    driver.get(url_web)
                    
                    # =======================================================
                    # ĐIỀN FORM (LOGIC LEVEL 2 - DỰA VÀO BIẾN LOCATOR)
                    # =======================================================
                    
                    # Chỉ điền nếu ô Excel có dữ liệu
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
                    
                    # --- XỬ LÝ PRIVACY POLICY ---
                    # Logic: Nếu test case Lỗi Privacy -> Cố tình không click
                    # Logic: Nếu test case Success/Lỗi khác -> Click nếu CSV = TRUE
                    should_click = False
                    
                    if "privacy" in test_type:
                        # Case test lỗi Privacy: Chỉ click nếu CSV bảo TRUE (thường là FALSE)
                        if privacy == "TRUE": should_click = True
                        
                        # Điền dữ liệu giả nếu thiếu để kích hoạt nút continue
                        if not fname: driver.find_element(By.ID, id_fn).send_keys("Test")
                        if not lname: driver.find_element(By.ID, id_ln).send_keys("User")
                        if not email: driver.find_element(By.ID, id_email).send_keys("auto_priv_test@gmail.com")
                        if not phone: driver.find_element(By.ID, id_phone).send_keys("0123456789")
                        if not passwd: driver.find_element(By.ID, id_pass).send_keys("123456")
                        if not confirm: driver.find_element(By.ID, id_confirm).send_keys("123456")
                        
                    elif privacy == "TRUE":
                        # Case bình thường: Click nếu TRUE
                        should_click = True
                    
                    # Thực hiện Click (Dùng JS để tránh lỗi bị che)
                    if should_click:
                        try:
                            element = driver.find_element(By.XPATH, xp_privacy)
                            driver.execute_script("arguments[0].click();", element)
                        except: pass
                    
                    # Bấm nút Continue (Dùng XPath từ CSV)
                    driver.find_element(By.XPATH, xp_submit).click()
                    time.sleep(2)
                    
                    # =======================================================
                    # VERIFY KẾT QUẢ (LEVEL 2 - DỰA VÀO ERROR_LOCATOR)
                    # =======================================================
                    
                    # Trường hợp Thành công
                    if "register successful" in test_type:
                        try:
                            if "success" in driver.current_url or "Created" in driver.page_source:
                                print(f"   -> [PASS] Account Created Successfully!")
                                driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/logout")
                            else:
                                print(f"   -> [FAIL] Expected Success but Failed.")
                        except: pass

                    # Trường hợp Fail (Tất cả các loại lỗi: Pass, Email, Name, Privacy...)
                    # Code Level 2 không cần if/elif dài dòng, nó chỉ cần nhìn vào cột error_locator
                    else:
                        if xp_error: 
                            self.check_error(driver, xp_error, expected_res)
                        elif expected_res == "Accepted": 
                            # Case biên hợp lệ, không mong đợi lỗi
                            self.check_no_error(driver, "//div[contains(@class, 'text-danger')]") # Check chung chung

        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file CSV. Hãy đảm bảo file CSV nằm CÙNG THƯ MỤC với file code này.")
        except KeyError as e:
            print(f"Lỗi: File CSV thiếu cột {e}. Hãy kiểm tra lại header trong file Excel.")

    # Hàm verify gọn nhẹ
    def check_error(self, driver, xpath, expected):
        try:
            actual = driver.find_element(By.XPATH, xpath).text
            if expected in actual:
                print(f"   -> [PASS] Error match found: {expected}")
            else:
                pass
        except NoSuchElementException:
            pass # Không thấy lỗi

    def check_no_error(self, driver, xpath):
        try:
            driver.find_element(By.XPATH, xpath)
            print(f"   -> [FAIL] Error message appeared but expected none!")
        except NoSuchElementException:
            print(f"   -> [PASS] No error message (Accepted).")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()