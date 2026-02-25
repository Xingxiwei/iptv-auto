import requests
import re
import datetime
from opencc import OpenCC
from concurrent.futures import ThreadPoolExecutor

# 初始化繁簡轉換器
cc = OpenCC('s2t')

# --- 設定區 (保持不變) ---
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

MANUAL_SINGLE_CHANNELS = [
    {"name": "翡翠台", "url": "https://HaNoiIPTV.short.gy/Que_huong_HaNoiIPTV-TVB_Fei_Cui_Tai"},
    {"name": "翡翠台", "url": "http://php.jdshipin.com/TVOD/iptv.php?id=fct2"},
    {"name": "翡翠台", "url": "http://php.jdshipin.com/TVOD/iptv.php?id=fct3"},
    {"name": "翡翠台", "url": "http://74.91.26.218:82/live/jade.m3u8"},
    {"name": "翡翠台", "url": "http://mytv.cdn.loc.cc/o12.php?id=fct"},
    {"name": "翡翠台", "url": "http://r.jdshipin.com/thuYX"},
    {"name": "翡翠台", "url": "https://o11.163189.xyz/stream/tvb/fct4k/"},
    {"name": "翡翠台", "url": "http://r.jdshipin.com/qrfbg"},
    {"name": "大灣區衛視", "url": "http://www.8888866.xyz:10000/udp/239.77.0.215:5146"},
    {"name": "大灣區衛視", "url": "http://183.11.239.36:808/hls/132/index.m3u8"},
    {"name": "大灣區衛視", "url": "http://yahao.myqnapcloud.com:4022/udp/239.77.0.215:5146"},
    {"name": "大灣區衛視", "url": "http://222.128.55.152:9080/live/dwq.m3u8"},
    {"name": "大灣區衛視", "url": "http://gmxw.7766.org:808/hls/132/index.m3u8"}
]

