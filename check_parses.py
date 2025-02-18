import requests
import time
import json

def fetch_and_parse_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 尝试解析 JSON 数据
        try:
            return response.json()
        except json.JSONDecodeError:
            # 如果 JSON 解析失败，尝试修复单引号问题
            raw_text = response.text
            fixed_text = raw_text.replace("'", '"')  # 将单引号替换为双引号
            return json.loads(fixed_text)  # 重新解析
    except Exception as e:
        print(f"请求JSON数据失败: {str(e)}")
        return None

def extract_parse_urls(json_data):
    if not json_data or "parses" not in json_data:
        return []
    
    # 直接提取所有HTTP/HTTPS开头的原始URL
    return [
        parse["url"]  # 不再处理参数
        for parse in json_data["parses"] 
        if parse.get("url", "").startswith(("http://", "https://"))  # 严格匹配协议头
    ]

def speed_test(url, test_times=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    total_time = 0
    success_count = 0
    
    for _ in range(test_times):
        try:
            # 构造测试URL（附加测试视频地址）
            test_url = url + "https://v.qq.com/x/cover/mzc00200jterl3u.html"
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
    
    if success_count == 0:
        return None
    
    return {
        "url": url,
        "avg_latency": round(total_time / success_count, 2),
        "success_rate": round(success_count / test_times * 100, 1)
    }

def main():
    json_url = "http://156.238.251.122:888/Lite.json"
    
    # 获取并解析JSON
    json_data = fetch_and_parse_json(json_url)
    if not json_data:
        return
    
    # 提取所有解析地址
    parsed_urls = extract_parse_urls(json_data)
    if not parsed_urls:
        print("未找到有效的解析地址")
        return
    
    print(f"找到 {len(parsed_urls)} 个解析地址:")
    for idx, url in enumerate(parsed_urls, 1):
        print(f"{idx}. {url}")
    
    # 执行测速
    print("\n开始测速...")
    results = []
    for url in parsed_urls:
        print(f"正在测试 {url}...")
        result = speed_test(url)
        if result:
            results.append(result)
    
    # 显示测速结果
    print("\n测速结果（按延迟排序）：")
    for idx, res in enumerate(sorted(results, key=lambda x: x["avg_latency"]), 1):
        print(f"{idx}. {res['url']}")
        print(f"  平均延迟: {res['avg_latency']}ms | 成功率: {res['success_rate']}%")
        print("-" * 50)

if __name__ == "__main__":
    main()
