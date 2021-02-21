import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 蘑菇代理的隧道订单
appKey = "bUpHU21ydDNRemY4SXc4bzo3bVB3VDdhMm9wWHROY0xv"

# 蘑菇隧道代理服务器地址
ip_port = 'secondtransfer.moguproxy.com:9001'

proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
headers = {
    "Proxy-Authorization": 'Basic ' + appKey,
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
}
r = requests.get(
    "https://api.ip.sb/ip",
    headers=headers,
    proxies=proxy,
    verify=False,
    allow_redirects=False,
)
print(r.status_code)
print(r.content)
if r.status_code == 302 or r.status_code == 301:
    loc = r.headers['Location']
    print(loc)
    url_f = loc
    r = requests.get(
        url_f, headers=headers, proxies=proxy, verify=False, allow_redirects=False
    )
    print(r.status_code)
    print(r.text)