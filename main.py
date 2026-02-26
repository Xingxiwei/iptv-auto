import requests
import re
import datetime
import time
from opencc import OpenCC  # 用嚟做繁簡轉換，統一台名
from concurrent.futures import ThreadPoolExecutor  # 多線程核心，提升掃描速度 30 倍

# 【第一步：初始化工具】
# 設定 OpenCC 為 's2t' (Simplified to Traditional)，將抓返嚟嘅簡體字轉做繁體
cc = OpenCC('s2t')

# --- 1. 網路訂閱源 (完整 42 條 URL，絕無縮略) ---
# 呢度匯集咗 GitHub 同網上熱門嘅港澳台 M3U 訂閱源
SOURCE_URLS = [
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A8202506.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A82023.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A82022-7.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A82022-11.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%B5%B7%E5%A4%96202005.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%B5%B7%E5%A4%96202003.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%B5%B7%E5%A4%96.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/1300%E4%B8%AA%E7%9B%B4%E6%92%AD%E6%BA%90%E5%85%A8%E9%83%A8%E6%9C%89%E6%95%88%E3%80%90%E5%85%A8%E9%83%A84k%E8%80%81%E7%94%B5%E8%84%91%E5%88%AB%E7%94%A8%E3%80%91.m3u8",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/5000%E4%B8%AA%E7%9B%B4%E6%92%AD%E6%BA%90%E5%85%A8%E9%83%A8%E6%9C%89%E6%95%88.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E6%88%91%E7%9A%84%E6%92%AD%E6%94%BE%E6%BA%90.m3u8",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/3100%E4%B8%AA%E5%85%A8%E9%83%A8%E6%9C%89%E6%95%88.m3u8",
    "https://raw.githubusercontent.com/billy21/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%B9%BF%E4%B8%9C%E8%81%94%E9%80%9A.m3u",
    "https://raw.githubusercontent.com/suxuang/myIPTV/refs/heads/main/ipv4.m3u",
    "https://raw.githubusercontent.com/vicjl/myIPTV/refs/heads/main/CNTV.m3u",
    "https://raw.githubusercontent.com/vicjl/myIPTV/refs/heads/main/IPTV-all.m3u",
    "https://raw.githubusercontent.com/Guovin/iptv-api/refs/heads/gd/output/result.m3u",
    "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u",
    "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.m3u",
    "https://iptv-org.github.io/iptv/index.m3u",
    "https://raw.githubusercontent.com/joevess/IPTV/main/home.m3u8",
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/refs/heads/master/streams/hk.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/refs/heads/master/playlists/playlist_hong_kong.m3u8",
    "https://raw.githubusercontent.com/vbskycn/iptv/refs/heads/master/tv/iptv4.m3u",
    "https://epg.pw/test_channels_hong_kong.m3u",
    "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/cnTV_AutoUpdate.m3u8",
    "https://raw.githubusercontent.com/MercuryZz/IPTVN/refs/heads/Files/GAT.m3u",
    "https://raw.githubusercontent.com/xiweiwong/iptv/refs/heads/master/iptv.m3u",
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/index.m3u",
    "https://raw.githubusercontent.com/Mitchll1214/m3u/main/港澳台.m3u",
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://iptv-org.github.io/iptv/countries/hk.m3u",
    "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u",
    "https://raw.githubusercontent.com/YueChan/Live/main/GNTV.m3u",
    "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/ipv6/result.m3u",
    "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/ipv4/result.m3u",
    "https://iptv-org.github.io/iptv/countries/tw.m3u",
    "https://raw.githubusercontent.com/melody0709/cmcc_iptv_auto_py/main/ku9.m3u",
    "https://raw.githubusercontent.com/melody0709/cmcc_iptv_auto_py/main/tv.m3u",
    "https://raw.githubusercontent.com/melody0709/cmcc_iptv_auto_py/main/tv2.m3u"
]

# --- 2. 手動補充源 ---
# 針對一啲網上訂閱源未必有，或者好穩定嘅特定 Link 進行手動注入
MANUAL_SINGLE_CHANNELS = [
    {"name": "翡翠台", "url": "https://HaNoiIPTV.short.gy/Que_huong_HaNoiIPTV-TVB_Fei_Cui_Tai"},
    {"name": "翡翠台", "url": "http://php.jdshipin.com/TVOD/iptv.php?id=fct2"},
    {"name": "大灣區衛視", "url": "http://183.11.239.36:808/hls/132/index.m3u8"}
]

# --- 3. 關鍵字與黑名單設定 ---
# KEYWORDS: 決定邊啲頻道「有資格」被收錄
KEYWORDS = [
    "ViuTV", "HOY", "RTHK",       # 香港主流免費台
    "Jade", "Pearl",              # TVB 翡翠/明珠英文名
    "J2", "J5",                   # 無線副頻道
    "Now", "無線", "有線",         # 品牌關鍵字
    "翡翠", "明珠", "港台",         # 核心台名
    "廣東", "珠江", "廣州", "大灣區", # 廣東粵語區熱門台
    "鳳凰", "民視", "東森", "三立",  # 鳳凰衛視及台灣大台
    "中視", "公視", "TVBS", "緯來", 
    "年代", "中天", "非凡", 
    "澳視", "澳門", "TDM", "澳亞"   # 澳門本地台
]

