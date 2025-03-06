import re
import requests
import logging
from collections import OrderedDict, defaultdict
from datetime import datetime
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                   handlers=[logging.FileHandler("function.log", "w", encoding="utf-8"), 
                            logging.StreamHandler()])

def fetch_channels(url):
    """从指定URL获取频道数据，返回分类字典结构 """
    channels = defaultdict(lambda: defaultdict(set))  # 分类 -> 频道名 -> URL集合
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        lines = [line.strip() for line in response.text.split("\n") if line.strip()]

        current_category = "未分类"
        is_m3u = any("#EXTM3U" in line for line in lines[:3])
        is_txt = any("#genre#" in line for line in lines)

        # 解析M3U格式
        if is_m3u:
            for i in range(len(lines)):
                if lines[i].startswith("#EXTINF"):
                    # 提取分类和频道名
                    group_match = re.search(r'group-title="(.*?)"', lines[i])
                    name_match = re.search(r',(.*?)(?:\n|$)', lines[i])
                    if group_match and name_match:
                        current_category = group_match.group(1).strip()
                        channel_name = name_match.group(1).strip()
                        # 提取URL
                        if i+1 < len(lines) and not lines[i+1].startswith("#"):
                            channel_url = lines[i+1].strip()
                            channels[current_category][channel_name].add(channel_url)
        
        # 解析TXT格式
        elif is_txt:
            for line in lines:
                if "#genre#" in line:
                    current_category = line.split(",")[0].replace("#genre#", "").strip()
                elif "," in line:
                    channel_name, channel_url = line.split(",", 1)
                    channels[current_category][channel_name.strip()].add(channel_url.strip())
        
        # 其他格式尝试通用解析
        else:
            current_category = "默认分类"
            for line in lines:
                if "," in line:
                    parts = line.split(",", 1)
                    channel_name = parts[0].strip()
                    channel_url = parts[1].strip() if len(parts) > 1 else ""
                    channels[current_category][channel_name].add(channel_url)

        logging.info(f"成功解析URL: {url} 分类数: {len(channels)}")
        
    except Exception as e:
        logging.error(f"解析URL失败 {url}: {str(e)}")
    
    return channels

def aggregate_channels(source_urls):
    """聚合所有源URL的频道数据并进行去重"""
    all_channels = defaultdict(lambda: defaultdict(set))
    
    for url in source_urls:
        source_data = fetch_channels(url)
        for category, channels in source_data.items():
            for channel, urls in channels.items():
                # 合并URL并去重
                all_channels[category][channel].update(urls)
    
    # 转换为有序字典并排序
    ordered_channels = OrderedDict()
    for category in sorted(all_channels.keys()):
        ordered_channels[category] = OrderedDict()
        for channel in sorted(all_channels[category].keys()):
            ordered_channels[category][channel] = list(all_channels[category][channel])
    
    return ordered_channels

def generate_output_files(channels_data):
    """生成直播文件"""
    current_date = datetime.now().strftime("%Y%m%d")
    
    with open("live.m3u", "w", encoding="utf-8") as m3u, \
         open("live.txt", "w", encoding="utf-8") as txt:
        
        # 写入M3U头部
        m3u_header = f"""#EXTM3U x-tvg-url="{','.join(config.epg_urls)}" refresh="3600"\n"""
        m3u.write(m3u_header)
        
        # 写入公告信息
        for group in config.announcements:
            m3u.write(f'\n#EXTINF:-1 group-title="{group["channel"]}", 公告\n')
            m3u.write(f'{group.get("url", "")}\n')
            
            txt.write(f'\n{group["channel"]},#genre#\n')
            for entry in group["entries"]:
                txt.write(f'{entry["name"]},{entry["url"]}\n')
        
        # 写入频道数据
        for category, channels in channels_data.items():
            # 写入分类标题
            m3u.write(f'\n#EXTINF:-1 group-title="{category}", {category}\n')
            txt.write(f'\n{category},#genre#\n')
            
            # 写入频道信息
            for channel, urls in channels.items():
                for i, url in enumerate(urls, 1):
                    # 生成带线路标识的频道名
                    display_name = f"{channel}" if len(urls) == 1 else f"{channel} 线路{i}"
                    
                    # 写入M3U
                    m3u.write(f'#EXTINF:-1 tvg-name="{channel}" group-title="{category}",{display_name}\n')
                    m3u.write(f"{url}\n")
                    
                    # 写入TXT（只写入第一个URL）
                    if i == 1:
                        txt.write(f"{display_name},{url}\n")

if __name__ == "__main__":
    # 从config.py获取配置
    source_urls = config.source_urls
    config.announcements = getattr(config, "announcements", [])
    config.epg_urls = getattr(config, "epg_urls", [])
    
    # 聚合频道数据
    aggregated_data = aggregate_channels(source_urls)
    
    # 生成输出文件
    generate_output_files(aggregated_data)
    logging.info("直播文件生成完成")
