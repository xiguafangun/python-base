import logging
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


# http://httpbin.org/get


class Worker:
    def __init__(self):
        self.futures = []

    def __len__(self):
        return len(self.futures)

    def add_future(self, future, priority):
        self.futures.append((future, priority))

    async def execute(self, max_task_amount=10):
        self.futures.sort(key=lambda x: x[1], reverse=True)

        tasks = [task for task, _ in self.futures[:max_task_amount]]
        await asyncio.gather(*tasks)
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
        self.last_time = int(time.time())

        if not self.inited:
            self.inited = True

            self.proxies = self.get_proxies()

            self.finded_urls = list()
            self.finded_movie_ids = list()

            self.movie_infos = dict()

            self.cache = list()

            self.last_time = int(time.time())

            self.handlers = dict()

            self.tasks = list()

            # 第一次运行
            index_url = 'https://movie.douban.com/'
            self.finded_urls.append(index_url)

            self.add_task('page_process', index_url)

    def add_task(self, name, data, priority=0):
        self.tasks.append((name, data, priority))

    async def save_data(self):
        print('开始保存配置')
        await worker.execute_until_finished()
        self.last_time = int(time.time())
        with open('data', 'wb') as datafile:
            pickle.dump(self, datafile)
        print('保存配置完成')

    async def running(self):
        async def process(name, data, priority, task):
            try:
                return await task
            except Exception as e:
                print(e)
                self.add_task(name, data, priority)

        while True:
            for name, data, priority in self.tasks:
                handler = self.handlers.get(name)
                if handler:
                    worker.add_future(
                        process(name, data, priority, handler(data).process()),
                        priority,
                    )
            self.tasks = []

            if time.time() - self.last_time > 10:
                await self.save_data()

            print('worker_amount:', len(worker))
            print('finded_movie_ids:', len(self.finded_movie_ids))

            await worker.execute()

            time.sleep(1)

    async def get_response(self, url):
        headers = {'User-Agent': random.choice(agents)}
        item = random.choice(self.proxies)
        proxy = {
            "http://": "http://%s:%s" % (item['ip'], item['port']),
            "https://": "http://%s:%s" % (item['ip'], item['port']),
        }

        async with httpx.AsyncClient(proxies=proxy) as client:
            r = await client.get(url, headers=headers)
        print(r.status_code)

        if r.status_code != 200:
            self.proxies.remove(item)
            if len(self.proxies) < 4:
                self.proxies += self.get_proxies()
            raise Exception('fail')

        return r

    def handle_result(self, title, year, score, comment_amount, comment):
        self.cache.append((title, year, score, comment_amount, comment))
        print('handle_result')
        if len(self.cache) >= 10:
            if not os.path.exists('comments.csv'):
                with open(
                    'comments.csv', 'a', newline='', encoding='utf-8-sig'
                ) as comment_file:
                    fieldnames = ['电影名', '年份', '评分', '影评数', '当前影评']
                    writer = csv.DictWriter(comment_file, fieldnames=fieldnames)
                    writer.writeheader()

            with open(
                'comments.csv', 'a', newline='', encoding='utf-8-sig'
            ) as comment_file:
                writer = csv.writer(comment_file)
                writer.writerows(self.cache)

            self.cache = []

    def register_handler(self, name, handler):
        self.handlers[name] = handler

    def get_proxies(self):
        response = httpx.get(
            'http://webapi.http.zhimacangku.com/getip?num=12&type=2&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions='
        )
        print(response.json())
        return response.json()['data']


# proxies = {
#     "http://": "http://127.0.0.1:8787",
#     "https://": "http://127.0.0.1:8787",
# }
# proxies = {
#     "http://": "http://220.201.85.80:4250",
#     "https://": "http://220.201.85.80:4250",
# }