# BLOCK_KEYWORDS: 即使命中關鍵字，如果包含以下字眼就「一票否決」
BLOCK_KEYWORDS = [
    "FOX", "UHD", "8K",           # 硬件要求太高或內容不符
    "浙江", "杭州", "深圳",         # 排除非目標地區嘅內地台
    "CCTV", "延时", "測試"         # 排除央視及無效測試訊號
]

# ORDER_KEYWORDS: 決定排位順序，排得愈前，在 TVBox 入面嘅「線路1」就愈大機會係佢
ORDER_KEYWORDS = [
    "廣東", "珠江", "廣州", "廣東衛視", "大灣區", "南方",  # 優先度 1: 粵語地區最快最穩嘅源
    "港台電視", "翡翠", "無線新聞", "明珠",              # 優先度 2: 香港人核心必睇台
    "J2", "J5", "財經", "Viu", "HOY", "奇妙", "有線", "Now", # 優先度 3: 香港其他娛樂台
    "民視", "中視", "華視", "公視", "TVBS", "三立",       # 優先度 4: 台灣熱門台
    "東森", "年代", "壹電視", "非凡", "中天", "緯來",      # 優先度 5: 台灣其他頻道
    "澳視", "澳門", "TDM", "澳亞"                        # 優先度 6: 澳門系列
]

# --- 4. 靜態官方源 ---
# 呢啲係官方長效連結，唔需要測速去重，直接放喺清單最頂
STATIC_CHANNELS = [
    {"name": "港台電視31 (官方)", "url": "https://rthklive1-lh.akamaihd.net/i/rthk31_1@167495/index_2052_av-b.m3u8", "speed": 10}, 
    {"name": "港台電視32 (官方)", "url": "https://rthklive2-lh.akamaihd.net/i/rthk32_1@168450/index_2052_av-b.m3u8", "speed": 10}
]

COMMON_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def check_url(item):
    """
    【測速邏輯】
    - 利用 HTTP GET 同步測試連線延遲
    - 使用 stream=True 避免下載整個 M3U8 文件，只讀取 Header 即刻關閉，極速慳流量
    """
    try:
        start_time = time.time()
        # 1.5 秒超時係黃金分割點：超過 1.5 秒嘅源在電視播通常都會轉圈卡餐死，直接放棄
        response = requests.get(item['url'], timeout=1.5, headers=COMMON_HEADERS, stream=True)
        if response.status_code == 200:
            item['speed'] = int((time.time() - start_time) * 1000)
            response.close()
            return item
    except:
        pass
    return None

def fetch_and_parse():
    """
    【爬蟲核心】下載 -> 解析 -> 測速 -> 篩選 -> 去重
    """
    all_valid_dict = {}  # 格式: { "url": {item_info} } -> 確保同一個 URL 唔會重複出現
    report_data = []     
    
    print("🚀 啟動 30 線程並發全方位掃描 (TVBox 優化版)...", flush=True)
    
    for index, source in enumerate(SOURCE_URLS):
        print(f"\n📡 [{index+1}/{len(SOURCE_URLS)}] 正在讀取: {source}", flush=True)
        # 針對台灣專用源做特別處理，即使名唔中關鍵字，只要係呢個源都入選
        is_taiwan_source = "tw.m3u" in source.lower()
        all_found_raw_data = [] 
        
        try:
            r = requests.get(source, timeout=15, headers=COMMON_HEADERS)
            r.encoding = 'utf-8'
            if r.status_code != 200:
                report_data.append(f"📡 來源: {source}\n   ❌ 下載失敗 (HTTP {r.status_code})\n{'─'*40}")
                continue
            
            # 解析 M3U 內容
            lines = r.text.split('\n')
            current_name = ""
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF"):
                    if ',' in line:
                        raw_name = line.split(',')[-1].strip()
                        # 繁簡統一 + 修正「臺」字，確保合併線路時名一致
                        current_name = cc.convert(raw_name).replace('臺', '台')
                elif line.startswith("http") and current_name:
                    all_found_raw_data.append({"name": current_name, "url": line})
                    current_name = ""

            if not all_found_raw_data:
                report_data.append(f"📡 來源: {source}\n   ⚪ 此源為空\n{'─'*40}")
                continue

            # --- 並發測速：30 匹馬同時跑，比傳統單線程快 3000% ---
            print(f"    ⏳ 盲測 {len(all_found_raw_data)} 條連結...", end="", flush=True)
            with ThreadPoolExecutor(max_workers=30) as executor:
                results = list(executor.map(check_url, all_found_raw_data))
            
            valid_this_source = [r for r in results if r is not None]
            matched_items_names = []
            missed_names = []

            for item in valid_this_source:
                # 關鍵字過濾邏輯
                is_match = any(k.lower() in item['name'].lower() for k in KEYWORDS)
                is_blocked = any(b.lower() in item['name'].lower() for b in BLOCK_KEYWORDS)
                
                if (is_match or is_taiwan_source) and not is_blocked:
                    url = item['url']
                    # 【去重邏輯】如果 URL 重複，保留測速最快嗰個對應嘅台名
                    if url not in all_valid_dict or item['speed'] < all_valid_dict[url]['speed']:
                        all_valid_dict[url] = item 
                    matched_items_names.append(item['name'])
                else:
                    missed_names.append(item['name'])

            # 構建 Emoji 報告
            report_entry = f"📡 來源: {source}\n"
            report_entry += f"   🔗 活鏈數: {len(valid_this_source)} 條\n"
            report_entry += f"   ✅ 命中 ({len(matched_items_names)} 個): {', '.join(matched_items_names[:15])}...\n"
            if missed_names:
                report_entry += f"   🔍 落選 ({len(missed_names)} 個): {', '.join(missed_names)}\n"
            report_entry += f"{'─'*40}"
            report_data.append(report_entry)

            print(f"\r    ✅ 完成：命中 {len(matched_items_names)} / 活鏈 {len(valid_this_source)}")

        except Exception as e:
            report_data.append(f"📡 來源: {source}\n   ❌ 出錯: {str(e)}\n{'─'*40}")
            print(f"\r    ❌ 出錯，已跳過")

    # 將掃描結果保存為 txt，方便檢查「落選名單」嚟調整關鍵字
    with open("source_report.txt", "w", encoding="utf-8") as f:
        f.write(f"IPTV 詳細掃描報告 - {datetime.datetime.now()}\n{'='*50}\n\n" + "\n".join(report_data))
            
    return list(all_valid_dict.values())

