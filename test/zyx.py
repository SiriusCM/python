import requests
import time
from bs4 import BeautifulSoup

url = 'https://clifftor.com/post/xingbiqi-diary/chap_'

for j in range(16, 17):
    file = open('E://zyx/chap_0' + str(j) + '.txt', 'w', encoding='utf-8')

    for i in range((j - 1) * 20 + 1, j * 20 + 1):
        index = ''
        if i < 10:
            index = '00' + str(i)
        elif i < 100:
            index = '0' + str(i)
        else:
            index = str(i)
        if 263 < i < 270:
            continue
        if i > 315:
            continue
        data = requests.get(url + index + '/')
        data.encoding = 'utf-8'
        soup = BeautifulSoup(data.text, "html.parser")
        h1 = soup.findAll('h1', attrs={"class": "entry__title"})

        div = soup.findAll('div', attrs={'class': 'entry__content'})
        content = div[0].text
        file.write(h1[0].text)
        file.write('\n')
        file.write(content)
        file.write('\n\n')