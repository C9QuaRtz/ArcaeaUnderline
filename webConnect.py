import requests
import json
import yaml
import re
import socket
import logging
import time
import os
from pwdCrypt import StableAESCipher, get_device_fingerprint
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
        
headersList = {
    'lowiro': {
        'Accept': 'application/json, text/plain, */*',
        'Cookie': '',
        'Dnt': '1',
        'Origin': 'https://arcaea.lowiro.com',
        'Priority': 'u=1, i',
        'Referer': 'https://arcaea.lowiro.com/',
        'Sec-Ch-Ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
    },
    'mcd': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'arcwiki.mcd.blue',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
}

retry = 3

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
def tastyCookies(accType):
    if accType == 'mainAccount':
        filename = 'config.yaml'
    elif accType == 'monitaringu':
        filename = 'monitaringu.yaml'

    login_url = 'https://webapi.lowiro.com/auth/login'

    cipher = StableAESCipher(get_device_fingerprint())

    with open(filename, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        username = config['username']
        password = cipher.decrypt(config['password'])
    
    if type(username) != str or type(password) != str:
        exit("\n欸…账密格式填的不对呢……(σ｀д′)σ")

    credentials = {
        'email': username,
        'password': password,
        'remember_me': 'true'  # 有些网站需要这个参数来持久化Cookie
    }
    cookies = get_login_cookies(login_url, credentials)
    cookies = f'sid={cookies['sid']}; ctrcode={cookies['ctrcode']}'
    if cookies:

        if os.path.exists('cookiesPot.yaml'):
            with open('cookiesPot.yaml', 'r', encoding='utf-8') as f:
                cookiesPot = yaml.safe_load(f)
        else:
            cookiesPot = {}
        cookiesPot[accType] = cookies
        with open('cookiesPot.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(cookiesPot, f, allow_unicode=True)
        
        return cookies
                
    else:
        exit("获取Cookie失败")

def jsonSave(data, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def simple_get(
        args: str,
        url = "https://webapi.lowiro.com",
        headers = headersList['lowiro'],
        accType = 'mainAccount'
    ):
    if os.path.exists('cookiesPot.yaml'):
        with open('cookiesPot.yaml', 'r', encoding='utf-8') as file:
            cookiesPot = yaml.safe_load(file)
        cookie = cookiesPot[accType] if accType in cookiesPot else tastyCookies(accType)
    else:
        cookie = tastyCookies(accType)
    headers['Cookie'] = cookie
    reFreshed = False

    for i in range(retry):
        try:
            if reFreshed:
                headers['Cookie'] = cookie
            
            response = requests.get(url + args, headers=headers)
            response.raise_for_status()
            return response.text
        
        except Exception as err:
            if "400" in str(err) and not reFreshed:
                print(f'\n呜哇！Σ(っ °Д °;)っ被Ai酱认出来了吗？！ 再试试用账密伪装一次喵……')
                cookie = tastyCookies(accType)
                reFreshed = True
            print(f"呜哇！Σ(っ °Д °;)っ和Ai酱交流的时候连接突然炸掉啦！问题好像是这个呢: \n{err}\n\n正在尝试第 {i + 1} 次喵……")
    
    print(f"呜呜呜……ヽ(*。>Д<)o゜ 连接不到Ai酱了喵……等一会再试试看吧？")
        
def simple_post(
        url: str, 
        data: Optional[Union[Dict[str, Any], str]],
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> requests.Response:
    
    default_headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'KoinoNano/1.0',
        'charset': 'utf-8'
    }

    # 创建带有重试机制的Session
    session = requests.Session()
    retry = Retry(
        total=max_retries,
        backoff_factor=retry_delay,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # 尝试发送请求
    for attempt in range(max_retries + 1):
        try:
            response = session.post(
                url=url,
                data=data,
                timeout=10
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout as e:
            if attempt == max_retries:
                print(f"请求超时，达到最大重试次数 {max_retries}: {url}")
                raise
            print(f"请求超时，正在进行第 {attempt + 1} 次重试: {url}")
            
        except requests.exceptions.ConnectionError as e:
            if attempt == max_retries:
                print(f"连接错误，达到最大重试次数 {max_retries}: {url}")
                raise
            print(f"连接错误，正在进行第 {attempt + 1} 次重试: {url}")
            
        except requests.exceptions.HTTPError as e:
            # 对于HTTP错误，只有5xx状态码会重试
            if e.response.status_code < 500 or attempt == max_retries:
                print(f"HTTP错误: {e}")
                raise
            print(f"HTTP错误，正在进行第 {attempt + 1} 次重试: {e}")
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                print(f"请求异常，达到最大重试次数 {max_retries}: {e}")
                raise
            print(f"请求异常，正在进行第 {attempt + 1} 次重试: {e}")
        
        # 如果不是最后一次尝试，等待一段时间再重试
        if attempt < max_retries:
            time.sleep(retry_delay * (attempt + 1))  # 指数退避
    
    # 理论上不会执行到这里，因为所有异常都会被上面的代码处理
    raise requests.exceptions.RequestException("未知错误，重试机制失败")

def extract_with_bs4(content, tag_name, **attrs):
    
    # 创建BeautifulSoup对象
    soup = BeautifulSoup(content, 'html.parser')
    
    # 查找指定标签
    elements = soup.find_all(tag_name, attrs=attrs)
    
    # 提取标签内容
    results = [element.get_text() for element in elements]
    return results

def getChartConstant():
    cc = json.loads(
            extract_with_bs4(
                simple_get(
                    url = "https://arcwiki.mcd.blue",
                    args = '/index.php?title=Template:ChartConstant.json&action=edit',
                    headers = headersList['mcd']
                ),
            'textarea',
            id = 'wpTextbox1'
            )[0]
        )
    jsonSave(cc, 'ChartConstant.json')
    return cc

def extract_table_data(html_content):
    """
    从HTML内容中提取指定的表格数据并转换为JSON格式
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找目标表格 - 根据class属性定位
    table = soup.find('table', class_='wikitable sortable')
    
    if not table:
        print("未找到目标表格")
        return None
    
    # 提取表头
    thead = table.find('thead')
    headers = []
    if thead:
        header_rows = thead.find_all('tr')
        for row in header_rows:
            row_headers = []
            for th in row.find_all(['th', 'td']):
                text = th.get_text(strip=True)
                if text:
                    row_headers.append(text)
            if row_headers:
                headers.append(row_headers)
    
    # 提取表格数据
    tbody = table.find('tbody')
    if not tbody:
        tbody = table  # 如果没有tbody，直接从table中查找tr
    
    rows_data = []
    for tr in tbody.find_all('tr'):
        row_data = {}
        cells = tr.find_all(['td', 'th'])
        
        if len(cells) == 0:
            continue
            
        # 根据图片中的表格结构，假设列的顺序
        for i, cell in enumerate(cells):
            cell_text = cell.get_text(strip=True)
            
            # 处理链接
            link = cell.find('a')
            if link:
                href = link.get('href', '')
                title = link.get('title', '')
                link_text = link.get_text(strip=True)
                
                row_data[f'column_{i}'] = {
                    'text': cell_text,
                    'link': {
                        'href': href,
                        'title': title,
                        'text': link_text
                    }
                }
            else:
                # 尝试将数字转换为适当的类型
                if cell_text.isdigit():
                    row_data[f'column_{i}'] = int(cell_text)
                elif re.match(r'^\d+(\.\d+)?$', cell_text):
                    row_data[f'column_{i}'] = float(cell_text)
                else:
                    row_data[f'column_{i}'] = cell_text
        
        if row_data:  # 只添加非空行
            rows_data.append(row_data)
    
    # 构建最终的JSON结构
    result = {
        'headers': headers,
        'data': rows_data,
        'total_rows': len(rows_data)
    }
    
    return result

def restructure_json_data(data):
    """
    重构JSON数据为更直观的格式
    
    Args:
        data: 原始的JSON数据列表
    
    Returns:
        重构后的JSON数据列表
    """
    # 删除前两项
    if len(data) >= 2:
        data = data[2:]
    elif len(data) == 1:
        data = []
    
    restructured_data = []
    
    for item in data:
        # 构建新的数据结构
        new_item = {
            "id": item.get("column_0"),
            "name": "",
            "wikilink": "",
            "type": item.get("column_2", ""),
            "statistics": {
                "Lv.1": {
                    "Frag": item.get("column_3"),
                    "Step": item.get("column_4"),
                    "Over": item.get("column_5")
                },
                "Lv.20": {
                    "Frag": item.get("column_6"),
                    "Step": item.get("column_7"),
                    "Over": item.get("column_8")
                },
                "Lv.30": {
                    "Frag": item.get("column_9"),
                    "Step": item.get("column_10"),
                    "Over": item.get("column_11")
                }
            },
            "skill": item.get("column_12", "")
        }
        
        # 处理column_1的复杂结构
        column_1 = item.get("column_1")
        if isinstance(column_1, dict):
            new_item["name"] = column_1.get("text", "")
            link_info = column_1.get("link", {})
            new_item["wikilink"] = link_info.get("href", "")
        else:
            # 如果column_1是字符串
            new_item["name"] = str(column_1) if column_1 is not None else ""
            new_item["wikilink"] = ""
        
        restructured_data.append(new_item)
    
    return restructured_data

def getPartnerData():
    html_sample = simple_get(
        args = '/%E6%90%AD%E6%A1%A3',
        url = 'https://arcwiki.mcd.blue',
        headers = headersList['mcd']
    )
    data = extract_table_data(html_sample)
    data = restructure_json_data(data['data'])
    
    if data:
        # 输出为格式化的JSON
        
        # 保存到文件
        jsonSave(data, 'partner.json')
        return data

def extract_fullmedia_href(html_input):
    """
    从HTML中提取class="fullMedia"的div元素内部的href参数
    
    参数:
    html_input: HTML文件路径或HTML字符串
    input_type: 'file' 表示输入是文件路径，'string' 表示输入是HTML字符串
    
    返回:
    list: 包含所有找到的href值的列表
    """
    
    # 读取HTML内容
    
    # 解析HTML
    soup = BeautifulSoup(html_input, 'html.parser')
    
    href_list = []
    
    # 查找所有class="fullMedia"的元素
    fullmedia_elements = soup.find_all(class_='fullMedia')
    
    # 在每个fullMedia元素内部查找所有带href的链接
    for element in fullmedia_elements:
        links = element.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if href:
                href_list.append(href)
    
    # 去重并保持顺序
    seen = set()
    unique_href_list = []
    for href in href_list:
        if href not in seen:
            seen.add(href)
            unique_href_list.append(href)
    
    return unique_href_list

def getSongCover(song_id, isBYD = False):
    if isBYD:
        song_id = f'{song_id}_byd'
    
    try:
        link = extract_fullmedia_href(
            simple_get(
                url = 'https://arcwiki.mcd.blue',
                args = f'/File:Songs_{song_id}.jpg',
                headers = headersList['mcd']
            )
        )[0]
        return f'https://arcwiki.mcd.blue{link}'
    except Exception as e:
        print(e)
        print(f'Feching cover for {song_id} failed.\nNow trying [FTR] cover...')
        try:
            link = extract_fullmedia_href(
                simple_get(
                    url = 'https://arcwiki.mcd.blue',
                    args = f'/File:Songs_{song_id[:-4]}.jpg',
                    headers = headersList['mcd']
                )
            )[0]
            return f'https://arcwiki.mcd.blue{link}'
        except Exception as e:
            print(e)
            print(f'Fetching cover for {song_id} failed.')
            return None

def send_parameter(param):
    # your notify code here...
    return

def doBark(msg, devicesKey: list):
    success = True
    for key in devicesKey:
        response = simple_post(
            url = f'https://api.day.app/{key}',
            data = msg
        )
        if response.json().get('code') != 200:
            logging.error(json.dumps(response.json(), ensure_ascii=False, indent=4))
            success = False
    return success