# -*- coding:utf-8 -*-

import os
import sys
import time
import configparser
import webbrowser
import requests
import PySimpleGUI as sg
from datetime import datetime
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader

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
        self.page = '0'
        self.configparser = configparser.ConfigParser()
        self.config_file = 'config.ini'
        self.unready_base64 = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAABUFBMVEUAAAAXHBwXHB8XHCAUGx4VGx4WGx4XGx4RGh0QGRwXHB8SGh0QGRwhICMuJSgTGx4WHB8hICMQGRweHyJGLjAQGRweHyIRGh0SGh0gHyJFLjAgHyISGh0RGh0sJCYUGx5AKy4WGx4UGx4RGh0QGRwRGh1DLS8WHB8+Ki0+Ky0RGh0SGh1HLjE+Ky0YHSATGh06KSsXHB8eJCg/Ky0WGh0bISUbIiYTGh0sJCcWGx4ZHiIfJioWGx4gHyISGh0WGx0YHiEWGx0XHB8eHyIRGh0WGx6HR0jKYWGKSEqFRkj5c3P/d3fSZGSJSEm+W1z/dXX/dna/W1zFXl7FXl/ZZmfGXl/QYmPTZGTYZmbMYGHLYGHTZGW2WFnna2vzcHD/dHQ/OT5KQEZIQEVhRkt8RUc7R09HV2FGV2E4Rk4tNj1FU11IV2GFRkc5RU28Wlv///+6P0bJAAAARnRSTlMAAAAAAAAAABk0BBwmu+9uAr8pvvRuwykZu/S/GjTvbvQBcG5wcPgB+PlybvT4Am70bvT0NO/0cO8cwPRwxB0qxHACyC0a7TGk3QAAAAFiS0dEb1UIYYEAAAAHdElNRQfkAQgJIheSZQoDAAABV0lEQVQ4y83SazcCQRjA8ZrdopV2US5R7WovCrkV6UoiKjZd3OVaRHz/l3barZ5O4zXzbs7/d/bszDwm079ZZoRXd9fZmAc6RY/amK5AiLGN0ZQZdot93MFyukCIYx0TkxYgEG2fOso5XR2hdZczdzw9Q6M+mJ07yReKbixwdxcL+dP5BQA83jNVLekC95Kqnns9ADA+vqwLQdB7hV9kAECc3xCiaHSJ6x8bClkmdSCqVWIHQus1QsdCkZYutFy6DASV4a4BQZSvMKjKokD6gHH+3n380q9viELryyu3+P8Cq2WCQCi0tn53X3+o8UGJJwjEbGw+Pj2/vG5JimLcmJOFVx2ONJrNt/ftnVD3PgqVKHys3Vjr47MRT4Q6z41FvZ1MAWBN77W+4vsZY2D8/Hf7IAsGhkIj6VgkkemNnC+azFoQZQLCehiGQ+tJ0bBjMTT2A/1v1w/od0m7w7z/ewAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAxOS0xMi0yOFQwOTozMTo1NiswMDowMLhrE7kAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMTktMDEtMDhUMTk6NDY6NDMrMDA6MDATQUaYAAAAIHRFWHRzb2Z0d2FyZQBodHRwczovL2ltYWdlbWFnaWNrLm9yZ7zPHZ0AAAAYdEVYdFRodW1iOjpEb2N1bWVudDo6UGFnZXMAMaf/uy8AAAAYdEVYdFRodW1iOjpJbWFnZTo6SGVpZ2h0ADUxMo+NU4EAAAAXdEVYdFRodW1iOjpJbWFnZTo6V2lkdGgANTEyHHwD3AAAABl0RVh0VGh1bWI6Ok1pbWV0eXBlAGltYWdlL3BuZz+yVk4AAAAXdEVYdFRodW1iOjpNVGltZQAxNTQ2OTc2ODAz+0aqYAAAABJ0RVh0VGh1bWI6OlNpemUAMTQzNzdCYRhbVQAAAFp0RVh0VGh1bWI6OlVSSQBmaWxlOi8vL2RhdGEvd3d3cm9vdC93d3cuZWFzeWljb24ubmV0L2Nkbi1pbWcuZWFzeWljb24uY24vZmlsZXMvMTE4LzExODcyNTIucG5nKZCMRQAAAABJRU5ErkJggg=='
        self.ready_base64 = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAABU1BMVEUAAAAXHB8XHBwWGx4XHCAXGx4XGx0YHh8XGh4TDRYWGh4XHB8WGh0WGx4XHB8WGx4cIiYZHiIWGh0YHSAhKCwZHiEWGR0WGR0eJCgZHiEWGx4XGx4WGh4ZJyYbISUWFxwgRDcfJioWGx4gQDUWGx0WFx0WGR0WGh4WGR0gJysgQjYZIyMWFxwaJCQgQTYYIiIePTMWGh4WGBwWFxwbLSkePDIWFxwXGx8WGB0ZIyMWFhwWFxwYISIYIiMWFhsgQTYePDMbLCkWGR0WGB09SVIvOUA+S1NJWGJHVl8vOT8vOj9IV2E6Rk4tcFQ8SlI7R087s3s3kWpCTlg6sHpE2ZM2j2lBTlg8SFBE1pFE15I2lGowOkAoZEtD1JBD1ZAzlWk7sXpC0I4tdlY3pnM3pXND1ZFCz40rcVJAyYkqcFIsdlYhRThCzow/woVAyok1n27///+tUAaaAAAARHRSTlMAAAAAAAAAAAAAAAQ0HAJu778pAvTDAm70vxoCbvTvbvT0cPRwAmWcKfT1wyn09MP0cAI07/RwAhzAKCrEwIXz9O9wGhId7HQAAAABYktHRHDYAGx0AAAAB3RJTUUH5AEICSIcBbfTiwAAAQtJREFUOMvNz9kjAlEUx/F7KlSTiZRQpMhW1mxF2WIw2ZcWJutI2f7/N91p7rgP93ju93g+35dDSPsO6Gz/ueTptjtsuMvenl5fB1YA9Hn9+f2Azw6I9wcHDpTDo8EhEHsoPHysqGphxANij4yenCrqWTQmgfVTJ+9j5xeXTR+XAcxbV5w9bfjV9c1tkXd5YnLKabzU8lK5cjfNeSgyc59I0sJ0rfowG2NOQArOPT49zzcL5trLwuIScwKp5dey/kYLy1dW1ywnsJ6uveu0yLhETsC9sVk3imxuS+DEAU6zaHyInCs+v3SR/xUa4lyBOCu+q5ibRe1nG/NWkd7ZRZ0W7r2UhDst6Eg77hdIKUIQ5bczeQAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAxOS0xMi0yOFQwOTozMTo1NiswMDowMLhrE7kAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMTktMDEtMDhUMTk6NDY6MzkrMDA6MDC99BDPAAAAIHRFWHRzb2Z0d2FyZQBodHRwczovL2ltYWdlbWFnaWNrLm9yZ7zPHZ0AAAAYdEVYdFRodW1iOjpEb2N1bWVudDo6UGFnZXMAMaf/uy8AAAAYdEVYdFRodW1iOjpJbWFnZTo6SGVpZ2h0ADUxMo+NU4EAAAAXdEVYdFRodW1iOjpJbWFnZTo6V2lkdGgANTEyHHwD3AAAABl0RVh0VGh1bWI6Ok1pbWV0eXBlAGltYWdlL3BuZz+yVk4AAAAXdEVYdFRodW1iOjpNVGltZQAxNTQ2OTc2Nzk5wQ2/CgAAABJ0RVh0VGh1bWI6OlNpemUAMTIzMTZC887jBgAAAFp0RVh0VGh1bWI6OlVSSQBmaWxlOi8vL2RhdGEvd3d3cm9vdC93d3cuZWFzeWljb24ubmV0L2Nkbi1pbWcuZWFzeWljb24uY24vZmlsZXMvMTE4LzExODcyMDcucG5nsb2ShgAAAABJRU5ErkJggg=='
        self.gui()

    def appPath(self, relativepath=''):
        """Returns the base application path."""
        if hasattr(sys, 'frozen'):
            basePath = os.path.dirname(sys.executable)
            # Handles PyInstaller
        else:
            basePath = os.path.dirname(__file__)
        return os.path.join(basePath, relativepath)

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
            sg.popup(e, title='哦豁',font=("微软雅黑", 12))
            pass

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
        keyword_list = keyword.split(',')   
        for article_info in article_infos:
            if article_info['dayoff'] <= dayoff:
                dayoff_notify.append(article_info)
                keyword_check = [x in article_info['title'] for x in keyword_list]
                if True in keyword_check:
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
        if dayoff_notify or keyword_notify:
            env = Environment(loader=FileSystemLoader(
                self.appPath()), autoescape=select_autoescape(['html', 'xml']))
            template = env.get_template('result.html')
            html = template.render(dayoff_notify=dayoff_notify,
                                   keyword_notify=keyword_notify)
            with open('resultpage.html', 'w', encoding='utf-8') as f:
                f.write(html)
            return (len(dayoff_notify), len(keyword_notify))
        else:
            return False

    def showPage(self, resultpage):
        '''
        简单界面提示信息监测结果,查看结果功能
        param: resultpage 监测结果是否有命中  bool
        '''
        if resultpage:
            dayoff_num = resultpage[0]
            keyword_num = resultpage[1]
            total_num = dayoff_num + keyword_num
            layout = [
                [sg.Text('共收集到{0}条信息,其中日期检索{1}条,关键词检索{2}条。点击“查看结果”按钮查看详情。'.format(
                    total_num, dayoff_num, keyword_num), size=(40, 2), font=("微软雅黑", 13))],
                [sg.Button('查看结果', key='_show_', size=(12, 1),
                           font=("微软雅黑", 13), pad=(120, 2))]
            ]
            result_window = sg.Window(
                '提示', default_element_size=(40, 3)).Layout(layout)
            button, values = result_window.Read()
            if button == '_show_':
                webbrowser.open('resultpage.html', 0, False)
            elif button in (None, 'Exit'):
                result_window.Close()

    def configWriter(self,time,dayoff,keyword):
        '''
        界面用于信息监测相关设置
        param: time,dayoff,keyword 可选参数,此处为实现配置文件存在时,修改配置文件时显示当前设置  str
        '''
        writer = configparser.ConfigParser()
        layout = [
            [sg.Text('监测间隔时间', size=(12, 1), font=("微软雅黑", 13)), sg.Input(time, key='_time_', size=(
                10, 1), font=("微软雅黑", 13)), sg.Text('分钟', size=(10, 1), font=("微软雅黑", 13))],
            [sg.Text('信息有效期', size=(12, 1), font=("微软雅黑", 13)), sg.Input(dayoff, key='_dayoff_', size=(
                10, 1), font=("微软雅黑", 13)), sg.Text('天', size=(10, 1), font=("微软雅黑", 13))],
            [sg.Text('监测关键词', size=(12, 1), font=("微软雅黑", 13)), sg.Input(keyword, key='_keyword_', size=(
                10, 1), font=("微软雅黑", 13)), sg.Text('多个关键词用英文逗号隔开', size=(20, 1), font=("微软雅黑", 13))],
            [sg.Submit(button_text='写入配置文件', key='_write_', size=(12, 1), font=(
                "微软雅黑", 13)), sg.Cancel(button_text='退出', key='_exit_', size=(12, 1), font=("微软雅黑", 13))]
        ]
        config_window = sg.Window(
            'CFR信息监测设置', default_element_size=(40, 3)).Layout(layout)
        while True:
            button, values = config_window.Read()
            if button == '_write_':
                time = values['_time_'],
                # pysimplegui Bug? 获取到的是一个tuple 形如(time,)
                time = time[0]
                keyword = values['_keyword_']
                dayoff = values['_dayoff_']
                if time:
                    if keyword:
                        if dayoff:
                            writer.add_section('setting')
                            writer.set('setting', 'time', time)
                            writer.set('setting', 'keyword', keyword)
                            writer.set('setting', 'dayoff', dayoff)
                            with open(self.appPath(self.config_file), 'w+', encoding='utf-8') as f:
                                writer.write(f)
                            sg.popup('配置文件写入成功', title='提示', font=("微软雅黑", 12))
                            break
                        else:
                            sg.popup('信息有效期未填写', font=("微软雅黑", 12), title='提示')
                            continue
                    else:
                        sg.popup('监测关键词未填写', font=("微软雅黑", 12), title='提示')
                        continue
                else:
                    sg.popup('信息有效期未填写', font=("微软雅黑", 12), title='提示')
                    continue
            elif button in (None, '_exit_'):
                break
        config_window.Close()

    def configReader(self):
        '''
        界面用于读取本地配置文件
        '''
        reader = configparser.ConfigParser()
        reader.read(self.appPath(self.config_file), encoding='utf-8')
        time = reader.getint('setting', 'time')
        dayoff = reader.getint('setting', 'dayoff')
        keyword = reader.get('setting', 'keyword')
        return (time, dayoff, keyword)

    def gui(self):
        '''
        程序入口
        '''
        if os.path.isfile(self.config_file):
            image_base64 = self.ready_base64
            ready_flag = True
            time,dayoff,keyword = self.configReader()
        else:
            image_base64 = self.unready_base64
            ready_flag = False
            time = dayoff = keyword = ''
        layout = [
            [sg.Text('若配置文件不存在或想修改配置文件内容,请点击“写入配置文件”按钮。', size=(
                33, 2), text_color='red', font=("微软雅黑", 15))],
            [sg.Text('配置文件是否存在：', size=(18, 1), border_width=5, pad=(
                (30, 15), (20, 20)), font=("微软雅黑", 15)), sg.Image(data=image_base64, key='_image_')],
            [sg.Button(button_text='写入配置文件', key='_config_', size=(12, 1), font=("微软雅黑", 13),pad=(40,0)), sg.Button(
                button_text='开始监测', key='_start_', visible=ready_flag, size=(12, 1), font=("微软雅黑", 13))],
        ]
        main_window = sg.Window(
            'CFR信息监测工具', default_element_size=(40, 3)).Layout(layout)
        while True:
            button, values = main_window.Read()
            if button == '_config_':
                self.configWriter(time,dayoff, keyword)
                main_window.find_element('_image_').update(
                    data=self.ready_base64)
                main_window.find_element('_start_').update(visible=True)
                time,dayoff,keyword = self.configReader()
                continue
            elif button == '_start_':
                main_window.Minimize()
                self.workflow()
            elif button in (None, '_exit_'):
                break
        main_window.Close()

    def workflow(self):
        '''
        监测程序流程控制
        '''
        time, dayoff, keyword = self.configReader()
        #轮训时间怎么确定
        content = self.getPage()
        article_infos = self.newsParser(content)
        notify_tuple = self.notify(article_infos, keyword, dayoff)
        resultPage = self.resultPage(notify_tuple)
        self.showPage(resultPage)


if __name__ == '__main__':
    cfr = CFRMonitor()