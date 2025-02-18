import requests
import time
import json

# 定义接口地址
url = "http://156.238.251.122:888/Lite.json"

# 获取JSON数据
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # 检查请求是否成功

    # 尝试解析 JSON 数据
    try:
        data = response.json()
    except json.JSONDecodeError:
        # 如果 JSON 解析失败，尝试修复单引号问题
        raw_text = response.text
        fixed_text = raw_text.replace("'", '"')  # 将单引号替换为双引号
        data = json.loads(fixed_text)  # 重新解析
except requests.exceptions.RequestException as e:
    print(f"Failed to fetch data: {e}")
    exit(1)

# 获取parses下的url
parses_urls = [item['url'] for item in data.get('parses', [])]

# 测试每个url的速度
def test_url_speed(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        end_time = time.time()
        speed = end_time - start_time
        return speed, response.status_code
    except requests.exceptions.RequestException as e:
        return None, str(e)

# 将结果保存到txt文件
output_file = "url_speed_results.txt"

with open(output_file, "w", encoding="utf-8") as file:
    for url in parses_urls:
        speed, status = test_url_speed(url)
        if speed is not None:
            result = f"URL: {url}, Speed: {speed:.2f} seconds, Status Code: {status}\n"
        else:
            result = f"URL: {url}, Error: {status}\n"
        file.write(result)  # 写入文件
        print(result.strip())  # 同时打印到控制台

print(f"Results have been saved to {output_file}")
