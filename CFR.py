# -*- coding:utf-8 -*-

import time
import requests
import PySimpleGUI as sg
import configparser
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
#TODO 
# configparser读取ini文件
# config(self) 写入ini文件
# 信息有效期dayoff？小时？
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
        self.page = '0'

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
        url_prefix = 'https://www.cfr.org'
        #遍历本页所有文章
        for item in cardSoup:
            article_info = {}
            article_topic = item.find(name='p', class_='card-article__topic-tag').text.strip()
            article_link = item.find(name='a', class_='card-article__link')['href'].strip()
            article_link = url_prefix + article_link
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
                if keyword in (article_info['title'] or article_info['topic']):
                    keyword_notify.append(article_info)
        notify_tuple = (dayoff_notify,keyword_notify)
        return notify_tuple

    def resultPage(self,notify_tuple):
        '''
        将筛选过的信息通过网页显示出来
        param:notify_tuple 筛选过的信息集合
        return：resultpage.html 写入html文件
        '''
        dayoff_notify,keyword_notify= notify_tuple
        env = Environment(loader=FileSystemLoader('.'),autoescape=select_autoescape(['html', 'xml']))
        template = env.get_template('result.html')
        html = template.render(dayoff_notify=dayoff_notify,keyword_notify=keyword_notify)
        with open('resultpage.html','w',encoding='utf-8') as f:
            f.write(html)

    #TODO 布局优化
    def config(self):
        '''
        利用PySimpleGUI构建简单的界面用于信息监测相关设置
        '''
        layout = [
        [sg.Text('轮训间隔时间',size=(12, 1), font=("宋体", 13)),sg.Input('',key='_time_',size=(10, 1), font=("宋体", 13)),sg.Text('分钟',size=(10, 1), font=("宋体", 13))],
        [sg.Text('监测关键词',size=(12, 1), font=("宋体", 13)),sg.Input('',key='_keyword_',size=(10, 1), font=("宋体", 13)),sg.Text('多个关键词用,隔开',size=(18, 1), font=("宋体", 13))],
        [sg.Text('信息有效期',size=(12, 1), font=("宋体", 13)),sg.Input('',key='_dayoff_',size=(10, 1), font=("宋体", 13)),sg.Text('小时',size=(10, 1), font=("宋体", 13))],
        [sg.Submit(button_text='开始监测',key='_start_',size=(12, 1),font=("宋体", 13)), sg.Cancel(button_text='退出',key='_exit_',size=(12, 1),font=("宋体", 13))]
        ]
        window = sg.Window('CFR信息监测设置', default_element_size=(40, 3)).Layout(layout)
        while True:
            button,values = window.Read()
            if button == '_start_':
                print(values)
                time = values['_time_'],
                #pysimplegui Bug? 获取到的是一个tuple 形如(time,)
                time= time[0]
                keyword = values['_keyword_']
                dayoff = values['_dayoff_']
                if time:
                    if keyword:
                        if dayoff:
                            value = {'time':time,
                                    'keyword':keyword,
                                    'dayoff':dayoff
                                    }
                        else:
                            sg.popup('信息有效期未填写',font=("微软雅黑", 12), title='提示')
                    else:
                            sg.popup('监测关键词未填写',font=("微软雅黑", 12), title='提示')
                else:
                    sg.popup('监测时间未填写',font=("微软雅黑", 12), title='提示')
                
            elif button in (None,'_exit_'):
                break


    def configReader(self):
        parser = configparser.ConfigParser()
        reader = parser.read(self.config_file)
        time = reader.getint('setting','time')
        dayoff = reader.getint('setting','dayoff')
        keyword = reader.get('setting','keyword')


#TODO keyword
if __name__ == '__main__':
    m = CFRMonitor()
    content = m.getPage()
    article_infos = m.newsParser(content)
    notify_tuple = m.notify(article_infos,'Conflicts',400)
    resultPage = m.resultPage(notify_tuple)
    webbrowser.open('resultpage.html',0,False)