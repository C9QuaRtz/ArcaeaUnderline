from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64
import hashlib
import platform
import subprocess

class StableAESCipher:
    def __init__(self, password, salt=None):
        """
        初始化加密器（密码派生密钥版本）
        :param password: 用户密码（字符串）
        :param salt: 固定盐值（建议至少16字节，不传则使用默认值）
        """
        # 固定盐值（确保相同密码每次生成相同密钥）
        self.salt = salt if salt else str.encode('特调卤汁小鱼干')  # 实际使用应改为随机生成后固定
        
        # 派生密钥（参数固定则结果固定）
        self.key = PBKDF2(password, self.salt, dkLen=32, count=1000000)
        
    def encrypt(self, plaintext):
        """加密方法（同前）"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        nonce = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        return base64.b64encode(nonce + ciphertext + tag).decode('utf-8')

    def decrypt(self, encrypted_data):
        """解密方法（同前）"""
        try:
            combined = base64.b64decode(encrypted_data)
            nonce, ciphertext, tag = combined[:16], combined[16:-16], combined[-16:]
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
        except Exception as e:
            raise ValueError("解密失败: 密钥错误或数据被篡改") from e
    
def get_device_fingerprint():
    # 1. 获取系统信息
    system_info = {
        "machine": platform.machine(),
        "processor": platform.processor(),
        "platform": platform.platform(),
    }

    # 2. 获取磁盘序列号（Windows/Linux/macOS兼容方法）
    try:
        if platform.system() == "Windows":
            disk_id = subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split("\n")[1].strip()
        else:
            disk_id = subprocess.check_output(["lsblk", "-o", "SERIAL"]).decode().split("\n")[1].strip()
    except:
        disk_id = "unknown"

    # 3. 获取主板信息
    try:
        if platform.system() == "Windows":
            baseboard = subprocess.check_output("wmic baseboard get serialnumber", shell=True).decode().split("\n")[1].strip()
        elif platform.system() == "Linux":
            baseboard = open("/sys/class/dmi/id/board_serial").read().strip()
        else:  # macOS
            baseboard = subprocess.check_output(["ioreg", "-l"]).decode()
    except:
        baseboard = "unknown"

    # 4. 生成组合指纹
    fingerprint_str = f"{system_info}{disk_id}{baseboard}"
    # print("系统信息:", fingerprint_str)
    return hashlib.sha256(fingerprint_str.encode()).hexdigest()


# 使用示例
if __name__ == "__main__":
    # 方案1：随机生成密钥（推荐）
    cipher = StableAESCipher(get_device_fingerprint())
    print("随机生成密钥:", base64.b64encode(cipher.key).decode('utf-8'))
    
    # 方案2：从密码派生密钥
    # cipher = SimpleAESCipher(SimpleAESCipher.generate_key_from_password("my-secret-password"))
    
    # 加密示例
    secret_msg = "这是一条需要加密的秘密信息"
    encrypted = cipher.encrypt(secret_msg)
    print("加密结果:", encrypted)
    
    # 解密示例
    decrypted = cipher.decrypt(encrypted)
    print("解密结果:", decrypted)