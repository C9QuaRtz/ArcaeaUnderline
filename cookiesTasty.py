import requests
import json
import yaml
from DataUpdate import configTemplate
from pwdCrypt import *

def get_login_cookies(login_url, credentials):
    """通过POST登录获取网站Cookie"""
    try:
        # 创建会话并设置一些常用头部
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://arcaea.lowiro.com/',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        session.headers.update(headers)

        # 发送登录请求
        response = session.post(login_url, data=credentials)
        response.raise_for_status()  # 如果请求失败会抛出HTTPError异常

        # 检查登录是否成功（根据网站实际情况调整）
        if json.loads(response.text)['isLoggedIn']:
            cookies = session.cookies.get_dict()
            return cookies
        else:
            print("登录失败，可能是凭证错误")
            return None

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None

# 使用示例
login_url = 'https://webapi.lowiro.com/auth/login'

cipher = StableAESCipher(get_device_fingerprint())

with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)
    username = config['username']
    password = cipher.decrypt(config['password'])

credentials = {
    'email': username,
    'password': password,
    'remember_me': 'true'  # 有些网站需要这个参数来持久化Cookie
}
cookies = get_login_cookies(login_url, credentials)
if cookies:
    config['Cookie'] = cookies
    with open('config.yaml', 'w', encoding='utf-8') as file:
        file.write(configTemplate.format(**config))
else:
    print("获取Cookie失败")