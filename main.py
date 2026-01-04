import requests
import datetime

# 這裡定義你的頻道列表
# 注意：這些 URL 必須是你收集到的潛在直播源，或是從其他 API 獲取的
channels = [
    {
        "name": "RTHK 31",
        "url": "https://rthklive1-lh.akamaihd.net/i/rthk31_1@167495/index_2052_av-b.m3u8",
        "group": "Hong Kong"
    },
    {
        "name": "RTHK 32",
        "url": "https://rthklive2-lh.akamaihd.net/i/rthk32_1@168450/index_2052_av-b.m3u8",
        "group": "Hong Kong"
    },
    # 你可以加入 ViuTV 或 HOY TV 的源，但它們通常會有 Token 或 Geo-block
    # 這裡僅作範例
]

def check_stream(url):
    try:
        # 發送 HEAD 請求來檢查鏈接是否有效，超時設為 5 秒
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def generate_m3u():
    content = '#EXTM3U x-tvg-url="https://epg.112114.xyz/pp.xml"\n'
    content += f'# Updated at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    
    valid_count = 0
    
    for channel in channels:
        print(f"Checking {channel['name']}...")
        if check_stream(channel['url']):
            content += f'#EXTINF:-1 group-title="{channel["group"]} tvg-name="{channel["name"]}" logo="",{channel["name"]}\n'
            content += f'{channel["url"]}\n'
            valid_count += 1
        else:
            print(f"  -> {channel['name']} is DOWN.")

    # 寫入文件
    with open('hk_live.m3u', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Update finished. Total valid channels: {valid_count}")

if __name__ == "__main__":
    generate_m3u()