class PageProcess:
    def __init__(self, url):
        self.url = url

    async def process(self):
        response = await Manager().get_response(self.url)
        text = response.text
        url_pattern = r'"(https://movie.douban.com/.*?)"'
        # pattern = r'https://movie.douban.com/subject/(.*?)/'
        # result = re.search(url_pattern, text)
        result = re.findall(url_pattern, text)

        for url in result:
            if url not in Manager().finded_urls:
                Manager().finded_urls.append(url)
                Manager().add_task('page_process', url)

        movie_pattern = r'https://movie.douban.com/subject/(.*?)/'
        result = re.findall(movie_pattern, text)

        for movie_id in result:
            if movie_id not in Manager().finded_movie_ids:
                Manager().finded_movie_ids.append(movie_id)
                Manager().add_task('movie_finder', movie_id, priority=3)

        return text


class MovieFinder:
    def __init__(self, id):
        self.id = id
        self.url = 'https://movie.douban.com/subject/%s/' % id

    async def process(self):
        """
        遍历影评所有页面
        将提取出得url加入任务队列
        """
        page_text = await PageProcess(self.url).process()

        title_pattern = r'<span property="v:itemreviewed">(.*?)</span>'

        result = re.search(title_pattern, page_text)
        self.title = result.group(1)

        year_pattern = r'<span class="year">\((.*?)\)</span>'
        result = re.search(year_pattern, page_text)

        self.year = int(result.group(1))

        score_pattern = (
            r'<strong class="ll rating_num" property="v:average">(.*?)</strong>'
        )
        result = re.search(score_pattern, page_text)

        if result.group(1) != '':
            self.score = float(result.group(1))
        else:
            self.score = ''

        comment_pattern = (
            r'<span class="pl">\( <a href="reviews">全部 (.*?) 条</a> \)</span>'
        )
        result = re.search(comment_pattern, page_text)

        self.comment_amount = int(result.group(1))

        Manager().movie_infos[self.id] = {
            'title': self.title,
            'year': self.year,
            'score': self.score,
            'comment_amount': self.comment_amount,
        }

        self.get_comments()

    def get_comments(self):
        for start in range(0, self.comment_amount, 20):
            # url = 'https://movie.douban.com/subject/35096844/reviews?start=%s' % start
            Manager().add_task(
                'comment_page', data={'id': self.id, 'start': start}, priority=4
            )


class CommentPage:
    def __init__(self, data):
        self.id, self.start = data['id'], data['start']
        self.url = 'https://movie.douban.com/subject/%s/reviews?start=%s' % (
            self.id,
            self.start,
        )

    async def process(self):
        page_text = await PageProcess(self.url).process()
        url_pattern = r'https://movie.douban.com/review/([0-9]*?)/'
        result = re.findall(url_pattern, page_text)
        for finded in set(result):
            Manager().add_task(
                'comment_detail', data={'id': finded, 'movie_id': self.id}, priority=5
            )


class CommentDetail:
    def __init__(self, data):
        self.id, self.movie_id = data['id'], data['movie_id']
        self.url = 'https://movie.douban.com/review/%s/' % self.id

    async def process(self):
        page_text = await PageProcess(self.url).process()

        soup = BeautifulSoup(page_text, features='lxml')

        contents = soup.find(name='div', attrs={"class": "review-content"})
        contents = contents.find_all(name='p')

        content = ''.join([a.text for a in contents])
        Manager().handle_result(
            title=Manager().movie_infos[self.movie_id]['title'],
            year=Manager().movie_infos[self.movie_id]['year'],
            score=Manager().movie_infos[self.movie_id]['score'],
            comment_amount=Manager().movie_infos[self.movie_id]['comment_amount'],
            comment=content,
        )


async def main():
    if os.path.exists('data'):
        print('读取记录文件')
        with open('data', 'rb') as datafile:
            manager = pickle.load(datafile)
            print('已发现的链接数：', len(manager.finded_urls))
            print('已发现的电影数：', len(manager.finded_movie_ids))
    else:
        manager = Manager()

    manager = Manager()
    manager.register_handler('page_process', PageProcess)
    manager.register_handler('movie_finder', MovieFinder)
    manager.register_handler('comment_page', CommentPage)
    manager.register_handler('comment_detail', CommentDetail)
    await manager.running()


asyncio.log.logger.setLevel(logging.ERROR)
asyncio.run(main())
