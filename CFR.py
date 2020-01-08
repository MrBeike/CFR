# -*- coding:utf-8 -*-

import time
import requests
import PySimpleGUI as sg
import configparser
import webbrowser
from datetime import datetime
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader

'''
Task:
每日监测新闻发布链接	
关于贸易方面的报告	https://www.cfr.org/publications?topics=All&regions=All&field_publication_type_target_id=All&sort_by=field_book_release_date_value&sort_order=DESC	
关于亚洲方面的报告	https://www.cfr.org/publications?topics=All&regions=115&field_publication_type_target_id=All&sort_by=field_book_release_date_value&sort_order=DESC
'''
# TODO
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
        self.configparser = configparser.ConfigParser()
        self.config_file = 'config.ini'
        self.ready_base64 = b'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'
        self.unready_base64 = b'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'

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

    def newsParser(self, content):
        '''
        通过BeautifulSoup解析页面内容,获取文章相关信息
        param:content 页面原始内容
        return:article_infos  包含所有文章信息的列表,单个文章信息用字典收纳   [{...},{...},...]
        '''
        soup = BeautifulSoup(content, 'lxml')
        cardSoup = soup.findAll(name='section', attrs={
                                'class': 'card-article'})
        # 初始化容器
        article_infos = []
        url_prefix = 'https://www.cfr.org'
        # 遍历本页所有文章
        for item in cardSoup:
            article_info = {}
            article_topic = item.find(
                name='p', class_='card-article__topic-tag').text.strip()
            article_link = item.find(
                name='a', class_='card-article__link')['href'].strip()
            article_link = url_prefix + article_link
            article_type = item.find(
                name='span', class_='card-article__publication-type').text.strip()
            # 可行，但是存在部分文章没有具体作者，且此项意义不大，暂时抛弃。
            # article_authors =item.find(name='span',class_='card-article__authors').get_text()
            article_title = item.find(
                name='p', class_='card-article__title').text.strip()
            article_date = item.find(
                name='span', class_='card-article__date').text.strip()
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

    def notify(self, article_infos, keyword, dayoff):
        '''
        筛选最近几天的文章,并弹窗提示
        param:article_infos 收集好的文章信息
        param:keyword keyword筛选结果 str
        param:dayoff dayoff筛选结果 int
        '''
        dayoff_notify = []
        keyword_notify = []
        for article_info in article_infos:
            if article_info['dayoff'] <= dayoff:
                dayoff_notify.append(article_info)
                if keyword in (article_info['title'] or article_info['topic']):
                    keyword_notify.append(article_info)
        notify_tuple = (dayoff_notify, keyword_notify)
        return notify_tuple

    def resultPage(self, notify_tuple):
        '''
        将筛选过的信息通过网页显示出来
        param:notify_tuple 筛选过的信息集合
        return：resultpage.html 写入html文件
        '''
        dayoff_notify, keyword_notify = notify_tuple
        env = Environment(loader=FileSystemLoader(
            '.'), autoescape=select_autoescape(['html', 'xml']))
        template = env.get_template('result.html')
        html = template.render(dayoff_notify=dayoff_notify,
                               keyword_notify=keyword_notify)
        with open('resultpage.html', 'w', encoding='utf-8') as f:
            f.write(html)

    # TODO 布局优化
    def configWriter(self):
        '''
        利用PySimpleGUI构建简单的界面用于信息监测相关设置
        '''
        layout = [
            [sg.Text('轮训间隔时间', size=(12, 1), font=("宋体", 13)), sg.Input('', key='_time_', size=(
                10, 1), font=("宋体", 13)), sg.Text('分钟', size=(10, 1), font=("宋体", 13))],
            [sg.Text('监测关键词', size=(12, 1), font=("宋体", 13)), sg.Input('', key='_keyword_', size=(
                10, 1), font=("宋体", 13)), sg.Text('多个关键词用,隔开', size=(18, 1), font=("宋体", 13))],
            [sg.Text('信息有效期', size=(12, 1), font=("宋体", 13)), sg.Input('', key='_dayoff_', size=(
                10, 1), font=("宋体", 13)), sg.Text('小时', size=(10, 1), font=("宋体", 13))],
            [sg.Submit(button_text='写入配置文件', key='_write_', size=(12, 1), font=(
                "宋体", 13)), sg.Cancel(button_text='退出', key='_exit_', size=(12, 1), font=("宋体", 13))]
        ]
        window = sg.Window(
            'CFR信息监测设置', default_element_size=(40, 3)).Layout(layout)
        while True:
            button, values = window.Read()
            if button == '_write_':
                time = values['_time_'],
                # pysimplegui Bug? 获取到的是一个tuple 形如(time,)
                time = time[0]
                keyword = values['_keyword_']
                dayoff = values['_dayoff_']
                if time:
                    if keyword:
                        if dayoff:
                            writer = self.configparser
                            writer.add_section('setting')
                            writer.set('setting', 'time', time)
                            writer.set('setting', 'keyword', keyword)
                            writer.set('setting', 'dayoff', dayoff)
                            with open(self.config_file, encoding='utf-8') as f:
                                writer.write(f)
                        else:
                            sg.popup('信息有效期未填写', font=("微软雅黑", 12), title='提示')
                    else:
                        sg.popup('监测关键词未填写', font=("微软雅黑", 12), title='提示')
                else:
                    sg.popup('监测时间未填写', font=("微软雅黑", 12), title='提示')
            elif button in (None, '_exit_'):
                break

    def configReader(self):
        '''
        利用configparser读取本地配置文件
        '''
        reader = self.configparser.read(self.config_file, encoding='utf-8')
        time = reader.getint('setting', 'time')
        dayoff = reader.getint('setting', 'dayoff')
        keyword = reader.get('setting', 'keyword')
        return

    def gui(self):
        if os.path.isfile(self.config_file):
            image_base64 = self.ready_base64
        else:
            image_base64 = self.unready_base64
        layout = [
            [sg.Text('CFR信息监测工具', size=(12, 1), font=("宋体", 13))],
            [sg.Text('配置文件存在？', size=(12, 1), font=("宋体", 13)),
             sg.Image(data=image_base64)],
            [sg.Button(button_text='开始监测', key='_start_', size=(12, 1), font=("宋体", 13)), sg.Button(
                button_text='写入配置文件', key='_config_', size=(12, 1), font=("宋体", 13))]
        ]
        window = sg.Window(
            'CFR信息监测工具', default_element_size=(40, 3)).Layout(layout)
        while True:
            button, values = window.Read()


# TODO keyword
if __name__ == '__main__':
    m = CFRMonitor()
    content = m.getPage()
    article_infos = m.newsParser(content)
    notify_tuple = m.notify(article_infos, 'Conflicts', 400)
    resultPage = m.resultPage(notify_tuple)
    webbrowser.open('resultpage.html', 0, False)
