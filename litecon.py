ip_version_priority = "ipv4"

source_urls = [
    "http://116.62.139.149:8089/static/output/iptv-api.m3u", #ADDED BY lee  ON 2025/2/19
    "http://116.62.139.149:8089/static/output/live_Lite.m3u", #ADDED BY lee  ON 2025/2/19
      
    "http://116.62.139.149:8089/static/output/user_result-xmbjm.m3u",  #ADDED BY lee  ON 2025/2/19      
    "http://175.178.251.183:6689/live.m3u", #ADDED BY lee from yuanlz77" ON 31/12/2024 
    "https://raw.githubusercontent.com/Guovin/TV/gd/output/result.m3u" #ADDED BY lee from Guovin/TV/gd/ (juhe) ON 31/12/2024 



]

url_blacklist = [
    "epg.pw/stream/",
    "103.40.13.71:12390",
    "[2409:8087:1a01:df::4077]/PLTV/",
    "8.210.140.75:68",
    "154.12.50.54",
    "yinhe.live_hls.zte.com",
    "8.137.59.151",
    "[2409:8087:7000:20:1000::22]:6060",
    "histar.zapi.us.kg",
    "www.tfiplaytv.vip",
    "dp.sxtv.top",
    "111.230.30.193",
    "148.135.93.213:81",
    "live.goodiptv.club",
    "iptv.luas.edu.cn"
]

announcements = [
    {
        "channel": "🤠小土豆ipv4直播",
        "entries": [
            {"name":"小土豆ipv4直播","url":","logo":""},
            {"name":"free by oneself","url":"","logo":""},
            {"name":"更新日期20250219","url":"","logo":""},
           
        ]
    }
]

epg_urls = [
    "https://live.fanmingming.com/e.xml",
    "http://epg.51zmt.top:8000/e.xml",
    "http://epg.aptvapp.com/xml",
    "https://epg.pw/xmltv/epg_CN.xml",
    "https://epg.pw/xmltv/epg_HK.xml",
    "https://epg.pw/xmltv/epg_TW.xml"
]
