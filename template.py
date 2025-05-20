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
configTemplate = """# 要把账密都写在小引号里哦，不要把引号删掉了喵ο(=•ω＜=)ρ⌒☆

username: {username} # 在这里填入主人的ID喵~
password: {password} # 这里填上主人的密码哦（本喵不会偷看的www

isVIP: {isVIP} # 主人有订阅 Arcaea Online 喵？如果有的话，就把这个直接改成 True 来启用更多功能吧~

Cookie: {Cookie} # 如果主人看不懂的话就不用管这行啦，交给本喵处理就好哦"""