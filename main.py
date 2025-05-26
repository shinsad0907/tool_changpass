import json
import threading
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import string
import requests

class Main:
    def __init__(self, account, index=0, type_run='change_pass'):
        self.type_run = type_run
        self.index = index
        self.account = account

        print(self.account)

        options = webdriver.ChromeOptions()
        # mobile_emulation = {"deviceName": "iPhone X"}
        # options.add_experimental_option("mobileEmulation", mobile_emulation)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--window-size=375,812")

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")

        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=options)

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

    def wait_and_click(self, xpath, timeout=60):
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        sleep(1.5)

    def wait_and_send_keys(self, xpath, keys, timeout=60):
        def human_typing(element, text, delay_range=(0.1, 0.3)):
            for char in text:
                element.send_keys(char)
                sleep(random.uniform(*delay_range))

        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        human_typing(element, keys)

    def get_cookies(self):
        try:
            cookies = self.driver.get_cookies()
            cookie_str = ';'.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            return cookie_str
        except Exception as e:
            print("Lỗi lấy cookie:", e)
            return None
        
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
        self.driver.get("https://m.facebook.com/login/identify/")
        try:
            self.driver.get(f"https://www.facebook.com/recover/password/?u={self.account['uid']}&n={self.account['code']}&fl=default_recover&sih=0&msgr=0")
            try:
                self.wait_and_click("/html/body/div[1]/div/div[6]/div[1]/div/div[2]/div[2]/div[3]/button[2]")
            except:
                pass
            # self.wait_and_click("/html/body/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div/div/div/div/div")
            # self.wait_and_send_keys("/html/body/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div/div/div/div[2]/div/div/div[1]/div/div/div[2]/div[2]/input", self.account['email'])
            # self.wait_and_click("/html/body/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div/div/div/div[2]/div/div/div[2]/div/div[1]/div/div/div/div/div/div")
            # self.wait_and_send_keys("/html/body/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div/div/div/div[3]/div/div/div[1]/div/div/div[2]/div[2]/input", self.account['code'])
            # self.wait_and_click("/html/body/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div/div/div/div[3]/div/div/div[3]/div/div[1]/div/div/div/div/div/div")
            # self.wait_and_send_keys("/html/body/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div/div/div/div[2]/div/div/div/div/div[2]/div[2]/input", self.generated_pass)
            # self.wait_and_click("/html/body/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div/div/div/div[3]/div/div/div/div[1]/div/div/div/div/div/div")
            self.wait_and_send_keys("/html/body/div[1]/div[1]/div[2]/div[2]/div/div/form/div[1]/section[2]/div/div/div[1]/div/input", self.generated_pass)
            self.wait_and_click("/html/body/div[1]/div[1]/div[2]/div[2]/div/div/form/div[2]/button")
            sleep(20)
            cookies = self.get_cookies()
            self.driver.quit()
            return True, self.generated_pass, cookies
        except Exception as e:
            print("Lỗi đổi mật khẩu:", e)
            self.driver.quit()
            return False, self.generated_pass, []

    def new_mail(self):
        self.driver.get("https://www.facebook.com/")
        sleep(3)
        try:
            try:
                self.wait_and_click("/html/body/div[1]/div/div[6]/div[1]/div/div[2]/div[2]/div[3]/button[2]")
            except:
                pass

            self.add_cookie()
            self.driver.get("https://accountscenter.facebook.com/personal_info/contact_points/?contact_point_type=email&dialog_type=add_contact_point")
            sleep(2)
            self.driver.get("https://accountscenter.facebook.com/personal_info/contact_points/?contact_point_type=email&dialog_type=add_contact_point")
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

            # Lấy mã xác nhận
            code = self.get_code_mail()
            if code is None:
                print("⚠️ Không lấy được mã xác nhận. Dừng thao tác.")
                self.driver.quit()
                return False, '', ''
            if code == '':
                print("⚠️ Không lấy được mã xác nhận. Dừng thao tác.")
                self.driver.quit()
                return False, '', ''
            # Nhập mã xác nhận
            self.wait_and_send_keys(
                "/html/body/div[1]/div/div/div/div[3]/div/div/div[2]/div/div/div/div/div/div/div/div[4]/div[2]/div[1]/div[2]/div/div/div/div/div[1]/input",
                code
            )
            sleep(1)
            self.wait_and_click(
                "/html/body/div[7]/div[1]/div/div[2]/div/div/div/div/div/div/div[4]/div[2]/div[1]/div/div/div/div/div/div[2]/div/div[2]/div/div/div"
            )
            return True, '', ''
        except Exception as e:
            print("Lỗi đổi mật khẩu:", e)
            self.driver.quit()
            return False, '', ''
        
    def  forgot_password(self):
        pass


    def main(self):
        pass
