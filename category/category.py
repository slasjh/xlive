import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
import re
import logging


#读取文本方法
def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            return lines
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []



def process_url(url):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 ... Chrome/58.0 ...')
        with urllib.request.urlopen(req) as response:
            text = response.read().decode('utf-8')
            lines = text.split('\n')
            print(f"行数: {len(lines)}")
            is_m3u = any("#EXTINF" in line for line in lines[:15])
            source_type = "m3u" if is_m3u else "txt"
            logging.info(f"url: {url} 获取成功，判断为{source_type}格式")
            
            if is_m3u:
                for line in lines:
                    line = line.strip()
                    if line.startswith("#EXTINF"):
                        match = re.search(r'group-title="(.*?)",(.*)', line)
                        if match:
                            channel_name = match.group(2).strip()
                    elif line and not line.startswith("#"):
                        channel_url = line.strip()
                        all_lines.append(f"{channel_name},{channel_url}")  # 添加由逗号分隔的字符串
                        #all_lines.append((channel_name, channel_url))
            else:
                for line in lines:
                    line = line.strip()
                    if "#genre#" not in line and "," in line and "://" in line:
                        all_lines.append(line)
    except Exception as e:
        print(f"处理URL时发生错误：{e}")
# 去重复源 2024-08-06 (检测前剔除重复url，提高检测效率)
def remove_duplicates_url(lines):
    urls =[]
    newlines=[]
    for line in lines:
        if "," in line and "://" in line:
            # channel_name=line.split(',')[0].strip()
            channel_url=line.split(',')[1].strip()
            if channel_url not in urls: # 如果发现当前url不在清单中，则假如newlines
                urls.append(channel_url)
                newlines.append(line)
    return newlines

# 处理带$的URL，把$之后的内容都去掉（包括$也去掉） 【2024-08-08 22:29:11】
#def clean_url(url):
#    last_dollar_index = url.rfind('$')  # 安全起见找最后一个$处理
#    if last_dollar_index != -1:
#        return url[:last_dollar_index]
#    return url
def clean_url(lines):
    urls =[]
    newlines=[]
    for line in lines:
        if "," in line and "://" in line:
            last_dollar_index = line.rfind('$')
            if last_dollar_index != -1:
                line=line[:last_dollar_index]
            newlines.append(line)
    return newlines

# 处理带#的URL  【2024-08-09 23:53:26】
def split_url(lines):
    newlines=[]
    for line in lines:
        # 拆分成频道名和URL部分
        channel_name, channel_address = line.split(',', 1)
        #需要加处理带#号源=予加速源
        if  "#" not in channel_address:
            newlines.append(line)
        elif  "#" in channel_address and "://" in channel_address: 
            # 如果有“#”号，则根据“#”号分隔
            url_list = channel_address.split('#')
            for url in url_list:
                if "://" in url: 
                    newline=f'{channel_name},{url}'
                    newlines.append(line)
    return newlines




def tiqu_gjz(output_file, feilei, gjz_or_gjzs):
    try:
        # 假设all_lines是从某个地方获取的文本行列表
        # 这里为了示例，我们将其硬编码在函数内部
        #all_lines = [
            #"这是一行测试文本。",
            #"包含chinamobile.com的文本行：http://www.chinamobile.com/something",
            #"另一行包含migu的文本：http://example.com/migu.php",
            #"还有一行包含mg的文本：http://example.com/mg.php",
            #"以及一行不包含目标网址的文本。"
        #]

        # 如果gjz_or_gjzs是字符串，则将其转换为单元素集合以便统一处理
        if isinstance(gjz_or_gjzs, str):
            gjz_set = {gjz_or_gjzs}
        else:
            gjz_set = set(gjz_or_gjzs)

        with open(output_file, 'w', encoding='utf-8') as f:
            # 注意：这里我们不再写入gjz_or_gjzs到文件，因为它可能是多个值
            # 如果您确实需要写入某种标识符，请考虑使用feilei参数
            f.write(f'{feilei},#genre#\n')  # 使用f-string格式化字符串并写入分类信息
            for line in all_lines:
                if any(gjz in line for gjz in gjz_set):
                    f.write(line + '\n')

        print(f"合并后的文本已保存到文件: {output_file}")
        #print("time: {}".format(datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")))

    except Exception as e:
        print(f"保存文件时发生错误：{e}")

