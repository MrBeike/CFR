# https://www.cfr.org/publications?topics=All&regions=All&type=All&sort_by=field_book_release_date_value&sort_order=DESC
import time
import requests
from bs4 import BeautifulSoup


# s = requests.Session()
# url = 'https://www.cfr.org/publications?topics=All&regions=All&type=All&sort_by=field_book_release_date_value&sort_order=DESC'
# headers = {
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
# }
# response = s.get(url, headers=headers)
# content = response.content.decode('utf-8')
# with open('page.html','w',encoding='utf-8') as f:
#     f.write(content)

# a = "April 2, 2019"
# k = time.strptime(a,"%B %d, %Y")
# kk = time.strftime('%Y-%m-%d',k)
# print(kk)

soup = BeautifulSoup(open('page.html', encoding='utf-8'), 'lxml')
cardSoup = soup.findAll(name='section', attrs={'class': 'card-article'})
#初始化容器
article_infos = []
#遍历网页获取所有文章信息
for item in cardSoup:
    article_info = {}
    article_topic = item.find(name='p', class_='card-article__topic-tag').text
    article_link = item.find(name='a', class_='card-article__link')['href']
    article_type = item.find(
        name='span', class_='card-article__publication-type').text
    # 可行，但是存在部分文章没有具体作者，且此项意义不大，暂时抛弃。
    # article_authors =item.find(name='span',class_='card-article__authors').get_text()
    article_title = item.find(name='p', class_='card-article__title').text
    article_date = item.find(name='span', class_='card-article__date').text
    article_info = {'topic': article_topic,
                    'link': article_link,
                    'type': article_type,
                    'title': article_title,
                    'date': article_date
                    }
    article_infos.append(article_info)
print(article_infos)
