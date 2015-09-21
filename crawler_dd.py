# -*- encoding: utf-8 -*-

'''
crawler for diandian.com
liyan30 @ 2015-08-26 16:48
'''

import os
import os.path
import sys
import re
import threading
import urllib2
import time
from bs4 import BeautifulSoup

dd_url_pattern = 'http://%s.diandian.com/page/%d'

class SystemCommandError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SystemHelper(object):
    def __init__(self, writer=sys.stderr):
        self.rlock = threading.RLock()
        self.writer = writer

    def __del__(self):
        self.writer.close()

    def get_tms(self):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return time_str

    def dump_out(self, outstr):
        self.rlock.acquire()
        self.writer.write(outstr)
        self.rlock.release()

    def notice(self, notice_str):
        self.dump_out('[System Notice: %s] %s\n' % (self.get_tms(), notice_str))

    def warp(self, command, need_assert=True):
        self.dump_out('[System Warpper: %s] %s\n' % (self.get_tms(), command))
        if os.system(command) != 0:
            if need_assert:
                raise SystemCommandError('Run system command [%s] failed' % (command, ))

    def popen(self, command):
        self.dump_out('[System Popener: %s] %s\n' % (self.get_tms(), command))
        return os.popen(command).read().strip()

class CrawlerDD(object):
    def __init__(self, blog_name):
        self.blog_name = blog_name
        self.url_pattern = dd_url_pattern

        self.sh = SystemHelper()
        self.article_cnt = 1
        self.index_content = ""

    def open_page(self, page_url):
        # print page_url
        retry_time = 10
        for i in xrange(retry_time):
            try:
                content = urllib2.urlopen(page_url).read()
                self.sh.notice('Open url [%s] success.' % (page_url, ))
                return content
            except:
                import traceback
                traceback.print_exc()
                self.sh.notice('Open url [%s] error. Retry opening page for %d times.' % (page_url, i + 1))
                continue

        self.sh.notice('Open url [%s] failed after %d trial.' % (page_url, retry_time))
        return None

    def create_parent_folder(self):
        self.parent_folder_name = './%s_auto-down' % (self.blog_name, )
        if not os.path.exists(self.parent_folder_name):
            os.makedirs(self.parent_folder_name)

    def create_index_page(self):
        title = '<h2>Blog <a href=%s>%s</a> (Auto downloaded)</h2>\n' % (self.url_pattern % (self.blog_name, 1), self.blog_name)
        file_name = '%s/index.html' % (self.parent_folder_name, )
        f = open(file_name, 'w+')
        f.write(title)
        f.write('<ul class="edui-filter-disc">\n')
        f.write(self.index_content.encode('gbk', 'ignore'))
        f.write('</ul>\n')
        f.close()

    def crawl(self):
        self.create_parent_folder()

        page_id = 1
        while True:
            url = self.url_pattern % (self.blog_name, page_id)

            retry_time = 1
            failed = False
            while True:
                content = self.open_page(url)
                # print content
                if not content or ('<article' not in content):
                    retry_time += 1
                    if retry_time < 10:
                        continue
                    failed = True
                    self.sh.notice('Max page=%d for %s.' % (page_id - 1, self.blog_name))
                break

            if failed: break

            self.process_main_page(content)
            page_id += 1

        self.create_index_page()

    def process_main_page(self, content):
        soup = BeautifulSoup(content)
        for link in soup.find_all('article'):
            article_name = link.a.string
            article_link = link.a.get('href')
            # print article_name, article_link
            self.process_article(article_name, article_link)

    def add_to_index_page(self, file_name, article_name):
        self.index_content += '<li><a href=%s>%s</a></li>\n' % (file_name, article_name)

    def process_article(self, article_name, article_link):
        file_name = "%s/article_%03d.html" % (self.parent_folder_name, self.article_cnt, )
        self.add_to_index_page('./article_%03d.html' % (self.article_cnt, ), article_name)
        self.article_cnt += 1

        retry_time = 1

        while True:
            content = self.open_page(article_link)
            soup = BeautifulSoup(content)

            article_content = soup.article
            try:
                f = open(file_name, 'w+') 
                f.write('<h3>Original Link: <a href=%s>%s</a></h3>\n' % (article_link, article_link))
                f.write(article_content.prettify().encode('gbk', 'ignore'))
                f.close()
                break
            except:
                retry_time += 1
                if retry_time >= 10:
                    import traceback
                    error_str = traceback.format_exc().replace('\n', '</p>\n<p>')
                    f = open(file_name, 'w+') 
                    f.write('<h2>Downloaded ERROR!</h2>\n')
                    f.write('<p>%s</p>' % (error_str, ))
                    f.write('<p>Please check <a href=%s>%s</a></p>\n' % (article_link, article_link))
                    f.close()
                    break

def main():
    crawler = CrawlerDD('sky2sea')
    crawler.crawl()

if __name__ == '__main__':
    main()
