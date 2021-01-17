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

            self.comment_pages = deque()

            self.comment_ids = deque()

            self.movie_infos = dict()

            self.cache = list()

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
            # while len(self.url_task) > 0 and len(worker) < 10:
            if len(self.url_task) > 0:
                url = self.url_task.popleft()
                worker.add_future(self.page_process(url))

            # while len(self.movie_task) > 0 and len(worker) < 20:
            if len(self.movie_task) > 0:
                movie_id = self.movie_task.popleft()
                movie = MoveFinder(movie_id)
                worker.add_future(movie.process())

            # while len(self.comment_pages) > 0 and len(worker) < 20:
            if len(self.comment_pages) > 0:
                comment_page_id, start = self.comment_pages.popleft()
                comment_page = CommentPage(comment_page_id, start)
                worker.add_future(comment_page.process())

            # while len(self.comment_ids) > 0 and len(worker) < 30:
            if len(self.comment_ids) > 0:
                comment_id, movie_id = self.comment_ids.popleft()
                comment = CommentDetail(comment_id, movie_id)
                worker.add_future(comment.process())

            if time.time() - self.last_time > 5:
                await self.save_data()

            print('worker_1:', len(worker))

            await worker.execute()

            time.sleep(1)
            print('len(self.finded_movie_ids)')
            print('url_task:', len(self.url_task))
            print('movie_task:', len(self.movie_task))
            print('comment_pages:', len(self.comment_pages))
            print('comment_ids:', len(self.comment_ids))
            print('worker_2:', len(worker))

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
            if movie_id not in self.finded_movie_ids:
                self.finded_movie_ids.append(movie_id)
                self.movie_task.append(movie_id)

        return text

    async def get_response(self, url):
        headers = {'User-Agent': random.choice(agents)}
        async with httpx.AsyncClient(proxies=proxies) as client:
            try:
                r = await client.get(url, headers=headers)
            except Exception as e:
                print('error')
            # print(url)
            # print(r.status_code)
        print(r.status_code)
        return r

    def handle_result(self, title, year, score, comment, comment_amount):
        self.cache.append((title, year, score, comment, comment_amount))
        print('handle_result')
        if len(self.cache) >= 1:
            with open('comments', 'a', encoding='utf-8') as comment_file:
                spamwriter = csv.writer(comment_file)
                spamwriter.writerows(self.cache)

            self.cache = []


proxies = {
    "http://": "http://127.0.0.1:8787",
    "https://": "http://127.0.0.1:8787",
}


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
            Manager().comment_pages.append((self.id, start))


class CommentPage:
    def __init__(self, id, page):
        self.id = id
        self.page = page
        self.url = 'https://movie.douban.com/subject/%s/reviews?start=%s' % (id, page)

    async def process(self):
        page_text = await Manager().page_process(self.url)
        url_pattern = r'https://movie.douban.com/review/([0-9]*?)/'
        result = re.findall(url_pattern, page_text)
        Manager().comment_ids += [(finded, self.id) for finded in result]


class CommentDetail:
    def __init__(self, id, movie_id):
        self.id = id
        self.movie_id = movie_id
        self.url = 'https://movie.douban.com/review/%s/' % id

    async def process(self):
        page_text = await Manager().page_process(self.url)

        soup = BeautifulSoup(page_text)

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
