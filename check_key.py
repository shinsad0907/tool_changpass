from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
                           QTreeWidget, QTreeWidgetItem, QLabel, QFrame, QCheckBox, QRadioButton,
                           QComboBox, QSpinBox, QPushButton, QHeaderView, QMenu, QAction, QGroupBox,
                           QLineEdit, QMessageBox, QFileDialog)
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import base64
from supabase import create_client
import os
import json
import sys
import uuid
import psutil


class KeyInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nhập Key Kích Hoạt")
        self.setFixedSize(350, 120)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Vui lòng nhập key để sử dụng phần mềm:"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Nhập key tại đây...")
        layout.addWidget(self.key_input)
        self.ok_btn = QPushButton("Xác nhận")
        self.ok_btn.clicked.connect(self.accept)
        layout.addWidget(self.ok_btn)

    def get_key(self):
        return self.key_input.text().strip()
base_url = "https://cgogqyorfzpxaiotscfp.supabase.co"
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNnb2dxeW9yZnpweGFpb3RzY2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5ODMyMzcsImV4cCI6MjA2MzU1OTIzN30.enehR9wGHJf1xKO7d4XBbmjfdm80EvBKzaaPO3NPVAM'
supabase = create_client(base_url, token)

def decode(key):
    decoded = base64.urlsafe_b64decode(key.encode()).decode()
    data = json.loads(decoded)
    return data["secret"], data["user"], data["rand"]

def check_version(key,id_product, version_client):
    res = supabase.table("PRODUCTS").select("*").execute()
    for data in res.data:
        if data['id'] == id_product:
            if data['version_client'] == version_client:
                return True
            else:
                return False
            

def get_mac():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family.name == 'AF_LINK':
                mac = addr.address
                # Lọc địa chỉ hợp lệ, bỏ qua MAC trống hoặc local-loopback
                if mac and mac != '00:00:00:00:00:00' and not interface.lower().startswith(('lo', 'vir', 'vm', 'docker')):
                    return mac
    return None  # nếu không tìm được MAC phù hợp



def check_key(key):
    version_client_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version_client.json")
    try:
        secret, user_id, rand = decode(key)
    except Exception:
        QMessageBox.critical(None, "Lỗi", "Key không hợp lệ (decode lỗi)!")
        return False
    res = supabase.table("data_user").select("*").execute()
    today = datetime.today().date()
    for data in res.data:
        if data['username'] == user_id:
            purchases = data['purchases']
            uid_mac = data['ip_mac']
            print("uid_mac:", uid_mac)
            for data_purchase in purchases:
                print(data_purchase['key'], key)
                if data_purchase['key'] == key:
                    print("Key:", key)
                    print("User ID:", user_id)
                    date_key_part = data_purchase.get('date_key_part')
                    id_product = data_purchase.get('product_id')
                    with open(version_client_path, 'r', encoding='utf-8-sig') as f:
                        version_client_data = json.load(f)
                    version_client = version_client_data.get('version_client')

                    if not date_key_part:
                        QMessageBox.critical(None, "Lỗi", "Không tìm thấy ngày hết hạn trong key!")
                        return False
                    try:
                        expire_date = datetime.strptime(date_key_part, "%Y-%m-%d").date()
                    except Exception:
                        QMessageBox.critical(None, "Lỗi", f"Không đọc được ngày hết hạn! (Giá trị: {date_key_part})")
                        return False
                    if expire_date < today:
                        QMessageBox.critical(None, "Lỗi", "Key đã hết hạn sử dụng!")
                        return False
                    else:
                        # ...existing code...
                        if check_version(key,id_product, version_client):
                            current_mac = get_mac()
                            if uid_mac is None:
                                # Trường hợp chưa có ip_mac, cập nhật ip_mac mới
                                supabase.table("data_user").update({"ip_mac": current_mac}).eq("username", user_id).execute()
                                QMessageBox.information(None, "Thông báo", "Key đã được kích hoạt thành công!")
                                return True
                            elif uid_mac == current_mac:
                                # Trường hợp ip_mac trùng khớp
                                QMessageBox.information(None, "Thông báo", "Key đã được kích hoạt thành công!")
                                return True
                            else:
                                # Trường hợp ip_mac không khớp
                                QMessageBox.critical(None, "Lỗi", "Key đã được kích hoạt trên thiết bị khác!")
                                return False
                        else:
                            QMessageBox.critical(None, "Lỗi", "Phiên bản client không tương thích với key!")
                            return False
                        # ...existing code...
                else:
                    QMessageBox.critical(None, "Lỗi", "Key không hợp lệ!")
                    return False
    # Nếu không tìm thấy user
    QMessageBox.critical(None, "Lỗi", "Key không hợp lệ!")
    return False


def get_or_create_key(parent=None):
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "key.json")
    key = None
    # Nếu đã có file key.json thì đọc key
    if os.path.exists(key_path):
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                key = data.get("key")
            if check_key(key):
                return key  # Trả về key hợp lệ
            else:
                os.remove(key_path)  # Xóa file key nếu không hợp lệ
                sys.exit()  # Thoát luôn
        except Exception:
            key = None
    # Nếu chưa có thì hiện dialog nhập key
    while not key:
        dialog = KeyInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            key = dialog.get_key()
            print("Key nhập vào:", key)
            if key:
                # Lưu key vào file
                if check_key(key):
                    with open(key_path, "w", encoding="utf-8") as f:
                        json.dump({"key": key}, f, ensure_ascii=False, indent=2)
                    return key  # Trả về key hợp lệ
                else:
                    key = None  # Nhập sai thì lặp lại
            else:
                QMessageBox.warning(parent, "Thiếu key", "Bạn phải nhập key để tiếp tục!")
        else:
            sys.exit()  # Thoát nếu người dùng bấm hủy
    return key
