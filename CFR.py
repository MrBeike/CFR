# -*- coding:utf-8 -*-

import time
import requests
import PySimpleGUI as sg
import webbrowser
from datetime import datetime
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape,FileSystemLoader

'''
Task:
每日监测新闻发布链接	
关于贸易方面的报告	https://www.cfr.org/publications?topics=All&regions=All&field_publication_type_target_id=All&sort_by=field_book_release_date_value&sort_order=DESC	
关于亚洲方面的报告	https://www.cfr.org/publications?topics=All&regions=115&field_publication_type_target_id=All&sort_by=field_book_release_date_value&sort_order=DESC
'''

class CFRMonitor():
    def __init__(self):
        # 代理
        self.proxies = {
            "http": "http://127.0.0.1:1008",
            "https": "http://127.0.0.1:1008",
        }
        # 浏览器头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
         # 网址
        self.url = 'https://www.cfr.org/publications'
        self.regions = 'All'
        self.page = '1'

    def getPage(self):
        '''
        GET指定页面
        param:page 通过页面数来控制搜索结果数量（每页显示固定数量，下一页不包含上一页内容） str
        param:regions 地区代码(通过CFR查询) ['All','115']  str 
        return:content 获取成功后的页面内容
        '''
        # GET查询关键字
        playload = {
            'topics': 'All',
            'regions': self.regions,
            'field_publication_type_target_id': 'All',
            'sort_by': 'field_book_release_date_value',
            'sort_order': 'DESC',
            'page': self.page
        }
        s = requests.Session()
        try:
            # response = s.get(self.url, headers=self.headers, params=playload, proxies=self.proxies)
            response = s.get(self.url, headers=self.headers, params=playload)
            code = response.status_code
            content = response.content
            if code == requests.codes.ok:
               content = response.content
               return content 
        except Exception as e:
            print('Error:', e)


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
            article_date_tuple = datetime.strptime(article_date, "%B %d, %Y")
            article_date = article_date_tuple.strftime('%Y-%m-%d')
            now = datetime.now()
            article_dayoff = (now - article_date_tuple).days
            article_info = {'topic': article_topic,
                            'link': article_link,
                            'type': article_type,
                            'title': article_title,
                            'date': article_date,
                            'dayoff': article_dayoff
                            }
            article_infos.append(article_info)
        return article_infos

    def notify(self,article_infos,keyword,dayoff):
        '''
        筛选最近几天的文章,并弹窗提示
        param:article_infos 收集好的文章信息
        param:keyword keyword筛选结果 str
        param:dayoff dayoff筛选结果 int
        ''' 
        dayoff_notify=[]
        keyword_notify=[]
        for article_info in article_infos:
            if article_info['dayoff'] <= dayoff:
                dayoff_notify.append(article_info)
            elif keyword in (article_info['title'] or article_info['topic']):
                keyword_notify.append(article_info)
            else:
                continue
        notify_tuple = (dayoff_notify,keyword_notify)
        return notify_tuple


    # def notifyGui(self,notify_tuple):
    #     '''
    #     简单提示GUI
    #     '''
    #     dayoff_notify,keyword_notify = notify_tuple
    #     dayoff_notify_num = len(dayoff_notify)
    #     keyword_notify_num = len(keyword_notify)
    #     total_num = dayoff_notify_num + keyword_notify_num
    #     layout = [
    #         [sg.Text('获取到符合条件的信息{0}条,其中符合时间条件{1}条,符合关键词条件{2}条。'.format(total_num,dayoff_notify_num,keyword_notify_num), size=(40, 1), font=("宋体", 13))],
    #         [sg.Submit(button_text='查看详情',key='more'), sg.Cancel(button_text='退出')]
    #     ]
    #     window = sg.Window('工作簿汇总工具', default_element_size=(40, 3)).Layout(layout)
    #     if not total_num:
    #         button, values = window.Read()
    #         if button == 'more':
    #             webbrowser.open()

    def resultPage(self,notify_tuple):
        dayoff_notify,keyword_notify= notify_tuple
        env = Environment(loader=FileSystemLoader('.'),autoescape=select_autoescape(['html', 'xml']))
        template = env.get_template('result.html')
        html = template.render(dayoff_notify=dayoff_notify,keyword_notify=keyword_notify)
        with open('resultpage.html','w',encoding='utf-8') as f:
            f.write(html)


    def config(self):
        layout = [
        [sg.Input('轮训间隔时间',key='_time_',size=(40, 1), font=("宋体", 13))],
        [sg.Submit(button_text='查看详情',key='more'), sg.Cancel(button_text='退出')]
        ]
        window = sg.Window('工作簿汇总工具', default_element_size=(40, 3)).Layout(layout)

#TODO keyword dont work
if __name__ == '__main__':
    m = CFRMonitor()
    content = m.getPage()
    article_infos = m.newsParser(content)
    notify_tuple = m.notify(article_infos,'How',400)
    resultPage = m.resultPage(notify_tuple)
    webbrowser.open('resultpage.html',0,False)