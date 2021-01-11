import requests
import random
import re

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


finded_urls = []
finded_movie_ids = []

url_queue = []
movie_queue = []

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
    def __init__(self):
        pass

    def runing(self):
        while True:
            if len(url_queue) > 0:
                url = url_queue.pop()
                webf = WebFinder(url)
                webf.process()
            
            if len(movie_queue) > 0:
                movie_id = movie_queue.pop()
                movie = MoveFinder(movie_id)
                movie.process()

                webf = WebFinder('https://movie.douban.com/subject/%s/' % movie_id)
                webf.process()


class WebFinder:
    def __init__(self, url):
        self.url = url

    def process(self):
        self.response = requests.get(self.url, headers=headers)
        self.soup = BeautifulSoup(response.text, 'lxml')
        pattern = r'https://movie.douban.com/subject/(.*?)/'
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                urls.append()

                result = re.search(pattern, href)
                if result:
                    movie_ids.append(result.group(1))


class MoveFinder:
    def __init__(self, id):
        self.id = id
        self.url = 'https://movie.douban.com/subject/%s/' % id

    def process(self):
        self.response = requests.get(self.url, headers=headers)
        self.soup = BeautifulSoup(response.text, 'lxml')
        pattern = r'https://movie.douban.com/subject/(.*?)/'
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                urls.append()

                result = re.search(pattern, href)
                if result:
                    movie_ids.append(result.group(1))


manager = Manager()

manager.runing()