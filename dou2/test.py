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

import random
import requests
import re

proxy = {
    "all://": "http://%s:%s" % ('127.0.0.1', '8787'),
}

proxies = {
    'http': "http://%s:%s" % ('127.0.0.1', '8787'),
    'https': "http://%s:%s" % ('127.0.0.1', '8787'),
}

headers = {'User-Agent': random.choice(agents)}
response = requests.get(
    'https://movie.douban.com/subject/26746801/', headers=headers, proxies=proxies
)
page_text = response.text

# pattern = r'<span property="v:itemreviewed">(.*?)</span>'
# result = re.search(pattern, response.text)

# print(result)

from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, features='lxml')

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
intro = result.text

'want_count',
'watched_count',

# 想看
result = re.search(r'([0-9]*?)人想看', page_text)
want_count = result.group(1)

# 看过
result = re.search(r'([0-9]*?)人看过', page_text)
watched_count = result.group(1)

# 演员数
result = soup.find(name='a', href=re.compile("/subject/.*?/celebrities"))
actor_count = result.text[3:]

# 短评数
result = soup.find(
    name='a',
    href=re.compile(r"https://movie.douban.com/subject/.*?/comments\?status=P"),
)
short_count = result.text[3:-2]

# 影评数
result = soup.find(name='a', href='reviews')
comment_count = result.text[3:-2]

# 讨论数
result = re.search(r'去这部影片的讨论区（全部(.*?)条）', page_text)
discuss_count = result.group(1)

# 问题数
result = re.search(r'全部(.*?)个问题', page_text)
if not result:
    question_count = 0
else:
    question_count = result.group(1)

abc = dict(
    movie_name=movie_name,
    length=length,
    year=year,
    score=score,
    score_count=score_count,
    # intro=intro,
    want_count=want_count,
    watched_count=watched_count,
    actor_count=actor_count,
    short_count=short_count,
    comment_count=comment_count,
    discuss_count=discuss_count,
    question_count=question_count,
)

from pprint import pprint

pprint(abc)
