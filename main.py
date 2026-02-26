import requests
import re
import datetime
import time  # 核心：用嚟計 Latency (反應時間)，數值愈細代表轉台愈快
from opencc import OpenCC  # 核心：簡轉繁，防止同一個台因為字體問題分開兩行
from concurrent.futures import ThreadPoolExecutor  # 核心：多線程引擎，將掃描速度提升 30 倍

# 【初始化】繁簡轉換器：s2t = Simplified to Traditional
cc = OpenCC('s2t')

# --- 1. 網路訂閱源 
SOURCE_URLS = [
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A8202506.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A82023.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A82022-7.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A82022-11.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%B5%B7%E5%A4%96202005.m3u",
    "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/refs/heads/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%B5%B7%E5%A4%99202003.m3u",
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

# --- 2. 手動補充源 (穩定嘅私藏 Source) ---
# 呢度可以放一啲唔喺 M3U 入面，但你一定要睇嘅台
MANUAL_SINGLE_CHANNELS = [
    {"name": "翡翠台", "url": "https://HaNoiIPTV.short.gy/Que_huong_HaNoiIPTV-TVB_Fei_Cui_Tai"},
    {"name": "翡翠台", "url": "http://php.jdshipin.com/TVOD/iptv.php?id=fct2"},
    {"name": "大灣區衛視", "url": "http://183.11.239.36:808/hls/132/index.m3u8"}
]

# --- 3. 關鍵字過濾 (命中先會入最終 M3U) ---
KEYWORDS = ["ViuTV", "HOY", "RTHK", "Jade", "Pearl", "J2", "J5", "Now", "無線", "有線", "翡翠", "明珠", "港台", "廣東", "珠江", "廣州", "大灣區", "鳳凰", "民視", "東森", "三立", "中視", "公視", "TVBS", "緯來", "年代", "中天", "非凡", "澳視", "澳門", "TDM", "澳亞"]

# --- 4. 黑名單 (包含呢啲字眼嘅台會被直接踢走) ---
BLOCK_KEYWORDS = ["FOX", "UHD", "8K", "浙江", "杭州", "深圳", "CCTV", "延时", "測試"]

# --- 5. 排序優先級 (越排前面代表權重越高) ---
ORDER_KEYWORDS = ["廣東", "珠江", "廣州", "廣東衛視", "大灣區", "南方", "港台電視", "翡翠", "無線新聞", "明珠", "J2", "J5", "財經", "Viu", "HOY", "奇妙", "有線", "Now", "民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "壹電視", "非凡", "中天", "緯來", "澳視", "澳門", "TDM", "澳亞"]

# --- 6. 官方固守源 (唔洗測速，直接塞入去) ---
STATIC_CHANNELS = [
    {"name": "港台電視31 (官方)", "url": "https://rthklive1-lh.akamaihd.net/i/rthk31_1@167495/index_2052_av-b.m3u8", "speed": 10}, 
    {"name": "港台電視32 (官方)", "url": "https://rthklive2-lh.akamaihd.net/i/rthk32_1@168450/index_2052_av-b.m3u8", "speed": 10}
]

# --- 核心邏輯區 ---

# 設置偽裝瀏覽器頭部，增加成功率
COMMON_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def check_url(item):
    """
    【單一連結測速函數】
    1. 紀錄發出請求嘅時間。
    2. 使用 requests.get 嘗試連線，timeout=2 秒 (防止卡死)。
    3. stream=True 只獲取回應頭 (Headers)，不下載內容以節省流量同時間。
    """
    try:
        start_time = time.time()
        response = requests.get(item['url'], timeout=2, headers=COMMON_HEADERS, stream=True)
        if response.status_code == 200:
            # 毫秒數 = (當前時間 - 開始時間) * 1000
            item['speed'] = int((time.time() - start_time) * 1000)
            response.close()
            return item
    except:
        pass  # 任何連線錯誤直接忽略，返回 None
    return None

def fetch_and_parse():
    """
    【主程序邏輯】全掃描盲測模式
    """
    all_valid_channels = []
    report_data = [] # 用嚟寫入 source_report.txt 嘅內容
    seen_urls = set() # 去重 (同一條 Link 唔測兩次)
    
    print("🚀 啟動 30 線程並發全掃描...", flush=True)
    
    for index, source in enumerate(SOURCE_URLS):
        print(f"\n📡 [{index+1}/{len(SOURCE_URLS)}] 讀取 M3U: {source}", flush=True)
        is_taiwan_source = "tw.m3u" in source.lower()
        all_found_raw_data = [] # 儲存呢個源搵到嘅所有台名同 Link
        
        try:
            # 下載 M3U 內容
            r = requests.get(source, timeout=15, headers=COMMON_HEADERS)
            r.encoding = 'utf-8'
            if r.status_code != 200:
                report_data.append(f"來源: {source}\n狀態: ❌ HTTP 錯誤 {r.status_code}\n{'-'*50}")
                continue
            
            lines = r.text.split('\n')
            current_name = ""
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF"):
                    # 提取台名並簡轉繁
                    if ',' in line:
                        raw_name = line.split(',')[-1].strip()
                        current_name = cc.convert(raw_name).replace('臺', '台')
                elif line.startswith("http") and current_name:
                    # 格式過濾：剔除一啲奇怪嘅 M3U 分類標籤
                    if "[" in line and "]" in line: continue
                    all_found_raw_data.append({"name": current_name, "url": line})
                    current_name = ""

            if not all_found_raw_data:
                report_data.append(f"來源: {source}\n狀態: ⚪ 空源\n{'-'*50}")
                continue

            # --- 核心改動：多線程盲測 (ThreadPoolExecutor) ---
            # 點解用 30？因為可以同時測 30 條 Link，速度比單線程快 30 倍！
            print(f"    ⏳ 盲測開始 ({len(all_found_raw_data)} 條連結)...", end="", flush=True)
            with ThreadPoolExecutor(max_workers=30) as executor:
                # 把任務分發俾 30 個工仔一齊做
                results = list(executor.map(check_url, all_found_raw_data))
            
            # 過濾出活生生嘅連結
            valid_this_source = [r for r in results if r is not None]
            matched_this_source = []
            unmatched_but_alive = []
            
            for item in valid_this_source:
                # 檢查關鍵字同黑名單
                is_match = any(k.lower() in item['name'].lower() for k in KEYWORDS)
                is_blocked = any(b.lower() in item['name'].lower() for b in BLOCK_KEYWORDS)
                
                if (is_match or is_taiwan_source) and not is_blocked:
                    if item['url'] not in seen_urls:
                        matched_this_source.append(item)
                        all_valid_channels.append(item)
                        seen_urls.add(item['url'])
                else:
                    # 呢啲就係通咗但你冇寫 Keyword 嘅「漏網之魚」
                    unmatched_but_alive.append(f"{item['name']} ({item['speed']}ms)")

            # 準備健康度報告
            report_info = f"來源: {source}\n"
            report_info += f"狀態: ✅ 命中 {len(matched_this_source)} / 總活鏈 {len(valid_this_source)}\n"
            if unmatched_but_alive:
                report_info += f"漏網之魚: {', '.join(unmatched_but_alive)}\n"
            report_info += f"{'-'*50}"
            report_data.append(report_info)
            
            print(f"\r    ✅ 完成：發現 {len(valid_this_source)} 個活鏈 (其中 {len(matched_this_source)} 個符合關鍵字)")

        except Exception as e:
            report_data.append(f"來源: {source}\n狀態: ❌ 下載報錯 ({str(e)})\n{'-'*50}")
            print(f"\r    ❌ 報錯: {e}")

    # 寫入報告
    with open("source_report.txt", "w", encoding="utf-8") as f:
        f.write(f"IPTV 全掃描健康度報告\n生成日期: {datetime.datetime.now()}\n{'='*50}\n\n")
        f.write("\n".join(report_data))
            
    return all_valid_channels

def get_sort_key(item):
    """
    【排序之魂】決定邊個台喺 M3U 排第一
    權重計算：分組權重 + 關鍵字索引 + 速度微調
    """
    name = item["name"]
    speed = item.get('speed', 9999)

    # 1. 大分組 (百位數)
    if any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): gp = 100
    elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "viu", "HOY", "奇妙", "有線", "Now", "J2", "J5"]): gp = 200
    elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): gp = 300
    elif any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): gp = 400
    else: gp = 500

    # 2. 頻道優先級 (十位數)
    kp = 99
    for i, k in enumerate(ORDER_KEYWORDS):
        if k.lower() in name.lower():
            kp = i
            break
    
    # 3. 速度微調 (小數點後位) - 數值愈細排愈前
    return gp + kp + (speed / 1000000)

