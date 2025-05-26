# code by voletrieulan hahahaha
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
                           QTreeWidget, QTreeWidgetItem, QLabel, QFrame, QCheckBox, QRadioButton,
                           QComboBox, QSpinBox, QPushButton, QHeaderView, QMenu, QAction, QGroupBox,
                           QLineEdit, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QCursor, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import pyperclip
import os
import json
import sys
from worker_module import WorkerThread
from check_key import get_or_create_key

class MailToolApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng Nhập - Đổi Pass - Đổi Mail - GMX Mail.com - HP Tools - FB: shinsad.copyright.97")
        self.setGeometry(100, 100, 780, 520)
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
        self.tab_widget.setCurrentWidget(self.tab_change_pass)
        self.tab_widget.setCurrentWidget(self.tab_forgot_pass)

        
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
        headers = ["###", "STT", "UID", "COOKIE", "MAIL", "PASSMAIL", "PROXY", "CODE", "STATUS"]
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
        
        # Password configuration
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Mật khẩu mới:")
        self.forgot_pass_type_combo = QComboBox()
        self.forgot_pass_type_combo.addItems(["Tự nhập", "Ngẫu nhiên"])
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.forgot_pass_type_combo)
        settings_layout.addLayout(pass_layout)
        
        # Password input
        self.forgot_pass_input = QLineEdit()
        self.forgot_pass_input.setPlaceholderText("Nhập mật khẩu mới")
        settings_layout.addWidget(self.forgot_pass_input)
        
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
        select_errors_action = QAction("Chọn bôi đen", self)
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
        add_proxy_action.triggered.connect(self.add_forgot_pass_proxy)
        select_all_action.triggered.connect(self.select_all_forgot_pass)
        deselect_all_action.triggered.connect(self.deselect_all_forgot_pass)
        select_errors_action.triggered.connect(self.select_errors_forgot_pass)
        delete_mail_action.triggered.connect(self.delete_forgot_pass_mail)
        
        context_menu.exec_(QCursor.pos())

    def add_forgot_pass_mail(self):
        copied_text = pyperclip.paste()
        sample_data = []
        
        for account in copied_text.strip().split('\n'):
            if '|' in account:
                parts = account.split('|')
                if len(parts) >= 2:
                    uid = parts[0]
                    email = parts[1]
                    sample_data.append((uid, email))
        
        start_index = self.forgot_pass_tree_widget.topLevelItemCount()
        for i, (uid, email) in enumerate(sample_data):
            item = QTreeWidgetItem(self.forgot_pass_tree_widget)
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.forgot_pass_tree_widget.setItemWidget(item, 0, checkbox)
            item.setText(1, str(start_index + i + 1))
            item.setText(2, uid)
            item.setText(3, "")
            item.setText(4, email)
            item.setText(5, "")
            item.setText(6, "")
            item.setText(7, "")
            item.setText(8, "")
        
        self.update_forgot_pass_counts()

    def start_forgot_pass_processing(self):
        # Logic xử lý quên mật khẩu
        pass

    def stop_forgot_pass_processing(self):
        # Logic dừng xử lý
        pass

    def export_forgot_pass_data(self):
        # Logic xuất dữ liệu
        pass










