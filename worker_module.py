from PyQt5.QtCore import QThread, pyqtSignal
import json
import threading
from main import Main
from run_ldplayer import LDPlayerRunner

class WorkerThread(QThread):
    update_status = pyqtSignal(int, str, str, str)  # index, new_pass, status, message
    update_counts = pyqtSignal(int, int)
    show_error = pyqtSignal(str)
    update_realtime_status = pyqtSignal(int, str)  # Signal mới để cập nhật status realtime

    def __init__(self, num_threads):
        super().__init__()
        self.num_threads = num_threads
        self.running = False
        self.account_instances = {}  # Lưu trữ các instance Main để lấy full cookie sau

    def status_callback(self, index, status_text):
        """Callback function để nhận status từ Main class"""
        self.update_realtime_status.emit(index, status_text)

    def run(self):
        with open('data.json', 'r') as f:
            data = json.load(f)
            self.type_run = data['type']

        # Nếu chỉ mở LDPlayer thì không cần account
        if self.type_run == 'open_ldplayer':
            self.running = True
            try:
                main_ldplayer = LDPlayerRunner(None, 0)
                # Kiểm tra số lượng máy ảo trước
                check_result = main_ldplayer.check_tab_ldplayer()
                if not check_result[0]:
                    self.show_error.emit(check_result[1])
                    self.running = False
                    return
                    
                # Nếu đủ số lượng máy ảo thì mới chạy
                vm_ids = main_ldplayer.get_id_machine()
                if vm_ids:
                    threads = []
                    for i in range(self.num_threads):
                        if not self.running:
                            break
                        if i < len(vm_ids):
                            main_ldplayer = LDPlayerRunner(None, i)
                            t = threading.Thread(target=main_ldplayer.open_ldplayer)
                            threads.append(t)
                            t.start()
                            
                    for t in threads:
                        t.join()
                else:
                    self.show_error.emit("Không tìm thấy máy ảo LDPlayer")
                    
            except Exception as e:
                self.show_error.emit(f"Lỗi: {str(e)}")
                print(f"Thread error: {e}")
            self.running = False
            return

        # Các loại còn lại cần account
        self.accounts = data['account']
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
                        account_index = i + idx  # Index thực tế trong danh sách
                        
                        if self.type_run == 'change_mail':
                            ldplayer = LDPlayerRunner(acc, idx)
                            success, error_msg = ldplayer.main()
                            if success:
                                results[idx] = (True, '', "Thay đổi email thành công!")
                            else:
                                results[idx] = (False, '', error_msg)
                                
                        elif self.type_run == 'change_pass':
                            # Tạo Main instance - dùng idx cho positioning, account_index cho callback
                            def status_callback_wrapper(index, status_text):
                                self.status_callback(account_index, status_text)  # Gửi account_index đúng về UI
                            
                            main_instance = Main(acc, idx, status_callback_wrapper)  # idx để positioning đúng
                            self.account_instances[account_index] = main_instance  # Lưu instance với key là account_index
                            
                            success, new_pass, cookie = main_instance.new_pass()
                            results[idx] = (success, new_pass, cookie, main_instance)
                            
                        elif self.type_run == 'forgot_pass':
                            # Tạo Main instance - dùng idx cho positioning, account_index cho callback
                            def status_callback_wrapper(index, status_text):
                                self.status_callback(account_index, status_text)  # Gửi account_index đúng về UI
                            
                            main_instance = Main(acc, idx, status_callback_wrapper)  # idx để positioning đúng
                            self.account_instances[account_index] = main_instance  # Lưu instance với key là account_index
                            
                            success, new_pass, cookie = main_instance.forgot_password()
                            results[idx] = (success, new_pass, cookie, main_instance)
                            
                    except Exception as e:
                        print(f"Thread error: {e}")
                        results[idx] = (False, '', str(e), None)

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
                    success_flag, new_pass, message, instance = False, '', 'Unknown error', None
                else:
                    if len(result) == 4:  # change_pass hoặc forgot_pass
                        success_flag, new_pass, message, instance = result
                    else:  # change_mail
                        success_flag, new_pass, message = result
                        instance = None

                # Cập nhật status với màu sắc và thông báo phù hợp
                if self.type_run == 'change_mail':
                    status = f"Thành công: {message}" if success_flag else f"Thất bại: {message}"
                    # Gửi cookie ngắn cho hiển thị, cookie đầy đủ sẽ được lấy khi export
                    short_cookie = ""
                else:
                    status = "Thành công" if success_flag else "Thất bại"
                    # Lấy cookie ngắn để hiển thị
                    if instance and success_flag:
                        short_cookie = instance.get_short_cookie()
                    else:
                        short_cookie = message if isinstance(message, str) else ""

                self.update_status.emit(index, new_pass, status, short_cookie)

                if success_flag:
                    success += 1
                else:
                    fail += 1

                self.update_counts.emit(success, fail)

        self.running = False

    def get_full_cookie_for_account(self, index):
        """Lấy cookie đầy đủ cho account theo index"""
        if index in self.account_instances:
            return self.account_instances[index].get_full_cookie()
        return ""

    def stop(self):
        self.running = False