import requests
import time
from urllib.parse import urlparse

def extract_parse_urls(json_data):
    if not json_data or "parses" not in json_data:
        return []
    
    urls = []
    for parse in json_data["parses"]:
        raw_url = parse.get("url", "").strip()
        if not raw_url.startswith("http"):
            continue
        
        urls.append(raw_url)
    return urls

def speed_test(url, test_times=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    total_time = 0
    success_count = 0
    
    for _ in range(test_times):
        try:
            # 使用真实测试地址
            test_url = url + "https://v.qq.com/x/cover/mzc00200jterl3u.html"
            start = time.time()
            response = requests.head(
                test_url, 
                headers=headers, 
                timeout=5, 
                allow_redirects=True
            )
            latency = (time.time() - start) * 1000  # 毫秒
            if response.status_code in [200, 301, 302]:
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
