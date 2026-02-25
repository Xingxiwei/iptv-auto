import requests
import re
import datetime
from opencc import OpenCC
from concurrent.futures import ThreadPoolExecutor

# 【初始化】繁簡轉換器 (s2t = Simplified to Traditional)
cc = OpenCC('s2t')

# --- 設定區 ---

# 1. 網路訂閱源列表：程式會逐個網址去爬 M3U 內容
SOURCE_URLS = [
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A8202506.m3u",
    # ... (中間省略，保持你原本嘅網址清單)
    "https://raw.githubusercontent.com/melody0709/cmcc_iptv_auto_py/main/tv2.m3u"
]

# 2. 手動補充源：如果你有啲私藏或者比較穩定番嘅 Link，可以寫死喺度
MANUAL_SINGLE_CHANNELS = [
    {"name": "翡翠台", "url": "https://HaNoiIPTV.short.gy/Que_huong_HaNoiIPTV-TVB_Fei_Cui_Tai"},
    # ... (中間省略，保持你原本嘅手動清單)
    {"name": "大灣區衛視", "url": "http://gmxw.7766.org:808/hls/132/index.m3u8"}
]

# 3. 關鍵字過濾：名入面一定要有呢啲字先至會收錄 (白名單)
KEYWORDS = ["ViuTV", "HOY", "RTHK", "Jade", "Pearl", "J2", "J5", "Now", "无线", "無線", "有线", "有線", "翡翠", "明珠", "港台", "廣東", "珠江", "广州", "廣州", "大灣區","鳳凰", "凤凰","成人", "民視", "東森", "三立", "中視", "公視", "TVBS", "緯來", "年代", "中天", "非凡", "澳視", "澳門", "TDM", "澳亞"]

# 4. 黑名單：名入面有呢啲字就一定唔要 (剔除美國台、購物台、測試台等)
BLOCK_KEYWORDS = ["FOX", "Pluto", "Local", "NBC", "CBS", "ABC", "AXS", "Snowy", "Reuters", "Mirror", "ET Now", "The Now", "Right Now", "News Now", "Chopper", "Wow", "UHD", "8K", "Career", "Comics", "Movies", "CBTV","Pearl","AccuWeather","Jadeed","Curiosity","Electric", "Warfare","Knowledge","MagellanTV","70s","80s","90s","Rock", "Winnipeg","Edmonton","RightNow","Times","True","Mindanow", "浙江", "杭州", "西湖", "深圳", "韶關", "CCTV", "CGTN", "華麗", "星河", "延时", "測試", "iHOY", "福建"]

