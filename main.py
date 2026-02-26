import requests
import re
import datetime
import time  # 必須匯入，用嚟計算由 Request 開始到 Response 完畢嘅時間差 (Latency)
from opencc import OpenCC
from concurrent.futures import ThreadPoolExecutor

# 【初始化】繁簡轉換器：將所有抓取到嘅簡體頻道名轉做繁體，費事同一個台因為繁簡問題分開兩行
cc = OpenCC('s2t')

# --- 設定區 ---
# 1. 網路訂閱源列表：程式會逐個讀取呢啲網址入面嘅 m3u 內容
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

# 2. 手動補充源：如果爬唔到嘅台，喺呢度強制加入 (例如一啲穩定嘅個人源)
MANUAL_SINGLE_CHANNELS = [
    {"name": "翡翠台", "url": "https://HaNoiIPTV.short.gy/Que_huong_HaNoiIPTV-TVB_Fei_Cui_Tai"},
    {"name": "翡翠台", "url": "http://php.jdshipin.com/TVOD/iptv.php?id=fct2"},
    {"name": "大灣區衛視", "url": "http://183.11.239.36:808/hls/132/index.m3u8"}
]

# 3. 關鍵字過濾：只有頻道名包含呢啲字眼嘅先會被捉出嚟
KEYWORDS = ["ViuTV", "HOY", "RTHK", "Jade", "Pearl", "J2", "J5", "Now", "无线", "無線", "有线",
            "有線", "翡翠", "明珠", "港台", "廣東", "珠江", "广州", "廣州", "大灣區","鳳凰", 
            "凤凰", "民視", "東森", "三立", "中視", "公視", "TVBS", "緯來", "年代", 
            "中天", "非凡", "澳視", "澳門", "TDM", "澳亞"]

# 4. 黑名單：就算符合關鍵字，但包含呢啲字眼就唔要 (例如重複嘅測試頻道)
BLOCK_KEYWORDS = ["FOX", "UHD", "8K", "浙江", "杭州", "深圳", "CCTV", "延时", "測試"]

# 5. 排序優先級：決定喺同一個分組入面，邊個台排喺最頂 (排喺越前面越優先)
ORDER_KEYWORDS = ["廣東", "珠江", "廣州", "廣東衛視", "大灣區", "南方", "港台電視", "翡翠", "無線新聞", 
                  "明珠", "J2", "J5", "財經", "Viu", "HOY", "奇妙", "有線", "Now", "民視", "中視", 
                  "華視", "公視", "TVBS", "三立", "東森", "年代", "壹電視", "非凡", "中天", "緯來", 
                  "澳視", "澳門", "TDM", "澳亞"]

# 6. 官方或固定源：唔洗爬、直接塞入去嘅 Link
STATIC_CHANNELS = [
    {"name": "港台電視31 (官方)", "url": "https://rthklive1-lh.akamaihd.net/i/rthk31_1@167495/index_2052_av-b.m3u8", "speed": 10}, 
    {"name": "港台電視32 (官方)", "url": "https://rthklive2-lh.akamaihd.net/i/rthk32_1@168450/index_2052_av-b.m3u8", "speed": 10}
]

# --- 核心邏輯區 ---

COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def check_url(item):
    """
    【功能】測速器：檢查網址開唔開到，並記錄反應時間 (Latency)
    - timeout=2: 如果 2 秒都連唔到，就當佢死咗，費事老人家等太耐。
    - stream=True: 唔洗下載成個影片，只要連通咗攞到 Header 就停，咁樣測速先快。
    """
    url = item['url']
    headers = COMMON_HEADERS.copy()
    headers['Referer'] = url # 有啲源會 Check 來源網址，加個 Referer 穩陣啲
    try:
        start_time = time.time()
        response = requests.get(url, timeout=2, headers=headers, stream=True)
        if response.status_code == 200:
            # 毫秒數 = (依家時間 - 開始時間) * 1000
            item['speed'] = int((time.time() - start_time) * 1000)
            response.close()
            return item
    except: 
        pass
    return None

