import requests
import json
import math
import os
import yaml

from tqdm import tqdm
from bs4 import BeautifulSoup

global cookie
global vip
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

def extract_with_bs4(content, tag_name, **attrs):
    soup = BeautifulSoup(content, 'html.parser')
    elements = soup.find_all(tag_name, attrs=attrs)
    results = [element.get_text() for element in elements]
    return results

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
    config = 'isVIP: False # 主人有订阅 Arcaea Online 喵？如果有的话，就把这个直接改成 True 来启用更多功能吧~\n\nheaders:\n    Cookie: \'\' # 在小引号里面填入你的 Cookie 哦，不要把引号删掉了喵ο(=•ω＜=)ρ⌒☆'
    with open('config.yaml', 'w', encoding='utf-8') as f:
        f.write(config)
    print("\n唔…… 没找到配置文件的说~(。>︿<)_\n本喵已经帮你创建好啦，填上去就行喵~")
    exit(1)

def loadConfig():
    global cookie
    global vip
    if not os.path.exists('config.yaml'):
        create_config_file()

    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        if 'headers' not in config or 'Cookie' not in config['headers'] or not config['headers']['Cookie'] or type(config['headers']['Cookie']) != str or 'isVIP' not in config or type(config['isVIP']) != bool:
            print("\n欸…人家看不懂你的配置文件啦……(σ｀д′)σ\n再检查一下，试试找找问题喵？")
            exit(1)
        cookie = config['headers']['Cookie']
        vip = config['isVIP']

def jsonSave(data, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def simple_get(
        args: str,
        url = "https://webapi.lowiro.com",
        headers = None
    ):
    try:
        global cookie
        global headersList
        
        if not headers:
            headers = headersList['lowiro']
            headers['Cookie'] = cookie
        
        response = requests.get(url + args, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as err:
        exit(f"呜哇！Σ(っ °Д °;)っ和Ai酱交流的时候连接突然炸掉啦！问题好像是这个呢: \n{err}")


if __name__ == "__main__":

    print("\n嗯嗯，开始工作了喵！╰(￣ω￣ｏ) 加油加油~\n")
    
    print("正在尝试伪装成主人的样子喵…… ")
    loadConfig()
    print("哼哼~ 伪装成功了喵！(￣y▽,￣)╭ ", end='')
    print("接下来就去跟Ai酱打小报告啦…… \n")

    print("第一步就先把主人的个人数据拿到手喵ο(=•ω＜=)ρ⌒☆…… ", end='')
    args = '/webapi/user/me'
    result = json.loads(simple_get(args))
    jsonSave(result, 'me.json')
    print("成功啦φ(≧ω≦*)♪\n")

    if not vip:
        print("呜呜… 主人没有订阅 Arcaea Online 的说……\n本喵只能帮你抓到这份数据了，对不起喵…o(TヘTo)\n")
        print("如果觉得本喵看错了的话，就在 config.yaml 里把 isVIP 的值改成 True 再试试喵~\n")
        exit(1)
    
    print("之后就来把所有 PTT 的变动记录抓过来吧~", end='')
    args = '/webapi/score/rating_progression/me?duration=5y'
    result = json.loads(simple_get(args))
    jsonSave(result, 'PTT.json')
    print("这个也没问题啦！\n\n接下来就是所有谱面成绩了喵…… 要耐心一点哦(づ￣ 3￣)づ\n")

    print("先从 [PST] 难度开始吧~")
    for difficulty in range(0, 5):

        if difficulty != 0:
            print(f"接下来是 {WhichDifficulty(difficulty)} 的数据了喵nya~")

        args = f"/webapi/score/song/me/all?difficulty={difficulty}&page=1&sort=title&term="

        print("现在试试把第一份数据抓过来喵…… ", end="")
        result = json.loads(simple_get(args))
        print("拿到啦ヾ(≧ ▽ ≦)ゝ果然是小菜一碟喵~")
        pages = math.ceil(result["value"]["count"] / 10)
        print(f"嗯，我看看…… 这个难度一共有 {pages} 页数据呢，会加油的喵！(๑•̀ㅂ•́)و✧\n")
        
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
    
    print("接下来的话，就去问问红要定数表啦(○｀ 3′○)\n")
    cc = extract_with_bs4(
        simple_get(
            url = "https://arcwiki.mcd.blue",
            args = '/index.php?title=Template:ChartConstant.json&action=edit',
            headers = headersList['mcd']
        ),
        'textarea',
        id = 'wpTextbox1'
    )[0]
    cc = json.loads(cc)
    jsonSave(cc, 'ChartConstant.json')
        
    print("好，定数表也没问题啦(*￣3￣)╭ 接下来就把所有东西整理到一起吧~\n")
    FullScore = {
        'PST': {},
        'PRS': {},
        'FTR': {},
        'BYD': {},
        'ETR': {}
    }
    for difficulty in range(0, 5):
        with open(f"result{WhichDifficulty(difficulty)}.json", 'r', encoding='utf-8') as f:
            result = json.load(f)

            for i in range(len(result["value"]["scores"])):
                song = result["value"]["scores"][i]["song_id"]
                FullScore[WhichDifficulty(difficulty)[1:-1]][song] = result["value"]["scores"][i]

                try:
                    FullScore[WhichDifficulty(difficulty)[1:-1]][song]['const'] = cc[song][difficulty]['constant']               
                except Exception as error:
                    print(f"欸… 定数表里 {song} 的 {WhichDifficulty(difficulty)} 数据好像有点问题呢…… 那就随便填一个空值吧~\n{error}")
                    FullScore[WhichDifficulty(difficulty)[1:-1]][song]['const'] = None
    
    jsonSave(FullScore, 'FullScore.json')
    print("嗯嗯，这样工作就结束啦~ 想要主人摸摸头作为奖励喵(*/ω＼*)")

else:
    exit("啊咧咧……？怎、怎么能这样调用本喵呢⁄(⁄⁄•⁄ω⁄•⁄⁄)⁄\n不可以啦绝对不行！")