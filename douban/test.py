# import httpx
# import asyncio


# async def main():
#     async with httpx.AsyncClient() as client:
#         response = await client.get('https://www.example.com/')
#         print(response)


# asyncio.run(main())


# class Manager:
#     # abc = False

#     def __new__(cls, *args, **kwargs):
#         # return '213123'
#         if not hasattr(cls, '_instance'):
#             # with cls._instance_lock:
#             if not hasattr(cls, '_instance'):
#                 cls._instance = super().__new__(cls)
#         return cls._instance

# def __init__(self):
#     print(self.abc)
#     self.abc = True
#     print('wfwefwef')


# Manager()
# Manager()
# Manager()
# Manager()

# agents = [
#     "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
#     "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
#     "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0);",
#     "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
#     "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
#     "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
#     "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
#     "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
#     "Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
# ]

# import random
# import requests
# import re

# headers = {'User-Agent': random.choice(agents)}
# response = requests.get(
#     'https://movie.douban.com/subject/35096844/?from=showing', headers=headers
# )

# url_pattern = r'<span property="v:itemreviewed">(.*?)</span>'
# result = re.search(url_pattern, response.text)

# url_pattern = r'<span class="year">\((.*?)\)</span>'
# result = re.search(url_pattern, response.text)


# url_pattern = r'<span class="pl">\( <a href="reviews">全部 (.*?) 条</a> \)</span>'
# result = re.search(url_pattern, response.text)

# response = requests.get(
#     'https://movie.douban.com/subject/26671361/reviews', headers=headers
# )

# url_pattern = r'https://movie.douban.com/review/([0-9]*?)/'
# result = re.findall(url_pattern, response.text)


# response = requests.get('https://movie.douban.com/review/8015528/', headers=headers)

# # url_pattern = r'<div class="review-content clearfix"(?:.|\n)*?(<p>((.|\n)*?)</p>.*?)*(?:.|\n)*?</div>'
# # result = re.search(url_pattern, response.text)

# from bs4 import BeautifulSoup

# soup = BeautifulSoup(response.text)

# abc = soup.find(name='div', attrs={"class": "review-content"})
# abc = abc.find_all(name='p')

# content = ''.join([a.text for a in abc])

# import ipdb

# ipdb.set_trace()

# import csv

# with open('comments.csv', 'r', newline='', encoding='utf-8-sig') as f:
#     reader = csv.reader(f)
#     for row in reader:
#         print(row[1])


# import httpx
# import asyncio


# async def main():
#     async with httpx.AsyncClient() as client:
#         r = await client.get('https://www.baidu.com')
#     print(r)


# asyncio.run(main())

import signal


def stop(signum, frame):
    print(213213123)


signal.signal(signal.SIGTERM, stop)  # kill pid
signal.signal(signal.SIGINT, stop)  # ctrl -c


while True:
    import time

    print('sfwww')
    time.sleep(1)