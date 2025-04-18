import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def visualize_ratings():
    try:
        n = 'PTT.json'
        with open(n, 'r', encoding='utf-8') as file:
            data = json.load(file)['value']
        n = 'me.json'
        with open(n, 'r', encoding='utf-8') as file:
            name = json.load(file)['value']['name']
    except FileNotFoundError:
        print(f"诶…… 没找到 {n} 哦？ 需要先用 DataUpdate.py 把数据抓过来才能统计 PTT 的说ヽ(*。>Д<)o゜")
        return
    except json.JSONDecodeError:
        print(f"Error: File {n} is not valid JSON.")
        return
    
    timestamps = []
    ratings = []
    
    for entry in data:
        time_played = datetime.fromtimestamp(entry['time_played'] / 1000)
        user_rating = entry['user_rating']
        
        timestamps.append(time_played)
        ratings.append(user_rating)
    
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, ratings, marker='o', markersize=3, linestyle='-', linewidth=1, color='royalblue')
    
    plt.title(f'{name}\'s PTT Over Time', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('PTT', fontsize=12)
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.grid(True, linestyle='--', alpha=0.7, which='both')
    
    min_rating = min(ratings)
    max_rating = max(ratings)
    plt.axhline(y=max_rating, color='b', linestyle='--', alpha=0.5)
    
    y_min = 0
    y_max = max_rating + 20
    plt.ylim(y_min, y_max)
    
    plt.xticks(rotation=45)
    
    plt.text(timestamps[0], max_rating + 1, f'Max: {max_rating}', color='blue')
    plt.text(timestamps[0], min_rating - 2, f'Min: {min_rating}', color='red')
    
    plt.tight_layout()
    
    plt.savefig('user_rating_trend.png', dpi=300)
    
    plt.show()

if __name__ == "__main__":
    visualize_ratings()