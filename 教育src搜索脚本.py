# -*- coding: utf-8 -*-
# @Time : 2022/2/3 22:17
# @Author : Ztop
# @Email : top.zeker@gmail.com
# @Link: https://www.zeker.top

import requests
import re
from lxml import etree
import os
from tqdm import tqdm
import time


def is_empty(file):  # 判断文件是否为空
    if os.path.exists(file):
        size = os.path.getsize(file)
        if size != 0:
            while True:
                print("文件%s内有数据，是否清空y/n？"%file, end=" ")
                result = input().lower()
                if result == 'y':
                    with open(file, "r+") as f:
                        f.seek(0)
                        f.truncate()  # 清空文件
                    print("%s已删除文件内数据%s" % (red, end))
                    break
                elif result == "n":
                    print("%s内容将在文件后追加！%s"% (red, end))
                    break
                else:
                    print("%s请重新输入%s\n" % (yellow, end))


def get_numEnd(choice, province_id=None):   # 获取对应列表页数
    print('%s正在处理中，请稍等...%s'%(blue, end))
    if choice == 1:
        url = 'https://src.sjtu.edu.cn/user/rank/'
        res = requests.get(url=url, headers=headers)
        data_html = etree.HTML(res.text)
        numEnd = data_html.xpath('//*[@id="show_list"]/ul/li[9]/a/text()')[0]
    elif choice == 3:
        url = 'https://src.sjtu.edu.cn/rank/firm/?province=' + str(province_id)
        res = requests.get(url=url, headers=headers)
        data_html = etree.HTML(res.text)
        numEnd = data_html.xpath('/html/body/div/div/div[1]/div/div/ul/li[last()-1]/a/text()')
        if numEnd:      # 是否存在
            numEnd = numEnd[0]
        else:
            numEnd = 1
    return int(numEnd)


def Exact_search(numEnd):     # 精确查找用户
    while True:
        name = input("%s【精确查询】%s >> 将查找的用户名："%(yellow, end))
        if name != "":
            break
    url = baseUrl + '/user/sum/?page='
    print("%s将查询页数总共：%s %s" % (blue, numEnd, end))
    time.sleep(0.5)
    flag = False
    for i in tqdm(range(numStart, numEnd + 1)):
        Surl = url + str(i)
        res = requests.get(url=Surl, headers=headers)
        data_html = etree.HTML(res.text)
        name_list = data_html.xpath('//div[@id="show_list"]/table/tr[@class="row"]/td[2]/a/text()')
        level_list = data_html.xpath('//*[@id="show_list"]/table/tr[@class="row"]/td[3]/span/text()')
        rank_list = data_html.xpath('//*[@id="show_list"]/table/tr[@class="row"]/td[1]/text()')
        for j in range(len(name_list)):
            list_name = str(name_list[j]).strip()      # 去前后空格
            if name == list_name:
                print("\n%s【+】目标在第 %s 页：%s\t称号：%s\t排名：%s%s\n" % (green, i, name_list[j], level_list[j], rank_list[j], end))
                flag = True
                break
        if flag:
            break


def Fuzzy_search(file, numEnd):     # 模糊查找用户
    is_empty(file)    # 判断文件内是否为空、有数据
    try:
        while True:
            name = input("%s【模糊查询】%s >> 将查找的用户名："%(yellow, end))
            if name != "":
                break
    except:
        pass
    is_ignoreCase = input('是否忽略字母大小写(默认)y/n？').lower()
    url = baseUrl + '/user/sum/?page='
    print("%s将查询页数总共：%s \n"
          "正在搜索，请耐心等候(查找到的相似用户名会在文件%s内详细显示)...%s" % (blue, numEnd, file, end))
    userNum = 0     # 人数记数（顺便的）
    count = 0       # 查找到的类似用户数
    for i in range(numStart, numEnd + 1):
        Surl = url + str(i)
        res_data = requests.get(url=Surl, headers=headers)
        data_html = etree.HTML(res_data.text)
        name_list = data_html.xpath('//div[@id="show_list"]/table/tr[@class="row"]/td[2]/a/text()')
        level_list = data_html.xpath('//*[@id="show_list"]/table/tr[@class="row"]/td[3]/span/text()')
        rank_list = data_html.xpath('//*[@id="show_list"]/table/tr[@class="row"]/td[1]/text()')
        rankNum = 0  # 记数
        for j in name_list:
            if is_ignoreCase == "n":        # 忽略字母大小写
                result = re.match('(.*)' + name + '(.*)', str(j))
            else:                           # 不忽略字母大小写（默认）
                pattern = re.compile(r'(.*)' + name + '(.*)', re.I)
                result = pattern.search(str(j))
            # print(j, type(result))
            if result:
                count += 1
                findName = result.group()
                print("[+] 第 %s%s%s 页发现类似用户名：%s%s%s" % (green, i, end, green, findName, end))
                with open(file, 'a', encoding="utf-8") as f:
                    f.write("第 %s 页：\t%s \t称号：%s\t排名：%s\n" % (i, findName, level_list[rankNum], rank_list[rankNum]))
            rankNum += 1
            userNum += 1
    if count != 0:
        print("\n%s查找用户人数共 %s，总计发现了%s个相似用户名%s\n" % (green, userNum, count, end))
    else:
        print("\n%s很遗憾，未找到相似用户名%s\n" % (red, end))


