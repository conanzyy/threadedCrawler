import time
import threading
import urllib.parse
from downloader import  Downloader

SLEEP_TIME=1

def normalize(seed_url,link):
    link,_=urllib.parse.urldefrag(link)
    return urllib.parse.urljoin(seed_url,link)


def thread_crawler(seed_url,delay=5,cache=None,links=None,user_agent='wswp',proxies=None,num_retries=1,max_threads=10,timeout=60):
    crawl_queue=[seed_url]
    seen=set([seed_url])
    D=Downloader(cache=cache,delay=delay,user_agent=user_agent,proxies=proxies,num_retries=num_retries,timeout=timeout)


    def process_queue():
        while True:
            try:
                url=crawl_queue.pop()
            except IndexError:
                break;
            else:
                html=D(url)
                if links:
                    try:
                        links=links
                    except Exception as e:
                        print ('Error in callback for:{}:{}'.format(url,e))
                    else:
                        for link in links:
                            link=normalize(seed_url,link)

                            if link not in seen:
                                seen.add(link)

                                crawl_queue.append(link)
    threads=[]
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) <max_threads and crawl_queue:
            thread=threading.Thread(target=process_queue)
            thread.setDaemon(True) # set daemon so main thread can exit when receive ctrl + C
            thread.start()
            threads.append(thread)
        time.sleep(SLEEP_TIME)

if __name__ == '__main__':
    #link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    thread_crawler('http://example.webscraping.com/')
    #link_crawler('http://weibo.com/u/5249921593','/5249921593', delay=0, num_retries=1, max_depth=-1,user_agent='Baiduspider')
    #link_crawler('https://www.zhihu.com/question', '/(question)?', delay=0, num_retries=1, max_depth=-1, user_agent='Baiduspider')
