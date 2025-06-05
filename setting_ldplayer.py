import subprocess
import json
import random
import uuid
import os

class LDPlayerSettings:
    def __init__(self):
        with open('setting_ldplayer.json', 'r') as configfile:
            config_data = json.load(configfile)
        self.ldplayer_path = config_data['ld_path']
        self.tess_path = config_data['tess_path']
        self.cpu = config_data['cpu']
        self.ram = config_data['ram']
        self.width = config_data['width']
        self.height = config_data['height']
        self.dpi = config_data['dpi']
        self.CACHE = config_data['CACHE']
        self.OTHER = config_data['OTHER']
        self.ADB = config_data['ADB']
        
        with open('data.json', 'r') as configfile:
            config_data = json.load(configfile)
        self.tab_ldplayer = config_data['thread']

    # def get_id_machine(self):
    #     result = subprocess.run([f'{self.ldplayer_path}\ldconsole.exe', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #     output = result.stdout.strip()
    #     # Mỗi dòng trong output đại diện cho một máy ảo
    #     vm_list = output.splitlines()
    #     if vm_list:
    #         # Lấy ID của máy ảo đầu tiên (giả sử ID là phần đầu tiên của mỗi dòng)
    #         return vm_list
        
    def random_imei(self):
        # 15 số, số cuối là checksum (Luhn)
        def luhn_residue(digits):
            return (10 - sum(sum(divmod(int(d)*(1 + i%2), 10))
                for i, d in enumerate(digits[::-1]))) % 10
        imei = [str(random.randint(0,9)) for _ in range(14)]
        imei.append(str(luhn_residue(''.join(imei))))
        return ''.join(imei)

    def random_imsi(self):
        # 15 số
        return ''.join([str(random.randint(0,9)) for _ in range(15)])

    def random_serial(self):
        # 20 số
        return ''.join([str(random.randint(0,9)) for _ in range(20)])

    def random_android_id(self):
        # 16 ký tự hex
        return uuid.uuid4().hex[:16]

    def random_mac(self):
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(12))

    def random_model(self):
        models = ["SM-G991B", "SM-N971N", "Pixel 7", "V2038", "M2012K11AG", "CPH2219", "M2101K6G"]
        return random.choice(models)

    def random_manufacturer(self):
        return random.choice(["samsung", "xiaomi", "oppo", "vivo", "google", "realme"])

    def random_phone_name(self):
        return random.choice(["Galaxy S21", "Galaxy Note10", "Pixel 7", "Redmi Note 10", "OPPO Reno6", "Vivo Y20"])

    def random_phone_number(self):
        return "09" + ''.join([str(random.randint(0,9)) for _ in range(8)])

    def random_mac_colon(self):
        mac = [random.randint(0,255) for _ in range(6)]
        return ':'.join(f"{x:02X}" for x in mac)

    def change_ldplayer_config(self, config_path):
        try:
            print(f"Updating LDPlayer config at {config_path}")
            # Read existing config
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Update config values
            data["propertySettings.phoneIMEI"] = self.random_imei()
            data["propertySettings.phoneIMSI"] = self.random_imsi()
            data["propertySettings.phoneSimSerial"] = self.random_serial()
            data["propertySettings.phoneAndroidId"] = self.random_android_id()
            data["propertySettings.phoneModel"] = self.random_model()
            data["propertySettings.phoneManufacturer"] = self.random_manufacturer()
            data["propertySettings.macAddress"] = self.random_mac()
            data["propertySettings.phoneNumber"] = self.random_phone_number()
            data["basicSettings.width"] = self.width
            data["basicSettings.height"] = self.height
            data["advancedSettings.resolution"] = {
                "width": data["basicSettings.width"],
                "height": data["basicSettings.height"]
            }
            data["advancedSettings.resolutionDpi"] = self.dpi
            data["advancedSettings.cpuCount"] = self.cpu
            data["advancedSettings.memorySize"] = self.ram
            data["advancedSettings.adbDebug"] = int(self.ADB)

            # Write updated config
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error updating config {config_path}: {e}")
