import os
import requests
import random
import re
import csv
import threading

from bs4 import BeautifulSoup

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


headers = {'User-Agent': random.choice(agents)}
response = requests.get('https://movie.douban.com', headers=headers)

soup = BeautifulSoup(response.text, 'lxml')

pattern = r'https://movie.douban.com/subject/(.*?)/'

for link in soup.find_all('a'):
    href = link.get('href')
    if href:
        if href not in finded_urls:
            finded_urls.append(href)
            url_queue.append(href)

        result = re.search(pattern, href)
        if result:
            movie_id = result.group(1)
            if movie_id not in finded_movie_ids:
                finded_movie_ids.append(movie_id)
                movie_queue.append(movie_id)


class Manager:
    finded_urls = []
    finded_movie_ids = []

    url_queue = []
    movie_queue = []

    comment_queue = []

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
        # self.read_data()

    def read_data(self):
        if os.path.exists('urls.csv'):
            with open('urls.csv', 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    print(row)

    def save_data(self):
        if os.path.exists('urls.csv'):
            with open('urls.csv', 'w') as csvfile:
                writer = csv.writer(csvfile)

    def runing(self):
        while True:
            if len(self.url_queue) > 0:
                url = self.url_queue.pop()
                self.page_process(url)

            if len(self.movie_queue) > 0:
                movie_id = self.movie_queue.pop()
                movie = MoveFinder(movie_id)
                movie.process()

    def page_process(self, url):
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')
        pattern = r'https://movie.douban.com/subject/(.*?)/'
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                self.urls.append()

                result = re.search(pattern, href)
                if result:
                    self.movie_ids.append(result.group(1))
        return response.text

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


manager = Manager()
manager.running()