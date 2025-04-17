import requests
import json
import math
import os
import yaml

from tqdm import tqdm

global cookie

def WhichDifficulty(a):
    if a == 0:
        return '[PST]'
    if a == 1:
        return '[PRS]'
    if a == 2:
        return '[FTR]'
    if a == 3:
        return '[BYD]'
    if a == 4:
        return '[ETR]'

def create_config_file():
    config = 'headers:\n    Cookie: \'\' # 在小引号里面填入你的 Cookie 哦，不要把引号删掉了喵ο(=•ω＜=)ρ⌒☆'
    with open('config.yaml', 'w', encoding='utf-8') as f:
        f.write(config)
    print("\n唔…… 没找到配置文件的说~(。>︿<)_\n本喵已经帮你创建好啦，填上去就行喵~")
    exit(1)

def loadCookie():
    global cookie
    
    if not os.path.exists('config.yaml'):
        create_config_file()

    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
        if 'headers' not in config or 'Cookie' not in config['headers'] or not config['headers']['Cookie'] or type(config['headers']['Cookie']) != str:
            print("\n欸…人家看不懂你的配置文件啦……(σ｀д′)σ\n再检查一下，试试找找问题喵？")
            exit(1)
        
        cookie = config['headers']['Cookie']

def jsonSave(data, filename: str) -> None:
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def simple_get(
        args: str,
        url = "https://webapi.lowiro.com",
        headers = {
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
        }
    ):
    try:
        global cookie
        headers['Cookie'] = cookie
        response = requests.get(url + args, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as err:
        exit(f"呜哇！Σ(っ °Д °;)っ和Ai酱交流的时候连接突然炸掉啦！问题好像是这个: \n{err}")

if __name__ == "__main__":
    print("正在尝试伪装成主人的样子喵…… ", end="")
    loadCookie()
    print("哼哼~ 伪装成功了喵！(￣y▽,￣)╭ ")
    print("接下来就去跟Ai酱打小报告啦…… ", end='')
    print("先从 [PST] 难度开始吧~")
    for difficulty in range(0, 5):

        if difficulty != 0:
            print(f"接下来是 {WhichDifficulty(difficulty)} 的数据了喵nya~")

        args = f"/webapi/score/song/me/all?difficulty={difficulty}&page=1&sort=title&term="

        print("现在试试把第一份数据抓过来喵…… ", end="")
        result = json.loads(simple_get(args))
        print("拿到啦ヾ(≧ ▽ ≦)ゝ果然是小菜一碟喵~")
        pages = math.ceil(result["value"]["count"] / 10)
        print(f"嗯，我看看…… 这个难度一共有 {pages} 页数据呢，会加油的喵！(๑•̀ㅂ•́)و✧")
        
        pbar = tqdm(total=pages, desc=f"{1} / {pages} 猫猫绝赞抓取 {WhichDifficulty(difficulty)} 数据中 o(*≧▽≦)ツ┏━┓ ……", ascii=False, ncols=100)
        pbar.update(1)
        
        for i in range(2, pages + 1):
            args = f"/webapi/score/song/me/all?difficulty={difficulty}&page={i}&sort=title&term="
            result["value"]["scores"].extend(json.loads(simple_get(args))["value"]["scores"])
            pbar.set_description(f"{i} / {pages} 猫猫绝赞抓取 {WhichDifficulty(difficulty)} 数据中 o(*≧▽≦)ツ┏━┓ ……")
            pbar.update(1)

        pbar.close()

        jsonSave(result, f"result{WhichDifficulty(difficulty)}.json")
        print(f"好耶！顺利把 {WhichDifficulty(difficulty)} 的所有数据都拿到手啦ヾ(≧∇≦*)ヾ\n")

    print("嗯嗯，这样工作就结束啦~ 想要主人摸摸头作为奖励喵(*/ω＼*)")