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

AGENTS = [
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

DATA_FILENAME = 'data'

# INDEX_URL = 'https://movie.douban.com/'
INDEX_URL = 'https://movie.douban.com/subject/26752564/'

MOVIES_FILENAME = 'movies.csv'
CATES_FILENAME = 'cates.csv'
LANGS_FILENAME = 'langs.csv'
DIRECTORS_FILENAME = 'directors.csv'
WRITERS_FILENAME = 'writers.csv'
REGIONS_FILENAME = 'regions.csv'
ACTORS_FILENAME = 'actors.csv'


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


class Data:
    def __init__(self):
        self.finded_urls = list()
        self.finded_movie_ids = list()

        self.tasks = list()


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
            year
        """

        if not self.inited:
            self.last_time = int(time.time())
            self.proxies = []
            self.handlers = dict()
            self.running = False

            self.inited = True

            self.worker = Worker()
            if os.path.exists(DATA_FILENAME):
                print('读取记录文件')
                with open(DATA_FILENAME, 'rb') as datafile:
                    self.data = pickle.load(datafile)
                    print('已发现的链接数：', len(self.data.finded_urls))
                    print('已发现的电影数：', len(self.data.finded_movie_ids))
            else:
                self.data = Data()

            # 第一次运行
            self.data.finded_urls.append(INDEX_URL)

            self.add_task('page_process', INDEX_URL)

            self.movies_saver = Saver(
                filename=MOVIES_FILENAME,
                fieldnames=[
                    'movie_id',
                    'movie_name',
                    'length',
                    'year',
                    'score',
                    'score_count',
                    'intro',
                    'want_count',
                    'watched_count',
                    'actor_count',
                    'short_count',
                    'comment_count',
                    'discuss_count',
                    'question_count',
                ],
            )
            # CATES_FILENAME = 'cates.csv'
            # LANGS_FILENAME = 'langs.csv'
            # DIRECTORS_FILENAME = 'directors.csv'
            # WRITERS_FILENAME = 'writers.csv'
            # REGIONS_FILENAME = 'regions.csv'
            # ACTORS_FILENAME = 'actors.csv'
            self.cates_saver = Saver(
                filename=CATES_FILENAME,
                fieldnames=[
                    'movie_id',
                    'cate',
                ],
            )

            self.langs_saver = Saver(
                filename=LANGS_FILENAME,
                fieldnames=[
                    'movie_id',
                    'lang',
                ],
            )
            self.directors_saver = Saver(
                filename=DIRECTORS_FILENAME,
                fieldnames=[
                    'movie_id',
                    'director',
                ],
            )
            self.writers_saver = Saver(
                filename=WRITERS_FILENAME,
                fieldnames=[
                    'movie_id',
                    'writer',
                ],
            )
            self.regions_saver = Saver(
                filename=REGIONS_FILENAME,
                fieldnames=[
                    'movie_id',
                    'region',
                ],
            )
            self.actors_saver = Saver(
                filename=ACTORS_FILENAME,
                fieldnames=[
                    'movie_id',
                    'actor',
                ],
            )

    def add_task(self, name, data, priority=0):
        self.data.tasks.append((name, data, priority))

    async def save_data(self):
        print('开始保存配置')
        await self.worker.execute_until_finished()
        with open(DATA_FILENAME, 'wb') as datafile:
            pickle.dump(self.data, datafile)

        self.movies_saver.save()
        self.cates_saver.save()
        self.langs_saver.save()
        self.directors_saver.save()
        self.writers_saver.save()
        self.regions_saver.save()
        self.actors_saver.save()
        print('保存配置完成')

    async def stop(self):
        print('终止程序中')
        self.running = False

    async def run(self):
        async def process(name, data, priority, task):
            try:
                return await task
            except Exception as e:
                import traceback

                traceback.print_exc()
                print(data)
                print(type(e))
                print(e)
                # import traceback

                # traceback.print_exc()
                self.add_task(name, data, priority)

        self.running = True

        while self.running:
            self.data.tasks.sort(key=lambda x: x[2], reverse=True)

            while len(self.worker) < 1 and len(self.data.tasks) > 0:
                name, data, priority = self.data.tasks.pop(0)
                handler = self.handlers.get(name)
                if handler:
                    self.worker.add_future(
                        process(name, data, priority, handler(data).process()),
                        priority,
                    )
                else:
                    raise Exception(name)
            print('task_amount:', len(self.data.tasks))
            print('finded_urls:', len(self.data.finded_urls))
            print('finded_movie_ids:', len(self.data.finded_movie_ids))

            await self.worker.execute(max_task_amount=100)

            if time.time() - self.last_time > 600:
                # 每分钟保存一次数据
                await self.save_data()

            time.sleep(2)

        await self.save_data()
        print('程序终止成功')

    async def get_response(self, url):
        headers = {'User-Agent': random.choice(AGENTS)}
        # if len(self.proxies) < 100:
        #     self.get_proxies()

        # item = random.choice(self.proxies)
        # proxy = {
        #     "http://": "http://%s:%s" % (item['ip'], item['port']),
        #     "https://": "http://%s:%s" % (item['ip'], item['port']),
        # }
        # proxy = {
        #     "http://": "http://%s" % (item),
        #     "https://": "http://%s" % (item),
        # }
        # proxy = {
        #     "all://": "http://%s:%s" % (item['ip'], item['port']),
        # }
        proxy = {
            "all://": "http://%s:%s" % ('127.0.0.1', '8787'),
        }

        def remove_proxy(item):
            if item in self.proxies:
                self.proxies.remove(item)

        # async with httpx.AsyncClient(proxies=proxy) as client:
        async with httpx.AsyncClient(proxies=proxy) as client:
            try:
                response = await client.get(url, headers=headers)
                if len(response.text) < 500:
                    raise Exception('数据太少')
            except Exception as e:
                import traceback

                traceback.print_exc()
                print(e)
                print(type(e))
                print(proxy)
                print('remove proxy')
                remove_proxy(item)
                raise e
            else:
                print(response.status_code)
                if response.status_code != 200:
                    print('remove proxy')
                    remove_proxy(item)
                    raise Exception('代理出错')
                return response

    # def handle_movies(self, movie_id, title, year, score, comment_amount, comment):
    #     self.movies_cache.append(
    #         (movie_id, title, year, score, comment_amount, comment)
    #     )
    #     print('handle_movies')
    #     if len(self.movies_cache) >= 10:
    #         self.save_movies()

    # def save_movies(self):
    #     if not os.path.exists('movies.csv'):
    #         with open(
    #             'movies.csv', 'a', newline='', encoding='utf-8-sig'
    #         ) as comment_file:
    #             fieldnames = [
    #                 'movie_id',
    #                 'movie_name',
    #                 'year',
    #                 'score',
    #                 'score_count',
    #                 'short_count',
    #                 'comment_count',
    #                 '讨论数',
    #                 '片长',
    #                 '简介',
    #             ]
    #             writer = csv.DictWriter(comment_file, fieldnames=fieldnames)
    #             writer.writeheader()

    #     with open(
    #         'comments.csv', 'a', newline='', encoding='utf-8-sig'
    #     ) as comment_file:
    #         writer = csv.writer(comment_file)
    #         writer.writerows(self.movies_cache)
    #     self.movies_cache = []

    def register_handler(self, name, handler):
        self.handlers[name] = handler

    def get_proxies(self):
        # 代理
        response = httpx.get(
            'http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=3bf9909f7534493cbc53a8749051abb1&count=5&expiryDate=0&format=1&newLine=2'
        )

        if response.json()['code'] == '0':
            # 提取成功
            self.proxies += response.json()['msg']
            print(self.proxies)


class Saver:
    def __init__(self, filename, fieldnames, cache_size=100):
        self.filename = filename
        self.fieldnames = fieldnames
        self.cache_size = cache_size
        self.cache = []

    def add(self, **kwargs):
        self.cache.append(kwargs)
        if len(self.cache) > self.cache_size:
            self.save()

    def save(self):
        if not os.path.exists(self.filename):
            with open(
                self.filename, mode='w', newline='', encoding='utf-8-sig'
            ) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()

        with open(self.filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writerows(self.cache)
        self.cache = []


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
            if url not in Manager().data.finded_urls:
                Manager().data.finded_urls.append(url)
                Manager().add_task('page_process', url)

        movie_pattern = r'https://movie.douban.com/subject/(.*?)/'
        result = re.findall(movie_pattern, text)

        for movie_id in result:
            if movie_id not in Manager().data.finded_movie_ids:
                Manager().data.finded_movie_ids.append(movie_id)
                Manager().add_task('movie_finder', movie_id, priority=2)

        return text


class MovieFinder:
    def __init__(self, id):
        self.id = id
        self.url = 'https://movie.douban.com/subject/%s/' % id

    async def process(self):
        page_text = await PageProcess(self.url).process()
        soup = BeautifulSoup(page_text, features='lxml')

        'movie_id',
        'movie_name',
        'length',
        'year',
        'score',
        'score_count',
        'intro',
        'actor_count',
        'short_count',
        'topic_count',
        'comment_count',
        'discuss_count',
        'question_count',

        # 电影名
        result = soup.find(name='span', attrs={"property": "v:itemreviewed"})
        movie_name = result.text

        # 年份
        result = soup.find(name='span', attrs={"class": "year"})
        year = result.text[1:-1]

        # 电影长度
        result = soup.find(name='span', attrs={"property": "v:runtime"})
        if result:
            length = result.attrs['content']
        else:
            length = ''

        # 评分
        result = soup.find(name='strong', attrs={"property": "v:average"})
        if result:
            score = result.text
        else:
            score = ''

        # 评分人数
        result = soup.find(name='span', attrs={"property": "v:votes"})
        if result:
            score_count = result.text
        else:
            score_count = 0

        # 简介
        result = soup.find(name='span', attrs={"property": "v:summary"})
        intro = result.text.replace(' ', '').replace('\n', '')

        # 想看
        result = re.search(r'([0-9]*?)人想看', page_text)
        if result:
            want_count = result.group(1)
        else:
            want_count = 0

        # 看过
        result = re.search(r'([0-9]*?)人看过', page_text)
        if result:
            watched_count = result.group(1)
        else:
            watched_count = 0

        # 演员数
        result = soup.find(name='a', href=re.compile("/subject/.*?/celebrities"))
        if result:
            actor_count = result.text[3:]
        else:
            actor_count = 0

        # 短评数
        result = re.search(
            r'<a href="https://movie.douban.com/subject/.*?/comments\?status=.">全部 (.*?) 条</a>',
            page_text,
        )
        short_count = result.group(1)

        # 影评数
        result = soup.find(name='a', href='reviews')
        comment_count = result.text[3:-2]

        # 讨论数
        result = re.search(r'去这部影片的讨论区（全部(.*?)条）', page_text)
        if result:
            discuss_count = result.group(1)
        else:
            discuss_count = 0

        # 问题数
        result = re.search(r'全部(.*?)个问题', page_text)
        if not result:
            question_count = 0
        else:
            question_count = result.group(1)

        # 以下为一对多的

        # 类型
        result = soup.find_all(name='span', attrs={'property': 'v:genre'})
        for element in result:
            Manager().cates_saver.add(movie_id=self.id, cate=element.text)

        # 语言
        result = re.search(r'<span class="pl">语言:</span>(.*?)<br/>', page_text)
        if result:
            for lang in result.group(1).replace(' ', '').split('/'):
                Manager().langs_saver.add(movie_id=self.id, lang=lang)

        # 导演
        result = soup.find_all(name='a', attrs={'rel': 'v:directedBy'})
        if result:
            for element in result:
                Manager().directors_saver.add(movie_id=self.id, director=element.text)

        # 编剧
        result = soup.find(name='span', text='编剧')
        if result:
            for element in result.parent.find_all(name='a'):
                Manager().writers_saver.add(movie_id=self.id, writer=element.text)

        # 地区
        result = re.search(r'<span class="pl">制片国家/地区:</span>(.*?)<br/>', page_text)
        if result:
            for region in result.group(1).replace(' ', '').split('/'):
                Manager().regions_saver.add(movie_id=self.id, region=region)

        # 主演
        result = soup.find_all(name='a', attrs={'rel': 'v:starring'})
        if result:
            for element in result:
                Manager().actors_saver.add(movie_id=self.id, actor=element.text)

        Manager().movies_saver.add(
            movie_id=self.id,
            movie_name=movie_name,
            length=length,
            year=year,
            score=score,
            score_count=score_count,
            intro=intro,
            want_count=want_count,
            watched_count=watched_count,
            actor_count=actor_count,
            short_count=short_count,
            comment_count=comment_count,
            discuss_count=discuss_count,
            question_count=question_count,
        )


async def main():
    import signal

    manager = Manager()

    manager.register_handler('page_process', PageProcess)
    manager.register_handler('movie_finder', MovieFinder)

    def stop(signum, frame):
        asyncio.gather(manager.stop())

    signal.signal(signal.SIGTERM, stop)  # kill pid
    signal.signal(signal.SIGINT, stop)  # ctrl -c

    await manager.run()


asyncio.log.logger.setLevel(logging.ERROR)
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