# ===========================================================





    def setup_change_mail_tab(self):
        # Main layout for the tab
        change_mail_layout = QVBoxLayout(self.tab_change_mail)
        change_mail_layout.setContentsMargins(10, 10, 10, 10)
        
        # Email list tree widget
        self.change_mail_tree_widget = QTreeWidget()
        self.change_mail_tree_widget.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.change_mail_tree_widget.setAlternatingRowColors(True)
        self.change_mail_tree_widget.setSelectionMode(QTreeWidget.ExtendedSelection)
        
        # Set headers for the tree widget
        headers = ["###", "STT", "UID", "PASSWORD", "COOKIE", "MAIL CŨ", "MAIL MỚI", "PASSMAIL", "PROXY", "STATUS"]
        self.change_mail_tree_widget.setColumnCount(len(headers))
        self.change_mail_tree_widget.setHeaderLabels(headers)
        # line = f"{uid}|{email}|{password}|{cookie}"
        # Adjust column widths
        self.change_mail_tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.change_mail_tree_widget.header().setSectionResizeMode(2, QHeaderView.Stretch)  # UID column stretches
        self.change_mail_tree_widget.header().setSectionResizeMode(4, QHeaderView.Stretch)  # Mail cũ column stretches
        self.change_mail_tree_widget.header().setSectionResizeMode(5, QHeaderView.Stretch)  # Mail mới column stretches
        
        # Style the header
        self.change_mail_tree_widget.setStyleSheet("""
            QTreeWidget::item:selected { background-color: #107bd2; color: white; }
            QTreeWidget::item { height: 25px; }
            QHeaderView::section { background-color: #d9e1f2; padding: 4px; }
        """)
        
        # Enable context menu
        self.change_mail_tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.change_mail_tree_widget.customContextMenuRequested.connect(self.show_change_mail_context_menu)
                
        change_mail_layout.addWidget(self.change_mail_tree_widget)
        
        # Add "Đã chọn" label at the bottom of tree widget
        self.change_mail_selection_label = QLabel("Đã chọn: 0")
        self.change_mail_selection_label.setAlignment(Qt.AlignRight)
        change_mail_layout.addWidget(self.change_mail_selection_label)
        
        # Create bottom section with data and settings
        bottom_layout = QHBoxLayout()
        
        # Data section
        data_group = QGroupBox("INFO")
        data_layout = QVBoxLayout(data_group)
        
        # Create labels with values
        self.change_mail_total_label = QLabel("0")
        self.change_mail_proxy_label = QLabel("1")
        self.change_mail_success_label = QLabel("0")
        self.change_mail_fail_label = QLabel("0")
        
        data_items = [
            ("Tổng Mail:", self.change_mail_total_label),
            ("Tổng Proxy:", self.change_mail_proxy_label),
            ("Đổi thành công:", self.change_mail_success_label),
            ("Đổi thất bại:", self.change_mail_fail_label)
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
        self.change_mail_proxy_check = QCheckBox("Dùng Proxy:")
        self.change_mail_proxy_check.setChecked(True)
        self.change_mail_proxy_combo = QComboBox()
        self.change_mail_proxy_combo.addItems(["Tmproxy.com", "ProxyV6", "911S5", "ShopLike"])
        proxy_layout.addWidget(self.change_mail_proxy_check)
        proxy_layout.addWidget(self.change_mail_proxy_combo)
        settings_layout.addLayout(proxy_layout)
        
        # # Mail API options
        # mail_api_layout = QHBoxLayout()
        # mail_api_label = QLabel("API Mail:")
        # self.change_mail_api_combo = QComboBox()
        # self.change_mail_api_combo.addItems(["dongvanfb.net", "mail.com", "mailnesia.com", "temp-mail.org"])
        # mail_api_layout.addWidget(mail_api_label)
        # mail_api_layout.addWidget(self.change_mail_api_combo)
        # settings_layout.addLayout(mail_api_layout)
        
        # # Email domain options
        # domain_layout = QHBoxLayout()
        # domain_label = QLabel("Tên miền:")
        # self.domain_combo = QComboBox()
        # self.domain_combo.addItems(["mail.com", "gmx.com", "gmx.us", "email.com"])
        # domain_layout.addWidget(domain_label)
        # domain_layout.addWidget(self.domain_combo)
        # settings_layout.addLayout(domain_layout)
        
        # # Email format options
        # email_format_layout = QHBoxLayout()
        # self.random_email_radio = QRadioButton("Email ngẫu nhiên")
        # self.random_email_radio.setChecked(True)
        # self.custom_email_radio = QRadioButton("Email tùy chỉnh")
        # email_format_layout.addWidget(self.random_email_radio)
        # email_format_layout.addWidget(self.custom_email_radio)
        # settings_layout.addLayout(email_format_layout)
        
        # # Email custom format
        # email_custom_layout = QHBoxLayout()
        # self.email_format_input = QLineEdit()
        # self.email_format_input.setPlaceholderText("Định dạng: name123, name.xyz, v.v...")
        # self.email_format_input.setEnabled(False)
        # email_custom_layout.addWidget(self.email_format_input)
        # settings_layout.addLayout(email_custom_layout)
        
        # # Connect radio buttons
        # self.random_email_radio.toggled.connect(self.toggle_email_format_input)
        # self.custom_email_radio.toggled.connect(self.toggle_email_format_input)
        
        # Thread configuration
        thread_layout = QHBoxLayout()
        thread_label = QLabel("Số luồng:")
        self.change_mail_thread_spin = QSpinBox()
        self.change_mail_thread_spin.setValue(5)
        self.change_mail_thread_spin.setRange(1, 20)
        thread_layout.addWidget(thread_label)
        thread_layout.addWidget(self.change_mail_thread_spin)
        settings_layout.addLayout(thread_layout)
        
        # Delay between operations
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Thời gian chờ (giây):")
        self.delay_spin = QSpinBox()
        self.delay_spin.setValue(3)
        self.delay_spin.setRange(1, 30)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_spin)
        settings_layout.addLayout(delay_layout)
        
        bottom_layout.addWidget(settings_group)
        
        # Add file output and action buttons
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
        self.change_mail_export_button.setEnabled(True)
        
        action_layout.addWidget(file_output_label)
        action_layout.addWidget(self.change_mail_start_button)
        action_layout.addWidget(self.change_mail_stop_button)
        action_layout.addWidget(self.change_mail_export_button)
        action_layout.addStretch()
        
        bottom_layout.addLayout(action_layout)
        change_mail_layout.addLayout(bottom_layout)

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
        
        select_errors_action = QAction("Chọn bôi đen", self)
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

    def add_mailnew_from_clipboard(self):
        # Khởi tạo chỉ số nếu chưa có
        if not hasattr(self, "mail_new_insert_index"):
            self.mail_new_insert_index = 0

        copied_text = pyperclip.paste().strip()
        if not copied_text:
            QMessageBox.warning(self, "Thông báo", "Clipboard không có dữ liệu")
            return

        mail_new_list = [line.strip() for line in copied_text.splitlines() if line.strip()]
        total_items = self.change_mail_tree_widget.topLevelItemCount()
        inserted = 0
        try:
            for mail_new in mail_new_list:
                if self.mail_new_insert_index >= total_items:
                    break  # Hết dòng, không thể thêm tiếp
                item = self.change_mail_tree_widget.topLevelItem(self.mail_new_insert_index)
                item.setText(6, mail_new)
                item.setText(7, mail_new.split('|')[1])
                self.mail_new_insert_index += 1
                inserted += 1
            QMessageBox.information(self, "Thành công", f"Đã thêm {inserted} MAIL MỚI.")
        except:
            QMessageBox.information(self, "Thất bại", f"Vui lòng nhập đúng định dạng mail mail|pass|token|client_id")

        


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
        # Get all checked items from the tree widget
        checked_items = []
        for i in range(self.change_mail_tree_widget.topLevelItemCount()):
            item = self.change_mail_tree_widget.topLevelItem(i)
            checkbox = self.change_mail_tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                item_data = {
                    "index": i,
                    "uid": item.text(2),
                    "old_email": item.text(5),
                    "new_email": item.text(6),
                }
                checked_items.append(item_data)
        
        # Check if any items are selected
        if not checked_items:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một email để xử lý!")
            return
        
        # Get configuration values
        proxy_enabled = self.change_mail_proxy_check.isChecked()
        proxy_type = self.change_mail_proxy_combo.currentText()
        # mail_api = self.change_mail_api_combo.currentText()
        # email_format = "random" if self.random_email_radio.isChecked() else "custom"
        # custom_format = self.email_format_input.text() if self.custom_email_radio.isChecked() else ""
        # domain = self.domain_combo.currentText()
        num_threads = self.change_mail_thread_spin.value()
        delay_time = self.delay_spin.value()
        
        # Validate inputs if using custom format
        # if email_format == "custom" and not custom_format:
        #     QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập định dạng email tùy chỉnh!")
        #     return
        
        # Create a worker thread for changing emails
        self.change_mail_worker_thread = WorkerThread(
            num_threads
        )
        
        # Connect signals from worker thread
        self.change_mail_worker_thread.update_status.connect(self.update_change_mail_status)
        self.change_mail_worker_thread.update_counts.connect(self.update_change_mail_result_counts)
        
        # Update UI
        self.change_mail_start_button.setEnabled(False)
        self.change_mail_stop_button.setEnabled(True)
        
        # Collect all items data
        all_items = []
        for i in range(self.change_mail_tree_widget.topLevelItemCount()):
            item = self.change_mail_tree_widget.topLevelItem(i)
            checkbox = self.change_mail_tree_widget.itemWidget(item, 0)
            if checkbox and checkbox.isChecked():
                item_data = {
                    "selected": True,
                    "stt": item.text(1),
                    "uid": item.text(2),
                    "password": item.text(3),
                    "cookie": item.text(4),
                    "old_email": item.text(5),
                    "new_email": item.text(6),
                    "password": item.text(7),
                    "proxy": item.text(8),
                    "status": item.text(9)
                }
                all_items.append(item_data)

        # Create configuration data
        config_info = {
            'account': all_items,
            'proxy': f"{'yes' if proxy_enabled else 'no'} ({proxy_type if proxy_enabled else ''})",
            # 'mail_api': mail_api,
            # 'email_format': email_format,
            # 'custom_format': custom_format,
            # 'domain': domain,
            'thread': num_threads,
            'delay': delay_time,
            'type': 'change_mail'
        }
        
        # Save configuration to file
        def get_app_dir():
            if getattr(sys, 'frozen', False):
                # Nếu là exe thì lấy thư mục chứa file exe
                return os.path.dirname(sys.executable)
            else:
                # Nếu là chạy bằng python thì lấy thư mục file .py
                return os.path.dirname(os.path.abspath(__file__))

        # Đường dẫn tuyệt đối tới change_mail_data.json
        json_path = os.path.join(get_app_dir(), 'data.json')

        # Ghi file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(config_info, f, ensure_ascii=False, indent=4)
            
        # Start the worker thread
        self.change_mail_worker_thread.start()

    def stop_change_mail_processing(self):
        if self.change_mail_worker_thread and self.change_mail_worker_thread.isRunning():
            self.change_mail_worker_thread.stop()
            self.change_mail_worker_thread.wait()
            self.change_mail_worker_thread = None
                
        self.change_mail_start_button.setEnabled(True)
        self.change_mail_stop_button.setEnabled(False)
        QMessageBox.information(self, "Thông báo", "Đã dừng xử lý đổi mail!")

    def update_change_mail_status(self, item_index, new_email, status, password):
        if 0 <= item_index < self.change_mail_tree_widget.topLevelItemCount():
            item = self.change_mail_tree_widget.topLevelItem(item_index)
            # Only update new email if provided
            # if new_email:
            #     item.setText(5, new_email)
            # # Update password and status
            # item.setText(6, password)
            item.setText(9, status)
            
            # Update color based on status
            if "thành công" in status.lower():
                for col in range(9):
                    item.setBackground(col, QColor("#90ee90"))  # Light green
            else:
                for col in range(9):
                    item.setBackground(col, QColor("#ff9999"))  # Light red

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
                password = item.text(6)
                cookie = item.text(3)
                line = f"{uid}|{old_email}|{new_email}|{password}|{cookie}"
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

        config_info = {
            'account': all_items,
            'proxy': f"{'yes' if proxy_enabled else 'no'} ({proxy_type if proxy_enabled else ''})",
            'type_password': password,
            'password': password_input if password_mode == "Tự nhập" else "********",
            'thread': num_threads,
            'type': 'change_pass'
        }
        def get_app_dir():
            if getattr(sys, 'frozen', False):
                # Nếu là exe thì lấy thư mục chứa file exe
                return os.path.dirname(sys.executable)
            else:
                # Nếu là chạy bằng python thì lấy thư mục file .py
                return os.path.dirname(os.path.abspath(__file__))

        # Đường dẫn tuyệt đối tới data.json
        json_path = os.path.join(get_app_dir(), 'data.json')

        # Ghi file
        with open(json_path, 'w', encoding='utf-8') as f:
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
    
    def update_item_status(self, item_index,password, status,cookie):
        if 0 <= item_index < self.tree_widget.topLevelItemCount():
            item = self.tree_widget.topLevelItem(item_index)
            item.setText(3, cookie)
            item.setText(5, password)
            item.setText(8, status)
            
            # Update color based on status
            if "thành công" in status.lower():
                for col in range(8):
                    item.setBackground(col, QColor("#90ee90"))  # Light green
            else:
                for col in range(8):
                    item.setBackground(col, QColor("#ff9999"))  # Light red
    
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
        
        select_errors_action = QAction("Chọn bôi đen", self)
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
        print("Add proxy action triggered")
        QMessageBox.information(self, "Thông báo", "Chức năng thêm proxy sẽ được phát triển trong phiên bản tiếp theo!")
        
    def select_all(self):
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
        # Select items with "Đăng nhập thất bại" status
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            if "thất bại" in item.text(7).lower():
                self.tree_widget.setCurrentItem(item)
                
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
        
        key_label = QLabel("Key: 8ff6d6348acbe82a8fb2b504280b02a4")
        copy_label = QLabel("COPY")
        copy_label.setStyleSheet("color: blue; text-decoration: underline; cursor: pointer;")
        copy_label.mousePressEvent = lambda event: self.copy_to_clipboard("8ff6d6348acbe82a8fb2b504280b02a4")
        
        hsd_label = QLabel("HSD: 29 days")
        check_label = QLabel("CheckChromedriver")
        check_label.setStyleSheet("color: red; text-decoration: underline; cursor: pointer;")
        
        author_label = QLabel("Author:")
        author_name_label = QLabel("Triều Lân")
        author_name_label.setStyleSheet("color: blue; text-decoration: underline; cursor: pointer;")
        
        footer_layout.addWidget(key_label)
        footer_layout.addWidget(copy_label)
        footer_layout.addWidget(hsd_label)
        footer_layout.addWidget(check_label)
        footer_layout.addWidget(author_label)
        footer_layout.addWidget(author_name_label)
        footer_layout.addStretch()
        
        layout.addLayout(footer_layout)
        
    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)


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