def gift_search(file):      # 查询未下架礼品
    is_empty(file)      # 判断文件内是否为空、有数据
    url = baseUrl + '/gift/'
    count = 0               # 未下架数量
    buyNum = 0              # 可买数量
    print("%s预计礼品数（可设）：%s \n"
          "正在搜索，请耐心等候(查询到的礼品会在文件%s内详细显示)...%s" % (blue, expectedGiftNum, file, end))
    for i in tqdm(range(expectedGiftNum)):
        gift_url = url + str(i)
        res = requests.get(url=gift_url, headers=headers)
        html = etree.HTML(res.text)
        if "Not Found" not in res.text:
            # print('[+]%s success' % gift_url)
            giftName = html.xpath('/html/body/div/div/div[1]/div/div/div[1]/div[2]/text()')[0].strip()
            num = html.xpath('/html/body/div/div/div[1]/div/div/div[3]/div[2]/span/strong/text()')[0].strip()
            coins = html.xpath('/html/body/div/div/div[1]/div/div/div[2]/div[2]/text()')[0].strip()
            if int(num) != 0:
                buyNum += 1
            with open(giftFile, 'a', encoding="utf-8") as f:
                f.write(gift_url + "\t\t库存" + num + "\t\t" + coins + "\t\t" + giftName + "\n")
            count += 1
    print("\n%s共有：%s 个未下架， 其中 %s 个可买，%s 个已无库存%s\n" % (yellow, count, buyNum, count - buyNum, end))


# 全国查找(已弃用)
def country_schoolFind(numEnd):        # 全国查找(已弃用)
    url = baseUrl + '/rank/firm/?page='
    flag = False
    try:
        while True:
            college_name = input("将查找的高校名：")
            if college_name != "":
                break
    except:
        pass
    print("%s【*】共 %s 页，请耐心等候，确保输入的高校名无误！%s" % (blue, numEnd, end))
    for i in tqdm(range(numStart, numEnd+1)):
        search_url = url + str(i)
        try:
            ress = requests.get(url=search_url, headers=headers)
            data_html = etree.HTML(ress.text)
            schoolNameList = data_html.xpath('/html/body/div/div/div[1]/div/div/table/tr[*]/td[2]/a/text()')
            bugNumList = data_html.xpath('/html/body/div/div/div[1]/div/div/table/tr[@class="row"]/td[3]/text()')
            bugThreatList = data_html.xpath('/html/body/div/div/div[1]/div/div/table/tr[@class="row"]/td[4]/text()')
            # print(schoolNameList[1].strip(), len(schoolNameList))
            for j in range(len(schoolNameList)):
                schoolName = schoolNameList[j].strip()  # 去前后空格
                if schoolName == college_name:
                    print('%s【+】目标在第 %s 页, 第 %s 个，id为%s，漏洞总数为%s，漏洞威胁值为%s%s\n'
                          %(green, i, j+1, (i-1)*15+(j+1), bugNumList[j], bugThreatList[j], end))
                    flag = True
                    break
            if flag:
                break
        except:
            pass
    if flag != True:
        print('%s【*】查询不到该高校信息，可能是高校名错误或暂未收录！%s\n' % (red, end))


