import requests
import xlwt
from bs4 import BeautifulSoup

book = xlwt.Workbook(encoding='ascii')


def handler(sheet, url, index):
    data = requests.get(url).text
    soup = BeautifulSoup(data, "html.parser", from_encoding="utf-8")
    divs = soup.findAll("div", attrs={"class": "info"})
    for div in divs:
        text = div.text.split()
        sheet.write(index, 0, text[0])
        print(text[0])
        for content in text:
            if "30天" in content:
                sheet.write(index, 1, content[5])
            elif '正在出租' in content:
                sheet.write(index, 2, content.split('套')[0][1:])
            elif '建成' in content:
                sheet.write(index, 3, content[0:4])
        index = index + 1
    return index


def area(name, url, first, last):
    index = 0
    sheet = book.add_sheet(name)
    index = handler(sheet, url, index)
    for i in range(first, last):
        index = handler(sheet, url + 'pg' + str(i) + '/', index)


# area("东城", 'https://bj.lianjia.com/xiaoqu/dongcheng/', 2, 31)
# area("西城", 'https://bj.lianjia.com/xiaoqu/xicheng/', 2, 31)
area("朝阳", 'https://bj.lianjia.com/xiaoqu/chaoyang/', 2, 31)
# area("海淀", 'https://bj.lianjia.com/xiaoqu/haidian/', 2, 31)
# area("丰台", 'https://bj.lianjia.com/xiaoqu/fengtai/', 2, 31)
# area("石景山", 'https://bj.lianjia.com/xiaoqu/shijingshan/', 2, 11)
area("通州", 'https://bj.lianjia.com/xiaoqu/tongzhou/', 2, 25)
#area("昌平", 'https://bj.lianjia.com/xiaoqu/changping/', 2, 27)
# area("大兴", 'https://bj.lianjia.com/xiaoqu/daxing/', 2, 21)
# area("亦庄", 'https://bj.lianjia.com/xiaoqu/yizhuangkaifaqu/', 2, 6)
# area("顺义", 'https://bj.lianjia.com/xiaoqu/shunyi/', 2, 14)
# area("房山", 'https://bj.lianjia.com/xiaoqu/fangshan/', 2, 20)
# area("门头沟", 'https://bj.lianjia.com/xiaoqu/mentougou/', 2, 9)
# area("平谷", 'https://bj.lianjia.com/xiaoqu/pinggu/', 2, 5)
# area("怀柔", 'https://bj.lianjia.com/xiaoqu/huairou/', 2, 8)
# area("密云", 'https://bj.lianjia.com/xiaoqu/miyun/', 2, 8)
# area("延庆", 'https://bj.lianjia.com/xiaoqu/yanqing/', 2, 4)
book.save('1' + ".xls")
