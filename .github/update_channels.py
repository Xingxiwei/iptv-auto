import requests
import os
import git

# 定义 M3U 文件的 URL 列表
m3u_urls = [
    "https://live.hacks.tools/tv/ipv4/categories/hong_kong.m3u",  # 这里可以放入你需要更新的多个 URL
]

def fetch_m3u_data(url):
    """从给定的 URL 获取 M3U 文件内容"""
    print(f"Fetching M3U file from {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # 返回 M3U 文件内容
        else:
            print(f"Failed to fetch M3U file from {url}. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching M3U file from {url}: {e}")
        return None

def save_m3u_file(data, filename):
    """将抓取的 M3U 数据保存到文件"""
    with open(filename, "w") as file:
        file.write(data)
    print(f"Saved M3U data to {filename}")

def commit_and_push_changes(repo_path, filename):
    """将更新的文件提交并推送到 GitHub"""
    try:
        # 打开本地的 Git 仓库
        repo = git.Repo(repo_path)
        repo.git.add(filename)  # 添加文件到 Git 暂存区
        repo.index.commit(f"Auto-update IPTV channel list: {filename}")  # 提交更改
        repo.git.push()  # 推送到 GitHub
        print("Changes have been committed and pushed.")
    except Exception as e:
        print(f"Error during commit and push: {e}")

def update_channels():
    """主函数：抓取并更新 IPTV 频道列表"""
    all_channels_data = ""
    
    # 循环抓取每个 M3U 文件的内容
    for url in m3u_urls:
        m3u_data = fetch_m3u_data(url)
        if m3u_data:
            all_channels_data += m3u_data  # 这里可以添加更多的处理步骤，比如提取有效频道等
    
    if all_channels_data:
        # 保存最新的 M3U 文件
        save_m3u_file(all_channels_data, "hong_kong.m3u")  # 假设文件名是 hong_kong.m3u
        
        # 获取 Git 仓库的路径（可以从环境变量或传入参数）
        repo_path = os.getcwd()  # 假设脚本在 Git 仓库的根目录运行
        commit_and_push_changes(repo_path, "hong_kong.m3u")
    else:
        print("No data fetched from M3U files.")

if __name__ == "__main__":
    update_channels()
