#-*- coding=utf-8 -*-
import re
import urllib.parse
import urllib
import urllib.request
import urllib.error
import time
from datetime import datetime
from imp import reload
import urllib.robotparser
import queue
from bs4 import BeautifulSoup
import sys
reload(sys)
import  csv
import lxml.html
import  cssselect
FIELDS=('area','population','iso','country','capital',
                     'continent','tld','currency_code','currency_name','phone','postal_code_format',
                     'postal_code_regex','language','neighbours')
class ScrapeCallback:
    def __int__(self):
        self.writer=csv.writer(open('countries.csv','w'))
        self.fields=('area','population','iso','country','capital',
                     'continent','tld','currency_code','currency_name','phone','postal_code_format',
                     'postal_code_regex','language','neighbours')
        self.writer.writerrow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/',html):
            tree = lxml.html.fromstring(html)
            row=[tree.cssselect('table > tr#places_%s__row >td.w2p_fw'%field)[0].text_content() for field in FIELDS]
            print (url,row)
            '''
            row=[]
            fields = ('area', 'population', 'iso', 'country', 'capital',
                      'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format',
                      'postal_code_regex', 'language', 'neighbours')
            for field in fields:
                row.append(tree.cssselect('table > tr#places_{}__row >td.w2p_fw'.format(field))[0].text_content())

            self.writer.writerrow(row)
            '''

def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='wswp',
                 proxy=None, num_retries=1,scrape_callback=None):
    crawl_queue = queue.deque([seed_url])
    seen = {seed_url: 0}
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    throttle = Throttle(delay)
    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent

    while crawl_queue:
        url = crawl_queue.pop()
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url, headers, proxy=proxy, num_retries=num_retries)
            links = []
            if scrape_callback:
                links.extend(scrape_callback.__call__(url, html) or [])

            depth = seen[url]
            if depth != max_depth:
                # can still crawl further
                if link_regex:
                    # filter for links matching our regular expression
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))

                for link in links:
                    link = normalize(seed_url, link)
                    # check whether already crawled this link
                    if link not in seen:
                        seen[link] = depth + 1
                        # check link is within same domain
                        if same_domain(seed_url, link):
                            # success! add this new link to queue
                            crawl_queue.append(link)

            # check whether have reached downloaded maximum
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print ('Blocked by robots.txt:', url)


class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """

    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}

    def wait(self, url):
        domain = urllib.parse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()


num_All=1

def download(url, headers, proxy, num_retries, data=None):
    print ('Downloading:', url)
    request = urllib.request.Request(url, data, headers)
    opener = urllib.request.build_opener()
    if proxy:
        proxy_params = {urllib.parse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib.request.ProxyHandler(proxy_params))
    try:
        response = opener.open(request)
        html = response.read().decode('utf-8')
        #解析html 文件的内容
        soup=BeautifulSoup(html,'html.parser')
        '''
        u1=soup.title.string
        print u1
        '''
        global  num_All
        ij=num_All
        file_object = open('D:/python/'+str(ij)+'.txt', 'w',encoding='utf-8')
        file_object.write(soup.get_text())
        file_object.close()
        num_All+=1
        code = response.code
    except urllib.error.URLError as e:
        print ('Download error:', e.reason)
        html = ''
        if hasattr(e, 'code'):
            code = e.code
            if num_retries > 0 and 500 <= code < 600:
                # retry 5XX HTTP errors
                return download(url, headers, proxy, num_retries - 1, data)
        else:
            code = None
    return html


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urllib.parse.urldefrag(link)  # remove hash to avoid duplicates
    return urllib.parse.urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urllib.parse.urlparse(url1).netloc == urllib.parse.urlparse(url2).netloc


def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urllib.parse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


def get_links(html):
    """Return a list of links from html
    """
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    return webpage_regex.findall(html)


if __name__ == '__main__':
    #link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com/', '/(index|view)', delay=0, num_retries=1, max_depth=-1,user_agent='GoodCrawler',scrape_callback=ScrapeCallback())
    #link_crawler('http://weibo.com/u/5249921593','/5249921593', delay=0, num_retries=1, max_depth=-1,user_agent='Baiduspider')
    #link_crawler('https://www.zhihu.com/question', '/(question)?', delay=0, num_retries=1, max_depth=-1, user_agent='Baiduspider')
