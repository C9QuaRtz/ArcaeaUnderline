from DataUpdate import WhichDifficulty
from pwdCrypt import *
from webConnect import simple_get, getPartnerData, getSongCover, doBark, getChartConstant
import json
import yaml
import time
from datetime import datetime
import logging
import sys
import os
import urllib.parse
import traceback
import asyncio
import math

coolDown: int = 60
lastInfo: dict = {}
lastPTT: dict = {}
partnerData: dict = {}
constantData: dict = {}
barkLevel: str = 'passive'
devicesKey: list = []

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def countdownBar(total_seconds: float, width: int = coolDown, interval: float = 1):
    """
    高级版倒计时进度条（支持浮点秒数）
    
    参数:
        description (str): 描述文本
        total_seconds (float): 总秒数（支持小数）
        width (int): 进度条宽度
        interval (float): 更新间隔(秒)
    """
    # print(f"\n{description}")
    start_time = time.time()
    end_time = start_time + total_seconds
    
    while (remaining := end_time - time.time()) > 0:
        # 计算进度
        elapsed = total_seconds - remaining
        progress = elapsed / total_seconds
        filled_length = min(width, int(width * progress))
        bar = '█' * filled_length + '░' * (width - filled_length)
        
        # 格式化输出
        # percent = f"{progress * 100:.1f}%"
        time_info = f"{math.ceil(remaining)}s..."
        sys.stdout.write(f"\rRefresh in: |{bar}| {time_info}\n")
        sys.stdout.flush()
        await asyncio.sleep(min(interval, remaining))
    
    # 倒计时结束后显示完成状态
    sys.stdout.write(f"\r    Refresh |{'█' * width}| Complete.\n")
    sys.stdout.flush()

def fileRec(data):
    id = data['user_id']
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
    if logFile[f'{id}'][len(logFile[f'{id}']) - 1] != data:
        logFile[f'{id}'].append(data)
    
        # 完全覆写文件
        with open(f'playerLog.json', 'w', encoding='utf-8') as file:
            json.dump(logFile, file, ensure_ascii=False, indent=2)
        
        return True

    else:
        print(f'{data['name']}\'s Log continues, skipping...')
        return False

def dictDiff(old, new):
    return {
        key: [old.get(key), new.get(key)]
        for key in set(old.keys()) | set(new.keys())
        if (key not in old or key not in new or old[key] != new[key]) and (True)
    }

def lastRec(data):
    global lastInfo
    lastInfo[f'{data['user_id']}'] = data
    if data['rating'] != -1:
        if f'{data['user_id']}' not in lastPTT:
            lastPTT[f'{data['user_id']}'] = {}
        lastPTT[f'{data['user_id']}']['rating'] = data['rating']
        lastPTT[f'{data['user_id']}']['rating_time'] = time.time() * 1000

def searchPartner(id):
    global partnerData
    return next((item for item in partnerData if item.get('id') == id), None)

def searchConstant(id, difficulty):
    global constantData
    try:
        return constantData.get(f'{id}')[difficulty].get('constant', None)
    except Exception as e:
        logging.warning(f'Error searching constant for song_id {id} with difficulty {difficulty}: {e}')
        return '--'

def getSongLink(songName):
    """
    处理字符串的函数
    
    参数:
        input_string (str): 输入的字符串
    
    返回:
        str: 处理后的URL编码字符串
    
    处理步骤:
        1. 将所有的"#"替换为全角符号"＃"
        2. 将所有的空格替换为下划线"_"
        3. 对结果进行URL编码
    """
    # 步骤1: 将半角"#"替换为全角"＃"
    processed_string = songName.replace('#', '＃') # 说的就是你 色号！
    
    # 步骤2: 将空格替换为下划线
    processed_string = processed_string.replace(' ', '_')
    
    # 步骤3: 进行URL编码
    encoded_string = urllib.parse.quote(processed_string, safe='')

    encoded_string = 'https://arcwiki.mcd.blue/' + encoded_string
    
    return encoded_string

