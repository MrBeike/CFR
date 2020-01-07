# from bs4 import BeautifulSoup
# import time
# from datetime import datetime

# content = open('page.html',encoding='utf-8')
# soup = BeautifulSoup(content, 'lxml')
# cardSoup = soup.findAll(name='section', attrs={'class': 'card-article'})
# # 初始化容器
# article_infos = []
# #遍历本页所有文章
# for item in cardSoup:
#     article_info = {}
#     article_topic = item.find(name='p', class_='card-article__topic-tag').text.strip()
#     article_link = item.find(name='a', class_='card-article__link')['href'].strip()
#     article_type = item.find(name='span', class_='card-article__publication-type').text.strip()
#     # 可行，但是存在部分文章没有具体作者，且此项意义不大，暂时抛弃。
#     # article_authors =item.find(name='span',class_='card-article__authors').get_text()
#     article_title = item.find(name='p', class_='card-article__title').text.strip()
#     article_date = item.find(name='span', class_='card-article__date').text.strip()
#     article_date_tuple = datetime.strptime(article_date, "%B %d, %Y")
#     now = datetime.now()
#     dayoff = (now - article_date_tuple).days
#     print(dayoff)
from jinja2 import Environment, PackageLoader, select_autoescape,FileSystemLoader
env = Environment(loader=FileSystemLoader('.'),autoescape=select_autoescape(['html', 'xml']))
template = env.get_template('result.html')
html = template.render(name='variables')
with open('resultpage.html','w',encoding='utf-8') as f:
    f.write(html)

