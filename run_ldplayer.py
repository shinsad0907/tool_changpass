from setting_ldplayer import LDPlayerSettings
import json
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
                           QTreeWidget, QTreeWidgetItem, QLabel, QFrame, QCheckBox, QRadioButton,
                           QComboBox, QSpinBox, QPushButton, QHeaderView, QMenu, QAction, QGroupBox,
                           QLineEdit, QMessageBox, QFileDialog)
from time import time, sleep
import time
import os
import requests
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

class LDPlayerRunner:
    def __init__(self,acc, i):
        self.settings = LDPlayerSettings()
        with open('setting_ldplayer.json', 'r') as configfile:
            config_data = json.load(configfile)
        self.ldplayer_path = config_data['ld_path']
        self.tess_path = config_data['tess_path']
        pytesseract.pytesseract.tesseract_cmd = rf"{self.tess_path}"

        with open('data.json', 'r') as configfile:
            config_data = json.load(configfile)
        self.tab_ldplayer = config_data['thread']
        self.SCREEN_WIDTH = 1920  # Độ rộng màn hình (có thể điều chỉnh)
        self.WINDOW_WIDTH = 400   # Độ rộng mỗi cửa sổ LDPlayer
        self.WINDOW_HEIGHT = 600  # Độ cao mỗi cửa sổ LDPlayer
        self.MARGIN = 10
        self.show_error = None
        self.container = None
        self.stt_ldplayer = i  # Lưu self.stt_ldplayer để sử dụng trong các phương thức khác
        self.account = acc  # Lưu acc để sử dụng trong các phương thức khác
        self.wait_time = 0
        self.error_message = ""

    def set_error_callback(self, callback):
        self.show_error = callback

    def get_id_machine(self):
        result = subprocess.run([f'{self.ldplayer_path}\ldconsole.exe', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip()
        # Mỗi dòng trong output đại diện cho một máy ảo
        vm_list = output.splitlines()
        if vm_list:
            # Lấy ID của máy ảo đầu tiên (giả sử ID là phần đầu tiên của mỗi dòng)
            return vm_list
        
    def open_ldplayer(self):
        vm_id = self.get_id_machine()
        self.settings.change_ldplayer_config(fr'{self.ldplayer_path}\vms\config\leidian{self.stt_ldplayer}.config')
        
        # Khởi động LDPlayer
        subprocess.run([
            fr"{self.ldplayer_path}\ldconsole.exe",
            'launch',
            '--name',
            vm_id[self.stt_ldplayer]
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Đợi một chút để LDPlayer khởi động
        sleep(10)
        
        # Khởi động lại ADB server để đảm bảo nhận diện đúng
        subprocess.run(fr"{self.ldplayer_path}\adb.exe kill-server", shell=True)
        sleep(2)
        subprocess.run(fr"{self.ldplayer_path}\adb.exe start-server", shell=True)
        sleep(2)
        
        # Kết nối ADB với LDPlayer
        subprocess.run([
            fr"{self.ldplayer_path}\ldconsole.exe",
            'adb',
            '--name',
            vm_id[self.stt_ldplayer]
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Kiểm tra devices
        while True:
            try:
                devices = self.DEVICE()
                if len(devices) > self.stt_ldplayer:
                    print(f"Device connected: {devices[self.stt_ldplayer]}")
                    break
                else:
                    print("Waiting for device connection...")
                    sleep(5)
            except Exception as e:
                print(f"Error checking devices: {e}")
                sleep(5)
                
        return devices[self.stt_ldplayer]
    
    def close(self):
        try:
            # Lấy list devices trước
            devices = self.get_id_machine()
            if devices and self.stt_ldplayer < len(devices):
                # Sử dụng quit --index thay vì --name
                command = [
                    fr"{self.ldplayer_path}\ldconsole.exe",
                    'quit',
                    '--index',
                    str(self.stt_ldplayer)
                ]
                
                # Thực thi lệnh
                result = subprocess.run(command, capture_output=True, text=True)
                print(f"Closing LDPlayer {self.stt_ldplayer}: {result.stdout}")
                
                # Đợi một chút để đảm bảo LDPlayer đã tắt
                time.sleep(2)
                
                # Kiểm tra xem LDPlayer đã tắt chưa
                new_devices = self.get_id_machine()
                if new_devices and len(new_devices) >= self.stt_ldplayer + 1:
                    # Nếu vẫn chưa tắt, thử kill process
                    kill_command = [
                        fr"{self.ldplayer_path}\ldconsole.exe",
                        'quit',
                        '--name',
                        devices[self.stt_ldplayer]
                    ]
                    subprocess.run(kill_command, capture_output=True, text=True)
                    
        except Exception as e:
            print(f"Error closing LDPlayer: {str(e)}")


    def DEVICE(self):
    # Đảm bảo ADB server đang chạy
        subprocess.run(fr"{self.ldplayer_path}\adb.exe start-server", shell=True)
        sleep(1)
        
        proc = subprocess.run(
            fr"{self.ldplayer_path}\adb.exe devices", 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        devices = []
        for line in proc.stdout.decode('utf-8').splitlines():
            if '\tdevice' in line:
                devices.append(line.split('\t')[0])
                
        print(f"Found devices: {devices}")
        return devices

    def is_app_installed(self):
        try:
            command = fr'{self.ldplayer_path}\\adb.exe -s {self.DEVICE()[self.stt_ldplayer]} shell pm list packages com.facebook.lite'
            stdout, stderr = self.adb_command(command)
            return 'com.facebook.lite' in stdout
        except:
            return False

    def check_tab_ldplayer(self):
        vm_id = self.get_id_machine()
        if not vm_id:
            return (False, "Không tìm thấy máy ảo LDPlayer nào.")
        elif len(vm_id) < int(self.tab_ldplayer):
            return (False, f"Chưa đủ {self.tab_ldplayer} máy ảo LDPlayer để chạy.")
        return (True, "")
    
    def openfb(self):
        if self.is_app_installed():
            self.cachefacebook()
        else:
            print('Installing Facebook Lite...')
            self.install_facebook()
            # Đợi 5 giây sau khi cài đặt
            sleep(5)
            self.cachefacebook()
        
        # Đợi 2 giây sau khi clear cache
        sleep(2)
        command = fr'{self.ldplayer_path}\\adb.exe -s {self.DEVICE()[self.stt_ldplayer]} shell am start -n com.facebook.lite/com.facebook.lite.MainActivity'
        stdout, stderr = self.adb_command(command)
        
        # Kiểm tra lỗi khi mở app
        if stderr:
            print(f"Error opening Facebook: {stderr}")
        else:
            print("Facebook Lite opened successfully")
        sleep(10)

    def capture_screen(self,image_path):
        adb = os.path.join(self.ldplayer_path, "adb.exe")
        print("[✓] Đang chụp màn hình...")
        
        subprocess.run([adb, "-s", self.DEVICE()[self.stt_ldplayer], "shell", "screencap", "-p", "/sdcard/screen.png"])
        subprocess.run([adb, "-s", self.DEVICE()[self.stt_ldplayer], "pull", "/sdcard/screen.png", f"ldplayer/ldplayer_screen{self.stt_ldplayer}.png"])
        
        if os.path.exists(image_path):
            print("[✓] Đã lưu ảnh:", image_path)
            return image_path
        else:
            print("[✗] Không thể lấy được ảnh màn hình.")
            return None
        
    def preprocess_image(self,image_path):
        img = Image.open(image_path)
        img = img.convert("L")  # Chuyển về grayscale
        img = img.filter(ImageFilter.SHARPEN)  # Làm sắc nét
        return img

    def get_red_text(self, image_path, status="", timeout=None):
        start_time = time.time()
        
        while True:
            if timeout and (time.time() - start_time > timeout):
                print(f"[!] Hết thời gian chờ ({timeout}s)")
                self.wait_time += 1
                return True
            
            if self.wait_time == 3:
                print("[!] Đã thử 3 lần mà không nhận được kết quả, thoát.")
                self.error_message = "Đổi mail bằng tay"
                return False
                
            try:
                self.capture_screen(image_path)
                img = self.preprocess_image(image_path)
                text = pytesseract.image_to_string(img, lang='vie')
                if status == "dane":
                    if "Đăng" in text:
                        self.error_message = "Lỗi 681"
                        return False
                if status in text:
                    return True
                time.sleep(1)
            except Exception as e:
                print("[!] Lỗi khi đọc ảnh OCR:", e)
                self.error_message = f"Lỗi OCR: {str(e)}"
                return False

    def input(self,text):
        command = fr'{self.ldplayer_path}\\adb.exe -s {self.DEVICE()[self.stt_ldplayer]} shell input text {text}'
        self.adb_command(command)
        sleep(2)

    def click(self,x,y):
        command = fr'{self.ldplayer_path}\\adb.exe -s {self.DEVICE()[self.stt_ldplayer]} shell input tap {x} {y}'
        self.adb_command(command)
        sleep(2)

    def clear_text(self):
        """Clear text in active input field using Ctrl+A and Delete"""
        try:
            # Press Ctrl+A to select all text
            subprocess.run([
                f"{self.ldplayer_path}/adb.exe", 
                "shell", "input keyevent KEYCODE_A --longpress"
            ], capture_output=True)
            
            # Press Delete/Backspace to remove selected text
            subprocess.run([
                f"{self.ldplayer_path}/adb.exe",
                "shell", "input keyevent KEYCODE_DEL"
            ], capture_output=True)
            
            time.sleep(0.5) # Đợi chút để đảm bảo text đã được xóa
            
        except Exception as e:
            print(f"[!] Lỗi khi xóa text: {str(e)}")

    def cachefacebook(self):
        command = fr'{self.ldplayer_path}\\adb.exe -s {self.DEVICE()[self.stt_ldplayer]} shell pm clear com.facebook.lite'
        self.adb_command(command)

    def install_facebook(self):
        apk_path = r'apk\Facebook_Lite.apk'
        command = fr'{self.ldplayer_path}\\adb.exe -s {self.DEVICE()[self.stt_ldplayer]} install {apk_path}'
        self.adb_command(command)

    def adb_command(self,command):
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
    
    def get_code(self):
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
            response = requests.post(url, headers=headers, json=data, timeout=120)
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

    def main(self):
        try:
            success = False
            error_msg = ""
            # Mở LDPlayer và Facebook
            device_id = self.open_ldplayer()
            print(f"Đang mở Facebook Lite trên device: {device_id}")
            self.openfb()
            # Kiểm tra và nhập thông tin đăng nhập
            if self.get_red_text(f"ldplayer/ldplayer_screen{self.stt_ldplayer}.png", 'email'):
                print("Đang nhập thông tin đăng nhập...")
                # Nhập username
                self.click(140, 250)
                self.input(self.account['uid'])
                # Nhập password
                self.click(140, 350)
                self.input(self.account['password'])
                # Click đăng nhập
                self.click(140, 450)
                sleep(2)
                if self.get_red_text(f"ldplayer/ldplayer_screen{self.stt_ldplayer}.png", "dane", timeout=30):
                    print("Đang xử lý bước xác nhận...")
                    self.click(140, 625)
                    if self.get_red_text(f"ldplayer/ldplayer_screen{self.stt_ldplayer}.png", "Facebooka?", timeout=30):
                        self.click(140, 600)
                        if self.get_red_text(f"ldplayer/ldplayer_screen{self.stt_ldplayer}.png", "obserwowania", timeout=30):
                            self.click(140, 630)
                            if self.get_red_text(f"ldplayer/ldplayer_screen{self.stt_ldplayer}.png", "e-mail", timeout=30):
                                print("Đang nhập email mới...")
                                self.click(140, 500)
                                sleep(2)
                                self.clear_text() # Thêm bước xóa text
                                self.input(self.account['new_email'].split('|')[0])
                                self.click(140, 650)
                                if self.get_red_text(f"ldplayer/ldplayer_screen{self.stt_ldplayer}.png", "e-maila", timeout=30):
                                    print("Đang lấy và nhập mã xác nhận...")
                                    code = self.get_code()
                                    if code:
                                        sleep(2)
                                        self.click(140, 400)
                                        sleep(2)
                                        self.input(code)
                                        sleep(2)
                                        self.click(140, 570)
                                        if self.get_red_text(f"ldplayer/ldplayer_screen{self.stt_ldplayer}.png", "Settings"):
                                            print("Thay đổi email thành công!")
                                            success = True
                                            error_msg = "Thay đổi email thành công!"  # Thêm thông báo thành công
                                            self.close()
                                            return success, error_msg
                                    else:
                                        if self.get_red_text(f"ldplayer/ldplayer_screen{self.stt_ldplayer}.png", "Settings"):
                                            print("Thay đổi email thành công!")
                                            success = True 
                                            error_msg = "Thay đổi email thành công!"  # Thêm thông báo thành công
                                            self.close()
                                            return success, error_msg
                                else:
                                    print(f"Lỗi: {self.error_message}")
                                    self.close()
                                    return False, self.error_message
                            else:
                                print(f"Lỗi: {self.error_message}")
                                self.close()
                                return False, self.error_message
                        else:
                            print(f"Lỗi: {self.error_message}")
                            self.close()
                            return False, self.error_message
                    else:
                        print(f"Lỗi: {self.error_message}")
                        self.close()
                        return False, self.error_message
                else:
                    print(f"Lỗi: {self.error_message}")
                    self.close()
                    return False, self.error_message
        except Exception as e:
            print(f"Lỗi trong quá trình thực hiện: {str(e)}")
            self.close()
            return False

# LDPlayerRunner().main()
        

        # Chạy LDPlayer với ID máy ảo
    # def run_ldplayer(self):
    #     # Command to run LDPlayer with the specified settings
    #     command = [
    #         f"{self.settings.ldplayer_path}/ldconsole.exe",
    #         "launch",
    #         "--cpu", str(self.settings.cpu),
    #         "--ram", str(self.settings.ram),
    #         "--width", str(self.settings.width),
    #         "--height", str(self.settings.height),
    #         "--dpi", str(self.settings.dpi),
    #         "--adb", self.settings.ADB
    #     ]
        
    #     # Execute the command
    #     subprocess.run(command, check=True)