# 5. 排序優先級：越排前面嘅字，喺 M3U 播放器入面就會排得越靠上
ORDER_KEYWORDS = ["廣東", "珠江", "廣州", "廣東衛視", "大灣區", "南方", "港台電視", "翡翠", "無線新聞", "明珠", "J2", "J5", "財經", "Viu", "HOY", "奇妙", "有線", "Now", "民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "壹電視", "非凡", "中天", "緯來", "澳視", "澳門", "TDM", "澳亞"]

# 6. 靜態源：絕對穩定、唔使 check 嘅官方 Link
STATIC_CHANNELS = [
    {"name": "港台電視31 (官方)", "url": "https://rthklive1-lh.akamaihd.net/i/rthk31_1@167495/index_2052_av-b.m3u8"},
    {"name": "港台電視32 (官方)", "url": "https://rthklive2-lh.akamaihd.net/i/rthk32_1@168450/index_2052_av-b.m3u8"}
]

# --- 核心邏輯區 ---

def check_url(item):
    """
    【功能】檢查單個網址係咪仲行得通
    1. 先試 HEAD (淨係讀 Header，快啲)
    2. 如果 HEAD 唔得就試 GET (只讀開頭)
    """
    url = item['url']
    headers = {'User-Agent': 'Mozilla/5.0...', 'Referer': url}
    try:
        # allow_redirects=True 處理跳轉 Link
        response = requests.head(url, timeout=2, headers=headers, allow_redirects=True)
        if response.status_code == 200: return item
        
        # 某啲源阻擋 HEAD，要用 GET stream 模式
        response = requests.get(url, timeout=3, headers=headers, stream=True)
        if response.status_code == 200:
            response.close() # 通咗就斷開，慳流量
            return item
    except: pass
    return None

def fetch_and_parse():
    """
    【功能】遍歷 SOURCE_URLS，下載 M3U 內容並解析出頻道名同 URL
    """
    found_channels = []
    seen_urls = set() # 用 Set 嚟做「全球唯一」去重，Link 一樣就唔要
    headers = {'User-Agent': 'Mozilla/5.0...', 'Referer': 'https://live.hacks.tools/'}
    
    print("🚀 任務開始！正在抓取網路源...", flush=True)
    
    for index, source in enumerate(SOURCE_URLS):
        print(f"  [{index+1}/{len(SOURCE_URLS)}] 正在讀取: {source}", flush=True)
        is_taiwan_source = "tw.m3u" in source.lower() # 標記係咪台灣專屬源
        try:
            r = requests.get(source, timeout=15, headers=headers)
            r.encoding = 'utf-8'
            if r.status_code != 200: continue
            
            lines = r.text.split('\n')
            current_name, count_added = "", 0
            for line in lines:
                line = line.strip()
                if not line: continue
                # 攞頻道名
                if line.startswith("#EXTINF"):
                    if ',' in line:
                        raw_name = line.split(',')[-1].strip()
                        current_name = cc.convert(raw_name).replace('臺', '台')
                # 攞網址並過濾
                elif line.startswith("http") and current_name:
                    if "[" in line and "]" in line: continue # 飛走 IPv6
                    if any(b.lower() in current_name.lower() for b in BLOCK_KEYWORDS): continue # 黑名單
                    
                    is_match = any(cc.convert(k).replace('臺', '台').lower() in current_name.lower() for k in KEYWORDS)
                    # 符合白名單關鍵字，或者係台灣專屬源，先至收錄
                    if is_match or is_taiwan_source:
                        if line not in seen_urls:
                            found_channels.append({"name": current_name, "url": line})
                            seen_urls.add(line)
                            count_added += 1
                    current_name = ""
            print(f"    ✅ 抓取成功，新增 {count_added} 個頻道", flush=True)
        except Exception as e:
            print(f"    ❌ 抓取錯誤: {e}", flush=True)
    return found_channels

def generate_m3u(channels):
    """
    【功能】檢測有效性、排序、並生成最終 M3U 檔案
    """
    print(f"\n🔍 共找到 {len(channels)} 個潛在頻道，開始檢測有效性...", flush=True)
    final_list = list(STATIC_CHANNELS) # 先放入官方源
    
    # 【多線程】20 條線程同時開工 Check Link，唔使一條一條等
    print(f"⚡ 啟動多線程檢測 (20 線程同步進行)...", flush=True)
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(check_url, channels))
    
    # 過濾出成功嘅結果
    valid_channels = [r for r in results if r is not None]
    valid_urls = {r['url'] for r in valid_channels}
    
    # 顯示死鏈 (Log 輸出)
    invalid_channels = [c for c in channels if c['url'] not in valid_urls]
    if invalid_channels:
        print(f"\n🚫 檢測到 {len(invalid_channels)} 個失效連結：")
        for ch in invalid_channels:
            print(f"  [X] 死鏈: {ch['name']} - {ch['url']}")

    final_list.extend(valid_channels)
    print(f"\n✅ 檢測完成！共收錄 {len(valid_channels)} 個有效網路頻道。", flush=True)

    # 排序
    print("🔄 正在進行排序...", flush=True)
    final_list.sort(key=get_sort_key)

    # 【寫入檔案】生成符合標準嘅 M3U 格式
    content = '#EXTM3U x-tvg-url="https://epg.112114.xyz/pp.xml"\n'
    content += f'# Update: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    
    # 分組寫入邏輯
    groups = ["廣東/廣州", "香港", "台灣", "澳門", "其他"]
    for current_group in groups:
        for item in final_list:
            name = item["name"].replace('臺', '台')
            # 根據關鍵字決定 group-title
            if any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): ig = "澳門"
            elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): ig = "台灣"
            elif any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): ig = "廣東/廣州"
            elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "Viu", "HOY", "奇妙", "有線", "Now", "J2", "J5"]): ig = "香港"
            else: ig = "其他"

            if ig == current_group:
                # 寫入 Logo 網址同頻道資料
                content += f'#EXTINF:-1 group-title="{ig}" logo="https://epg.112114.xyz/logo/{name}.png",{name}\n{item["url"]}\n'

    with open("hk_live.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n🎉 全部完成！共生成 {len(final_list)} 個頻道。", flush=True)

def get_sort_key(item):
    """
    【功能】計算排序權重。數字越細排越先。
    """
    name = item["name"]
    # 1. 決定大組優先級
    if any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): gp = 100
    elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "Viu", "HOY", "奇妙", "有線", "Now", "J2", "J5"]): gp = 200
    elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): gp = 300
    elif any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): gp = 400
    else: gp = 500
    
    # 2. 喺組內根據 ORDER_KEYWORDS 細分優先級
    kp = 99
    for i, k in enumerate(ORDER_KEYWORDS):
        if k.lower() in name.lower():
            kp = i
            break
    return gp + kp

# --- 程式入口 ---
if __name__ == "__main__":
    # 第一步：爬取網路源
    candidates = fetch_and_parse()
    
    # 攞出所有已經爬到嘅 URL 做對比
    existing_urls = {c['url'] for c in candidates}
    
    # 第二步：注入手動源 (檢查係咪重複)
    print(f"\n📦 正在注入手動源...", flush=True)
    for item in MANUAL_SINGLE_CHANNELS:
        item['name'] = cc.convert(item['name']).replace('臺', '台')
        if item['url'] not in existing_urls:
            print(f"  [+] 注入成功: {item['name']}")
            candidates.append(item)
            existing_urls.add(item['url'])
        else:
            print(f"  [!] 手動源已存在，跳過: {item['name']} ({item['url']})")
    
    # 第三步：校驗並生成檔案
    generate_m3u(candidates)
