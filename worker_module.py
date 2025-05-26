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
                    if self.type_run == 'change_pass':
                        result = Main(acc, idx, self.type_run).new_pass()
                    else:
                        result = Main(acc, idx, self.type_run).new_mail()
                    results[idx] = result

                t = threading.Thread(target=thread_func, args=(j, account))
                threads.append(t)
                t.start()


            for t in threads:
                t.join()

            # Cập nhật GUI
            for j, result in enumerate(results):
                index = i + j
                if index >= total:
                    continue

                success_flag, new_pass_value,cookie = result

                status = "Thành công" if success_flag else "Thất bại"
                cookies_str = json.dumps(cookie)
                self.update_status.emit(index,new_pass_value, status,cookies_str)

                if success_flag:
                    success += 1
                else:
                    fail += 1

                self.update_counts.emit(success, fail)


        self.running = False

    def stop(self):
        self.running = False
