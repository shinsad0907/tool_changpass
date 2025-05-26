# worker_module.py
from PyQt5.QtCore import QThread, pyqtSignal
import json
import time
import threading
import tempfile
from main import Main  # Import hàm selenium
import os,sys

class WorkerThread(QThread):
    update_status = pyqtSignal(int, str, str ,str)
    update_counts = pyqtSignal(int, int)

    def __init__(self, num_threads):
        super().__init__()
        self.num_threads = num_threads
        self.running = False
        
        # Đọc JSON tại khởi tạo
        

    def run(self):
        with open('data.json', 'r') as f:
            data = json.load(f)
            self.accounts = data['account']
            self.type_run = data['type']
        
        success = 0
        fail = 0
        self.running = True
        total = len(self.accounts)

        for i in range(0, total, self.num_threads):
            if not self.running:
                break
                
            threads = []
            results = [None] * self.num_threads
            
            for j, account in enumerate(self.accounts[i:i+self.num_threads]):
                def thread_func(idx, acc):
                    try:
                        main_instance = Main(acc, idx)
                        if self.type_run == 'change_pass':
                            result = main_instance.new_pass()
                        elif self.type_run == 'forgot_pass':
                            result = main_instance.forgot_password()
                        else:
                            result = main_instance.new_mail()
                        results[idx] = result
                    except Exception as e:
                        print(f"Thread error: {e}")
                        results[idx] = (False, '', '')

                t = threading.Thread(target=thread_func, args=(j, account))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            # Process results
            for j, result in enumerate(results):
                index = i + j
                if index >= total:
                    continue

                if result is None:
                    success_flag, new_pass, cookie = False, '', ''
                else:
                    try:
                        success_flag, new_pass, cookie = result
                    except:
                        success_flag, new_pass, cookie = False, '', ''

                status = "Thành công" if success_flag else "Thất bại"
                
                # Convert cookie list to string if needed
                cookie_str = json.dumps(cookie) if isinstance(cookie, list) else str(cookie)
                
                # Emit signal với đầy đủ thông tin 
                if self.type_run == 'change_pass':
                    self.update_status.emit(index, new_pass, status, cookie_str)
                else:  # forgot_pass hoặc new_mail
                    self.update_status.emit(index, '', status, '')

                if success_flag:
                    success += 1
                else:
                    fail += 1

                self.update_counts.emit(success, fail)

        self.running = False

    def stop(self):
        self.running = False