def fetch_and_parse():
    """
    【功能】主爬蟲邏輯：爬取所有來源，過濾關鍵字，並生成「健康度分析報告」
    - 亮點：如果源入面冇你要嘅台，會列出「內容樣本」，等你知道使唔使加 Keyword。
    """
    all_valid_channels = []
    report_data = [] # 用嚟儲存每一份 Source 嘅狀態，最後寫入 source_report.txt
    seen_urls = set() # 用嚟去重 (Duplicate Removal)，同一個 URL 唔洗掃兩次
    
    print("🚀 任務開始！正在即時抓取與測速...", flush=True)
    
    for index, source in enumerate(SOURCE_URLS):
        print(f"\n📡 [{index+1}/{len(SOURCE_URLS)}] 正在讀取: {source}", flush=True)
        # 針對台灣專用源做特別處理 (就算名唔夾 Keyword 都捉，因為台灣源通常比較雜)
        is_taiwan_source = "tw.m3u" in source.lower()
        current_candidates = []
        all_found_names = [] # 儲存呢個 Source 入面所有搵到嘅台名 (無論夾唔夾 Keyword)
        
        try:
            r = requests.get(source, timeout=15, headers=COMMON_HEADERS)
            r.encoding = 'utf-8'
            if r.status_code != 200: 
                report_data.append(f"來源: {source}\n狀態: ❌ 無法存取 (HTTP {r.status_code})\n{'-'*50}")
                continue
            
            lines = r.text.split('\n')
            current_name = ""
            for line in lines:
                line = line.strip()
                if not line: continue
                # M3U 格式：#EXTINF 呢行係名，下一行係 URL
                if line.startswith("#EXTINF"):
                    if ',' in line:
                        raw_name = line.split(',')[-1].strip()
                        # 繁體化頻道名，並統一將「臺」轉做「台」
                        current_name = cc.convert(raw_name).replace('臺', '台')
                        all_found_names.append(current_name)
                elif line.startswith("http") and current_name:
                    # 1. 排除一啲奇怪嘅廣告或非影片連結
                    if "[" in line and "]" in line: continue
                    # 2. 檢查黑名單
                    if any(b.lower() in current_name.lower() for b in BLOCK_KEYWORDS): continue
                    
                    # 3. 檢查關鍵字命中
                    is_match = any(cc.convert(k).replace('臺', '台').lower() in current_name.lower() for k in KEYWORDS)
                    
                    # 4. 如果中 Keyword 兼未見過呢條 Link，就加入「待測名單」
                    if (is_match or is_taiwan_source) and line not in seen_urls:
                        current_candidates.append({"name": current_name, "url": line})
                        seen_urls.add(line)
                    current_name = ""
            
            # --- 對「待測名單」進行多線程並發測速 (提高速度) ---
# --- 處理檢測與報告 ---
            if current_candidates:
                # (呢部分係處理有命中關鍵字嘅邏輯，保持不變)
                total_found = len(current_candidates)
                print(f"    📥 命中關鍵字 {total_found} 條，啟動 20 線程測速...", end="", flush=True)
                with ThreadPoolExecutor(max_workers=20) as executor:
                    results = list(executor.map(check_url, current_candidates))
                
                valid_ones = [r for r in results if r is not None]
                count_valid = len(valid_ones)
                all_valid_channels.extend(valid_ones)
                
                health = f"✅ 有效 (活鏈 {count_valid})" if count_valid > 0 else "⚠️ 連結失效 (搵到關鍵字但全死)"
                report_data.append(f"來源: {source}\n狀態: {health} | 命中數: {total_found}\n{'-'*50}")
                print(f"\r    ✅ 完成：{count_valid} 條可用...")
            else:
                # 【重點更新】當冇符合關鍵字時，列出該源「所有」頻道名，不再省略
                # 1. 使用 set() 去除重複名稱
                # 2. 使用 sorted() 按名稱排序，方便你閱讀
                all_names_str = ", ".join(sorted(list(set(all_found_names))))
                
                health = "⚪ 略過 (此源冇你設定嘅關鍵字頻道)"
                # 將所有頻道名完整寫入報告
                report_data.append(f"來源: {source}\n狀態: {health}\n所有頻道清單: {all_names_str}\n{'-'*50}")
                
                # 終端機 (Console) 依然顯示簡短版本，費事洗晒你個 Screen
                print(f"    ⚪ 略過 (已將 {len(set(all_found_names))} 個頻道名寫入報告)")

        except Exception as e:
            report_data.append(f"來源: {source}\n狀態: ❌ 報錯 ({str(e)})\n{'-'*50}")
            print(f"    ❌ 錯誤: {e}")

    # 寫入報告檔案，方便你之後 check 返邊啲 Source 係廢嘅
    with open("source_report.txt", "w", encoding="utf-8") as f:
        f.write(f"IPTV 來源健康度分析報告\n生成時間: {datetime.datetime.now()}\n{'='*50}\n")
        f.write("\n".join(report_data))
            
    return all_valid_channels

