from DataUpdate import simple_get, WhichDifficulty
from cookiesTasty import tastyCookies
from pwdCrypt import *
from template import headersList
import json
import yaml
import time
from datetime import datetime
# import socket
import logging
import sys
import os

pttCheck = {
    'isInit': True
}
coolDown = 60

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def visual_countdown_bar(total_seconds, width=coolDown):
    """
    创建一个视觉上真正倒退的进度条
    
    参数:
        total_seconds: 总倒计时秒数
        width: 进度条的宽度
    """
    start_time = time.time()
    end_time = start_time + total_seconds
    
    # 填充和空字符
    fill_char = '█'
    empty_char = '░'
    
    while True:
        # 计算剩余时间
        current_time = time.time()
        elapsed_time = current_time - start_time
        remaining_time = total_seconds - elapsed_time
        
        if remaining_time <= 0:
            break
        
        # 计算进度条长度（从右向左减少）
        ratio = remaining_time / total_seconds
        filled_length = int(width * ratio)
        
        # 创建进度条（从右到左填充）
        bar = empty_char * (width - filled_length) + fill_char * filled_length
        
        # 剩余秒数（四舍五入到整数）
        remaining_seconds = round(remaining_time)
        
        # 输出进度条
        sys.stdout.write(f'\rRefresh in: |{bar}| {remaining_seconds}s... ')
        sys.stdout.flush()
        
        # 短暂暂停以减少CPU使用
        time.sleep(0.1)
    
    # 完成后清空并显示完成消息
    sys.stdout.write('\r     Refresh|' + empty_char * width + '| Complete.\n')
    sys.stdout.flush()

def rec(id, data):
    # 首先读取文件内容
    try:
        with open(f'playerLog.json', 'r', encoding='utf-8') as file:
            logFile = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # 如果文件不存在或为空，创建新的数据结构
        logFile = {}
        # exit(e)
    
    # 确保id键存在
    if f'{id}' not in logFile:
        logFile[f'{id}'] = []
    
    # 添加新数据
    logFile[f'{id}'].append(data)
    
    # 完全覆写文件
    with open(f'playerLog.json', 'w', encoding='utf-8') as file:
        json.dump(logFile, file, ensure_ascii=False, indent=2)

def notification(param):
    # your notification method here...

    return

def pttDiff(user_id, ptt) -> str:
    global pttCheck
    if pttCheck['isInit']:
        pttCheck[f'{user_id}'] = ptt
        return f'PTT = {ptt / 100}'
    else:
        tmp = pttCheck[f'{user_id}']
        if ptt > pttCheck[f'{user_id}']:
            pttCheck[f'{user_id}'] = ptt
            return f'PTT = {tmp / 100} +{(ptt - tmp) / 100}'
        elif ptt < pttCheck[f'{user_id}']:
            pttCheck[f'{user_id}'] = ptt
            return f'PTT = {tmp / 100} -{(tmp - ptt) / 100}'
        else:
            return f'PTT = {tmp / 100} Keep'
        

if __name__ == '__main__':
    args = '/webapi/user/me'
    cipher = StableAESCipher(get_device_fingerprint())
    
    if not os.path.exists('monitaringu.yaml'):
        config = {}
        config['username'] = input('username: ')
        config['password'] = cipher.encrypt(input('password: '))
        config['Cookie'] = 'SANA♡TSU Chocolate Cookie 12枚入'
        nameList = input('userID(splits with space): ').split()
        config['objects'] = []
        for i in range(len(nameList)):
            config['objects'].append({
                'name': nameList[i],
                'user_id': 0x0d000721
            })
        with open('monitaringu.yaml', 'w', encoding='utf-8') as file:
            yaml.dump(config, file, allow_unicode=True)
        tastyCookies('monitaringu.yaml')
    
    nameList = []

    with open('monitaringu.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        for i in range(len(config['objects'])):
            nameList.append(config['objects'][i]['name'])
        preHeaders = headersList['lowiro']
        preHeaders['Cookie'] = f'sid={config["Cookie"]['sid']}; ctrcode={config["Cookie"]['ctrcode']}'
            
    friendList = json.loads(simple_get(args, headers=preHeaders))['value']['friends']
    userID = []
    
    for i in range(len(nameList)):
        for j in range(len(friendList)):
            if nameList[i] == friendList[j]['name']:
                config['objects'][i]['user_id'] = friendList[j]['user_id']
                userID.append(friendList[j]['user_id'])
                break
            if j == len(friendList) - 1:
                notification(f'{nameList[i]} may not your account\'s friend.\nCan\'t get {nameList[i]}\'s [\'user_id\'].')
                print(f'{nameList[i]} may not your account\'s friend.\nCan\'t get {nameList[i]}\'s [\'user_id\'].')
                config['objects'][i]['user_id'] = 'o(*≧д≦)o!!'
  
    with open('monitaringu.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(config, file)
    
    notification("StartUp Finished.")
    while True:
        try:
            now = time.time() * 1000

            rcy = 0
            for i in range(len(friendList)):
                if rcy == len(userID):
                    break
                for j in range(len(userID)):
                    if friendList[i]['user_id'] == userID[j] and (now - friendList[i]['recent_score'][0]['time_played'] <= 61500 or pttCheck['isInit']):
                    
                        userName = friendList[i]['name']
                        song = friendList[i]['recent_score'][0]['title']['ja']
                        difficulty = WhichDifficulty(friendList[i]['recent_score'][0]['difficulty'])
                        score = friendList[i]['recent_score'][0]['score']
                        t = datetime.fromtimestamp(friendList[i]['recent_score'][0]['time_played'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                        pttInfo = pttDiff(friendList[i]['user_id'], friendList[i]['rating'])

                        rec(friendList[i]['user_id'], friendList[i])
                        notification(f"{userName}\n{song} {difficulty} {score}\n{pttInfo}\n{t}")
                        print(f"{userName}\n{song} {difficulty} {score}\n{pttInfo}\n{t}\n")
                        rcy += 1
                        break
            
            if pttCheck['isInit']:
                pttCheck['isInit'] = False
            visual_countdown_bar(coolDown)
            result = json.loads(simple_get(args, headers=preHeaders))
            friendList = result['value']['friends']
        except Exception as error:
            logging.error(f'{error}')
            notification(f'{error}')