async def updateCheck(newData):
    global lastInfo
    global lastPTT
    updateInfo = {
        'user_id': newData['user_id'],
        'userName': newData['name'],
        'nowRating': newData['rating'],
        'icon': f'https://webassets.lowiro.com/chr/{newData['icon']}.png'
    }
    id = newData['user_id']
    oldData = lastInfo[f'{id}']
    lastRec(newData)

    diff = dictDiff(oldData, newData)
    if diff:
        if 'character' in diff:
            oldChar = searchPartner(oldData['character'])
            newChar = searchPartner(newData['character'])
            updateInfo['character'] = {
                'old': {
                    'name': oldChar['name'] if oldChar else 'Unknown',
                    'icon': f'https://webassets.lowiro.com/chr/{oldData['icon']}.png',
                    'wikilink': f'https://arcwiki.mcd.blue{oldChar['wikilink']}',
                    'is_char_uncapped': oldData['is_char_uncapped'],
                    'is_char_uncapped_override': oldData['is_char_uncapped_override']
                },
                'new': {
                    'name': newChar['name'] if newChar else 'Unknown',
                    'icon': f'https://webassets.lowiro.com/chr/{newData['icon']}.png',
                    'wikilink': f'https://arcwiki.mcd.blue{newChar['wikilink']}',
                    'is_char_uncapped': newData['is_char_uncapped'],
                    'is_char_uncapped_override': newData['is_char_uncapped_override']
                }
            }

        if 'recent_score' in diff:
            song_id = newData['recent_score'][0]['song_id']
            isBYD = True if newData['recent_score'][0]['difficulty'] == 3 else False
            now = time.time() * 1000
            timeBefore = round((now - newData['recent_score'][0]['time_played']) / 1000, 1)
            updateInfo['recent_score'] = {
                'old': oldData['recent_score'][0],
                'new': newData['recent_score'][0],
                'newCover': getSongCover(song_id, isBYD),
                'timeBefore': timeBefore
            }

        if 'rating' in diff:
            if newData['rating'] == -1 and oldData['rating'] != -1:
                t = datetime.fromtimestamp(lastPTT[f'{id}']['rating_time'] / 1000).strftime("%m-%d %H:%M:%S")
                info = f'PTT Hidden. ({lastPTT[f'{id}']['rating'] / 100:.2f} at {t})'
                lastPTT[f'{id}']['info'] = info
            elif newData['rating'] != -1 and oldData['rating'] == -1:
                info = f'PTT = {newData['rating'] / 100:.2f} Shown.'
                lastPTT[f'{id}']['info'] = None
            elif newData['rating'] != -1 and oldData['rating'] != -1:
                if newData['rating'] > oldData['rating']:
                    bonus = f' +{(newData['rating'] - oldData['rating']) / 100:.2f}'
                elif newData['rating'] < oldData['rating']:
                    bonus = f' -{(oldData['rating'] - newData['rating']) / 100:.2f}'
                info = f'PTT = {oldData['rating'] / 100:.2f}{bonus}'

            updateInfo['rating'] = {
                'old': oldData['rating'],
                'new': newData['rating'],
                'info': info
            }
        
        if 'recent_score' in diff and 'rating' not in diff:
            updateInfo['rating'] = {
                'old': oldData['rating'],
                'new': newData['rating'],
                'info': lastPTT[f'{id}']['info'] if lastPTT[f'{id}'].get('info') else f'PTT = {newData['rating'] / 100:.2f} Keep'
            }
        
        if 'name' in diff:
            updateInfo['name'] = {
                'old': oldData['name'],
                'new': newData['name']
            }
        
        barkInfoMerge(updateInfo)
    
def barkInfoMerge(info):
    global barkLevel
    msgs = []

    if 'character' in info:
        msgs.append({
            'title': f'{info['userName']} 更换了搭档！',
            'body': f'{info['character']['old']['name']} -> {info['character']['new']['name']}',
            'level': barkLevel,
            'icon': info['character']['new']['icon'],
            'group': info['user_id'],
            'url': info['character']['new']['wikilink']
        })
    
    if 'recent_score' in info and 'rating' in info:
        score = f'{info['recent_score']['new']['score']:,}'.replace(',', '\'')
        if info['recent_score']['new']['score'] < 10000000:
            score = '0' + score
        msgs.append({
            'title': f'{info['userName']} {info['rating']['info'] if 'Keep' not in info['rating']['info'] else '提交了新成绩！'}',
            'subtitle': f'{info['recent_score']['new']['title']['ja']} {WhichDifficulty(info['recent_score']['new']['difficulty'])[:-1]} {searchConstant(info['recent_score']['new']['song_id'], info['recent_score']['new']['difficulty'])}]',
            'body': f'{score}{'   /'+info['rating']['info'] if 'Keep' in info['rating']['info'] else ''}\n/{info['recent_score']['timeBefore']}s before',
            'level': barkLevel,
            'icon': info['icon'],
            'image': info['recent_score']['newCover'],
            'group': info['user_id'],
            'url': getSongLink(info['recent_score']['new']['title']['en'])
        })
    
    if 'recent_score' not in info and 'rating' in info:
        msgs.append({
            'title': f'{info['userName']} 变更了 PTT 的展示选项！',
            'body': f'{info['rating']['info']}',
            'level': barkLevel,
            'icon': info['icon'],
            'group': info['user_id']
        })
    
    if 'name' in info:
        msgs.append({
            'title': f'{info['name']['old']} 更换了名称！',
            'body': f'{info['name']['old']} -> {info['name']['new']}',
            'level': barkLevel,
            'icon': info['icon'],
            'group': info['user_id']
        })
    
    for msg in msgs:
        try:
            doBark(msg, devicesKey)
        except Exception as error:
            logging.error(error)
            print('Bark Notification Failed.')
            traceback.print_exc()
        print(json.dumps(msg, ensure_ascii=False, indent=4))
        print()