KEYWORDS = ["ViuTV", "HOY", "RTHK", "Jade", "Pearl", "J2", "J5", "Now", "无线", "無線", "有线", "有線", "翡翠", "明珠", "港台", "廣東", "珠江", "广州", "廣州", "大灣區","鳳凰", "凤凰","成人", "民視", "東森", "三立", "中視", "公視", "TVBS", "緯來", "年代", "中天", "非凡", "澳視", "澳門", "TDM", "澳亞"]
BLOCK_KEYWORDS = ["FOX", "Pluto", "Local", "NBC", "CBS", "ABC", "AXS", "Snowy", "Reuters", "Mirror", "ET Now", "The Now", "Right Now", "News Now", "Chopper", "Wow", "UHD", "8K", "Career", "Comics", "Movies", "CBTV","Pearl","AccuWeather","Jadeed","Curiosity","Electric", "Warfare","Knowledge","MagellanTV","70s","80s","90s","Rock", "Winnipeg","Edmonton","RightNow","Times","True","Mindanow", "浙江", "杭州", "西湖", "深圳", "韶關", "CCTV", "CGTN", "華麗", "星河", "延时", "測試", "iHOY", "福建"]
ORDER_KEYWORDS = ["廣東", "珠江", "廣州", "廣東衛視", "大灣區", "南方", "港台電視", "翡翠", "無線新聞", "明珠", "J2", "J5", "財經", "Viu", "HOY", "奇妙", "有線", "Now", "民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "壹電視", "非凡", "中天", "緯來", "澳視", "澳門", "TDM", "澳亞"]
STATIC_CHANNELS = [{"name": "港台電視31 (官方)", "url": "https://rthklive1-lh.akamaihd.net/i/rthk31_1@167495/index_2052_av-b.m3u8"}, {"name": "港台電視32 (官方)", "url": "https://rthklive2-lh.akamaihd.net/i/rthk32_1@168450/index_2052_av-b.m3u8"}]

# --- 邏輯區 ---

def check_url(item):
    url = item['url']
    headers = {'User-Agent': 'Mozilla/5.0...', 'Referer': url}
    try:
        response = requests.head(url, timeout=2, headers=headers, allow_redirects=True)
        if response.status_code == 200: return item
        response = requests.get(url, timeout=3, headers=headers, stream=True)
        if response.status_code == 200:
            response.close()
            return item
    except: pass
    return None

def fetch_and_parse():
    found_channels = []
    seen_urls = set()
    headers = {'User-Agent': 'Mozilla/5.0...', 'Referer': 'https://live.hacks.tools/'}
    print("🚀 任務開始！正在抓取網路源...", flush=True)
    
    for index, source in enumerate(SOURCE_URLS):
        print(f"  [{index+1}/{len(SOURCE_URLS)}] 正在讀取: {source}", flush=True)
        is_taiwan_source = "tw.m3u" in source.lower()
        try:
            r = requests.get(source, timeout=15, headers=headers)
            r.encoding = 'utf-8'
            if r.status_code != 200: continue
            
            lines = r.text.split('\n')
            current_name, count_added = "", 0
            for line in lines:
                line = line.strip()
                if not line: continue
                if line.startswith("#EXTINF"):
                    if ',' in line:
                        raw_name = line.split(',')[-1].strip()
                        current_name = cc.convert(raw_name).replace('臺', '台')
                elif line.startswith("http") and current_name:
                    if "[" in line and "]" in line: 
                        current_name = ""
                        continue
                    if any(b.lower() in current_name.lower() for b in BLOCK_KEYWORDS):
                        current_name = ""
                        continue
                    
                    is_match = any(cc.convert(k).replace('臺', '台').lower() in current_name.lower() for k in KEYWORDS)
                    if is_match or is_taiwan_source:
                        if line not in seen_urls:
                            found_channels.append({"name": current_name, "url": line})
                            seen_urls.add(line)
                            count_added += 1
                        else:
                            # 呢度就可以見到邊啲係重複
                            pass 
                    current_name = ""
            print(f"    ✅ 抓取成功，新增 {count_added} 個頻道", flush=True)
        except Exception as e:
            print(f"    ❌ 抓取錯誤: {e}", flush=True)
    return found_channels

def generate_m3u(channels):
    print(f"\n🔍 共找到 {len(channels)} 個潛在頻道，開始檢測有效性...", flush=True)
    final_list = list(STATIC_CHANNELS)
    
    print(f"⚡ 啟動多線程檢測 (20 線程同步進行)...", flush=True)
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(check_url, channels))
    
    valid_channels = [r for r in results if r is not None]
    
    # --- 修正後的死鏈顯示邏輯 ---
    valid_urls = {r['url'] for r in valid_channels}
    invalid_channels = [c for c in channels if c['url'] not in valid_urls]
    
    if invalid_channels:
        print(f"\n🚫 檢測到 {len(invalid_channels)} 個失效連結：")
        for ch in invalid_channels:
            print(f"  [X] 死鏈: {ch['name']} - {ch['url']}")

    final_list.extend(valid_channels)
    print(f"\n✅ 檢測完成！共收錄 {len(valid_channels)} 個有效網路頻道。", flush=True)

    print("🔄 正在進行排序...", flush=True)
    final_list.sort(key=get_sort_key)

    content = '#EXTM3U x-tvg-url="https://epg.112114.xyz/pp.xml"\n'
    content += f'# Update: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    
    groups = ["廣東/廣州", "香港", "台灣", "澳門", "其他"]
    for current_group in groups:
        for item in final_list:
            name = item["name"].replace('臺', '台')
            # 分組邏輯
            if any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): ig = "澳門"
            elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): ig = "台灣"
            elif any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): ig = "廣東/廣州"
            elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "Viu", "HOY", "奇妙", "有線", "Now", "J2", "J5"]): ig = "香港"
            else: ig = "其他"

            if ig == current_group:
                content += f'#EXTINF:-1 group-title="{ig}" logo="https://epg.112114.xyz/logo/{name}.png",{name}\n{item["url"]}\n'

    with open("hk_live.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n🎉 全部完成！共生成 {len(final_list)} 個頻道。", flush=True)

def get_sort_key(item):
    name = item["name"]
    if any(x in name for x in ["廣州", "廣東", "珠江", "大灣區", "南方"]): gp = 100
    elif any(x in name for x in ["翡翠", "無線", "明珠", "港台", "RTHK", "Viu", "HOY", "奇妙", "有線", "Now", "J2", "J5"]): gp = 200
    elif any(x in name for x in ["民視", "中視", "華視", "公視", "TVBS", "三立", "東森", "年代", "緯來", "中天", "非凡"]): gp = 300
    elif any(x in name for x in ["澳門", "澳視", "澳亞", "TDM"]): gp = 400
    else: gp = 500
    
    kp = 99
    for i, k in enumerate(ORDER_KEYWORDS):
        if k.lower() in name.lower():
            kp = i
            break
    return gp + kp

if __name__ == "__main__":
    candidates = fetch_and_parse()
    existing_urls = {c['url'] for c in candidates}
    
    print(f"\n📦 正在注入手動源...", flush=True)
    for item in MANUAL_SINGLE_CHANNELS:
        item['name'] = cc.convert(item['name']).replace('臺', '台')
        if item['url'] not in existing_urls:
            print(f"  [+] 注入成功: {item['name']}")
            candidates.append(item)
            existing_urls.add(item['url'])
        else:
            print(f"  [!] 手動源已存在，跳過: {item['name']} ({item['url']})")
        
    generate_m3u(candidates)
