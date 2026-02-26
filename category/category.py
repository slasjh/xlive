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

def tiqu_gjz_juhe3(output_file, feilei, gjz_or_gjzs1,gjz_or_gjzs2,gjz_or_gjzs3):
    try:
        # 如果gjz_or_gjzs是字符串，则将其转换为单元素集合以便统一处理
        if isinstance(gjz_or_gjzs1, str):
            gjz_set1 = {gjz_or_gjzs1}
        else:
            gjz_set1 = set(gjz_or_gjzs1)
        if isinstance(gjz_or_gjzs2, str):
            gjz_set2 = {gjz_or_gjzs2}
        else:
            gjz_set2 = set(gjz_or_gjzs2)
        if isinstance(gjz_or_gjzs3, str):
            gjz_set3 = {gjz_or_gjzs3}
        else:
            gjz_set3 = set(gjz_or_gjzs3)  

        with open(output_file, 'w', encoding='utf-8') as f:
            # 注意：这里我们不再写入gjz_or_gjzs到文件，因为它可能是多个值
            # 如果您确实需要写入某种标识符，请考虑使用feilei参数
            f.write(f'{feilei},#genre#\n')  # 使用f-string格式化字符串并写入分类信息
            for line in all_lines:
                if any(gjz in line for gjz in gjz_set1):
                    if any(gjz in line for gjz in gjz_set2):    
                        if any(gjz in line for gjz in gjz_set3):    
                            f.write(line + '\n')

        print(f"合并后的文本已保存到文件: {output_file}")
        #print("time: {}".format(datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")))

    except Exception as e:
        print(f"保存文件时发生错误：{e}")
def tiqu_gjz_juhe2(output_file, feilei, gjz_or_gjzs1,gjz_or_gjzs2):
    try:
        # 如果gjz_or_gjzs是字符串，则将其转换为单元素集合以便统一处理
        if isinstance(gjz_or_gjzs1, str):
            gjz_set1 = {gjz_or_gjzs1}
        else:
            gjz_set1 = set(gjz_or_gjzs1)
        if isinstance(gjz_or_gjzs2, str):
            gjz_set2 = {gjz_or_gjzs2}
        else:
            gjz_set2 = set(gjz_or_gjzs2)

        with open(output_file, 'w', encoding='utf-8') as f:
            # 注意：这里我们不再写入gjz_or_gjzs到文件，因为它可能是多个值
            # 如果您确实需要写入某种标识符，请考虑使用feilei参数
            f.write(f'{feilei},#genre#\n')  # 使用f-string格式化字符串并写入分类信息
            for line in all_lines:
                if any(gjz in line for gjz in gjz_set1):
                    if any(gjz in line for gjz in gjz_set2):    
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
output_file0 = "category/dm.txt"
feilei_dm = "動画"
gjz_dm = ["動画", "动漫"]  # 使用列表来存储多个关键字
output_file1 = "category/3p.txt"
feilei_3p = "3p"
gjz_3p = ["3p", "3P", "4P", "4p", "5P", "前后夹击", "群P", "前后一起", "翘屁股"]  # 使用列表来存储多个关键字

output_file2 = "category/tai.txt"
feilei_tai = "tai分类"
gjz_tai = ["台", "花花公子", "电影18+", "松视", "欧美", "香蕉", "俄罗斯成人","卫星机房","午夜"]  # 使用列表来存储多个关键字

output_file3 = "category/jiaochuang.txt"
feilei_jiao = "叫床分类"
gjz_jiao = ["叫声", "叫床", "淫叫", "大叫", "呻吟", "嗷嗷叫", "叫爸爸", "浪叫", "操死我", "不要停", "求饶", "娇喘", "惨叫", "我还要", "骚叫"]

output_file4 = "category/haiyun.txt"
feilei_yun = "怀孕分类"
gjz_yun = ["怀孕", "大肚"]  # 使用列表来存储多个关键字

output_file5 = "category/houru.txt"
feilei_yun = "后入分类"
gjz_yun = ["后入", "老牛推车", "大屁股", "打桩机", "翘起屁股", "菊花", "阳台"]  # 使用列表来存储多个关键字

output_file6 = "category/tunjing.txt"
feilei_jing = "吞精分类"
gjz_jing = ["深喉", "吞精", "舔屌", "口爆", "舔屌", "吃鸡", "精液", "插嘴", "喷脸","撸管","打飞机"]  # 使用列表来存储多个关键字

