from PyQt5.QtCore import QThread, pyqtSignal
import json
import threading
from main import Main
from run_ldplayer import LDPlayerRunner

class WorkerThread(QThread):
    update_status = pyqtSignal(int, str, str, str)
    update_counts = pyqtSignal(int, int)
    show_error = pyqtSignal(str)

    def __init__(self, num_threads):
        super().__init__()
        self.num_threads = num_threads
        self.running = False

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
                        if self.type_run == 'change_mail':
                            ldplayer = LDPlayerRunner(acc, idx)
                            success, error_msg = ldplayer.main()
                            if success:
                                results[idx] = (True, '', "Thay đổi email thành công!")
                            else:
                                results[idx] = (False, '', error_msg)
                        elif self.type_run == 'change_pass':
                            main_instance = Main(acc, idx)
                            success, new_pass, cookie = main_instance.new_pass()
                            results[idx] = (success, new_pass, cookie)
                        elif self.type_run == 'forgot_pass':
                            main_instance = Main(acc, idx)
                            success, new_pass, cookie = main_instance.forgot_password()
                            results[idx] = (success, new_pass, cookie)
                    except Exception as e:
                        print(f"Thread error: {e}")
                        results[idx] = (False, '', str(e))

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
                    success_flag, new_pass, message = False, '', 'Unknown error'
                else:
                    success_flag, new_pass, message = result

                # Cập nhật status với màu sắc và thông báo phù hợp
                if self.type_run == 'change_mail':
                    status = f"Thành công: {message}" if success_flag else f"Thất bại: {message}"
                else:
                    status = "Thành công" if success_flag else "Thất bại"

                self.update_status.emit(index, new_pass, status, message if message else '')

                if success_flag:
                    success += 1
                else:
                    fail += 1

                self.update_counts.emit(success, fail)

        self.running = False

    def stop(self):
        self.running = False