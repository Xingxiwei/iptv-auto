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

# --- 2. 手動補充源 (記得將你原本嗰幾十個貼返喺度) ---
MANUAL_SINGLE_CHANNELS = [
    {"name": "翡翠台", "url": "https://HaNoiIPTV.short.gy/Que_huong_HaNoiIPTV-TVB_Fei_Cui_Tai"},
    {"name": "翡翠台", "url": "http://php.jdshipin.com/TVOD/iptv.php?id=fct2"},
    {"name": "大灣區衛視", "url": "http://183.11.239.36:808/hls/132/index.m3u8"}
]

# --- 3. 關鍵字與黑名單設定 ---
KEYWORDS = ["ViuTV", "HOY", "RTHK", "Jade", "Pearl", "J2", "J5", "Now", "無線", "有線", "翡翠", "明珠", "港台", "廣東", "珠江", "廣州", "大灣區", "鳳凰", "民視", "東森", "三立", "中視", "公視", "TVBS", "緯來", "年代", "中天", "非凡", "澳視", "澳門", "TDM", "澳亞"]
BLOCK_KEYWORDS = ["FOX", "UHD", "8K", "浙江", "杭州", "深圳", "CCTV", "延时", "測試"]
ORDER_KEYWORDS = ["廣東", "珠江", "廣州", "廣東衛視", "大灣區", "南方", "港台電視", "翡翠", "無線新聞", "明珠", "J2", "J5", "財經", "Viu", "HOY", "奇妙", "有線", "Now", "民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "壹電視", "非凡", "中天", "緯來", "澳視", "澳門", "TDM", "澳亞"]

# --- 4. 靜態官方源 ---
STATIC_CHANNELS = [
    {"name": "港台電視31 (官方)", "url": "https://rthklive1-lh.akamaihd.net/i/rthk31_1@167495/index_2052_av-b.m3u8", "speed": 10}, 
    {"name": "港台電視32 (官方)", "url": "https://rthklive2-lh.akamaihd.net/i/rthk32_1@168450/index_2052_av-b.m3u8", "speed": 10}
]

# --- 核心邏輯區 ---

# 模擬瀏覽器 Header，防止被拒絕存取
COMMON_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def check_url(item):
    """
    【測速函數】
    - 使用 requests.get 進行連線測試
    - timeout=1.5 秒：平衡掃描速度與成功率
    - stream=True：只攞 Response Header，唔下載內容，慳流量
    """
    try:
        start_time = time.time()
        response = requests.get(item['url'], timeout=1.5, headers=COMMON_HEADERS, stream=True)
        if response.status_code == 200:
            # 計算回應時間 (ms)
            item['speed'] = int((time.time() - start_time) * 1000)
            response.close()
            return item
    except:
        pass  # 發生錯誤 (例如連線超時) 直接略過
    return None

def fetch_and_parse():
    """
    【主爬蟲與資料處理邏輯】
    - 遍歷 SOURCE_URLS 下載 M3U 內容
    - 使用 ThreadPoolExecutor (30線程) 進行並發測速
    - 【重要】優化命名邏輯：如果 URL 重複，會保留反應最快嗰個源嘅台名
    """
    all_valid_dict = {}  # 格式：{ "url": {item_data} }，用字典嚟自動去重
    report_data = []     # 儲存健康度報告內容
    
    print("🚀 啟動 30 線程並發全方位掃描 (優勝劣汰命名版)...", flush=True)
    
    for index, source in enumerate(SOURCE_URLS):
        print(f"\n📡 [{index+1}/{len(SOURCE_URLS)}] 正在讀取: {source}", flush=True)
        # 針對台灣專用源做特別處理
        is_taiwan_source = "tw.m3u" in source.lower()
        all_found_raw_data = [] 
        
        try:
            # 下載 M3U 檔案，15秒超時防止卡死
            r = requests.get(source, timeout=15, headers=COMMON_HEADERS)
            r.encoding = 'utf-8'
            if r.status_code != 200:
                report_data.append(f"來源: {source} | ❌ 下載失敗 (HTTP {r.status_code})")
                continue
            
            # 解析 M3U 行列
            lines = r.text.split('\n')
            current_name = ""
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF"):
                    # 提取台名
                    if ',' in line:
                        raw_name = line.split(',')[-1].strip()
                        # 簡轉繁，並統一「台」字
                        current_name = cc.convert(raw_name).replace('臺', '台')
                elif line.startswith("http") and current_name:
                    # 將名同 URL 執埋一齊
                    all_found_raw_data.append({"name": current_name, "url": line})
                    current_name = ""

            if not all_found_raw_data:
                report_data.append(f"來源: {source} | ⚪ 此源為空")
                continue

            # --- 啟動並發測速 ---
            print(f"    ⏳ 盲測 {len(all_found_raw_data)} 條連結...", end="", flush=True)
            with ThreadPoolExecutor(max_workers=30) as executor:
                # 把任務交給 30 個線程同步執行
                results = list(executor.map(check_url, all_found_raw_data))
            
            # 過濾出活著的連結 (results 入面唔係 None 嘅)
            valid_this_source = [r for r in results if r is not None]
            matched_count = 0
            
            for item in valid_this_source:
                # 關鍵字命中檢查
                is_match = any(k.lower() in item['name'].lower() for k in KEYWORDS)
                # 黑名單排除檢查
                is_blocked = any(b.lower() in item['name'].lower() for b in BLOCK_KEYWORDS)
                
                if (is_match or is_taiwan_source) and not is_blocked:
                    url = item['url']
                    # 【核心去重邏輯】
                    # 如果 URL 係第一次見，或者呢個新源比之前見過嘅更快
                    if url not in all_valid_dict or item['speed'] < all_valid_dict[url]['speed']:
                        # 覆蓋資料，確保保留最快線路嘅台名同速度
                        all_valid_dict[url] = item 
                    matched_count += 1

            report_data.append(f"來源: {source} | ✅ 命中 {matched_count} / 活鏈 {len(valid_this_source)}")
            print(f"\r    ✅ 完成：發現 {len(valid_this_source)} 個活鏈 (其中 {matched_count} 個入選)")

        except Exception as e:
            report_data.append(f"來源: {source} | ❌ 出錯: {str(e)}")
            print(f"\r    ❌ 出錯，已跳過")

    # 寫入 source_report.txt 健康度報告
    with open("source_report.txt", "w", encoding="utf-8") as f:
        f.write(f"IPTV 全掃描報告 - {datetime.datetime.now()}\n{'='*50}\n\n" + "\n".join(report_data))
            
    # 將字典入面嘅 item 轉返做 List 傳出去
    return list(all_valid_dict.values())

def get_sort_key(item):
    """
    【權重排序計算法】
    - gp: 大分組權重 (廣東100, 香港200...)
    - kp: 台名權重 (依照 ORDER_KEYWORDS 順序)
    - speed: 速度微調 (除以一百萬，確保同台快者排先)
    """
    name, speed = item["name"], item.get('speed', 9999)
    # 1. 決定大分組 GP
    if any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): gp = 100
    elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "viu", "HOY", "Now", "J2", "J5"]): gp = 200
    elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): gp = 300
    elif any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): gp = 400
    else: gp = 500
    
    # 2. 決定台名排序 KP
    kp = 99
    for i, k in enumerate(ORDER_KEYWORDS):
        if k.lower() in name.lower():
            kp = i
            break
            
    # 回傳總權重數值 (愈細排愈前)
    return gp + kp + (speed / 1000000)

