import os
import requests
import random
import re
import csv

# import threading
from collections import deque
import pickle
import time

# from bs4 import BeautifulSoup

agents = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0);",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
    "Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
]

# http://httpbin.org/get


class Manager:
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        判断如果文件存在就读取文件
        主要需要四个文件
        1.识别到的url链接
        2.识别到的movie id
        3.url任务队列
        4.movie id任务队列
        5.影评url
        5.影评
            字段：
            movie_id
            标题
            年份
        """
        self.finded_urls = list()
        self.finded_movie_ids = list()

        self.url_task = deque()
        self.movie_task = deque()

        self.comment_queue = deque()

        self.comment_ids = deque()

        self.last_time = int(time.time())

        # 第一次运行
        index_url = 'https://movie.douban.com/'
        self.finded_urls.append(index_url)
        self.url_task.append(index_url)

    # def read_data(self):
    #     if os.path.exists('data.json'):
    #         with open('data.json', 'r') as datafile:
    #             import ipdb

    #             ipdb.set_trace()
    #             data = json.loads(datafile.read())
    #             self.finded_urls = data['finded_urls']
    #             self.finded_movie_ids = data['finded_movie_ids']

    #             self.url_task = data['url_task']
    #             self.movie_task = data['movie_task']

    #             self.comment_queue = data['comment_queue']
    #             self.comment_ids = data['comment_ids']
    #         return True
    #     return False

    def save_data(self):
        print('保存配置中')
        self.last_time = int(time.time())
        with open('data', 'wb') as datafile:
            print(self.finded_urls)
            pickle.dump(self, datafile)

    # def running(self):
    #     while True:
    #         try:
    #             url = self.url_task.popleft(block=True, timeout=1)
    #         except Exception as e:
    #             pass
    #         else:
    #             print(url)
    #             self.page_process(url)

    #         try:
    #             movie_id = self.movie_task.popleft(block=True, timeout=1)
    #         except Exception as e:
    #             pass
    #         else:
    #             print(movie_id)
    #             movie = MoveFinder(movie_id)
    #             movie.process()

    #         if time.time() - self.last_time > 5:
    #             self.save_data()

    #         print('sleep')
    #         # print(self.url_task.qsize())
    #         # print(self.url_task.qsize())
    #         time.sleep(1)

    def page_process(self, url):
        response = self.get_response(url)
        text = response.text
        url_pattern = r'"https://movie.douban.com/.*?"'
        # pattern = r'https://movie.douban.com/subject/(.*?)/'
        # result = re.search(url_pattern, text)
        result = re.findall(url_pattern, text)

        for url in result:
            if url not in self.finded_urls:
                self.finded_urls.append(url)
                self.url_task.append(url)

        movie_pattern = r'https://movie.douban.com/subject/(.*?)/'
        result = re.findall(movie_pattern, text)

        for movie_id in result:
            if url not in self.finded_movie_ids:
                self.finded_movie_ids.append(movie_id)
                self.url_task.append(movie_id)

        return text

    def get_response(self, url):
        headers = {'User-Agent': random.choice(agents)}
        return requests.get('https://movie.douban.com', headers=headers)


class MoveFinder:
    def __init__(self, id):
        self.id = id
        self.url = 'https://movie.douban.com/subject/%s/' % id

    def process(self):
        """
        遍历影评所有页面
        将提取出得url加入任务队列
        """
        page_text = Manager().page_process(self.url)
        self.title = ''
        self.year = None
        self.score = None
        self.comment_amount = None

    def get_comments(self, url):
        page_text = Manager().page_process(url)
        for page in range(0, 10000, 20):
            page_text = Manager().page_process(page)
            pattern = r'https://movie.douban.com/review/(.*?)/'
            result = re.search(pattern, page_text)
            Manager().comment_ids.put('')


if os.path.exists('data'):
    print('读取记录文件')
    with open('data', 'rb') as datafile:
        manager = pickle.load(datafile)
        print(manager.finded_urls)
else:
    manager = Manager()

manager.running()