def generate_m3u(valid_channels):
    """
    【功能】最後生成：將結果按照「分組」及「速度」排好，輸出 M3U
    - 排序重點：大分組 (香港/廣東/台灣) -> 頻道排名 (翡翠台先、J2後) -> 速度 (快嘅排先)
    """
    final_list = list(STATIC_CHANNELS)
    final_list.extend(valid_channels)

    print(f"\n🔄 正在進行權重排序 (總數: {len(final_list)})...", flush=True)
    # 利用 get_sort_key 返回的數值進行升序排序 (細數行先)
    final_list.sort(key=get_sort_key)

    content = '#EXTM3U x-tvg-url="https://epg.112114.xyz/pp.xml"\n'
    content += f'# Update: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'

    # 分組輸出邏輯
    groups = ["廣東/廣州", "香港", "台灣", "澳門", "其他"]
    for current_group in groups:
        for item in final_list:
            name = item["name"]
            speed = item.get('speed', 0)
            
            # 【分組判定規則】同 get_sort_key 入面嘅邏輯要對應
            if any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): ig = "澳門"
            elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): ig = "台灣"
            elif any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): ig = "廣東/廣州"
            elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "viu", "HOY", "奇妙", "有線", "Now", "J2", "J5"]): ig = "香港"
            else: ig = "其他"

            if ig == current_group:
                # 寫入 M3U 檔案，標註埋測速結果 (ms) 方便除錯
                content += f'#EXTINF:-1 group-title="{ig}" logo="https://epg.112114.xyz/logo/{name}.png",{name} ({speed}ms)\n{item["url"]}\n'

    with open("hk_live.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n🎉 大功告成！檔案已儲存為 hk_live.m3u", flush=True)

def get_sort_key(item):
    """
    【功能】權重計算法 (排序核心)
    - gp (Group Point): 大分類，廣東(100) < 香港(200) < 台灣(300) ...
    - kp (Keyword Point): 台名優先級，ORDER_KEYWORDS 入面愈前嘅愈細分。
    - speed 微調: 將 speed 除以 1,000,000，確保唔會影響 gp 同 kp，但喺同一個台嘅時候，快嘅排先。
    """
    name = item["name"]
    speed = item.get('speed', 9999)

    # 1. 決定大分組權重
    if any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): gp = 100
    elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "viu", "HOY", "奇妙", "有線", "Now", "J2", "J5"]): gp = 200
    elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): gp = 300
    elif any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): gp = 400
    else: gp = 500

    # 2. 決定頻道名權重 (依照 ORDER_KEYWORDS 的 index)
    kp = 99
    for i, k in enumerate(ORDER_KEYWORDS):
        if k.lower() in name.lower():
            kp = i
            break
    
    # 3. 速度微調：例如 200ms 會變成 0.0002，300ms 變成 0.0003
    return gp + kp + (speed / 1000000)

if __name__ == "__main__":
    # 第一步：執行主爬蟲
    live_channels = fetch_and_parse()
    
    # 第二步：處理手動補充源 (同樣要經過測速)
    existing_urls = {c['url'] for c in live_channels}
    print(f"\n📦 正在檢查手動補充源...", flush=True)
    for item in MANUAL_SINGLE_CHANNELS:
        item['name'] = cc.convert(item['name']).replace('臺', '台')
        if item['url'] not in existing_urls:
            checked = check_url(item)
            if checked:
                live_channels.append(checked)
                existing_urls.add(item['url'])
                print(f"    [+] 手動源注入成功: {item['name']} ({checked.get('speed')}ms)")
        else:
            print(f"    [!] 重複 Link，跳過: {item['name']}")

    # 第三步：生成最終檔案
    generate_m3u(live_channels)
