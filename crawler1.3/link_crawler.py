#-*- coding=utf-8 -*-
import re
import urlparse
import time
import urllib2
import datetime
import robotparser
from downloader import Downloader

def normalize(seed_url,link):
    #格式URl链接
    link,_=urlparse.urldefrag(link)
    return urlparse.urljoin(seed_url,link)

def same_domain(url1,url2):
    #返回True 如果两个url属于同一个域
    return urlparse.urlparse(url1).netloc==urlparse.urlparse(url2).netloc

def get_robots(url):
    #从这个网域中获取网址的robots
    rp=robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url,'/robots.txt'))
    rp.read()
    return rp

def get_links(html):
    #返回一个html 里面的链接
    webpage_regex=re.compile('<a[^>]+href=["\'](.*?)["\']',re.IGNORECASE)
    return webpage_regex.findall(html)

def link_crawler(seed_url,link_regex=None,delay=5,max_depth=1,max_urls=-1,user_agent='wswp',proxies=None,num_retries=1,scrape_callback=None,cache=None):
    #爬去 链接网址种子，紧跟的链接后面有link_regex
    crawl_queue=[seed_url]
    seen={seed_url:0}
    num_urls=0
    rp=get_robots(seed_url)
    #D=Downloader(delay=delay,user_agent=user_agent,proxies=proxies,num_retries=num_retries,cache=cache)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)

    while crawl_queue:
        url=crawl_queue.pop()
        depth=seen[url]
        if rp.can_fetch(user_agent,url):
            html=D(url)
            links=[]
            if scrape_callback:
                links.extend(scrape_callback(url,html)or[])
            if depth!=max_depth:
                if link_regex:
                    links.extend(link for link in get_links(html)if re.match(link_regex,link))

                for link in links:
                    link=normalize(seed_url,link)
                    if link not in seen:
                        seen[link]=depth+1
                        if same_domain(seed_url,link):
                            crawl_queue.append(link)
            num_urls+=1
            if num_urls==max_urls:
                break
        else:
            print 'Block by robots.txt',url




if __name__=='__main__':
    link_crawler('http://example.webscraping.com','/(index|view)',delay=0,num_retries=2,max_depth=1,user_agent='GoodCrawler')
