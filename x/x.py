import requests
import time
import json
import re
import os
from datetime import datetime
from urllib.parse import urlparse

fail_output = []

def remove_single_line_comments(json_str):
    cleaned_json_str = re.sub(r'^\s*//.*', '', json_str, flags=re.MULTILINE)
    return cleaned_json_str

def remove_control_characters(s):
    """移除所有无效控制字符（保留 \n, \r, \t）"""
    allowed_control = {0x0A, 0x0D, 0x09}  # \n, \r, \t
    return ''.join(c for c in s if ord(c) >= 0x20 or ord(c) in allowed_control)

def remove_bom(s):
    """移除 UTF-8 BOM 字符（\ufeff）"""
    if s.startswith('\ufeff'):
        return s[1:]
    return s

def fetch_and_sites_json(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()

        # 关键修复：先移除 BOM
        text = response.text
        text = remove_bom(text)
        
        try:
            return response.json()
        except json.JSONDecodeError:
            # 移除注释 + 控制字符
            cleaned_text = remove_single_line_comments(text)
            cleaned_text = remove_control_characters(cleaned_text)
            
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                # 保存调试文件（用于检查问题）
                current_dir = os.path.dirname(os.path.abspath(__file__))
                debug_cleaned = os.path.join(current_dir, 'debug_cleaned.json')
                with open(debug_cleaned, 'w', encoding='utf-8') as f:
                    f.write(cleaned_text)
                print(f"JSON 解析失败，清理后的文本已保存到 debug_cleaned.json。错误: {e}")
                raise
    except Exception as e:
        print(f"此接口 {url} 请求JSON数据失败: {str(e)}")
        fail_message = f"此接口 {url} 请求JSON数据失败: {str(e)} \n"
        fail_output.append(fail_message)
        return None

def extract_sites_urls(json_data, source_url):
    urls = []
    if "sites" in json_data:
        for site in json_data["sites"]:
            url = site.get("api", "")
            if url.startswith(("http://", "https://")):
                urls.append({"source": source_url, "url": url, "site_data": site})
    return urls

def is_in_blacklist(url, blacklist_file='blacklist.txt'):
    """检查URL的host是否在黑名单中"""
    try:
        # 解析URL获取host部分
        parsed_url = urlparse(url)
        host = parsed_url.netloc  # 例如: "example.com:8080"
        
        # 去除端口号
        if ':' in host:
            host = host.split(':')[0]
        
        # 读取黑名单文件
        if os.path.exists(blacklist_file):
            with open(blacklist_file, 'r', encoding='utf-8') as f:
                blacklist = [line.strip() for line in f.readlines() if line.strip()]
            
            # 检查是否在黑名单中
            return host in blacklist
    except Exception:
        pass
    return False

def add_to_blacklist(url, blacklist_file='blacklist.txt'):
    """将URL的host添加到黑名单"""
    try:
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        
        # 去除端口号
        if ':' in host:
            host = host.split(':')[0]
        
        # 检查是否已经在黑名单中
        if not is_in_blacklist(url, blacklist_file):
            with open(blacklist_file, 'a', encoding='utf-8') as f:
                f.write(f"{host}\n")
            print(f"已将 {host} 添加到黑名单")
    except Exception as e:
        print(f"添加黑名单失败: {e}")

def speed_test(url, test_times=3):
    # 检查是否在黑名单中
    if is_in_blacklist(url):
        print(f"跳过黑名单中的URL: {url}")
        return None
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    total_time = 0
    success_count = 0
    
    for _ in range(test_times):
        try:
            test_url = url
            start = time.time()
            response = requests.head(
                test_url, 
                headers=headers, 
                timeout=5, 
                allow_redirects=True
            )
            latency = (time.time() - start) * 1000  # 毫秒
            if response.status_code in [200, 302, 301]:
                total_time += latency
                success_count += 1
        except Exception as e:
            print(f"测速失败 {url}: {str(e)}")
            fail_message = f"测速失败 {url}: {str(e)}\n"
            fail_output.append(fail_message)
            
            # 将URL的host添加到黑名单
            add_to_blacklist(url)
            
            # 不继续测试，直接返回None
            return None
    
    if success_count == 0:
        return None
    
    return {
        "url": url,
        "avg_latency": round(total_time / success_count, 2),
        "success_rate": round(success_count / test_times * 100, 1)
    }

def create_sorted_tvbox_json(json_urls, all_sites_with_speed, results):
    """
    根据测速延迟排序，生成适配TVBox的JSON文件
    类似于 http://545211.xyz:888/xingfu.json 的结构
    """
    
    # 创建URL到延迟的映射
    url_to_latency = {}
    for result in results:
        url = result["url"]
        latency = result["avg_latency"]
        url_to_latency[url] = latency
    
    # 为每个站点添加延迟信息
    for site_info in all_sites_with_speed:
        url = site_info.get("url", "")
        if url in url_to_latency:
            site_info["latency"] = url_to_latency[url]
        else:
            site_info["latency"] = float('inf')  # 如果没有延迟数据，设为无穷大
    
    # 按延迟排序站点（延迟低的在前）
    sorted_sites_info = sorted(all_sites_with_speed, key=lambda x: x["latency"])
    
    # 提取排序后的完整站点数据
    sorted_sites_data = []
    for site_info in sorted_sites_info:
        site_data = site_info["site_data"]
        # 可选：添加延迟信息到站点数据中（可作为参考）
        # site_data["latency"] = site_info["latency"]
        sorted_sites_data.append(site_data)
    
    # 构建TVBox JSON结构（参考xingfu.json）
    # 使用第一个来源的JSON作为模板，保留其他字段如spider、lives等
    tvbox_json = {}
    
    # 尝试从第一个来源获取完整的JSON结构
    for json_url in json_urls:
        json_data = fetch_and_sites_json(json_url)
        if json_data:
            # 复制所有字段
            for key in json_data:
                if key != "sites":  # sites字段我们将替换为排序后的
                    tvbox_json[key] = json_data[key]
            break  # 只使用第一个有效的JSON作为模板
    
    # 如果上面没有获取到模板，创建一个基本结构
    if not tvbox_json:
        tvbox_json = {
            "spider": "",
            "wallpaper": "",
            "lives": [],
            "sites": [],
            "parses": [],
            "flags": [],
            "ads": []
        }
    
    # 添加排序后的sites
    tvbox_json["sites"] = sorted_sites_data
    
    # 添加生成信息
    #tvbox_json["generated_info"] = {
    #    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #    "source_urls": json_urls,
    #    "total_sites": len(sorted_sites_data),
    #    "description": "根据测速延迟自动排序的TVBox配置"
    #}
    
    # 保存到文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    #tvbox_json_path = os.path.join(current_dir, f"tvbox_sorted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    tvbox_json_path = os.path.join(current_dir,'x.json')
    
    with open(tvbox_json_path, "w", encoding="utf-8") as f:
        json.dump(tvbox_json, f, ensure_ascii=False, indent=2)
    
    print(f"TVBox适配的JSON已保存到 {tvbox_json_path}")
    
    return tvbox_json_path

def main():
    json_urls = [
        "http://545211.xyz:888/xingfu.json",
        "http://116.62.139.149:3000/slasjh/xingfu/raw/branch/main/xingfu.json",
    ]

    all_sites_with_speed = []  # 存储所有站点信息（包括完整数据和URL）
    sites_urls = []  # 存储用于测速的URL列表

    for json_url in json_urls:
        json_data = fetch_and_sites_json(json_url)
        if json_data:
            extracted_urls = extract_sites_urls(json_data, json_url)
            sites_urls.extend(extracted_urls)
            
            # 存储完整的站点信息
            for item in extracted_urls:
                all_sites_with_speed.append({
                    "url": item["url"],
                    "source": item["source"],
                    "site_data": item["site_data"]
                })

    if not sites_urls:
        print("未找到有效的url")
        return

    print(f"找到 {len(sites_urls)} 个解析地址")

    # 创建黑名单文件（如果不存在）
    blacklist_file = 'blacklist.txt'
    if not os.path.exists(blacklist_file):
        with open(blacklist_file, 'w', encoding='utf-8') as f:
            f.write("# URL黑名单文件，每行一个host（如：example.com）\n")
        print(f"已创建黑名单文件: {blacklist_file}")

    print("\n开始测速...")
    results = []
    for item in sites_urls:
        source_url, url = item["source"], item["url"]
        site_name = item["site_data"].get("name", "未知站点")
        site_key = item["site_data"].get("key", "未知key")
        print(f"正在测试 {site_name}({site_key}): {url}")
        result = speed_test(url)
        if result:
            result["source"] = source_url
            result["key"] = site_key
            result["name"] = site_name
            results.append(result)

    if not results:
        print("没有成功的测速结果")
        return

    # 生成适配TVBox的排序JSON
    tvbox_json_path = create_sorted_tvbox_json(json_urls, all_sites_with_speed, results)

    # 准备写入文件的内容
    output_lines = []
    output_lines.append(f"找到 {len(sites_urls)} 个解析地址:\n")
    for idx, item in enumerate(sites_urls, 1):
        source_url, url = item["source"], item["url"]
        site_name = item["site_data"].get("name", "未知站点")
        site_key = item["site_data"].get("key", "未知key")
        output_lines.append(f"{idx}. {site_name}({site_key}): {url}（来自 {source_url}）\n")

    output_lines.append(f"\n已生成TVBox适配的JSON文件: {os.path.basename(tvbox_json_path)}\n")

    output_lines.append("\n测速结果（按延迟排序）：\n")
    for idx, res in enumerate(sorted(results, key=lambda x: x["avg_latency"]), 1):
        output_lines.append(f"{idx}. {res['name']}({res['key']}): {res['url']}（来自 {res['source']}）\n")
        output_lines.append(f"  平均延迟: {res['avg_latency']}ms | 成功率: {res['success_rate']}%\n")
        output_lines.append("-" * 50 + "\n")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    x_results = os.path.join(current_dir, 'x_results.txt')
    #fail_result = os.path.join(current_dir, f"{datetime.now().strftime('%Y%m%d_%H_%M_%S')}_fail_result.txt")
    fail_result = os.path.join(current_dir, 'fail_result.txt')
    with open(x_results, "w", encoding="utf-8") as f:
        f.writelines(output_lines)
    
    print("测速结果已保存到 x_results.txt 文件中。")
    
    if fail_output:
        with open(fail_result, "a", encoding="utf-8") as f:
            f.writelines(fail_output)
        print(f"fail结果已保存到 {fail_result} 文件中。")

if __name__ == "__main__":
    main()