def get_sort_key(item):
    """
    【排序算法權重設計】
    數值愈細，排得愈前。
    1. gp (大組): 廣東=100, 香港=200, 台灣=300... (確保分組整齊)
    2. kp (關鍵字權重): 根據 ORDER_KEYWORDS 嘅索引值 (0, 1, 2...)
    3. speed (測速): 同台比較時，0.0001ms 嘅差距都會決定邊條係「線路1」
    """
    name, speed = item["name"], item.get('speed', 9999)
    # 分大組
    if any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): gp = 100
    elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "viu", "HOY", "Now", "J2", "J5"]): gp = 200
    elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): gp = 300
    elif any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): gp = 400
    else: gp = 500
    
    # 算組內細分排序
    kp = 99
    for i, k in enumerate(ORDER_KEYWORDS):
        if k.lower() in name.lower():
            kp = i
            break
    return gp + kp + (speed / 1000000)

def generate_m3u(valid_channels):
    """
    【輸出 M3U】
    TVBox 合併線路靠嘅係「台名一致」。
    我哋輸出時已經按 gp -> kp -> speed 排序，所以同名台會排埋一齊。
    """
    final_list = list(STATIC_CHANNELS) + valid_channels
    final_list.sort(key=get_sort_key)
    
    content = '#EXTM3U x-tvg-url="https://epg.112114.xyz/pp.xml"\n'
    content += f'# Update: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    
    groups = ["廣東/廣州", "香港", "台灣", "澳門", "其他"]
    written_urls = set() # 二次檢查 URL 唯一性

    for g in groups:
        for item in final_list:
            name, url = item["name"], item["url"]
            if url in written_urls: continue
            
            # 動態分配 group-title
            if any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): ig = "澳門"
            elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): ig = "台灣"
            elif any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): ig = "廣東/廣州"
            elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "viu", "HOY", "Now", "J2", "J5"]): ig = "香港"
            else: ig = "其他"
            
            if ig == g:
                # 輸出格式符合 TVBox/IPTV 播放器標準
                content += f'#EXTINF:-1 group-title="{ig}" logo="https://epg.112114.xyz/logo/{name}.png",{name}\n{url}\n'
                written_urls.add(url)
    
    with open("hk_live.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n🎉 TVBox 多線路版本已儲存！同名頻道將自動合併。")

if __name__ == "__main__":
    # 流程：掃描訂閱源 -> 注入手動源 -> 測速過濾 -> 排序輸出
    live_channels = fetch_and_parse()
    
    print(f"\n📦 正在檢查並注入手動補充源...", flush=True)
    existing_urls = {c['url'] for c in live_channels}
    for item in MANUAL_SINGLE_CHANNELS:
        item['name'] = cc.convert(item['name']).replace('臺', '台')
        if item['url'] not in existing_urls:
            checked = check_url(item)
            if checked:
                live_channels.append(checked)
                print(f"    [+] 手動源注入成功: {item['name']} ({checked['speed']}ms)")
    
    generate_m3u(live_channels)
