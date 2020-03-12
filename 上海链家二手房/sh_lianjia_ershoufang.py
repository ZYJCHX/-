# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 14:37:26 2020

@author: ZYJ
"""

#导入basicSpider.py模块
from basicSpider import BasicSpider
import random
import re
import csv
import time
import numpy
import matplotlib.pyplot as plt

#设置User-Agent池
ua_pool = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
           'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
           'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
           'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
           'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
           'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
           ]

#设置headers
headers = [('User-Agent',random.choice(ua_pool)),
           ("Host","sh.lianjia.com"),
           ("Connection","keep-alive"),
           ("Accept-Language","zh-CN,zh;q=0.9")
           ]

#设置proxy代理服务器
proxy = None

#创建basicSpider实例
#设置日志文件名
basicSpider = BasicSpider(logName = 'sh_lianjia_ershoufang',
                          logFileName = 'sh_lianjia_ershoufang.log')


# 将页面中每一条房屋信息保存为一个字典，将所有的字典保存在列表中，返回列表
def get_house_info_list(url):
    house_info_list = []
    #获取一页中所有房屋信息的页面
    house_html= basicSpider.downloadHtml(url = url,
                                       headers = headers,
                                       proxy=proxy)
    
    try:
        #标题
        title_pattern = re.compile('<div class="title">[\s\S]*?data-sl="">([\s\S]*?)</a>')
        title_list = re.findall(title_pattern,house_html)
        
        #小区
        block_pattern = re.compile('<div class="positionInfo">[\s\S]*?data-el="region">([\s\S]*?)</a>')
        block_list = re.findall(block_pattern,house_html)
        
        #价格
        price_pattern = re.compile('<div class="totalPrice"><span>([\s\S]*?)</span>')
        price_list = re.findall(price_pattern,house_html)
        
        # 获取信息数据（例：1室1厅 | 55.08平米 | 南 | 简装 | 高楼层(共6层) | 2011年建 | 板楼），通过“|”符号分割字符串
        info_pattern = re.compile('<div class="houseInfo">[\s\S]*?</span>([\s\S]*?)</div>')
        info_list = re.findall(info_pattern,house_html)
        #房型
        house_type_list = []
        #面积大小
        size_list = []
        
        for info in info_list:           
            house_type_list.append(info.split('|')[0].strip())
            size = info.split('|')[1].strip()
            size = re.findall('\d+\.*\d*',size)
            size_list.extend(size)
#        print(size_list)
        #组成字典,添加到列表中
        for index in range(len(title_list)):
            d = {}
            d['title'] = title_list[index]
            d['price'] = price_list[index]
            d['size'] = size_list[index]
            d['block'] = block_list[index]
            d['house_type'] = house_type_list[index]
            house_info_list.append(d)
            
    except Exception as e:
        print(e)
    print(len(house_info_list))
    return house_info_list
    
#第一页URL:https://sh.lianjia.com/ershoufang/pg1/
#第二页URL:https://sh.lianjia.com/ershoufang/pg2/

minPage = 1
maxPage = 11
minTime = 1
maxTime = 3
basicUrl = 'https://sh.lianjia.com/ershoufang/'

#读取房屋信息，将信息保存到 house.csv 文件中
def houseSpider(url):
    house_info_list = []
    
    #设置抓取页面数
    for pg in range(minPage,maxPage):
        startUrl = url+'pg'+str(pg)
        house_info_list.extend(get_house_info_list(startUrl))
        #随机设置睡眠时间
        time.sleep(random.randint(minTime,maxTime))
        
    if house_info_list:
        # 将数据保存到 house.csv 文件中
        with open("house.csv", "w+") as f:
            # writer 对象，修改默认分隔符为 "-"
            writer = csv.writer(f, delimiter="$")
            for house_info in house_info_list:
                title = house_info.get("title")
                price = house_info.get("price")
                size = house_info.get("size")
                block = house_info.get("block")
                house_type = house_info.get("house_type")
                # 写入一行

                try:
                    writer.writerow([title, price, size, block, house_type])
#                    print(block, price, size)

                except:

                    continue
    
#get_house_info_list(basicUrl)
houseSpider(basicUrl)

#读取 house.csv 文件中价格和面积列
price, size = numpy.loadtxt('house.csv', delimiter='$', usecols=(1, 2), unpack=True)
print(price,size)

# 求价格和面积的平均值
price_mean = numpy.mean(price)
size_mean = numpy.mean(size)
print("平均价格为：(万元)", price_mean)
print("平均面积为：(平方米)", size_mean)

## 求价格和面积的方差
#price_var = numpy.std(price)
#size_var = numpy.std(size)
#print("价格的标准差为：(万元)", price_var)
#print("面积的标准差为：(平方米)", size_var)

plt.figure()
plt.subplot(211)
plt.title("Price/10000yuan")
plt.hist(price)

plt.subplot(212)
plt.xlabel("Size/m**2")

plt.hist(size)


#关闭日志
basicSpider.closeLogger()

 