def generate_m3u(valid_channels):
    """
    【M3U 檔案生成】
    - 合併靜態官方源同掃返嚟嘅源
    - 按權重進行最終排序
    - 寫入分組標籤
    """
    final_list = list(STATIC_CHANNELS) + valid_channels
    # 執行最終排序
    final_list.sort(key=get_sort_key)
    
    content = '#EXTM3U x-tvg-url="https://epg.112114.xyz/pp.xml"\n'
    content += f'# Update: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    
    # 依照分組順序循環寫入
    groups = ["廣東/廣州", "香港", "台灣", "澳門", "其他"]
    for g in groups:
        for item in final_list:
            name, speed = item["name"], item.get('speed', 0)
            # 再次判斷分組，用嚟對應 group-title
            if any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): ig = "澳門"
            elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): ig = "台灣"
            elif any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): ig = "廣東/廣州"
            elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "viu", "HOY", "Now", "J2", "J5"]): ig = "香港"
            else: ig = "其他"
            
            if ig == g:
                # 寫入 M3U 格式行，顯示毫秒數方便參考
                content += f'#EXTINF:-1 group-title="{ig}" logo="https://epg.112114.xyz/logo/{name}.png",{name} ({speed}ms)\n{item["url"]}\n'
    
    # 保存檔案
    with open("hk_live.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n🎉 任務完成！檔案已保存為: hk_live.m3u")

# --- 程式主入口 ---
if __name__ == "__main__":
    # 1. 執行 42 個源嘅全自動掃描
    live_channels = fetch_and_parse()
    
    # 2. 處理手動源
    print(f"\n📦 正在檢查並注入手動補充源...", flush=True)
    existing_urls = {c['url'] for c in live_channels}
    for item in MANUAL_SINGLE_CHANNELS:
        # 手動源台名簡轉繁
        item['name'] = cc.convert(item['name']).replace('臺', '台')
        # 如果網路源冇掃到呢條 Link，就幫佢測速並加入
        if item['url'] not in existing_urls:
            checked = check_url(item)
            if checked:
                live_channels.append(checked)
                print(f"    [+] 手動源注入成功: {item['name']} ({checked['speed']}ms)")
    
    # 3. 輸出最終 M3U 播放清單
    generate_m3u(live_channels)