async def main():
    global coolDown
    global lastInfo
    global lastPTT
    global partnerData
    global constantData
    global barkLevel
    global devicesKey
    while 39:
        try:
            args = '/webapi/user/me'
            cipher = StableAESCipher(get_device_fingerprint())
            
            if not os.path.exists('monitaringu.yaml'):
                config = {
                    'username': '',
                    'password': '',
                    'Cookie': 'SANA♡TSU Chocolate Cookie 12枚入',
                    'objects': [],
                    'devicesKey': []
                }
                config['username'] = input('username: ')
                config['password'] = cipher.encrypt(input('password: '))
                config['Cookie'] = 'SANA♡TSU Chocolate Cookie 12枚入'
                nameList = input('userID(splits with space): ').split()
                devices = input('Bark devices Key(splits with space, or you can also leave it blank): ').split()
                for i in range(len(nameList)):
                    config['objects'].append({
                        'name': nameList[i],
                        'user_id': 0x0d000721
                    })
                for i in range(len(devices)):
                    config['devicesKey'].append(devices[i])
                with open('monitaringu.yaml', 'w', encoding='utf-8') as file:
                    yaml.dump(config, file, allow_unicode=True)
            
            configName = []
            configID = []

            with open('monitaringu.yaml', 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            for i in range(len(config['objects'])):
                configName.append(config['objects'][i]['name'])
                configID.append(config['objects'][i]['user_id'])
            for i in range(len(config['devicesKey'])):
                devicesKey.append(config['devicesKey'][i])
            logging.info('Config loaded...')
            
            friendList = json.loads(simple_get(args, accType='monitaringu'))['value']['friends']
            userID = []

            for i in range(len(configName)):
                for j in range(len(friendList)):
                    if configID[i] == friendList[j]['user_id'] or configName[i] == friendList[j]['name']:
                        config['objects'][i]['name'] = friendList[j]['name']
                        config['objects'][i]['user_id'] = friendList[j]['user_id']
                        userID.append(friendList[j]['user_id'])
                        lastRec(friendList[j])
                        fileRec(friendList[j])
                        break
                    if j == len(friendList) - 1:
                        logging.warning(f'{configName[i]} may not your account\'s friend.\nCan\'t get {configName[i]}\'s [\'user_id\'].')
                        config['objects'][i]['user_id'] = '[ACCESS_DENINED] o(*≧д≦)o!!'
            
            with open('monitaringu.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(config, file, allow_unicode=True)
            
            logging.info('Friend List Initialized...')

            try:
                partnerData = getPartnerData()
            except Exception as error:
                if os.path.exists('partner.json'):
                    with open('partner.json', 'r', encoding='utf-8') as file:
                        partnerData = json.load(file)
                    logging.warning(f'Partner data updated failed.\n{error}\nUsing old partner data.')
                else:
                    logging.error(f'No partner data found.\nPlease check your network connection or try again later.\nerror: {error}')
                    exit(1)
            logging.info('Partner Data Fetched...')

            try:
                constantData = getChartConstant()
            except Exception as error:
                if os.path.exists('ChartConstant.json'):
                    with open('ChartConstant.json', 'r', encoding='utf-8') as file:
                        constantData = json.load(file)
                    logging.warning(f'Chart constant data updated failed.\n{error}\nUsing old chart constant data.')
                else:
                    logging.error(f'No chart constant data found.\nPlease check your network connection or try again later.\nerror: {error}')
                    exit(1)
            logging.info('Chart Constant Data Fetched...')

            logging.info("StartUp Finished.\n")
            await countdownBar(coolDown)
            while True:
                try:
                    
                    result = json.loads(simple_get(args, accType='monitaringu'))
                    friendList = result['value']['friends']

                    tasks = []
                    try:
                        async with asyncio.TaskGroup() as tg:
                            tasks.append(tg.create_task(countdownBar(coolDown)))

                            for i in range(len(userID)):
                                for j in range(len(friendList)):
                                    if userID[i] == friendList[j]['user_id']:
                                        task = tg.create_task(updateCheck(friendList[j]))
                                        tasks.append(task)
                                        break
                    
                    except* Exception as eg:
                        for exc in eg.exceptions:
                            print(f'Error in task: {exc}')
                            traceback.print_exc()
                                
                except Exception as error:
                    logging.error(f'{error}')
                    traceback.print_exc()
    
        except Exception as error:
            logging.critical(f'\n\nFATAL ERROR: {error}')
            traceback.print_exc()
            print(f'Retrying in {coolDown} seconds...')
            await countdownBar(coolDown)

if __name__ == '__main__':
    while 39:
        try:
            asyncio.run(main())
        except Exception as error:
                logging.critical(f'\n\nFATAL ERROR: {error}')
                traceback.print_exc()
                print(f'Retrying in {coolDown} seconds', end='')
                for _ in range(coolDown):
                    print('.', end='')
                    time.sleep(1)
        except KeyboardInterrupt:
            print('\nExiting...')
            break