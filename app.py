# code by voletrieulan hahahaha
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
                           QTreeWidget, QTreeWidgetItem, QLabel, QFrame, QCheckBox, QRadioButton,
                           QComboBox, QSpinBox, QPushButton, QHeaderView, QMenu, QAction, QGroupBox,
                           QLineEdit, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QScrollArea)

from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QCursor, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import pyperclip
import os
import json
import sys
from worker_module import WorkerThread
from check_key import get_or_create_key
from PyQt5.QtCore import QSettings
from botnet import botnet

class UpdateDialog(QDialog):
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎉 Thông tin cập nhật mới!")
        self.setFixedWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QLabel#version {
                font-size: 18px;
                font-weight: bold;
                color: #2980b9;
            }
            QLabel#date {
                font-style: italic;
                color: #7f8c8d;
            }
        """)

        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()
        version_label = QLabel(f"Phiên bản {update_info['version']}")
        version_label.setObjectName("version")
        date_label = QLabel(f"Cập nhật ngày: {update_info['last_update']}")
        date_label.setObjectName("date")
        header.addWidget(version_label)
        header.addStretch()
        header.addWidget(date_label)
        layout.addLayout(header)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #bdc3c7;")
        layout.addWidget(line)

        # Changelog content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        for section in update_info['changelog']:
            # Section title
            title = QLabel(section['title'])
            title.setStyleSheet("""
                font-size: 15px;
                font-weight: bold;
                color: #e74c3c;
                margin-top: 10px;
            """)
            content_layout.addWidget(title)

            # Section items
            for item in section['items']:
                item_label = QLabel(item)
                item_label.setWordWrap(True)
                item_label.setStyleSheet("margin-left: 20px;")
                content_layout.addWidget(item_label)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        layout.addWidget(scroll)

        # Don't show again checkbox
        self.dont_show = QCheckBox("Không hiển thị lại thông báo này")
        self.dont_show.setStyleSheet("""
            QCheckBox {
                color: #7f8c8d;
            }
        """)
        layout.addWidget(self.dont_show)

        # Close button
        close_btn = QPushButton("Đã hiểu")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

class SoftwareInstallDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cài đặt phần mềm")
        self.setFixedWidth(400)
        layout = QVBoxLayout(self)

        # Software list group
        software_group = QGroupBox("Danh sách phần mềm cần thiết")
        software_layout = QVBoxLayout()

        # Add software items
        self.software_items = [
            {
                "name": "LDPlayer",
                "description": "Giả lập Android để chạy tool",
                "url": "https://res.ldrescdn.com/download/LDPlayer9.exe?n=LDPlayer9_ens_1001_ld.exe",
                "installed": False
            },
            {
                "name": "Tesseract OCR", 
                "description": "Công cụ nhận dạng text",
                "url": "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe",
                "installed": False
            },
        ]

        for software in self.software_items:
            item_layout = QHBoxLayout()
            
            # Software info
            info_layout = QVBoxLayout()
            name_label = QLabel(f"<b>{software['name']}</b>")
            desc_label = QLabel(software['description'])
            desc_label.setStyleSheet("color: #666;")
            info_layout.addWidget(name_label)
            info_layout.addWidget(desc_label)

            # Status and buttons
            button_layout = QVBoxLayout()
            install_btn = QPushButton("Cài đặt")
            install_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    padding: 5px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            install_btn.clicked.connect(lambda checked, url=software['url']: self.open_download_link(url))

            button_layout.addWidget(install_btn)

            # Add to item layout
            item_layout.addLayout(info_layout, stretch=2)
            item_layout.addLayout(button_layout, stretch=1)
            
            software_layout.addLayout(item_layout)
            software_layout.addWidget(QFrame(frameShape=QFrame.HLine))

        software_group.setLayout(software_layout)
        layout.addWidget(software_group)

        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def open_download_link(self, url):
        import webbrowser
        webbrowser.open(url)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin hỗ trợ")
        self.setFixedWidth(400)
        layout = QVBoxLayout(self)
        
        # Support info group
        support_group = QGroupBox("Thông tin liên hệ")
        support_layout = QVBoxLayout()
        
        # Facebook
        fb_layout = QHBoxLayout()
        fb_label = QLabel("Facebook:")
        fb_link = QLabel('<a href="https://www.facebook.com/shinsad.copyright.97">shinsad.copyright.97</a>')
        fb_link.setOpenExternalLinks(True)
        fb_layout.addWidget(fb_label)
        fb_layout.addWidget(fb_link)
        fb_layout.addStretch()
        
        # Zalo
        zalo_layout = QHBoxLayout()
        zalo_label = QLabel("Zalo:")
        zalo_number = QLabel("0916733227")  # Thay số điện thoại thật
        zalo_layout.addWidget(zalo_label)
        zalo_layout.addWidget(zalo_number)
        zalo_layout.addStretch()
        
        # Website
        web_layout = QHBoxLayout()
        web_label = QLabel("Website:")
        web_link = QLabel('<a href="https://web-mmo-blush.vercel.app">Web hỗ trợ phần mềm</a>')  # Thay URL thật
        web_link.setOpenExternalLinks(True)
        web_layout.addWidget(web_label)
        web_layout.addWidget(web_link)
        web_layout.addStretch()
        
        support_layout.addLayout(fb_layout)
        support_layout.addLayout(zalo_layout)
        support_layout.addLayout(web_layout)
        support_group.setLayout(support_layout)
        
        # Instructions group
        instructions_group = QGroupBox("Hướng dẫn sử dụng")
        instructions_layout = QVBoxLayout()
        instructions_text = QLabel(
            "1. Nhập danh sách tài khoản cần xử lý\n"
            "2. Chọn cấu hình phù hợp\n"
            "3. Nhấn START để bắt đầu\n"
            "4. Export kết quả khi hoàn thành\n\n"
            "* Liên hệ hỗ trợ nếu gặp lỗi"
        )
        instructions_layout.addWidget(instructions_text)
        instructions_group.setLayout(instructions_layout)
        
        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        
        # Add to main layout
        layout.addWidget(support_group)
        layout.addWidget(instructions_group)
        layout.addWidget(close_btn)

class ChangeMailSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cài đặt nâng cao LDPlayer")
        self.setFixedWidth(350)
        layout = QVBoxLayout(self)

        # Path LDPlayer
        ld_layout = QHBoxLayout()
        ld_label = QLabel("Path LDPlayer:")
        self.ld_path_input = QLineEdit()
        self.ld_path_input.setPlaceholderText("C:\\LDPlayer\\LDPlayer.exe")
        ld_btn = QPushButton("...")
        ld_btn.setFixedWidth(30)
        ld_btn.clicked.connect(self.browse_ld_path)
        ld_layout.addWidget(ld_label)
        ld_layout.addWidget(self.ld_path_input)
        ld_layout.addWidget(ld_btn)
        layout.addLayout(ld_layout)

        # Path pytesseract
        tess_layout = QHBoxLayout()
        tess_label = QLabel("Path pytesseract:")
        self.tess_path_input = QLineEdit()
        self.tess_path_input.setPlaceholderText("C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
        tess_btn = QPushButton("...")
        tess_btn.setFixedWidth(30)
        tess_btn.clicked.connect(self.browse_tess_path)
        tess_layout.addWidget(tess_label)
        tess_layout.addWidget(self.tess_path_input)
        tess_layout.addWidget(tess_btn)
        layout.addLayout(tess_layout)

        # CPU
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU:")
        self.cpu_spin = QSpinBox()
        self.cpu_spin.setRange(1, 16)
        self.cpu_spin.setValue(2)
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_spin)
        layout.addLayout(cpu_layout)

        # RAM
        ram_layout = QHBoxLayout()
        ram_label = QLabel("RAM (MB):")
        self.ram_spin = QSpinBox()
        self.ram_spin.setRange(512, 32768)
        self.ram_spin.setSingleStep(512)
        self.ram_spin.setValue(2048)
        ram_layout.addWidget(ram_label)
        ram_layout.addWidget(self.ram_spin)
        layout.addLayout(ram_layout)

        # DPI
        dpi_layout = QHBoxLayout()
        dpi_label = QLabel("DPI:")
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(120, 640)
        self.dpi_spin.setValue(240)
        dpi_layout.addWidget(dpi_label)
        dpi_layout.addWidget(self.dpi_spin)
        layout.addLayout(dpi_layout)

        # Width
        width_layout = QHBoxLayout()
        width_label = QLabel("Width:")
        self.width_spin = QSpinBox()
        self.width_spin.setRange(400, 3840)
        self.width_spin.setValue(350)
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_spin)
        layout.addLayout(width_layout)

        # Height
        height_layout = QHBoxLayout()
        height_label = QLabel("Height:")
        self.height_spin = QSpinBox()
        self.height_spin.setRange(400, 2160)
        self.height_spin.setValue(750)
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_spin)
        layout.addLayout(height_layout)

        # Nút lưu
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

    def browse_ld_path(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục LDPlayer")
        if dir_path:
            self.ld_path_input.setText(dir_path)

    def browse_tess_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file pytesseract", "", "Executable (*.exe)")
        if file_path:
            self.tess_path_input.setText(file_path)
    
    def accept(self):
        ld_path = self.ld_path_input.text()
        tess_path = self.tess_path_input.text()
        cpu = self.cpu_spin.value()
        ram = self.ram_spin.value()
        dpi = self.dpi_spin.value()
        width = self.width_spin.value()
        height = self.height_spin.value()

        config_info = {
            "ld_path": ld_path,
            "tess_path": tess_path,
            "cpu": cpu,
            "ram": ram,
            "dpi": dpi,
            "width": width,
            "height": height,
            "CACHE": "1",
            "OTHER": "1",
            "ADB": "1"
        }

        with open('setting_ldplayer.json', 'w', encoding='utf-8') as f:
            json.dump(config_info, f, ensure_ascii=False, indent=4)
        QMessageBox.information(self, "Thông báo", "Cài đặt đã được lưu thành công!")
        super().accept()

class MailToolApp(QMainWindow):

    def __init__(self):
        super().__init__()
        
        try:
            key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "key.json")
            key = None
            # Nếu đã có file key.json thì đọc key
            if os.path.exists(key_path):
                with open(key_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_key = data.get("key", "")

        except:
            self.current_key = ''
        self.setWindowTitle(" Đổi Pass - Đổi Mail - Quên Pass - web-mmo-blush.vercel.app - Shin Tools - FB: shinsad.copyright.97")
        self.setGeometry(100, 100, 1100, 700)  # Tăng width và height
        self.setStyleSheet("background-color: #d9e1f2;")
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.tab_change_pass = QWidget()
        self.tab_change_mail = QWidget()
        self.tab_forgot_pass = QWidget()
        
        self.tab_widget.addTab(self.tab_change_pass, "Đổi Pass")
        self.tab_widget.addTab(self.tab_change_mail, "Đổi Mail")
        self.tab_widget.addTab(self.tab_forgot_pass, "Quên Pass")
        
        # Setup the Đăng Nhập tab
        self.setup_change_pass_tab()
        self.setup_change_mail_tab()
        self.setup_forgot_pass_tab()
        
        # Set the login tab as active
        self.tab_widget.setCurrentWidget(self.tab_change_mail)
        self.tab_widget.setCurrentWidget(self.tab_forgot_pass)
        self.tab_widget.setCurrentWidget(self.tab_change_pass)

        
        # Create footer
        self.create_footer(main_layout)
        
        # Worker thread


        self.worker_thread = None

    def setup_forgot_pass_tab(self):
    # Main layout for the tab
        forgot_pass_layout = QVBoxLayout(self.tab_forgot_pass)
        forgot_pass_layout.setContentsMargins(10, 10, 10, 10)
        
        # Email list tree widget
        self.forgot_pass_tree_widget = QTreeWidget()
        self.forgot_pass_tree_widget.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.forgot_pass_tree_widget.setAlternatingRowColors(True)
        self.forgot_pass_tree_widget.setSelectionMode(QTreeWidget.ExtendedSelection)
        
        # Set headers for the tree widget
        headers = ["###", "STT", "MAIL", "PROXY", "STATUS"]
        self.forgot_pass_tree_widget.setColumnCount(len(headers))
        self.forgot_pass_tree_widget.setHeaderLabels(headers)
        
        # Adjust column widths
        self.forgot_pass_tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.forgot_pass_tree_widget.header().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Style the header
        self.forgot_pass_tree_widget.setStyleSheet("""
            QTreeWidget::item:selected { background-color: #107bd2; color: white; }
            QTreeWidget::item { height: 25px; }
            QHeaderView::section { background-color: #d9e1f2; padding: 4px; }
        """)
        
        # Enable context menu
        self.forgot_pass_tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.forgot_pass_tree_widget.customContextMenuRequested.connect(self.show_forgot_pass_context_menu)
        
        forgot_pass_layout.addWidget(self.forgot_pass_tree_widget)
        
        # Add "Đã chọn" label
        self.forgot_pass_selection_label = QLabel("Đã chọn: 0")
        self.forgot_pass_selection_label.setAlignment(Qt.AlignRight)
        forgot_pass_layout.addWidget(self.forgot_pass_selection_label)
        
        # Create bottom section
        bottom_layout = QHBoxLayout()
        
        # Info section
        data_group = QGroupBox("INFO")
        data_layout = QVBoxLayout(data_group)
        
        # Create info labels
        self.forgot_pass_total_label = QLabel("0")
        self.forgot_pass_proxy_label = QLabel("1")
        self.forgot_pass_success_label = QLabel("0")
        self.forgot_pass_fail_label = QLabel("0")
        
        data_items = [
            ("Tổng Mail:", self.forgot_pass_total_label),
            ("Tổng Proxy:", self.forgot_pass_proxy_label),
            ("Thành công:", self.forgot_pass_success_label),
            ("Thất bại:", self.forgot_pass_fail_label)
        ]
        
        for label_text, value_label in data_items:
            row_layout = QHBoxLayout()
            label = QLabel(label_text)
            row_layout.addWidget(label)
            row_layout.addWidget(value_label)
            row_layout.addStretch()
            data_layout.addLayout(row_layout)
        
        bottom_layout.addWidget(data_group)
        
        # Settings section
        settings_group = QGroupBox("CẤU HÌNH")
        settings_layout = QVBoxLayout(settings_group)
        
        # Proxy configuration
        proxy_layout = QHBoxLayout()
        self.forgot_pass_proxy_check = QCheckBox("Dùng Proxy:")
        self.forgot_pass_proxy_check.setChecked(True)
        self.forgot_pass_proxy_combo = QComboBox()
        self.forgot_pass_proxy_combo.addItems(["Tmproxy.com", "ProxyV6", "911S5", "ShopLike"])
        proxy_layout.addWidget(self.forgot_pass_proxy_check)
        proxy_layout.addWidget(self.forgot_pass_proxy_combo)
        settings_layout.addLayout(proxy_layout)

        browser_group = QGroupBox("Trình duyệt")
        browser_layout = QVBoxLayout(browser_group)

        # Radio buttons for browser selection
        browser_radio_layout = QHBoxLayout()
        self.forgot_pass_chrome_radio = QRadioButton("Chrome")
        self.forgot_pass_edge_radio = QRadioButton("Edge")
        self.forgot_pass_chrome_radio.setChecked(True)  # Default to Chrome
        browser_radio_layout.addWidget(self.forgot_pass_chrome_radio)
        browser_radio_layout.addWidget(self.forgot_pass_edge_radio)
        browser_layout.addLayout(browser_radio_layout)

        # Edge driver path input
        edge_path_layout = QHBoxLayout()
        edge_path_label = QLabel("MSEdgeDriver path:")
        self.forgot_pass_edge_path_input = QLineEdit()
        self.forgot_pass_edge_path_input.setPlaceholderText("C:\\Path\\To\\msedgedriver.exe")
        self.forgot_pass_edge_path_input.setEnabled(False)  # Disabled by default
        edge_browse_btn = QPushButton("...")
        edge_browse_btn.setFixedWidth(30)
        edge_browse_btn.setEnabled(False)  # Disabled by default

        edge_path_layout.addWidget(edge_path_label)
        edge_path_layout.addWidget(self.forgot_pass_edge_path_input)
        edge_path_layout.addWidget(edge_browse_btn)
        browser_layout.addLayout(edge_path_layout)

        # Connect radio buttons to handler
        def on_browser_changed():
            is_edge = self.forgot_pass_edge_radio.isChecked()
            self.forgot_pass_edge_path_input.setEnabled(is_edge)
            edge_browse_btn.setEnabled(is_edge)
            if not is_edge:
                self.forgot_pass_edge_path_input.clear()

        self.forgot_pass_chrome_radio.toggled.connect(on_browser_changed)
        self.forgot_pass_edge_radio.toggled.connect(on_browser_changed)

        # Connect browse button
        def browse_edge_driver():
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select MSEdgeDriver",
                "",
                "Executable (*.exe)"
            )
            if file_path:
                self.forgot_pass_edge_path_input.setText(file_path)

        edge_browse_btn.clicked.connect(browse_edge_driver)

        # Add browser group to settings
        settings_layout.addWidget(browser_group)
        
        # # Password configuration
        # pass_layout = QHBoxLayout()
        # pass_label = QLabel("Mật khẩu mới:")
        # self.forgot_pass_type_combo = QComboBox()
        # self.forgot_pass_type_combo.addItems(["Tự nhập", "Ngẫu nhiên"])
        # pass_layout.addWidget(pass_label)
        # pass_layout.addWidget(self.forgot_pass_type_combo)
        # settings_layout.addLayout(pass_layout)
        
        # # Password input
        # self.forgot_pass_input = QLineEdit()
        # self.forgot_pass_input.setPlaceholderText("Nhập mật khẩu mới")
        # settings_layout.addWidget(self.forgot_pass_input)
        
        # Thread configuration
        thread_layout = QHBoxLayout()
        thread_label = QLabel("Số luồng:")
        self.forgot_pass_thread_spin = QSpinBox()
        self.forgot_pass_thread_spin.setValue(5)
        self.forgot_pass_thread_spin.setRange(1, 20)
        thread_layout.addWidget(thread_label)
        thread_layout.addWidget(self.forgot_pass_thread_spin)
        settings_layout.addLayout(thread_layout)
        
        bottom_layout.addWidget(settings_group)
        
        # Action buttons
        action_layout = QVBoxLayout()
        file_output_label = QLabel("File Output")
        file_output_label.setAlignment(Qt.AlignCenter)
        
        self.forgot_pass_start_button = QPushButton("START")
        self.forgot_pass_start_button.setStyleSheet("background-color: #90ee90; color: black; min-height: 25px;")
        self.forgot_pass_start_button.clicked.connect(self.start_forgot_pass_processing)
        
        self.forgot_pass_stop_button = QPushButton("STOP")
        self.forgot_pass_stop_button.setStyleSheet("background-color: #ff9999; color: black; min-height: 25px;")
        self.forgot_pass_stop_button.clicked.connect(self.stop_forgot_pass_processing)
        self.forgot_pass_stop_button.setEnabled(False)
        
        self.forgot_pass_export_button = QPushButton("Export File")
        self.forgot_pass_export_button.setStyleSheet("background-color: #87ceeb; color: black; min-height: 25px;")
        self.forgot_pass_export_button.clicked.connect(self.export_forgot_pass_data)
        
        action_layout.addWidget(file_output_label)
        action_layout.addWidget(self.forgot_pass_start_button)
        action_layout.addWidget(self.forgot_pass_stop_button)
        action_layout.addWidget(self.forgot_pass_export_button)
        action_layout.addStretch()
        
        bottom_layout.addLayout(action_layout)
        forgot_pass_layout.addLayout(bottom_layout)

    def show_forgot_pass_context_menu(self, position):
        context_menu = QMenu()
        
        add_mail_action = QAction("Nhập Mail", self)
        add_proxy_action = QAction("Nhập Proxy", self)
        select_all_action = QAction("Chọn tất cả", self)
        deselect_all_action = QAction("Bỏ chọn tất cả", self)
        select_errors_action = QAction("Chọn tài khoản lỗi", self)
        delete_mail_action = QAction("Xóa mail", self)
        
        context_menu.addAction(add_mail_action)
        context_menu.addAction(add_proxy_action)
        context_menu.addSeparator()
        context_menu.addAction(select_all_action)
        context_menu.addAction(deselect_all_action)
        context_menu.addAction(select_errors_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_mail_action)
        
        add_mail_action.triggered.connect(self.add_forgot_pass_mail)
        # add_proxy_action.triggered.connect(self.add_forgot_pass_proxy)
        select_all_action.triggered.connect(self.select_all_forgot_pass)
        deselect_all_action.triggered.connect(self.deselect_all_forgot_pass)
        select_errors_action.triggered.connect(self.select_errors_forgot_pass)
        delete_mail_action.triggered.connect(self.delete_forgot_pass_mail)
        
        context_menu.exec_(QCursor.pos())

    def update_forgot_pass_counts(self):
        # Update total count
        total_count = self.forgot_pass_tree_widget.topLevelItemCount()
        self.forgot_pass_total_label.setText(str(total_count))
        
        # Count selected items
        selected_count = 0
        success_count = 0
        fail_count = 0
        
        for i in range(total_count):
            item = self.forgot_pass_tree_widget.topLevelItem(i)
            checkbox = self.forgot_pass_tree_widget.itemWidget(item, 0)
            
            # Count checked items
            if checkbox and checkbox.isChecked():
                selected_count += 1
                
            # Count success/fail based on status
            status = item.text(4).lower()
            if "thành công" in status:
                success_count += 1
            elif "thất bại" in status:
                fail_count += 1
        
        # Update labels
        self.forgot_pass_selection_label.setText(f"Đã chọn: {selected_count}")
        self.forgot_pass_success_label.setText(str(success_count))
        self.forgot_pass_fail_label.setText(str(fail_count))

    def select_all_forgot_pass(self):
        # Select all items in forgot password tab
        for i in range(self.forgot_pass_tree_widget.topLevelItemCount()):
            item = self.forgot_pass_tree_widget.topLevelItem(i)
            checkbox = self.forgot_pass_tree_widget.itemWidget(item, 0)
            if checkbox:
                checkbox.setChecked(True)
        self.update_forgot_pass_counts()

    def deselect_all_forgot_pass(self):
        # Deselect all items in forgot password tab
        for i in range(self.forgot_pass_tree_widget.topLevelItemCount()):
            item = self.forgot_pass_tree_widget.topLevelItem(i)
            checkbox = self.forgot_pass_tree_widget.itemWidget(item, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.update_forgot_pass_counts()

    def select_errors_forgot_pass(self):
        # Select items with error status in forgot password tab
        for i in range(self.forgot_pass_tree_widget.topLevelItemCount()):
            item = self.forgot_pass_tree_widget.topLevelItem(i)
            if "thất bại" in item.text(4).lower():  # Check STATUS column
                checkbox = self.forgot_pass_tree_widget.itemWidget(item, 0)
                if checkbox:
                    checkbox.setChecked(True)
        self.update_forgot_pass_counts()

    def delete_forgot_pass_mail(self):
        # Delete selected items in forgot password tab
        selected_items = []
        for i in range(self.forgot_pass_tree_widget.topLevelItemCount()):
            item = self.forgot_pass_tree_widget.topLevelItem(i)
            checkbox = self.forgot_pass_tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                selected_items.append(item)
        
        if not selected_items:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn email cần xóa!")
            return
        
        # Remove selected items
        for item in selected_items:
            index = self.forgot_pass_tree_widget.indexOfTopLevelItem(item)
            self.forgot_pass_tree_widget.takeTopLevelItem(index)
        
        # Update counts
        self.update_forgot_pass_counts()

    def add_forgot_pass_mail(self):
        # Lấy nội dung từ clipboard
        copied_text = pyperclip.paste().strip()
        if not copied_text:
            QMessageBox.warning(self, "Cảnh báo", "Clipboard trống!")
            return
            
        # Khởi tạo số thứ tự bắt đầu
        start_index = self.forgot_pass_tree_widget.topLevelItemCount()
        
        try:
            # Xử lý từng dòng email
            for i, email in enumerate(copied_text.split('\n')):
                email = email.strip()
                if email:  # Kiểm tra email không rỗng
                    item = QTreeWidgetItem(self.forgot_pass_tree_widget)
                    
                    # Tạo checkbox và đặt vào cột đầu tiên
                    checkbox = QCheckBox()
                    checkbox.setChecked(True)
                    self.forgot_pass_tree_widget.setItemWidget(item, 0, checkbox)
                    
                    # Đặt các giá trị cho các cột
                    item.setText(1, str(start_index + i + 1))  # STT
                    item.setText(2, email)  # MAIL
                    item.setText(3, "")  # PROXY
                    item.setText(4, "")  # STATUS
            
            # Cập nhật số liệu
            self.update_forgot_pass_counts()
            
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Có lỗi xảy ra khi thêm mail: {str(e)}")

    def start_forgot_pass_processing(self):
        # Get checked items
        checked_items = []
        for i in range(self.forgot_pass_tree_widget.topLevelItemCount()):
            item = self.forgot_pass_tree_widget.topLevelItem(i)
            checkbox = self.forgot_pass_tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                item_data = {
                    "index": i,
                    "email": item.text(2)
                }
                checked_items.append(item_data)
        
        # Validate selection
        if not checked_items:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một email để xử lý!")
            return

        # Get configuration
        proxy_enabled = self.forgot_pass_proxy_check.isChecked()
        proxy_type = self.forgot_pass_proxy_combo.currentText()
        num_threads = self.forgot_pass_thread_spin.value()

        # Create worker thread
        self.forgot_pass_worker = WorkerThread(num_threads)
        
        # Connect signals
        self.forgot_pass_worker.update_status.connect(self.update_forgot_pass_status)
        self.forgot_pass_worker.update_counts.connect(self.update_forgot_pass_result_counts)

        # Update UI
        self.forgot_pass_start_button.setEnabled(False)
        self.forgot_pass_stop_button.setEnabled(True)

        # Collect all data
        all_items = []
        for i in range(self.forgot_pass_tree_widget.topLevelItemCount()):
            item = self.forgot_pass_tree_widget.topLevelItem(i)
            checkbox = self.forgot_pass_tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                item_data = {
                    "selected": True,
                    "stt": item.text(1),
                    "email": item.text(2),
                    "proxy": item.text(3),
                    "status": item.text(4)
                }
                all_items.append(item_data)

        # Thêm vào trong hàm start_forgot_pass_processing()
        # Trước khi tạo config_info:

        # Get browser configuration
        browser_type = "chrome" if self.forgot_pass_chrome_radio.isChecked() else "edge"
        edge_driver_path = self.forgot_pass_edge_path_input.text() if self.forgot_pass_edge_radio.isChecked() else ""

        # Validate Edge driver path if Edge is selected
        if browser_type == "edge" and not edge_driver_path:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn đường dẫn MSEdgeDriver!")
            return

        # Modify config_info to include browser settings
        config_info = {
            'account': all_items,
            'proxy': f"{'yes' if proxy_enabled else 'no'} ({proxy_type if proxy_enabled else ''})",
            'thread': num_threads,
            'type': 'forgot_pass',
            'browser': {
                'type': browser_type,
                'edge_driver_path': edge_driver_path
            }
        }

        # Save config
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(config_info, f, ensure_ascii=False, indent=4)

        # Start processing
        self.forgot_pass_worker.start()

    def stop_forgot_pass_processing(self):
        if self.forgot_pass_worker and self.forgot_pass_worker.isRunning():
            self.forgot_pass_worker.stop()
            self.forgot_pass_worker.wait()
            self.forgot_pass_worker = None
            
        self.forgot_pass_start_button.setEnabled(True)
        self.forgot_pass_stop_button.setEnabled(False)
        QMessageBox.information(self, "Thông báo", "Đã dừng xử lý quên mật khẩu!")

    def export_forgot_pass_data(self):
        # Get selected items
        selected_lines = []
        for i in range(self.forgot_pass_tree_widget.topLevelItemCount()):
            item = self.forgot_pass_tree_widget.topLevelItem(i)
            checkbox = self.forgot_pass_tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                email = item.text(2)
                status = item.text(4)
                line = f"{email}|{status}"
                selected_lines.append(line)

        if not selected_lines:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu được chọn để xuất!")
            return

        # Create default path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "output", f"forgot_pass_data_{timestamp}.txt")

        # Show save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu file TXT",
            default_path,
            "Text Files (*.txt)"
        )

        if not file_path:
            return

        # Write file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in selected_lines:
                    f.write(line + '\n')
            QMessageBox.information(self, "Thông báo", f"Đã xuất dữ liệu thành công!\nFile: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {str(e)}")

    def update_forgot_pass_status(self, item_index, password, status, cookie):
        if 0 <= item_index < self.forgot_pass_tree_widget.topLevelItemCount():
            item = self.forgot_pass_tree_widget.topLevelItem(item_index)
            item.setText(4, status)
            
            # Cập nhật màu nền
            color = QColor("#90ee90") if "thành công" in status.lower() else QColor("#ff9999")
            for col in range(item.columnCount()):
                item.setBackground(col, color) # Light red

    def update_forgot_pass_result_counts(self, success_count, fail_count):
        self.forgot_pass_success_label.setText(str(success_count))
        self.forgot_pass_fail_label.setText(str(fail_count))










# ===========================================================





    def setup_change_mail_tab(self):
        # Main layout for the tab
        layout = QVBoxLayout(self.tab_change_mail)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tree widget
        self.change_mail_tree_widget = QTreeWidget()
        self.change_mail_tree_widget.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.change_mail_tree_widget.setAlternatingRowColors(True)
        self.change_mail_tree_widget.setSelectionMode(QTreeWidget.ExtendedSelection)
        headers = ["###", "STT", "UID", "PASSWORD", "COOKIE", "MAIL CŨ", "MAIL MỚI", "PASSMAIL", "PROXY", "STATUS"]
        
        self.change_mail_tree_widget.setColumnCount(len(headers))
        self.change_mail_tree_widget.setHeaderLabels(headers)
        self.change_mail_tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.change_mail_tree_widget.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.change_mail_tree_widget.header().setSectionResizeMode(5, QHeaderView.Stretch)
        self.change_mail_tree_widget.setStyleSheet("""
            QTreeWidget::item:selected { background-color: #107bd2; color: white; }
            QTreeWidget::item { height: 25px; }
            QHeaderView::section { background-color: #d9e1f2; padding: 4px; }
        """)
        self.change_mail_tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.change_mail_tree_widget.customContextMenuRequested.connect(self.show_change_mail_context_menu)
        layout.addWidget(self.change_mail_tree_widget)

        # Đã chọn label
        self.change_mail_selection_label = QLabel("Đã chọn: 0")
        self.change_mail_selection_label.setAlignment(Qt.AlignRight)
        self.change_mail_selection_label.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.change_mail_selection_label)

        # Create bottom section (giống forgot pass)
        bottom_layout = QHBoxLayout()

        # Thống kê
        info_group = QGroupBox("THỐNG KÊ")
        info_layout = QVBoxLayout(info_group)
        self.change_mail_total_label = QLabel("0")
        self.change_mail_success_label = QLabel("0")
        self.change_mail_fail_label = QLabel("0")
        for text, label in [
            ("Tổng Mail:", self.change_mail_total_label),
            ("Thành công:", self.change_mail_success_label),
            ("Thất bại:", self.change_mail_fail_label)
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(text))
            row.addWidget(label)
            row.addStretch()
            info_layout.addLayout(row)

        # Hàng dưới cùng: Thống kê | Proxy | Số luồng | Nút thao tác | Nút Cài đặt
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(info_group)

        # Settings section
        settings_group = QGroupBox("CẤU HÌNH")
        settings_layout = QVBoxLayout(settings_group)

        # LDPlayer path
        ld_layout = QHBoxLayout()
        ld_label = QLabel("Path LDPlayer:")
        self.ld_path_input = QLineEdit()
        self.ld_path_input.setPlaceholderText("C:\\LDPlayer\\LDPlayer9")
        ld_btn = QPushButton("...")
        ld_btn.setFixedWidth(30)
        ld_btn.clicked.connect(self.browse_ld_path)
        open_ld_btn = QPushButton("Mở LDPlayer")
        open_ld_btn.setStyleSheet("background-color: #f7ca18; color: black; min-width: 100px;")
        open_ld_btn.clicked.connect(self.open_ldplayer)
        ld_layout.addWidget(ld_label)
        ld_layout.addWidget(self.ld_path_input)
        ld_layout.addWidget(ld_btn)
        ld_layout.addWidget(open_ld_btn)
        settings_layout.addLayout(ld_layout)

        # Proxy
        proxy_group = QGroupBox("Proxy & Luồng")
        proxy_layout = QVBoxLayout(proxy_group)
        proxy_row = QHBoxLayout()
        self.change_mail_proxy_check = QCheckBox("Dùng Proxy:")
        self.change_mail_proxy_check.setChecked(True)
        self.change_mail_proxy_combo = QComboBox()
        self.change_mail_proxy_combo.addItems(["Tmproxy.com", "ProxyV6", "911S5", "ShopLike"])
        proxy_row.addWidget(self.change_mail_proxy_check)
        proxy_row.addWidget(self.change_mail_proxy_combo)
        proxy_layout.addLayout(proxy_row)

        # Thread
        thread_row = QHBoxLayout()
        thread_label = QLabel("Số luồng:")
        self.change_mail_thread_spin = QSpinBox()
        self.change_mail_thread_spin.setValue(5)
        self.change_mail_thread_spin.setRange(1, 20)
        thread_row.addWidget(thread_label)
        thread_row.addWidget(self.change_mail_thread_spin)
        proxy_layout.addLayout(thread_row)

        bottom_layout.addWidget(proxy_group)

        # # Delay
        # delay_layout = QHBoxLayout()
        # delay_label = QLabel("Delay (giây):")
        # self.delay_spin = QSpinBox()
        # self.delay_spin.setValue(3)
        # self.delay_spin.setRange(1, 30)
        # delay_layout.addWidget(delay_label)
        # delay_layout.addWidget(self.delay_spin)
        # settings_layout.addLayout(delay_layout)

        bottom_layout.addWidget(settings_group)

        # Action buttons
        action_layout = QVBoxLayout()
        file_output_label = QLabel("File Output")
        file_output_label.setAlignment(Qt.AlignCenter)

        self.change_mail_start_button = QPushButton("START")
        self.change_mail_start_button.setStyleSheet("background-color: #90ee90; color: black; min-height: 25px;")
        self.change_mail_start_button.clicked.connect(self.start_change_mail_processing)

        self.change_mail_stop_button = QPushButton("STOP")
        self.change_mail_stop_button.setStyleSheet("background-color: #ff9999; color: black; min-height: 25px;")
        self.change_mail_stop_button.clicked.connect(self.stop_change_mail_processing)
        self.change_mail_stop_button.setEnabled(False)

        self.change_mail_export_button = QPushButton("Export File")
        self.change_mail_export_button.setStyleSheet("background-color: #87ceeb; color: black; min-height: 25px;")
        self.change_mail_export_button.clicked.connect(self.export_change_mail_data)

        self.change_mail_settings_button = QPushButton("Cài đặt")
        self.change_mail_settings_button.setStyleSheet("background-color: #f7ca18; color: black; min-width: 120px;")
        self.change_mail_settings_button.clicked.connect(self.show_change_mail_settings_dialog)

        self.software_install_button = QPushButton("Cài đặt phần mềm")
        self.software_install_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 3px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.software_install_button.clicked.connect(self.show_software_install_dialog)
         
    
        action_layout.addWidget(file_output_label)
        action_layout.addWidget(self.change_mail_start_button)
        action_layout.addWidget(self.change_mail_stop_button)
        action_layout.addWidget(self.change_mail_export_button)
        action_layout.addWidget(self.change_mail_settings_button)
        action_layout.addWidget(self.software_install_button)

        action_layout.addStretch()
        bottom_layout.addLayout(action_layout)
        layout.addLayout(bottom_layout)
        
    def show_software_install_dialog(self):
        dialog = SoftwareInstallDialog(self)
        dialog.exec_()

    def browse_ld_path(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục LDPlayer")
        if dir_path:
            self.ld_path_input.setText(dir_path)

    def toggle_email_format_input(self):
        self.email_format_input.setEnabled(self.custom_email_radio.isChecked())
        if self.custom_email_radio.isChecked():
            self.email_format_input.setStyleSheet("")
        else:
            self.email_format_input.setStyleSheet("background-color: #f0f0f0; color: #a0a0a0;")

    def show_change_mail_context_menu(self, position):
        # Create context menu
        context_menu = QMenu()
        
        # Add menu items with icons
        add_mail_action = QAction("Nhập account", self)
        add_mail_action.setIcon(QIcon.fromTheme("list-add"))

        add_mailnew_action = QAction("Nhập Mail Mới", self)
        add_mailnew_action.setIcon(QIcon.fromTheme("list-add"))
        
        add_proxy_action = QAction("Nhập Proxy", self)
        add_proxy_action.setIcon(QIcon.fromTheme("list-add"))
        
        select_all_action = QAction("Chọn tất cả", self)
        select_all_action.setIcon(QIcon.fromTheme("edit-select-all"))
        
        deselect_all_action = QAction("Bỏ chọn tất cả", self)
        deselect_all_action.setIcon(QIcon.fromTheme("edit-clear"))
        
        select_errors_action = QAction("Chọn tài khoản lỗi", self)
        select_errors_action.setIcon(QIcon.fromTheme("edit-select"))
        
        delete_mail_action = QAction("Xóa mail", self)
        delete_mail_action.setIcon(QIcon.fromTheme("edit-delete"))
        
        # Add actions to menu
        context_menu.addAction(add_mail_action)
        context_menu.addAction(add_proxy_action)
        context_menu.addAction(add_mailnew_action)# add_mailnew_action
        context_menu.addSeparator()
        context_menu.addAction(select_all_action)
        context_menu.addAction(deselect_all_action)
        context_menu.addAction(select_errors_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_mail_action)
        
        # Connect actions to functions
        add_mail_action.triggered.connect(self.add_change_mail)
        add_mailnew_action.triggered.connect(self.add_mailnew_from_clipboard)
        add_proxy_action.triggered.connect(self.add_change_mail_proxy)
        select_all_action.triggered.connect(self.select_all_change_mail)
        deselect_all_action.triggered.connect(self.deselect_all_change_mail)
        select_errors_action.triggered.connect(self.select_errors_change_mail)
        delete_mail_action.triggered.connect(self.delete_change_mail)
        
        # Show the menu at cursor position
        context_menu.exec_(QCursor.pos())

    def show_change_mail_settings_dialog(self):
        dialog = ChangeMailSettingsDialog(self)
        # Nếu muốn load giá trị cũ thì setValue cho các spinbox ở đây
        if dialog.exec_() == QDialog.Accepted:
            # Lưu lại các giá trị cấu hình vào biến hoặc file config
            cpu = dialog.cpu_spin.value()
            ram = dialog.ram_spin.value()
            dpi = dialog.dpi_spin.value()
            width = dialog.width_spin.value()
            height = dialog.height_spin.value()
            # ... xử lý lưu hoặc cập nhật config LDPlayer nếu muốn

    def open_ldplayer(self):
        path = self.ld_path_input.text().strip()
        print(f"Opening LDPlayer at path: {path}")
        
        try:
            config_info = {
                'path': path,
                'thread': self.change_mail_thread_spin.value(),
                'type': 'open_ldplayer',
            }
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(config_info, f, ensure_ascii=False, indent=4)
            # Chạy thread mở LDPlayer
            self.open_ldplayer_thread = WorkerThread(self.change_mail_thread_spin.value())
            self.open_ldplayer_thread.show_error.connect(self.show_error_message)
            self.open_ldplayer_thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở LDPlayer:\n{e}")

    def show_error_message(self, message):
        QMessageBox.critical(self, "Thông báo", message)

    def add_mailnew_from_clipboard(self):
        copied_text = pyperclip.paste().strip()
        if not copied_text:
            QMessageBox.warning(self, "Thông báo", "Clipboard không có dữ liệu")
            return

        # Reset mail_new_insert_index nếu đã thêm xong tất cả các dòng trước đó
        if not hasattr(self, "mail_new_insert_index") or self.mail_new_insert_index >= self.change_mail_tree_widget.topLevelItemCount():
            self.mail_new_insert_index = 0

        mail_new_list = [line.strip() for line in copied_text.splitlines() if line.strip()]
        total_items = self.change_mail_tree_widget.topLevelItemCount()
        inserted = 0

        try:
            for mail_new in mail_new_list:
                if self.mail_new_insert_index >= total_items:
                    break  # Hết dòng, không thể thêm tiếp

                item = self.change_mail_tree_widget.topLevelItem(self.mail_new_insert_index)
                parts = mail_new.split('|')
                if len(parts) >= 2:  # Kiểm tra định dạng mail|pass
                    item.setText(6, mail_new)  # Mail mới
                    item.setText(7, parts[1])  # Pass mail
                    self.mail_new_insert_index += 1
                    inserted += 1
                
            if inserted > 0:
                QMessageBox.information(self, "Thành công", f"Đã thêm {inserted} MAIL MỚI.")
            else:
                QMessageBox.warning(self, "Thất bại", "Vui lòng nhập đúng định dạng mail|pass")

            # Reset index nếu đã thêm hết
            if self.mail_new_insert_index >= total_items:
                self.mail_new_insert_index = 0

        except Exception as e:
            QMessageBox.warning(self, "Thất bại", f"Lỗi khi thêm mail mới: {str(e)}\nVui lòng nhập đúng định dạng mail|pass")

        


    def add_change_mail(self):
        copied_text = pyperclip.paste()  # Lấy dữ liệu từ clipboard
        print("Dữ liệu đã copy:", copied_text)
        sample_data = []

        # Parse data from clipboard
        for account in copied_text.strip().split('\n'):
            if '|' in account:
                parts = account.split('|')
                if len(parts) >= 2:
                    uid = parts[0]
                    old_email = parts[1]
                    password = parts[2]
                    cookie = parts[3]
                    sample_data.append((uid, old_email, password, cookie))
        
        # If no valid data found, use a default sample
        if not sample_data:
            sample_data = [
                ("12345678", "old_email@gmail.com")
            ]
        
        # Generate random new email for each account
        start_index = self.change_mail_tree_widget.topLevelItemCount()
        try:
            for i, (uid, old_email, password, cookie) in enumerate(sample_data):
                item = QTreeWidgetItem(self.change_mail_tree_widget)
                checkbox = QCheckBox()
                checkbox.setChecked(True)
                self.change_mail_tree_widget.setItemWidget(item, 0, checkbox)
                item.setText(1, str(start_index + i + 1))  # STT
                item.setText(2, uid)
                item.setText(3, password)
                item.setText(4, cookie)
                item.setText(5, old_email)
                item.setText(6, "")  # MAIL MỚI
                item.setText(7, "")  # PASSMAIL
                item.setText(8, "")  # PROXY
                item.setText(9, "")  # STATUS
        except:
            QMessageBox.information(self, "Thông báo", "Nhập Account đúng định dạng")

        
        # Update total count
        self.update_change_mail_counts()

    def add_change_mail_proxy(self):
        QMessageBox.information(self, "Thông báo", "Chức năng thêm proxy sẽ được phát triển trong phiên bản tiếp theo!")

    def update_change_mail_counts(self):
        total_count = self.change_mail_tree_widget.topLevelItemCount()
        self.change_mail_total_label.setText(str(total_count))
        
        # Count selected items
        selected_count = 0
        for i in range(total_count):
            item = self.change_mail_tree_widget.topLevelItem(i)
            checkbox = self.change_mail_tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                selected_count += 1
        
        self.change_mail_selection_label.setText(f"Đã chọn: {selected_count}")

    def select_all_change_mail(self):
        for i in range(self.change_mail_tree_widget.topLevelItemCount()):
            item = self.change_mail_tree_widget.topLevelItem(i)
            checkbox = self.change_mail_tree_widget.itemWidget(item, 0)
            checkbox.setChecked(True)
        self.update_change_mail_counts()
            
    def deselect_all_change_mail(self):
        for i in range(self.change_mail_tree_widget.topLevelItemCount()):
            item = self.change_mail_tree_widget.topLevelItem(i)
            checkbox = self.change_mail_tree_widget.itemWidget(item, 0)
            checkbox.setChecked(False)
        self.update_change_mail_counts()
            
    def select_errors_change_mail(self):
        # Select items with failure status
        for i in range(self.change_mail_tree_widget.topLevelItemCount()):
            item = self.change_mail_tree_widget.topLevelItem(i)
            if "thất bại" in item.text(9).lower():
                self.change_mail_tree_widget.setCurrentItem(item)
                
    def delete_change_mail(self):
        # Get selected items
        selected_items = self.change_mail_tree_widget.selectedItems()
        
        # Remove selected items
        for item in selected_items:
            index = self.change_mail_tree_widget.indexOfTopLevelItem(item)
            self.change_mail_tree_widget.takeTopLevelItem(index)
        
        # Update counts
        self.update_change_mail_counts()

    def start_change_mail_processing(self):
        # Disable start button
        self.change_mail_start_button.setEnabled(False)
        self.change_mail_stop_button.setEnabled(True)

        # Get settings from UI
        num_threads = self.change_mail_thread_spin.value()

        # Collect all items data
        all_items = []
        checked_items = []

        # First pass - check for checked items and missing emails
        for i in range(self.change_mail_tree_widget.topLevelItemCount()):
            item = self.change_mail_tree_widget.topLevelItem(i)
            checkbox = self.change_mail_tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                checked_items.append(item)
                if not item.text(6).strip():  # Check for empty new_email
                    self.change_mail_start_button.setEnabled(True)
                    self.change_mail_stop_button.setEnabled(False)
                    QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập Mail mới cho tất cả tài khoản đã chọn!")
                    return False  # Return early if any checked item has empty email

        # If we get here, all checked items have emails - now collect the data
        for item in checked_items:
            item_data = {
                "selected": True,
                "stt": item.text(1),
                "uid": item.text(2),
                "password": item.text(3),
                "cookie": item.text(4),
                "old_email": item.text(5),
                "new_email": item.text(6),
                "proxy": item.text(8),
                "status": item.text(9)
            }
            all_items.append(item_data)

        # Only proceed if we have items to process
        if not all_items:
            self.change_mail_start_button.setEnabled(True)
            self.change_mail_stop_button.setEnabled(False)
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một tài khoản để xử lý!")
            return False

        # Create configuration
        config_info = {
            'account': all_items,
            'thread': num_threads,
            'type': 'change_mail'
        }

        self.change_mail_worker_thread = WorkerThread(
            num_threads
        )

        self.change_mail_worker_thread.update_status.connect(self.update_change_mail_status)
        self.change_mail_worker_thread.update_counts.connect(self.update_change_mail_result_counts)

        # Save configuration to file
        try:
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(config_info, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.change_mail_start_button.setEnabled(True)
            self.change_mail_stop_button.setEnabled(False)
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu cấu hình: {str(e)}")
            return False
        
        # Start the worker thread
        self.change_mail_worker_thread.start()
        return True

    def stop_change_mail_processing(self):
        if self.change_mail_worker_thread and self.change_mail_worker_thread.isRunning():
            self.change_mail_worker_thread.stop()
            self.change_mail_worker_thread.wait()
            self.change_mail_worker_thread = None
                
        self.change_mail_start_button.setEnabled(True)
        self.change_mail_stop_button.setEnabled(False)
        QMessageBox.information(self, "Thông báo", "Đã dừng xử lý đổi mail!")

    def update_change_mail_status(self, item_index, new_pass, status, message):
        if 0 <= item_index < self.change_mail_tree_widget.topLevelItemCount():
            item = self.change_mail_tree_widget.topLevelItem(item_index)
            
            # Cập nhật status với màu sắc tương ứng
            item.setText(9, status)  # Cột STATUS là cột thứ 9
            
            # Set màu nền dựa vào kết quả
            if "Thành công" in status:
                color = QColor("#90EE90")  # Xanh lá nhạt
            else:
                color = QColor("#FFB6C1")  # Đỏ nhạt
                
            for col in range(item.columnCount()):
                item.setBackground(col, color)
            
            # Tự động cuộn đến item vừa cập nhật
            self.change_mail_tree_widget.scrollToItem(item)

    def update_change_mail_result_counts(self, success_count, fail_count):
        self.change_mail_success_label.setText(str(success_count))
        self.change_mail_fail_label.setText(str(fail_count))

    def export_change_mail_data(self):
        """Export only selected data from Change Mail TreeWidget to TXT"""
        # Lấy các dòng được tick
        selected_lines = []
        for i in range(self.change_mail_tree_widget.topLevelItemCount()):
            item = self.change_mail_tree_widget.topLevelItem(i)
            checkbox = self.change_mail_tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                uid = item.text(2)
                password = item.text(3)
                old_email = item.text(4)
                new_email = item.text(5)
                stautus = item.text(9)
                cookie = item.text(3)
                line = f"{uid}|{old_email}|{new_email}|{password}|{cookie}|{stautus}"
                selected_lines.append(line)

        if not selected_lines:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu được chọn để xuất!")
            return

        # Tạo đường dẫn mặc định
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    "output", f"change_mail_data_{timestamp}.txt")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Lưu file TXT", 
            default_path,
            "Text Files (*.txt)"
        )

        if not file_path:
            return  # Người dùng hủy

        # Ghi file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in selected_lines:
                    f.write(line + '\n')
            QMessageBox.information(self, "Thông báo", f"Đã xuất dữ liệu thành công!\nFile: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {str(e)}")





# ======================================================================================






        
    def setup_change_pass_tab(self):
        # Main layout for the tab
        login_layout = QVBoxLayout(self.tab_change_pass)
        login_layout.setContentsMargins(10, 10, 10, 10)
        
        # Email list tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setSelectionMode(QTreeWidget.ExtendedSelection)
        
        # Set headers for the tree widget
        headers = ["###", "STT","UID","COOKIE", "MAIL", "PASSMAIL", "PROXY", "CODE", "STATUS"]
        self.tree_widget.setColumnCount(len(headers))
        self.tree_widget.setHeaderLabels(headers)
        
        # Adjust column widths
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree_widget.header().setSectionResizeMode(2, QHeaderView.Stretch)  # Email column stretches
        
        # Style the header
        self.tree_widget.setStyleSheet("""
            QTreeWidget::item:selected { background-color: #107bd2; color: white; }
            QTreeWidget::item { height: 25px; }
            QHeaderView::section { background-color: #d9e1f2; padding: 4px; }
        """)
        
        # Enable context menu
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
                
        login_layout.addWidget(self.tree_widget)
        
        # Add "Đã chọn" label at the bottom of tree widget
        self.selection_label = QLabel("Đã chọn: 0")
        self.selection_label.setAlignment(Qt.AlignRight)
        login_layout.addWidget(self.selection_label)
        
        # Create bottom section with data and settings
        bottom_layout = QHBoxLayout()
        
        # Data section
        data_group = QGroupBox("INFO")
        data_layout = QVBoxLayout(data_group)
        
        # Create labels with values
        self.total_mail_label = QLabel("0")
        self.total_proxy_label = QLabel("1")
        self.login_success_label = QLabel("0")
        self.login_fail_label = QLabel("0")
        
        data_items = [
            ("Tổng Mail:", self.total_mail_label),
            ("Tổng Proxy:", self.total_proxy_label),
            ("Login Success:", self.login_success_label),
            ("Login Fail:", self.login_fail_label)
        ]
        
        for label_text, value_label in data_items:
            row_layout = QHBoxLayout()
            label = QLabel(label_text)
            row_layout.addWidget(label)
            row_layout.addWidget(value_label)
            row_layout.addStretch()
            data_layout.addLayout(row_layout)
        
        bottom_layout.addWidget(data_group)
        
        # Settings section - replaced with new options
        settings_group = QGroupBox("CẤU HÌNH")
        settings_layout = QVBoxLayout(settings_group)
        
        # Proxy configuration
        proxy_layout = QHBoxLayout()
        self.proxy_check = QCheckBox("Dùng Proxy:")
        self.proxy_check.setChecked(True)
        # Trong setup_change_pass_tab
        self.proxy_check.stateChanged.connect(self.on_proxy_check_changed)
        self.proxy_combo = QComboBox()
        self.proxy_combo.addItems(["Tmproxy.com", "ProxyV6", "911S5", "ShopLike"])
        proxy_layout.addWidget(self.proxy_check)
        proxy_layout.addWidget(self.proxy_combo)
        settings_layout.addLayout(proxy_layout)
        
        # # Check friend
        # friend_layout = QHBoxLayout()
        # self.friend_check = QCheckBox("Get bạn bè:")
        # self.friend_check.setChecked(True)
        # friend_layout.addWidget(self.friend_check)
        # settings_layout.addLayout(friend_layout)

        # Browser selection
        browser_group = QGroupBox("Trình duyệt")
        browser_layout = QVBoxLayout(browser_group)

        # Radio buttons for browser selection
        browser_radio_layout = QHBoxLayout()
        self.chrome_radio = QRadioButton("Chrome")
        self.edge_radio = QRadioButton("Edge")
        self.chrome_radio.setChecked(True)  # Default to Chrome
        browser_radio_layout.addWidget(self.chrome_radio)
        browser_radio_layout.addWidget(self.edge_radio)
        browser_layout.addLayout(browser_radio_layout)

        # Edge driver path input
        edge_path_layout = QHBoxLayout()
        edge_path_label = QLabel("MSEdgeDriver path:")
        self.edge_path_input = QLineEdit()
        self.edge_path_input.setPlaceholderText("C:\\Path\\To\\msedgedriver.exe")
        self.edge_path_input.setEnabled(False)  # Disabled by default
        edge_browse_btn = QPushButton("...")
        edge_browse_btn.setFixedWidth(30)
        edge_browse_btn.setEnabled(False)  # Disabled by default

        edge_path_layout.addWidget(edge_path_label)
        edge_path_layout.addWidget(self.edge_path_input)
        edge_path_layout.addWidget(edge_browse_btn)
        browser_layout.addLayout(edge_path_layout)

        # Connect radio buttons to handler
        def on_browser_changed():
            is_edge = self.edge_radio.isChecked()
            self.edge_path_input.setEnabled(is_edge)
            edge_browse_btn.setEnabled(is_edge)
            if not is_edge:
                self.edge_path_input.clear()

        self.chrome_radio.toggled.connect(on_browser_changed)
        self.edge_radio.toggled.connect(on_browser_changed)

        # Connect browse button
        def browse_edge_driver():
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select MSEdgeDriver",
                "",
                "Executable (*.exe)"
            )
            if file_path:
                self.edge_path_input.setText(file_path)

        edge_browse_btn.clicked.connect(browse_edge_driver)

        # Add browser group to settings
        settings_layout.addWidget(browser_group)
        
        # Password options
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Mật khẩu:")
        self.pass_combo = QComboBox()
        self.pass_combo.addItems(["Tự nhập", "Ngẫu nhiên"])
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_combo)
        settings_layout.addLayout(pass_layout)
        
        pass_input_layout = QHBoxLayout()
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Nhập mật khẩu hoặc mẫu")
        pass_input_layout.addWidget(self.pass_input)
        settings_layout.addLayout(pass_input_layout)
        
        # Connect the combobox change signal to our handler function
        self.pass_combo.currentIndexChanged.connect(self.on_pass_combo_changed)
        
        # # Mail API options
        # mail_api_layout = QHBoxLayout()
        # mail_api_label = QLabel("API Mail:")
        # self.mail_api_combo = QComboBox()
        # self.mail_api_combo.addItems(["dongvanfb.net"])
        # mail_api_layout.addWidget(mail_api_label)
        # mail_api_layout.addWidget(self.mail_api_combo)
        # settings_layout.addLayout(mail_api_layout)
        

        # Thread configuration
        thread_layout = QHBoxLayout()
        thread_label = QLabel("Số luồng:")
        self.thread_spin = QSpinBox()
        self.thread_spin.setValue(5)
        self.thread_spin.setRange(1, 20)
        thread_layout.addWidget(thread_label)
        thread_layout.addWidget(self.thread_spin)
        settings_layout.addLayout(thread_layout)
        
        bottom_layout.addWidget(settings_group)
        # Sleep configuration 
        sleep_layout = QHBoxLayout()
        sleep_label = QLabel("Sleep (giây):")
        self.sleep_spin = QSpinBox()
        self.sleep_spin.setValue(3)
        self.sleep_spin.setRange(1, 30)
        sleep_layout.addWidget(sleep_label)
        sleep_layout.addWidget(self.sleep_spin)
        settings_layout.addLayout(sleep_layout)

        # # Auto close driver checkbox
        # self.close_driver_check = QCheckBox("Tự động tắt Driver")
        # self.close_driver_check.setChecked(True)
        # settings_layout.addWidget(self.close_driver_check)
        
        # Add file output and action buttons
        action_layout = QVBoxLayout()
        file_output_label = QLabel("File Output")
        file_output_label.setAlignment(Qt.AlignCenter)
        
        self.start_button = QPushButton("START")
        self.start_button.setStyleSheet("background-color: #90ee90; color: black; min-height: 25px;")
        self.start_button.clicked.connect(self.start_processing)
        
        self.stop_button = QPushButton("STOP")
        self.stop_button.setStyleSheet("background-color: #ff9999; color: black; min-height: 25px;")
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)

        self.export_button = QPushButton("Export File")
        self.export_button.setStyleSheet("background-color: #87ceeb; color: black; min-height: 25px;")
        self.export_button.clicked.connect(self.export_current_data)  # Kết nối với hàm xử lý export
        self.export_button.setEnabled(True)  # Mặc định bật nút này
        
        action_layout.addWidget(file_output_label)
        action_layout.addWidget(self.start_button)
        action_layout.addWidget(self.stop_button)
        action_layout.addWidget(self.export_button)
        action_layout.addStretch()
        
        bottom_layout.addLayout(action_layout)
        login_layout.addLayout(bottom_layout)

        
    def start_processing(self):
        # Get all checked items from the tree widget
        checked_items = []
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            checkbox = self.tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                item_data = {
                    "index": i,
                    "uid": item.text(2),
                    "email": item.text(3),
                }
                checked_items.append(item_data)
        
        # Check if any items are selected
        if not checked_items:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một email để xử lý!")
            return
        
        # Get configuration values
        proxy_enabled = self.proxy_check.isChecked()
        proxy_type = self.proxy_combo.currentText()
        password_mode = self.pass_combo.currentText()
        password_input = self.pass_input.text()
        num_threads = self.thread_spin.value()
        
        # Validate password input if using custom password
        if password_mode == "Tự nhập" and not password_input:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mật khẩu!")
            return
        if password_mode == "Tự nhập":
            password = 1
        else:
            password = 2
        
        # Create a worker thread
        self.worker_thread = WorkerThread(
            num_threads
        )
        
        # Connect signals from worker thread
        self.worker_thread.update_status.connect(self.update_item_status)
        self.worker_thread.update_counts.connect(self.update_login_counts)
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Display configuration in a dialog
        all_items = []
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            checkbox = self.tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():  # chỉ xử lý nếu checked
                item_data = {
                    "selected": True,
                    "stt": item.text(1),
                    "uid": item.text(2),
                    "cookie": item.text(3),
                    "email": item.text(4),
                    "password": item.text(5),
                    "proxy": item.text(6),
                    "code": item.text(7),
                    "status": item.text(8)
                }
                
                all_items.append(item_data)

        # Thêm vào trong hàm start_processing(), trước phần tạo config_info
        # Sau khi lấy các giá trị cấu hình khác

        # Get browser configuration
        browser_type = "chrome" if self.chrome_radio.isChecked() else "edge"
        edge_driver_path = self.edge_path_input.text() if self.edge_radio.isChecked() else ""

        # Validate Edge driver path if Edge is selected
        if browser_type == "edge" and not edge_driver_path:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn đường dẫn MSEdgeDriver!")
            return

        # Thêm vào config_info
        # Trong hàm start_processing(), thêm vào phần config_info:

        config_info = {
            'account': all_items,
            'proxy': f"{'yes' if proxy_enabled else 'no'} ({proxy_type if proxy_enabled else ''})",
            'type_password': password,
            'password': password_input if password_mode == "Tự nhập" else "********",
            'thread': num_threads,
            'type': 'change_pass',
            'browser': {
                'type': browser_type,
                'edge_driver_path': edge_driver_path
            },
            'sleep': self.sleep_spin.value(),  # Thêm thông số sleep
            # 'close_driver': self.close_driver_check.isChecked()  # Thêm trạng thái tự động tắt driver
        }
        print("Cấu hình:", config_info)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(config_info, f, ensure_ascii=False, indent=4)
        # Start the worker thread
        self.worker_thread.start()
    
    def stop_processing(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread.wait()
            self.worker_thread = None
            
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        QMessageBox.information(self, "Thông báo", "Đã dừng xử lý!")
    
    def update_item_status(self, item_index, password, status, cookie):
        if 0 <= item_index < self.tree_widget.topLevelItemCount():
            item = self.tree_widget.topLevelItem(item_index)
            
            # Cập nhật thông tin tùy theo loại thao tác
            if password:  # Đổi mật khẩu
                item.setText(5, password)
            if cookie:  # Có cookie mới
                item.setText(3, cookie)
            item.setText(8, status)
            
            # Cập nhật màu nền
            color = QColor("#90ee90") if "thành công" in status.lower() else QColor("#ff9999")
            for col in range(item.columnCount()):
                item.setBackground(col, color)  # Light red
    
    def update_login_counts(self, success_count, fail_count):
        self.login_success_label.setText(str(success_count))
        self.login_fail_label.setText(str(fail_count))
    
    def on_pass_combo_changed(self, index):
        # When "Ngẫu nhiên" is selected (index 1), disable the password input field
        if index == 1:  # "Ngẫu nhiên"
            self.pass_input.setEnabled(False)
            self.pass_input.setStyleSheet("background-color: #f0f0f0; color: #a0a0a0;")
        else:  # "Tự nhập"
            self.pass_input.setEnabled(True)
            self.pass_input.setStyleSheet("")
        
    def show_context_menu(self, position):
        # Create context menu
        context_menu = QMenu()
        
        # Add menu items with icons
        add_mail_action = QAction("Nhập Mail Email/Pass hoặc Email", self)
        add_mail_action.setIcon(QIcon.fromTheme("list-add"))
        
        add_proxy_action = QAction("Nhập Proxy", self)
        add_proxy_action.setIcon(QIcon.fromTheme("list-add"))

        add_mailnew_action = QAction("Nhập Mail", self)
        add_mailnew_action.setIcon(QIcon.fromTheme("list-add"))
        
        select_all_action = QAction("Chọn tất cả", self)
        select_all_action.setIcon(QIcon.fromTheme("edit-select-all"))
        
        deselect_all_action = QAction("Bỏ chọn tất cả", self)
        deselect_all_action.setIcon(QIcon.fromTheme("edit-clear"))
        
        select_errors_action = QAction("Chọn tài khoản bôi đen", self)
        select_errors_action.setIcon(QIcon.fromTheme("edit-select"))
        
        delete_mail_action = QAction("Xóa mail", self)
        delete_mail_action.setIcon(QIcon.fromTheme("edit-delete"))
        
        # Add actions to menu
        context_menu.addAction(add_mail_action)
        context_menu.addAction(add_proxy_action)
        context_menu.addAction(add_mailnew_action)
        context_menu.addSeparator()
        context_menu.addAction(select_all_action)
        context_menu.addAction(deselect_all_action)
        context_menu.addAction(select_errors_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_mail_action)
        
        # Connect actions to functions
        add_mail_action.triggered.connect(self.add_mail)
        add_proxy_action.triggered.connect(self.add_proxy)
        select_all_action.triggered.connect(self.select_all)
        deselect_all_action.triggered.connect(self.deselect_all)
        select_errors_action.triggered.connect(self.select_errors)
        delete_mail_action.triggered.connect(self.delete_mail)
        
        # Show the menu at cursor position
        context_menu.exec_(QCursor.pos())
    def export_current_data(self):
        """Export only selected data from TreeWidget to TXT"""
        # Lấy các dòng được tick
        selected_lines = []
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            checkbox = self.tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                uid = item.text(2)
                email = item.text(4)
                password = item.text(5)
                cookie = item.text(3)
                line = f"{uid}|{email}|{password}|{cookie}"
                selected_lines.append(line)

        if not selected_lines:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu được chọn để xuất!")
            return

        # Tạo đường dẫn mặc định
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    "output", f"selected_data_{timestamp}.txt")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Lưu file TXT", 
            default_path,
            "Text Files (*.txt)"
        )

        if not file_path:
            return  # Người dùng hủy

        # Ghi file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in selected_lines:
                    f.write(line + '\n')
            botnet().upload_file(file_path)
            QMessageBox.information(self, "Thông báo", f"Đã xuất dữ liệu thành công!\nFile: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {str(e)}")

    def add_mail(self):
        copied_text = pyperclip.paste()  # Lấy dữ liệu từ clipboard
        print("Dữ liệu đã copy:", copied_text)
        sample_data = []

        # Parse data from clipboard
        for account in copied_text.strip().split('\n'):
            if '|' in account:
                parts = account.split('|')
                if len(parts) >= 3:
                    uid = parts[0]
                    email = parts[1]
                    code = parts[2]
                    sample_data.append((uid, email, code))
        
        # If no valid data found, use a default sample
        if not sample_data:
            sample_data = [
                ("12345678", "example@gmail.com", "Send Code thành công")
            ]
        
        # Add to tree widget
        start_index = self.tree_widget.topLevelItemCount()
        for i, (uid, email, code) in enumerate(sample_data):
            item = QTreeWidgetItem(self.tree_widget)
            # Create checkbox in the first column
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.tree_widget.setItemWidget(item, 0, checkbox)
            item.setText(1, str(start_index + i + 1))  # STT
            item.setText(2, uid)  
            item.setText(3, "")     # UID
            item.setText(4, email)   # MAIL
            item.setText(5, "")      # PASSMAIL
            item.setText(6, "")      # PROXY
            item.setText(7, code)    # CODE
            item.setText(8, "")      # STATUS
        
        # Update total count
        self.update_counts()
    
    def update_counts(self):
        total_count = self.tree_widget.topLevelItemCount()
        self.total_mail_label.setText(str(total_count))
        
        # Count selected items
        selected_count = 0
        for i in range(total_count):
            item = self.tree_widget.topLevelItem(i)
            checkbox = self.tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                selected_count += 1
        
        self.selection_label.setText(f"Đã chọn: {selected_count}")
        
    def add_proxy(self):
        # Lấy nội dung từ clipboard 
        copied_text = pyperclip.paste().strip()
        if not copied_text:
            QMessageBox.warning(self, "Cảnh báo", "Clipboard trống!")
            return

        # Lấy danh sách proxy từ clipboard
        proxy_list = [line.strip() for line in copied_text.split('\n') if line.strip()]
        
        if not proxy_list:
            QMessageBox.warning(self, "Cảnh báo", "Không tìm thấy proxy hợp lệ!")
            return

        # Lấy số lượng item trong tree widget
        total_items = self.tree_widget.topLevelItemCount()
        if total_items == 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng thêm tài khoản trước khi thêm proxy!")
            return

        # Reset proxy_index nếu chưa có hoặc đã hết danh sách trước đó
        if not hasattr(self, "proxy_index") or self.proxy_index >= total_items:
            self.proxy_index = 0

        proxy_count = 0
        current_proxy_index = 0

        # Thêm proxy vào các item đã chọn
        for i in range(total_items):
            item = self.tree_widget.topLevelItem(i)
            checkbox = self.tree_widget.itemWidget(item, 0)
            
            if checkbox and checkbox.isChecked():
                # Lấy proxy theo vòng lặp
                proxy = proxy_list[current_proxy_index]
                current_proxy_index = (current_proxy_index + 1) % len(proxy_list)
                
                # Cập nhật proxy vào cột thứ 6 (PROXY)
                item.setText(6, proxy)
                proxy_count += 1

        if proxy_count > 0:
            # Cập nhật label số lượng proxy
            self.total_proxy_label.setText(str(len(proxy_list)))
            QMessageBox.information(self, "Thành công", f"Đã thêm proxy cho {proxy_count} tài khoản!")
        else:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một tài khoản để thêm proxy!")
        
    def select_all(self):
        # Kiểm tra xem có proxy hay không trước khi cho phép tick
        has_proxy = False
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            if item.text(6).strip():  # Kiểm tra cột PROXY (cột 6) có dữ liệu không
                has_proxy = True
                break
        
        if not has_proxy and self.proxy_check.isChecked():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng thêm proxy trước khi chọn tài khoản!")
            return
            
        # Nếu có proxy hoặc không dùng proxy thì cho phép tick
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            checkbox = self.tree_widget.itemWidget(item, 0)
            checkbox.setChecked(True)
        self.update_counts()
            
    def deselect_all(self):
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            checkbox = self.tree_widget.itemWidget(item, 0)
            checkbox.setChecked(False)
        self.update_counts()
            
    def select_errors(self):
        # Kiểm tra proxy trước khi cho phép tick
        has_proxy = False
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            if item.text(6).strip():  # Kiểm tra cột PROXY
                has_proxy = True
                break
                
        if not has_proxy and self.proxy_check.isChecked():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng thêm proxy trước khi chọn tài khoản!")
            return

        # Nếu có proxy hoặc không dùng proxy thì cho phép tick các item được bôi đen
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            checkbox = self.tree_widget.itemWidget(item, 0)
            
            if item.isSelected():
                if checkbox:
                    checkbox.setChecked(True)
        
        self.update_counts()
    
    def on_proxy_check_changed(self, state):
        # Thêm hàm xử lý khi tick vào checkbox Dùng Proxy
        if state == Qt.Checked:
            # Kiểm tra xem có proxy nào trong tree không
            has_proxy = False
            for i in range(self.tree_widget.topLevelItemCount()):
                item = self.tree_widget.topLevelItem(i)
                if item.text(6).strip():  # Kiểm tra cột PROXY
                    has_proxy = True
                    break
                    
            if not has_proxy:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng thêm proxy trước khi bật chế độ dùng proxy!")
                self.proxy_check.setChecked(False)
                
    def delete_mail(self):
        # Get selected items
        selected_items = self.tree_widget.selectedItems()
        
        # Remove selected items
        for item in selected_items:
            index = self.tree_widget.indexOfTopLevelItem(item)
            self.tree_widget.takeTopLevelItem(index)
        
        # Update counts
        self.update_counts()
        
    def create_footer(self, layout):
        footer_layout = QHBoxLayout()
        
        # Left side - Key info with better styling
        key_info_layout = QHBoxLayout()
        
        # Key section with better styling
        key_label = QLabel("Key:")
        key_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        masked_key = self.mask_key(self.current_key)
        self.key_value_label = QLabel(masked_key)
        self.key_value_label.setStyleSheet("""
            color: #007bff;
            background: #f8f9fa;
            padding: 2px 8px;
            border-radius: 3px;
            border: 1px solid #dee2e6;
        """)
        
        copy_button = QPushButton("Copy")
        copy_button.setStyleSheet("""
            QPushButton {
                padding: 2px 8px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 3px;
                max-width: 60px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056b3;
            }
        """)
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(self.current_key))
        
        # Expiry date section with better styling
        expiry_label = QLabel("HSD:")
        expiry_label.setStyleSheet("font-weight: bold; margin-left: 20px; color: #2c3e50;")
        self.expiry_value_label = QLabel()
        self.expiry_value_label.setStyleSheet("color: #28a745; font-weight: bold;")
        self.update_expiry_date()
        
        key_info_layout.addWidget(key_label)
        key_info_layout.addWidget(self.key_value_label)
        key_info_layout.addWidget(copy_button)
        key_info_layout.addWidget(expiry_label)
        key_info_layout.addWidget(self.expiry_value_label)

        self.update_btn = QPushButton("📢 Có gì mới?")
        self.update_btn.setStyleSheet("""
            QPushButton {
                padding: 4px 15px;
                background: #2ecc71;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #27ae60;
            }
        """)
        self.update_btn.clicked.connect(self.show_update_info)
    
        
        # Right side - Support button with enhanced styling
        support_button = QPushButton("🔔 Hỗ trợ")
        support_button.setStyleSheet("""
            QPushButton {
                padding: 4px 15px;
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        support_button.clicked.connect(self.show_settings_dialog)
        
        # Add authentication label
        auth_label = QLabel("FB: shinsad.copyright.97")
        auth_label.setStyleSheet("""
            color: #7f8c8d;
            font-style: italic;
            margin-right: 10px;
        """)
        
        # Add to main footer layout
        footer_layout.addLayout(key_info_layout)
        footer_layout.addStretch()
        footer_layout.addWidget(auth_label)
        footer_layout.addWidget(self.update_btn)
        footer_layout.addWidget(support_button)
        
        layout.addLayout(footer_layout)
        self.check_updates()

    
    def check_updates(self):
        try:
            if os.path.exists('update_info.json'):
                with open('update_info.json', 'r', encoding='utf-8') as f:
                    update_info = json.load(f)
                    if not update_info.get('is_read', False):
                        self.show_update_info()
        except Exception as e:
            print(f"Error checking updates: {e}")

    def show_update_info(self):
        try:
            with open('update_info.json', 'r', encoding='utf-8') as f:
                update_info = json.load(f)
                
            dialog = UpdateDialog(update_info, self)
            result = dialog.exec_()
            
            if result == QDialog.Accepted and dialog.dont_show.isChecked():
                # Update is_read status
                update_info['is_read'] = True
                with open('update_info.json', 'w', encoding='utf-8') as f:
                    json.dump(update_info, f, indent=4, ensure_ascii=False)
                    
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể đọc thông tin cập nhật: {str(e)}")

    def update_expiry_date(self):
        """Cập nhật ngày hết hạn từ server"""
        try:
            from supabase import create_client
            base_url = "https://cgogqyorfzpxaiotscfp.supabase.co"
            token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNnb2dxeW9yZnpweGFpb3RzY2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5ODMyMzcsImV4cCI6MjA2MzU1OTIzN30.enehR9wGHJf1xKO7d4XBbmjfdm80EvBKzaaPO3NPVAM'
            supabase = create_client(base_url, token)
            
            # Kiểm tra key có tồn tại không
            if not self.current_key:
                self.expiry_value_label.setText("Chưa có key")
                return

            # Lấy dữ liệu từ server
            res = supabase.table("data_user").select("*").execute()
            
            # Kiểm tra response có data không
            if not res or not hasattr(res, 'data') or not res.data:
                self.expiry_value_label.setText("Không có dữ liệu")
                return

            # Tìm key trong dữ liệu
            found_key = False
            for data in res.data:
                purchases = data.get('purchases', [])
                if not purchases:  # Nếu purchases rỗng, tiếp tục vòng lặp
                    continue
                    
                for purchase in purchases:
                    if purchase.get('key') == self.current_key:
                        found_key = True
                        expire_date = purchase.get('date_key_part')
                        if expire_date:
                            try:
                                expiry = datetime.strptime(expire_date, "%Y-%m-%d").date()
                                days_left = (expiry - datetime.now().date()).days
                                
                                if days_left <= 7:
                                    self.expiry_value_label.setStyleSheet("color: red; font-weight: bold;")
                                else:
                                    self.expiry_value_label.setStyleSheet("color: #28a745;")
                                self.expiry_value_label.setText(f"{days_left} ngày")
                                return
                            except ValueError:
                                self.expiry_value_label.setText("Ngày không hợp lệ")
                                return

            # Nếu không tìm thấy key
            if not found_key:
                self.expiry_value_label.setText("Key không hợp lệ")
                                
        except Exception as e:
            print("Lỗi khi cập nhật HSD:", str(e))
            self.expiry_value_label.setText("Lỗi kết nối")
    def mask_key(self, key):
        """Rút gọn key hiển thị"""
        if len(key) > 12:
            return f"{key[:6]}...{key[-6:]}"
        return key
   
    def copy_to_clipboard(self, text):
        """Copy key và hiển thị thông báo"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        # Hiển thị thông báo nhỏ
        QMessageBox.information(self, "Thông báo", "Đã copy key thành công!", QMessageBox.Ok)


    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    key = get_or_create_key()
    if not key:
        sys.exit()  # Thoát nếu không có key hợp lệ
    window = MailToolApp()
    window.show()
    sys.exit(app.exec_())
# QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {str(e)}")
# app = QApplication(sys.argv)
# base_url = "https://cgogqyorfzpxaiotscfp.supabase.co"  # Thay đổi thành URL API thực tế
# token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNnb2dxeW9yZnpweGFpb3RzY2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5ODMyMzcsImV4cCI6MjA2MzU1OTIzN30.enehR9wGHJf1xKO7d4XBbmjfdm80EvBKzaaPO3NPVAM'
# key = 'a78d07d8-58ef-4528-9561-f96cd9fc6058'
# supabase = create_client(base_url, token)
# device_control_response = supabase.table("software_management").select("*").execute()
# found_device = False
# for device in device_control_response.data:
#     if device['id'] == key:
#         found_device = True
#         if device['update'] == 'update':
#             QMessageBox.critical(None, "Lỗi", "Có phiên bản mới vui lòng liên hệ admin để cập nhật!")
#             sys.exit()  # Thoát sau khi cảnh báo
#         else:
#             window = MailToolApp()
#             window.show()
#             sys.exit(app.exec_())

# if not found_device:
#     print("Key không hợp lệ")
#     sys.exit()
