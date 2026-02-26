import requests
import time
import json
import re
import os
from datetime import datetime

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
                urls.append({"source": source_url, "url": url})
    return urls

def speed_test(url, test_times=3):
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
    
    if success_count == 0:
        return None
    
    return {
        "url": url,
        "avg_latency": round(total_time / success_count, 2),
        "success_rate": round(success_count / test_times * 100, 1)
    }

def main():
    json_urls = [
        "http://545211.xyz:888/xingfu.json",
        "http://116.62.139.149:3000/slasjh/xingfu/raw/branch/main/xingfu.json",
    ]

    sites_urls = []

    for json_url in json_urls:
        json_data = fetch_and_sites_json(json_url)
        if json_data:
           sites_urls.extend(extract_sites_urls(json_data, json_url))

    if not sites_urls:
        print("未找到有效的url")
        return

    print("\n开始测速...")
    results = []
    for item in sites_urls:
        source_url, url = item["source"], item["url"]
        print(f"正在测试 {url}（来自 {source_url}）...")
        result = speed_test(url)
        if result:
            result["source"] = source_url
            results.append(result)

    # 准备写入文件的内容
    output_lines = []
    output_lines.append(f"找到 {len(sites_urls)} 个解析地址:\n")
    for idx, item in enumerate(sites_urls, 1):
        source_url, url = item["source"], item["url"]
        output_lines.append(f"{idx}. {url}（来自 {source_url}）\n")

    output_lines.append("\n测速结果（按延迟排序）：\n")
    for idx, res in enumerate(sorted(results, key=lambda x: x["avg_latency"]), 1):
        output_lines.append(f"{idx}. {res['url']}（来自 {res['source']}）\n")
        output_lines.append(f"  平均延迟: {res['avg_latency']}ms | 成功率: {res['success_rate']}%\n")
        output_lines.append("-" * 50 + "\n")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    x_results = os.path.join(current_dir, 'x_results.txt')
    fail_result = os.path.join(current_dir, f"{datetime.now().strftime('%Y%m%d_%H_%M_%S')}_fail_result.txt")
    
    with open(x_results, "w", encoding="utf-8") as f:
        f.writelines(output_lines)
    
    print("测速结果已保存到 x_results.txt 文件中。")
    
    if fail_output:
        with open(fail_result, "a", encoding="utf-8") as f:
            f.writelines(fail_output)
        print(f"fail结果已保存到 {fail_result} 文件中。")

if __name__ == "__main__":
    main()