output_file7 = "category/riben.txt"
feilei_you = "東京分类"
gjz_you = ["東京熱", "女优系列", "一本道", "日本", "無碼", "Japan", "無修正"]  # 使用列表来存储多个关键字

output_file8 = "category/shunv.txt"
feilei_sjh = "熟女分类"
gjz_sjh = ["熟妇", "熟女", "淫荡", "风骚", "反差婊", "白浆", "肥臀", "喷水", "高潮", "腰细胸大", "蜜桃美臀", "饥渴", "极品白虎", "骚妻", "骑乘", "撑爆", "嫩穴","猛操"]  # 使用列表来存储多个关键字
output_file9 = "category/guochan.txt"
feilei_china = "国产分类"
gjz_china = ["探花系列", "探花", "91大神","国产精品","偷情","外围","御姐","自拍","嫖娼大师","潜规则","91康先生","91CM","良家","少妇","寻花"]  # 使用列表来存储多个关键字

output_file10 = "category/lulian.txt"
feilei_lian = "露脸分类"
gjz_lian = ["露脸", "表情", "镜子", "一脸", "欲求不満", "吐舌头", "看镜头", "享受"]  # 使用列表来存储多个关键字


output_file11 = "category/penshui.txt"
feilei_shui = "喷水分类"
gjz_shui = ["喷水", "失禁", "噴射", "喷潮", "水汪汪"]  # 使用列表来存储多个关键字
output_file12 = "category/duibai.txt"
feilei_talk = "对白分类"
gjz_talk = ["国语对白", "对白", "电话", "通话", "聊天", "满嘴", "骚话"]  # 使用列表来存储多个关键字

output_file13 = "category/haoru.txt"
feilei_ru = "豪乳分类"
gjz_ru = [ "豪乳", "哺乳", "巨乳", "奶", "爆乳", "杯", "大乳"]  # 使用列表来存储多个关键字
output_file14 = "category/ziwei.txt"
feilei_ziwei = "自慰分类"
gjz_ziwei = [ "自慰"]  # 使用列表来存储多个关键字

output_file31 = "category/3plulianjiao.txt"
feilei31 = "3p-露脸-叫分类"
output_file21 = "category/houlian.txt"
feilei21 = "后入-脸分类"
output_file22 = "category/talksjh.txt"
feilei22 = "对白-淫分类"
output_file23 = "category/chinalian.txt"
feilei23 = "国产-脸分类"
output_file24 = "category/chinajiao.txt"
feilei24 = "国产-叫分类"
output_file25 = "category/3pjiao.txt"
feilei25 = "3p-叫分类"



# 调用函数示例，注意现在第三个参数对于第二个文件是一个列表
tiqu_gjz(output_file0, feilei_dm, gjz_dm)
tiqu_gjz(output_file1, feilei_3p, gjz_3p)
tiqu_gjz(output_file2, feilei_tai, gjz_tai)
tiqu_gjz(output_file3, feilei_jiao, gjz_jiao)
tiqu_gjz(output_file4, feilei_yun, gjz_yun)
tiqu_gjz(output_file5, feilei_yun, gjz_yun)
tiqu_gjz(output_file6, feilei_jing, gjz_jing)
tiqu_gjz(output_file7, feilei_you, gjz_you)
tiqu_gjz(output_file8, feilei_sjh, gjz_sjh)
tiqu_gjz(output_file9, feilei_china, gjz_china)
tiqu_gjz(output_file10, feilei_lian, gjz_lian)
tiqu_gjz(output_file11, feilei_shui, gjz_shui)
tiqu_gjz(output_file12, feilei_talk, gjz_talk)
tiqu_gjz(output_file13, feilei_ru, gjz_ru)
tiqu_gjz(output_file14, feilei_ziwei, gjz_ziwei)

# 调用函数示例，注意现在第三个参数对于第二个文件是一个列表

tiqu_gjz_juhe3(output_file31, feilei31, gjz_3p,gjz_lian,gjz_jiao) 
tiqu_gjz_juhe2(output_file21, feilei21, gjz_yun,gjz_lian) 
tiqu_gjz_juhe2(output_file22, feilei22, gjz_talk,gjz_sjh) 
tiqu_gjz_juhe2(output_file23, feilei23, gjz_china,gjz_lian) 
tiqu_gjz_juhe2(output_file24, feilei24, gjz_china,gjz_jiao) 
tiqu_gjz_juhe2(output_file25, feilei25, gjz_3p,gjz_jiao) 