def generate_m3u(valid_channels):
    """
    【最終生成】將資料整理成 M3U 標準格式
    """
    # 結合靜態源同爬返嚟嘅源
    final_list = list(STATIC_CHANNELS) + valid_channels
    # 使用 get_sort_key 進行升序排序
    final_list.sort(key=get_sort_key)

    content = '#EXTM3U x-tvg-url="https://epg.112114.xyz/pp.xml"\n'
    content += f'# Update: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'

    # 分組邏輯
    groups = ["廣東/廣州", "香港", "台灣", "澳門", "其他"]
    for current_group in groups:
        for item in final_list:
            name, speed = item["name"], item.get('speed', 0)
            # 再次判斷分組標籤以便寫入 group-title
            if any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): ig = "澳門"
            elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): ig = "台灣"
            elif any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): ig = "廣東/廣州"
            elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "viu", "HOY", "奇妙", "有線", "Now", "J2", "J5"]): ig = "香港"
            else: ig = "其他"

            if ig == current_group:
                # 寫入 M3U 格式行，標註速度方便除錯
                content += f'#EXTINF:-1 group-title="{ig}" logo="https://epg.112114.xyz/logo/{name}.png",{name} ({speed}ms)\n{item["url"]}\n'

    with open("hk_live.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n🎉 大功告成！共有 {len(final_list)} 個頻道，檔案儲存為: hk_live.m3u")

if __name__ == "__main__":
    # 執行流程：1. 爬蟲測速 -> 2. 注入手動源 -> 3. 生成檔案
    live_channels = fetch_and_parse()
    
    print(f"\n📦 正在檢查手動補充源...", flush=True)
    existing_urls = {c['url'] for c in live_channels}
    for item in MANUAL_SINGLE_CHANNELS:
        item['name'] = cc.convert(item['name']).replace('臺', '台')
        if item['url'] not in existing_urls:
            checked = check_url(item)
            if checked:
                live_channels.append(checked)
                print(f"    [+] 手動源注入成功: {item['name']} ({checked.get('speed')}ms)")
    
    generate_m3u(live_channels)