def collegeFind(choice):      # 各区域/省份查找
    url = baseUrl + '/rank/firm/'
    print('%s正在获取各区域/省份信息....%s'%(blue, end))
    res = requests.get(url=url, headers=headers)
    data_html = etree.HTML(res.text)
    provinceList = data_html.xpath('//*[@id="id_province"]/option/text()')
    for i in range(len(provinceList)):
        print(f'{i}. {provinceList[i]}', end="\t"*4)
        if (i+1)%6 == 0 or i == len(provinceList)-1:
            print('')
    try:
        while True:
            province_id = int(input('请输入高校所在区域/省份对应编号：'))
            if province_id < 0 or province_id >= len(provinceList):
                print('%s输入超出限制！%s'%(red, end))
            else:
                break
    except:
        pass
    print("\n%s【%s】 >>%s 将查找的高校名："%(green, provinceList[province_id], end), end="")
    college_name = input('')
    numEnd = get_numEnd(choice, province_id)
    for i in tqdm(range(numStart, numEnd+1)):
        search_url = url + '?province=%s&page=%s' % (province_id, i)
        try:
            flag = False
            ress = requests.get(url=search_url, headers=headers)
            data_html = etree.HTML(ress.text)
            schoolNameList = data_html.xpath('/html/body/div/div/div[1]/div/div/table/tr[*]/td[2]/a/text()')
            bugNumList = data_html.xpath('/html/body/div/div/div[1]/div/div/table/tr[@class="row"]/td[3]/text()')
            bugThreatList = data_html.xpath('/html/body/div/div/div[1]/div/div/table/tr[@class="row"]/td[4]/text()')
            # print(schoolNameList[1].strip(), len(schoolNameList))
            for j in range(len(schoolNameList)):
                schoolName = schoolNameList[j].strip()  # 去前后空格
                if schoolName == college_name:
                    print('%s【+】目标【%s】在【%s】列表中第 %s 页, 第 %s 个，id为%s，漏洞总数为%s，漏洞威胁值为%s%s\n'
                        % (green, college_name, provinceList[province_id], i, j+1, (i-1)*15+(j+1), bugNumList[j], bugThreatList[j], end))
                    flag = True
                    break
            if flag:
                break
        except:
            pass
    if flag != True:
        print('%s【*】查询不到该高校信息，可能是高校名错误或暂未收录%s\n' % (red, end))


if __name__ == '__main__':
    global baseUrl, headers
    global numStart, expectedGiftNum
    global red, green, yellow, blue, end
    red = '\033[1m\033[31m'
    green = '\033[1m\033[32m'
    yellow = '\033[1m\033[33m'
    blue = '\033[1m\033[34m'
    end = "\033[0m"

    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Host': 'src.sjtu.edu.cn'
    }

    searchFile = 'search.txt'               # 查找用户名结果
    giftFile = 'gift.txt'                   # 查找礼品结果
    baseUrl = 'https://src.sjtu.edu.cn'     # 教育src网址
    numStart = 1                            # 用户列表起始页
    expectedGiftNum = 150                   # 预计有多少个礼品（可设）

    print('\neduSrc平台脚本（小型搜索脚本） —— by Ztop')

    while True:
        print('\033[1m\033[35m------------功能描述---------------\n'
              '1.根据用户名搜索用户信息（精确、模糊）\n'
              '2.搜索平台未下架礼品\n'
              '3.搜索指定区域内高校信息\n'
              '-----------------------------------\033[0m')
        choice = int(input(">>"))
        if choice == 1:
            print('精确查找1 | 模糊查找2')
            fchoice = int(input('>>'))
            if fchoice > 0 and fchoice < 3:
                numEnd = get_numEnd(choice)  # 获取用户列表End页
                if fchoice == 1:  # 精确查找
                    Exact_search(numEnd)
                else:  # 模糊查找
                    Fuzzy_search(searchFile, numEnd)
            else:
                print("%s未知选项！%s\n" % (yellow, end))
        elif choice == 2:  # 未下架礼品搜索
            gift_search(giftFile)
        elif choice == 3:  # 省份高校的查找
            # print('全国查找(slower)——1 / 各省份查找(faster)——2')
            # inter_choice = int(input('>>'))
            # if inter_choice == 1:        # 全国查找
            #     numEnd = get_numEnd(choice)
            #     country_schoolFind(numEnd)
            # elif inter_choice == 2:      # 各省份查找
            #     collegeFind(choice)
            # else:
            #     pass
            collegeFind(choice)
        else:
            print("%s请重新输入%s\n" % (red, end))
