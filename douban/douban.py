import os

# import httpx
import random
import re
import csv
import httpx
import asyncio

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


class Worker:
    def __init__(self):
        self.futures = []

    def __len__(self):
        return len(self.futures)

    def add_future(self, future):
        self.futures.append(future)

    async def execute(self, max_task_amount=10):
        await asyncio.gather(*self.futures[:max_task_amount])
        self.futures = self.futures[max_task_amount:]

    async def execute_until_finished(self):
        await self.execute(max_task_amount=len(self))


worker = Worker()


class Manager:
    inited = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # with cls._instance_lock:
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
        if not self.inited:
            self.inited = True

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

    async def save_data(self):
        print('开始保存配置')
        await worker.execute_until_finished()
        self.last_time = int(time.time())
        with open('data', 'wb') as datafile:
            pickle.dump(self, datafile)
        print('保存配置完成')

    async def running(self):
        while True:
            while len(self.url_task) > 0 and len(worker) < 100:
                url = self.url_task.popleft()
                worker.add_future(self.page_process(url))

            while len(self.movie_task) > 0 and len(worker) < 100:
                movie_id = self.movie_task.popleft()
                movie = MoveFinder(movie_id)
                worker.add_future(movie.process())

            if time.time() - self.last_time > 5:
                await self.save_data()

            await worker.execute()

            time.sleep(1)
            print('len(self.finded_movie_ids)')
            print(len(self.finded_movie_ids))

    async def page_process(self, url):
        response = await self.get_response(url)
        text = response.text
        url_pattern = r'"(https://movie.douban.com/.*?)"'
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
                self.movie_task.append(movie_id)

        return text

    async def get_response(self, url):
        headers = {'User-Agent': random.choice(agents)}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers)
            # print(url)
            # print(r.status_code)
        return r


class MoveFinder:
    def __init__(self, id):
        self.id = id
        self.url = 'https://movie.douban.com/subject/%s/' % id

    async def process(self):
        """
        遍历影评所有页面
        将提取出得url加入任务队列
        """
        page_text = await Manager().page_process(self.url)
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


async def main():
    # if os.path.exists('data'):
    #     print('读取记录文件')
    #     with open('data', 'rb') as datafile:
    #         manager = pickle.load(datafile)
    #         print(manager.finded_urls)
    # else:
    #     manager = Manager()

    manager = Manager()
    await manager.running()


asyncio.run(main())
