import json
import threading
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service
import random
import string
import requests
import imaplib
import email
import re
import time
from email.header import decode_header
from email.utils import parsedate_to_datetime

class Main:
    def __init__(self, account, index=0, status_callback=None):
        self.index = index
        self.account = account
        self.status_callback = status_callback  # Callback để gửi status về UI
        self.full_cookie = ""  # Lưu cookie đầy đủ
        
        with open('data.json', 'r') as f:
            data = json.load(f)
        if data['browser']['type'] == 'chrome':
            options = ChromeOptions()
        else:
            options = EdgeOptions()
            
        # Các tùy chọn cho Edge
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=375,812")
        options.add_argument("--lang=pl-PL")

        # Fake User-Agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")

        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)

        if data['browser']['type'] == 'chrome':
            self.driver = Chrome(options=options)
        else:
            service = Service(executable_path=data['browser']['edge_driver_path'])
            self.driver = webdriver.Edge(service=service, options=options)

        # Set vị trí cửa sổ
        SCREEN_WIDTH = 1920
        WINDOW_WIDTH = 400
        WINDOW_HEIGHT = 600
        COLUMNS = SCREEN_WIDTH // WINDOW_WIDTH
        row = self.index // COLUMNS
        col = self.index % COLUMNS
        x = col * WINDOW_WIDTH
        y = row * WINDOW_HEIGHT
        self.driver.set_window_position(x, y)

    def update_status(self, status_text):
        """Hàm để cập nhật trạng thái về UI"""
        if self.status_callback:
            self.status_callback(self.index, status_text)

    def wait_and_click(self, locator, locator_type="xpath", timeout=60):
        # Convert locator type to By class attribute
        if locator_type.lower() == "xpath":
            by = By.XPATH
        elif locator_type.lower() == "id":
            by = By.ID 
        elif locator_type.lower() == "name":
            by = By.NAME
        else:
            raise ValueError("Unsupported locator type. Use 'xpath', 'id', or 'name'")

        # Chờ đến khi element có thể click được
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )

        element.click()
        sleep(1.5)

    def wait_and_send_keys(self, locator, keys, locator_type="xpath", timeout=60):
        def human_typing(element, text, delay_range=(0.1, 0.3)):
            for char in text:
                element.send_keys(char)
                sleep(random.uniform(*delay_range))

        # Convert locator type to By class attribute
        if locator_type.lower() == "xpath":
            by = By.XPATH
        elif locator_type.lower() == "id":
            by = By.ID 
        elif locator_type.lower() == "name":
            by = By.NAME
        else:
            raise ValueError("Unsupported locator type")

        # ✅ ĐỔI THÀNH element_to_be_clickable thay vì presence_of_element_located
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        # Clear field trước khi type
        element.clear()
        human_typing(element, keys)
        sleep(1.5)
            
    def wait_and_get_text(self, xpath, timeout=60):
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text

    def get_cookies(self):
        try:
            cookies = self.driver.get_cookies()
            cookie_str = ';'.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            self.full_cookie = cookie_str  # Lưu cookie đầy đủ
            return cookie_str
        except Exception as e:
            print("Lỗi lấy cookie:", e)
            return None

    def get_short_cookie(self):
        """Trả về cookie ngắn gọn cho hiển thị trong TreeView"""
        # if self.full_cookie:
        #     if len(self.full_cookie) > 50:
        #         return self.full_cookie[:47] + "..."
        #     return self.full_cookie
        # return ""
        return self.full_cookie

    def get_full_cookie(self):
        """Trả về cookie đầy đủ cho export file"""
        return self.full_cookie
        
    def add_cookie(self):
        self.driver.delete_all_cookies()

        raw_cookie = self.account['cookie']

        # Nếu là chuỗi, parse thành list dict
        cookies_list = []
        if isinstance(raw_cookie, str):
            try:
                parts = raw_cookie.strip().strip(';').split(';')
                for part in parts:
                    if '=' in part:
                        name, value = part.strip().split('=', 1)
                        cookies_list.append({
                            'name': name.strip(),
                            'value': value.strip(),
                            'domain': '.facebook.com'
                        })
            except Exception as e:
                print(f"Lỗi parse cookie chuỗi: {e}")
                return
        elif isinstance(raw_cookie, list):
            cookies_list = raw_cookie  # Trường hợp đã đúng định dạng list of dict

        # Add từng cookie
        for cookie in cookies_list:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                print(f"Không thể thêm cookie: {cookie.get('name', '')} - {e}")

    def get_code_mail(self):
        data_mail = self.account['new_email']

        url = 'https://tools.dongvanfb.net/api/graph_code'
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "email": data_mail.split('|')[0],
            "refresh_token": data_mail.split('|')[2],
            "client_id": data_mail.split('|')[3],
            "type": "facebook"
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=300)
            response.raise_for_status()  # Gây lỗi nếu mã trạng thái HTTP không phải 2xx
            json_data = response.json()

            if 'code' in json_data:
                return json_data['code']
            else:
                print("Không có mã xác nhận trong phản hồi:", json_data)
                return None
        except requests.exceptions.Timeout:
            print("⏰ Hết thời gian chờ phản hồi từ API.")
            return None
        except requests.exceptions.RequestException as e:
            print("❌ Lỗi khi gọi API:", e)
            return None
        
    def check_die(self):
        try:
            current_url = self.driver.current_url
            print(f"Current URL: {current_url}")
            
            if "956" in current_url:
                print("Checkpoint 956 detected")
                self.update_status("Tài khoản bị checkpoint 956")
                self.driver.quit()
                return False
            elif "681" in current_url:
                print("Checkpoint 681 detected")
                self.update_status("Tài khoản bị checkpoint 681")
                self.driver.quit()
                return False
            elif "282" in current_url:
                print("Checkpoint 282 detected")
                self.update_status("Tài khoản bị checkpoint 282")
                self.driver.quit()
                return False
            else:
                print("No checkpoint detected, account is live")
                return True
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False

    def get_code_onet(self, mail, code):
        """
        Hàm lấy code từ email onet.pl
        Args:
            mail: string định dạng "email|password|target_email"
            code: code hiện tại cần so sánh để tránh trùng lặp
        Returns:
            string: code mới nếu tìm thấy, None nếu không tìm thấy hoặc trùng code
        """
        try:
            # Parse thông tin từ mail string
            parts = mail.split('|')
            if len(parts) != 3:
                print(f"[ERROR] Định dạng mail không đúng: {mail}")
                return None
                
            email_account = parts[0].strip()
            password = parts[1].strip()
            target_email = parts[2].strip()
            
            print(f"[INFO] Bắt đầu lấy code cho: {email_account} -> {target_email}")
            
            # Kết nối IMAP
            mail_conn = imaplib.IMAP4_SSL("imap.poczta.onet.pl", 993)
            
            try:
                mail_conn.login(email_account, password)
            except imaplib.IMAP4.error as e:
                print(f"[ERROR] Đăng nhập thất bại cho {email_account}: {e}")
                return None
            
            # Danh sách folder cần check (INBOX check trước với 5 mail mới nhất)
            folders_config = {
                "INBOX": 5,  # Chỉ check 5 mail mới nhất trong INBOX
                '"Spo&AUI-eczno&AVs-ci"': 5,  # Check nhiều hơn trong Spam
                "Spam": 5
            }
            
            found_code = None
            target_email_lower = target_email.lower()
            
            for folder, mail_limit in folders_config.items():
                if found_code:
                    break
                    
                try:
                    status, _ = mail_conn.select(folder)
                    if status != "OK":
                        print(f"[WARNING] Không thể chọn folder {folder}")
                        continue
                except Exception as e:
                    print(f"[WARNING] Lỗi khi chọn folder {folder}: {e}")
                    continue
                
                # Tìm tất cả mail
                status, data = mail_conn.search(None, "ALL")
                if status != "OK":
                    print(f"[WARNING] Không thể search trong folder {folder}")
                    continue
                
                mail_ids = data[0].split()
                # Lấy số lượng mail theo cấu hình (mới nhất)
                mail_ids = mail_ids[-mail_limit:] if len(mail_ids) > mail_limit else mail_ids
                
                print(f"[INFO] Checking {len(mail_ids)} mails trong folder {folder}")
                
                # Duyệt từ mail mới nhất (reverse)
                for mail_id in reversed(mail_ids):
                    try:
                        status, msg_data = mail_conn.fetch(mail_id, "(RFC822)")
                        if status != "OK":
                            continue
                        
                        msg = email.message_from_bytes(msg_data[0][1])
                        
                        # Kiểm tra mail có gửi đến target_email không
                        to_addr = msg.get("To", "").lower()
                        if target_email_lower not in to_addr:
                            continue
                        
                        # Decode và lấy nội dung mail
                        body_text, body_html = self._extract_email_content(msg)
                        
                        # Tìm code trong nội dung
                        new_code = self._extract_facebook_code(body_text, body_html)
                        
                        if new_code:
                            # Kiểm tra code có trùng với code hiện tại không
                            if new_code == code:
                                print(f"[INFO] Code {new_code} trùng với code hiện tại, bỏ qua")
                                continue
                            
                            print(f"[SUCCESS] Tìm thấy code mới: {new_code}")
                            found_code = new_code
                            break
                        
                    except Exception as e:
                        print(f"[ERROR] Lỗi khi xử lý mail {mail_id}: {e}")
                        continue
                    
                    time.sleep(0.05)  # Tránh spam server
                
                if found_code:
                    print(f"[INFO] Đã tìm thấy code trong folder {folder}")
                    break
            
            # Đóng kết nối
            try:
                mail_conn.logout()
            except:
                pass
            
            if found_code:
                print(f"[SUCCESS] Lấy code thành công: {found_code}")
                return found_code
            else:
                print(f"[INFO] Không tìm thấy code mới cho {target_email}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Lỗi trong get_code_onet: {e}")
            return None

    def _extract_email_content(self, msg):
        """Trích xuất nội dung text và HTML từ email"""
        body_text, body_html = "", ""
        
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    body_text += part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="ignore"
                    )
                elif ctype == "text/html":
                    body_html += part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="ignore"
                    )
        else:
            ctype = msg.get_content_type()
            if ctype == "text/plain":
                body_text = msg.get_payload(decode=True).decode(
                    msg.get_content_charset() or "utf-8", errors="ignore"
                )
            elif ctype == "text/html":
                body_html = msg.get_payload(decode=True).decode(
                    msg.get_content_charset() or "utf-8", errors="ignore"
                )
        
        return body_text, body_html

    def _extract_facebook_code(self, body_text, body_html):
        """Trích xuất code Facebook từ nội dung email"""
        # Pattern tìm link Facebook recovery
        patterns = [
            r'https://www\.facebook\.com/login/recover/cancel/\?n=(\d+)&amp;id=(\d+)',
            r'https://www\.facebook\.com/login/recover/cancel/\?n=(\d+)&id=(\d+)'
        ]
        
        # Tìm trong HTML trước
        for pattern in patterns:
            match = re.search(pattern, body_html)
            if match:
                n_val = match.group(1)
                id_val = match.group(2)
                return f"{id_val}|{n_val}"  # Hoặc format khác tùy bạn muốn
        
        # Tìm trong text nếu không có trong HTML
        for pattern in patterns:
            match = re.search(pattern, body_text)
            if match:
                n_val = match.group(1)
                id_val = match.group(2)
                return f"{id_val}|{n_val}"  # Hoặc format khác tùy bạn muốn
        
        return None

    def decode_mime_words(self, s):
        """Decode MIME words trong header email"""
        decoded_fragments = decode_header(s)
        return ''.join(
            fragment.decode(charset or 'utf-8') if isinstance(fragment, bytes) else fragment
            for fragment, charset in decoded_fragments
        )

    def get_new_password(self, mail, code):
        self.update_status("Đang lấy code từ email...")
        
        self.driver.get('https://www.facebook.com/recover/initiate/')
        self.wait_and_click('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div[1]/div/div/div/div/div[6]/div/div[2]/div/div[2]/div[1]/div')
        sleep(10)
        
        self.update_status("Đang chờ code từ email...")
        code = self.get_code_onet(mail, code)
        if code:
            self.update_status("Đang nhập code xác nhận...")
            self.wait_and_send_keys('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div[1]/div/div/div[2]/div[2]/div[1]/div/div/label/div/input', code.split('|')[1])
            self.wait_and_click('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div[1]/div/div/div[3]/div[2]/div[2]/div[1]/div')
            self.update_status("Đang nhập nhập mật khẩu...")
            self.wait_and_send_keys('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div[1]/div/div/div/div/div[4]/div/div/div[3]/div/div[1]/div/div/div/label/div[1]/input', self.generated_pass)
            self.wait_and_click('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div[1]/div/div/div/div/div[6]/div/div[2]/div[1]/div')
            self.driver.get('https://www.facebook.com/')
        else:
            self.update_status("Đang chờ tự lấy code nhập bằng tay")
            check = self.wait_and_get_text('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div[1]/div/div/div/div/div[4]/div/div/div[3]/div/div[1]/div/div/div/label/div[1]/input', timeout = 300)
            if check:
                self.wait_and_send_keys('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div[1]/div/div/div/div/div[4]/div/div/div[3]/div/div[1]/div/div/div/label/div[1]/input', self.generated_pass)
                self.wait_and_click('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div[1]/div/div/div/div/div[6]/div/div[2]/div[1]/div')
                self.driver.get('https://www.facebook.com/')

    def new_pass(self):
        def tao_mat_khau(do_dai=12, co_ky_tu_dac_biet=True):
            ky_tu = string.ascii_letters + string.digits
            if co_ky_tu_dac_biet:
                ky_tu += string.punctuation
            return ''.join(random.choice(ky_tu) for _ in range(do_dai))
            
        with open('data.json', 'r') as f:
            data = json.load(f)
        self.generated_pass = (
            tao_mat_khau() if data['type_password'] == 2 else data['password']
        )
        
        self.update_status("Bắt đầu quên mật khẩu...")
        self.driver.get("https://m.facebook.com/login/identify/")
        
        try:
            try:
                self.wait_and_click("/html/body/div[3]/div/div/div/div/div/div[3]/div[2]/div/div[2]/div[1]/div")
            except:
                pass
                
            self.update_status("Nhập email khôi phục...")
            self.wait_and_send_keys(" /html/body/div[1]/div[1]/div[1]/div/div[2]/div/div/form/div/div[2]/div/table/tbody/tr[2]/td[2]/input", self.account['email'].split('|')[2])
            self.wait_and_click("did_submit", locator_type="name")
            
            self.update_status("Chọn phương thức khôi phục...")
            self.wait_and_click("/html/body/div[1]/div[1]/div[1]/div/div[2]/form/div/div[3]/div/div[1]/button")
            
            self.update_status("Nhập code khôi phục...")
            code = ''.join(filter(str.isdigit, self.account['code'])).zfill(6)
            self.wait_and_send_keys("recovery_code_entry", code, locator_type="id")
            self.wait_and_click(" /html/body/div[1]/div[1]/div[1]/div/div[2]/form/div/div[3]/div/div[1]/button")
            self.check_login()
            
            try:
                self.update_status("Đang đổi mật khẩu...")
                self.wait_and_send_keys("password_new", self.generated_pass, locator_type="name", timeout=10)
                self.wait_and_click("btn_continue", locator_type="name")
            except:
                self.get_new_password(self.account['email'], code)
            
            self.update_status("Lấy cookie mới...")
            cookies = self.get_cookies()
            
            sleep(data['sleep'])
            self.driver.quit()
            
            self.update_status("Thành công!")
            return True, self.generated_pass, cookies
            
        except Exception as e:
            print("Lỗi đổi mật khẩu:", e)
            self.update_status(f"Lỗi: {str(e)}")
            self.driver.quit()
            return False, self.generated_pass, []

    def new_mail(self):
        self.update_status("Bắt đầu đổi email...")
        self.driver.get("https://www.facebook.com/")
        sleep(3)
        
        try:
            try:
                self.wait_and_click("/html/body/div[1]/div/div[6]/div[1]/div/div[2]/div[2]/div[3]/button[2]")
            except:
                pass

            self.update_status("Thêm cookie...")
            self.add_cookie()
            
            self.update_status("Truy cập trang đổi email...")
            self.driver.get("https://accountscenter.facebook.com/personal_info/contact_points/?contact_point_type=email&dialog_type=add_contact_point")
            sleep(2)
            self.driver.get("https://accountscenter.facebook.com/personal_info/contact_points/?contact_point_type=email&dialog_type=add_contact_point")
            
            self.update_status("Nhập email mới...")
            # Nhập email mới
            self.wait_and_send_keys(
                "/html/body/div[1]/div/div/div/div[3]/div/div/div[2]/div/div/div/div/div/div/div/div[4]/div[2]/div[1]/div[2]/div/div/div/div/div[1]/input",
                self.account['new_email'].split('|')[0]
            )
            sleep(1)
            self.wait_and_click(
                "/html/body/div[1]/div/div/div/div[3]/div/div/div[2]/div/div/div/div/div/div/div/div[4]/div[2]/div[1]/div[3]/div/div[2]/div/div/div/div/label/div[1]/div/div[3]/div/input"
            )
            sleep(1)
            self.wait_and_click(
                "/html/body/div[1]/div/div/div/div[3]/div/div/div[2]/div/div/div/div/div/div/div/div[5]/div/div/div/div/div/div/div/div/div"
            )
            sleep(1)

            self.update_status("Lấy mã xác nhận...")
            # Lấy mã xác nhận
            code = self.get_code_mail()
            if code is None:
                print("⚠️ Không lấy được mã xác nhận. Dừng thao tác.")
                self.update_status("Lỗi: Không lấy được mã")
                self.driver.quit()
                return False, '', ''
            if code == '':
                print("⚠️ Không lấy được mã xác nhận. Dừng thao tác.")
                self.update_status("Lỗi: Mã trống")
                self.driver.quit()
                return False, '', ''
                
            self.update_status("Nhập mã xác nhận...")
            # Nhập mã xác nhận
            self.wait_and_send_keys(
                "/html/body/div[1]/div/div/div/div[3]/div/div/div[2]/div/div/div/div/div/div/div/div[4]/div[2]/div[1]/div[2]/div/div/div/div/div[1]/input",
                code
            )
            sleep(1)
            self.wait_and_click(
                "/html/body/div[7]/div[1]/div/div[2]/div/div/div/div/div/div/div[4]/div[2]/div[1]/div/div/div/div/div/div[2]/div/div[2]/div/div/div"
            )
            
            self.update_status("Thành công!")
            return True, '', ''
            
        except Exception as e:
            print("Lỗi đổi email:", e)
            self.update_status(f"Lỗi: {str(e)}")
            self.driver.quit()
            return False, '', ''
        
    def forgot_password(self):
        try:
            self.update_status("Truy cập trang quên mật khẩu...")
            # Truy cập trang quên mật khẩu Facebook
            self.driver.get("https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0")
            
            self.update_status("Nhập email...")
            # Nhập email vào ô input 
            self.wait_and_send_keys(
                "/html/body/div[1]/div[1]/div[1]/div/div[2]/div/div/form/div/div[2]/div/table/tbody/tr[2]/td[2]/input",
                self.account['email']  # Email lấy từ dữ liệu tài khoản
            )
            
            self.update_status("Tìm kiếm tài khoản...")
            # Click nút Tìm kiếm
            self.wait_and_click(
                "/html/body/div[1]/div[1]/div[1]/div/div[2]/div/div/form/div/div[3]/div/div[1]/button"
            )
            
            try:
                self.update_status("Kiểm tra lỗi...")
                # Chờ và kiểm tra xem có thông báo lỗi không
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[2]/div/div/form/div/div[2]/div[1]/div[1]'))
                )
                element.click()
                
                # Nếu thấy thông báo lỗi -> trả về thất bại
                if element.is_displayed():
                    self.update_status("Lỗi: Không tìm thấy tài khoản")
                    self.driver.quit()
                    return False, '', ''
                    
            except:
                self.update_status("Chọn phương thức khôi phục...")
                # Nếu không có lỗi -> click nút Tiếp tục
                self.wait_and_click("/html/body/div[1]/div[1]/div[1]/div/div[2]/form/div/div[3]/div/div[1]/button")
                check_text = self.wait_and_get_text('/html/body/div[1]/div[1]/div[1]/div/div[2]/form/div/div[1]/div/div[2]/h2')
                print("Kiểm tra văn bản:", check_text)
                
                if "Wprowadź kod zabezpieczający" in check_text.split():
                    self.update_status("Thành công!")
                    self.driver.quit()
                    return True, '', ''  # Trả về thành công
                else:
                    self.update_status("Thành công!")
                    self.driver.quit()
                    return True, '', ''  # Trả về thành công

        except Exception as e:
            # Xử lý lỗi nếu có
            print("Lỗi quên mật khẩu:", e)
            self.update_status(f"Lỗi: {str(e)}")
            self.driver.quit()  # Đóng trình duyệt
            return False, '', ''  # Trả về thất bại

    def main(self):
        pass