all_lines =  []
#读取文本
excudelist_lines=read_txt_to_array('category/ExcludeList.txt') 
# 定义
urls = [

    "https://raw.githubusercontent.com/slasjh/xlive/refs/heads/main/checkspeed/whitelist_auto_tv.txt",

]
# 处理
for url in urls:
    if url.startswith("http"):        
        # print(f"time: {datetime.now().strftime("%Y%m%d_%H_%M_%S")}")
        print(f"处理URL: {url}")
        process_url(url)
# 分级带#号直播源地址
all_lines=split_url(all_lines)
# 去$
all_lines=clean_url(all_lines)
# 去重
all_lines=remove_duplicates_url(all_lines)
# 将合并后的文本写入文件
output_file1 = "category/3p.txt"
feilei1 = "3p"
gjz1 = ["3p", "3P", "4P", "4p", "5P", "前后夹击"]  # 使用列表来存储多个关键字

output_file2 = "category/tai.txt"
feilei2 = "tai分类"
gjz2 = ["台"]  # 使用列表来存储多个关键字

output_file3 = "category/jiaochuang.txt"
feilei3 = "叫床分类"
gjz3 = ["叫声", "叫床", "淫叫", "大叫", "呻吟", "嗷嗷叫"]

output_file4 = "category/haiyun.txt"
feilei4 = "怀孕分类"
gjz4 = ["怀孕", "大肚"]  # 使用列表来存储多个关键字

output_file5 = "category/houru.txt"
feilei5 = "后入分类"
gjz5 = ["后入", "老牛推车", "大屁股", "打桩机", "打桩机"]  # 使用列表来存储多个关键字

output_file6 = "category/tunjing.txt"
feilei6 = "吞精分类"
gjz6 = ["深喉", "吞精"]  # 使用列表来存储多个关键字

output_file7 = "category/riben.txt"
feilei7 = "東京分类"
gjz7 = ["東京熱", "女优系列", "一本道"]  # 使用列表来存储多个关键字

output_file8 = "category/shunv.txt"
feilei8 = "熟女分类"
gjz8 = ["熟妇", "熟女", "淫荡", "风骚", "反差婊", "舔屌", "白浆"]  # 使用列表来存储多个关键字
output_file9 = "category/guochan.txt"
feilei9 = "国产分类"
gjz9 = ["探花系列", "探花", "91大神","国产精品","偷情","外围"]  # 使用列表来存储多个关键字

output_file10 = "category/lulian.txt"
feilei10 = "露脸分类"
gjz10 = ["露脸", "表情"]  # 使用列表来存储多个关键字


output_file11 = "category/penshui.txt"
feilei11 = "喷水分类"
gjz11 = ["喷水", "失禁", "噴射", "喷潮"]  # 使用列表来存储多个关键字
output_file12 = "category/duibai.txt"
feilei12 = "对白分类"
gjz12 = ["国语对白", "对白", "电话"]  # 使用列表来存储多个关键字

output_file13 = "category/haoru.txt"
feilei13 = "豪乳分类"
gjz13 = [ "豪乳", "哺乳", "巨乳", "奶"]  # 使用列表来存储多个关键字
output_file14 = "category/ziwei.txt"
feilei14 = "自慰分类"
gjz14 = [ "自慰"]  # 使用列表来存储多个关键字

# 调用函数示例，注意现在第三个参数对于第二个文件是一个列表
tiqu_gjz(output_file1, feilei1, gjz1)
tiqu_gjz(output_file2, feilei2, gjz2)
tiqu_gjz(output_file3, feilei3, gjz3)
tiqu_gjz(output_file4, feilei4, gjz4)
tiqu_gjz(output_file5, feilei5, gjz5)
tiqu_gjz(output_file6, feilei6, gjz6)
tiqu_gjz(output_file7, feilei7, gjz7)
tiqu_gjz(output_file8, feilei8, gjz8)
tiqu_gjz(output_file9, feilei9, gjz9)
tiqu_gjz(output_file10, feilei10, gjz10)
tiqu_gjz(output_file11, feilei11, gjz11)
tiqu_gjz(output_file12, feilei12, gjz12)
tiqu_gjz(output_file13, feilei13, gjz13)
tiqu_gjz(output_file14, feilei14, gjz14)

 
