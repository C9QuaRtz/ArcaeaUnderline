import json
import math
import os
import yaml
import getpass

from tqdm import tqdm
from pwdCrypt import *
from template import *
from webConnect import jsonSave, getChartConstant, simple_get

cookie : str
vip : bool
retry = 3
    
def WhichDifficulty(a) -> str:
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
    return '[???]'

def create_config_file():
    print("\n唔…… 没找到配置文件的说~(。>︿<)_\n那就偷偷把你的账号和密码告诉本喵吧~\n")
    username = input("首先是你的用户名哦：")
    password = getpass.getpass("接下来是密码喵，本喵用了隐式输入，相信你一次就能成功的（可以开始按键盘了哦~")
    cipher = StableAESCipher(get_device_fingerprint())

    with open('config.yaml', 'w', encoding='utf-8') as f:
        tmp = {
            'username': username,
            'password': cipher.encrypt(password),
            'isVIP': False,
        }
        f.write(configTemplate.format(**tmp))

def loadConfig():
    if not os.path.exists('config.yaml'):
        create_config_file()
    

if __name__ == "__main__":

    print("\n嗯嗯，开始工作了喵！╰(￣ω￣ｏ) 加油加油~\n")
    
    print("正在尝试伪装成主人的样子喵…… ")
    loadConfig()
    print("哼哼~ 伪装成功了喵！(￣y▽,￣)╭ ", end='')
    print("接下来就去跟Ai酱打小报告啦…… \n")

    print("第一步就先把主人的个人数据拿到手喵ο(=•ω＜=)ρ⌒☆……", end='')

    args = '/webapi/user/me'
    result = json.loads(simple_get(args))
    jsonSave(result, 'me.json')
    print("成功啦φ(≧ω≦*)♪\n")

    if result['value']['arcaea_online_expire_ts'] == 0:
        print("呜呜… 主人没有订阅 Arcaea Online 的说……\n本喵只能帮你抓到这份数据了，对不起喵…o(TヘTo)\n")
        print("如果觉得本喵看错了的话，就在 config.yaml 里把 isVIP 的值改成 True 再试试喵~\n")
        exit(1)
    
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    config['isVIP'] = True
    with open('config.yaml', 'w', encoding='utf-8') as file:
        file.write(configTemplate.format(**config))

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

    cc = getChartConstant()
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