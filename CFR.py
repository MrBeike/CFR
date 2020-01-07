# -*- coding:utf-8 -*-

import time
import requests
from bs4 import BeautifulSoup


'''
Task:
每日监测新闻发布链接	
关于贸易方面的报告	https://www.cfr.org/publications?topics=All&regions=All&field_publication_type_target_id=All&sort_by=field_book_release_date_value&sort_order=DESC	
关于亚洲方面的报告	https://www.cfr.org/publications?topics=All&regions=115&field_publication_type_target_id=All&sort_by=field_book_release_date_value&sort_order=DESC
'''

class CFRMonitor():
    def __init__(self):
        pass

    # TODO
    def gui(self):
        '''
        简单GUI
        '''
        pass 

    def getPage(self,page):
        '''
        GET指定页面
        param:page 通过页面数来控制搜索结果数量（每页显示固定数量，下一页不包含上一页内容）
        return:content 获取成功后的页面内容
        '''
        # 访问网页相关项目配置
        # 浏览器头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        # 代理
        proxies = {
            "http": "http://127.0.0.1:1008",
            "https": "http://127.0.0.1:1008",
        }
        # 网址
        url = 'https://www.cfr.org/publications'
        # 查询关键字
        playload = {
            'topics': 'All',
            'regions': 'All',
            'field_publication_type_target_id': 'All',
            'sort_by': 'field_book_release_date_value',
            'sort_order': 'DESC',
            'page': str(page)
        }
        s = requests.Session()
        try:
            response = s.get(url, headers=headers, param=playload)
            code = response.status_code
            content = response.content
            if code == requests.codes.ok:
               content = response.content
               return content 
        except Exception as e:
            print('Error:', e)


    def today(self):
        now = time.localtime()
        year = now.tm_year
        month = now.tm_mon
        day = now.tm_mday
        return(year,month,day)

    def newsParser(self,content):
        '''
        通过BeautifulSoup解析页面内容,获取文章相关信息
        param:content 页面原始内容
        return:article_infos  包含所有文章信息的列表,单个文章信息用字典收纳   [{...},{...},...]
        '''
        soup = BeautifulSoup(content, 'lxml')
        cardSoup = soup.findAll(name='section', attrs={'class': 'card-article'})
        # 初始化容器
        article_infos = []
        #遍历本页所有文章
        for item in cardSoup:
            article_info = {}
            article_topic = item.find(name='p', class_='card-article__topic-tag').text.strip()
            article_link = item.find(name='a', class_='card-article__link')['href'].strip()
            article_type = item.find(name='span', class_='card-article__publication-type').text.strip()
            # 可行，但是存在部分文章没有具体作者，且此项意义不大，暂时抛弃。
            # article_authors =item.find(name='span',class_='card-article__authors').get_text()
            article_title = item.find(name='p', class_='card-article__title').text.strip()
            article_date = item.find(name='span', class_='card-article__date').text.strip()
            article_date_tuple = time.strptime(article_date, "%B %d, %Y")
            article_year = article_date_tuple.tm_year
            article_month = article_date_tuple.tm_mon
            article_day = article_date_tuple.tm_mday
            year,month,day = self.today()
            if (article_year == year) & (article_month == month):
                aritcle_dayoff = day - article_day
            article_info = {'topic': article_topic,
                            'link': article_link,
                            'type': article_type,
                            'title': article_title,
                            'date': article_date,
                            'dayoff': aritcle_dayoff
                            }
            article_infos.append(article_info)
        return article_infos

    # TODO
    def notify(self,article_infos,keyword,dayoff):
        '''
        筛选最近几天的文章,并弹窗提示
        param:article_infos 收集好的文章信息
        param:keyword keyword筛选结果
        param:dayoff dayoff筛选结果
        ''' 
        pass
