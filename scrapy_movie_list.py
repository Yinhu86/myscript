#!/usr/bin/env python
#-*-coding:utf8 -*-

#import pymysql # (windows)
import MySQLdb
import requests
import random
import time
import re
import bs4
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class scrapy_dytt(object):
    #初始化2个列表
    def __init__(self):
        self.index_list = []
        self.info_list = []
     
    #抓取网页信息
    def get_html(self,url):
        #准备要使用的浏览器头信息
        headers_list =  [{ 'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'},
                { 'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
                { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'},
                { 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)'},
                { 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)'},
                { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}]
        try:
            html_page = requests.get(url,headers=random.choice(headers_list))
            if html_page.status_code == 200:
                #获取html编码
                page_coding = html_page.apparent_encoding
                #转换编码
                if "gb" or "iso" in page_coding.lower():
                    hcontent = unicode(html_page.content,'gb2312','ignore')
                    html_content = hcontent.encode('utf8')
                else:
                    html_content = html_page.content
                return html_content
        except Exception,err:
            pass
    
    #抓取索引页中电影标题和详细页信息
    def search_url(self,html_content):
        self.index_list = []
        root_url = "http://www.ygdy8.net"
        try:
            soup = BeautifulSoup(html_content,'html.parser',from_encoding='utf8')
            urls = soup.find_all('a',class_='ulink')
            for url in urls:
                full_url = root_url + url['href']
                self.index_list.append((url.text, full_url))
        except Exception,err:
            print html_content
            print err
    
    #抓取详细页中所需各个字段信息
    def get_detail_info(self,html_content,index_url):
        list_tmp = []
#        print index_url[1]
        #抓取所需信息,因为网页关于信息的格式有多种，因此根据情况判断使用不同的抓取方法
        try:
            soup = BeautifulSoup(html_content,'html.parser',from_encoding='utf8')
        except Exception,err:
            print html_content
            print err
        print "len ",len(soup.find_all('div', id='Zoom'))    
        if len(soup.find_all('div', id='Zoom')) > 0:   
            movie_info = soup.find_all('div', id='Zoom')[0].find('span')
            if isinstance(movie_info,bs4.element.Tag):
#               print "In span"
                if isinstance(movie_info.find('div',id='read_tpc'),bs4.element.Tag):
#                    print "In span-read_tpc"
                    movie_info = movie_info.find('div',id='read_tpc')
                elif isinstance(movie_info.find('p'),bs4.element.Tag):
#                    print "In span-p"
                    if isinstance(movie_info.find('p').find('span'),bs4.element.Tag):
#                        print "In span-p-span"
                        movie_info = movie_info.find('p').find('span')
                    elif isinstance(movie_info.find('p').find('font'),bs4.element.Tag) and len(movie_info.find('p').find('font').text) > 300:
#                        print "IN span-p-font"
                        movie_info = movie_info.find('p').find('font')
                    else:
#                        print "Is span-p"
                        movie_info = movie_info.find('p')
                elif isinstance(movie_info.find('span'),bs4.element.Tag):
#                    print "In span-span"
                    movie_info = movie_info.find('span')
                elif isinstance(movie_info.find('font'),bs4.element.Tag):
#                    print "In span-font"
                    movie_info = movie_info.find('font')
                else:
                    print "Maybe blank page ",index_url[1]
                    return "Blank info"
        else:
            return "404" 
         
            #抓取下载链接
        try:
            download_link = re.search(r'>(ftp://.*.[mp4,rmvb,mkv])',html_content).group().strip('>')
        except Exception,err:
            pass
        #判断movie_info.contents是否为空，如果为空使用text方法获取文本 
        if isinstance(movie_info.contents,type(None)): 
#            print "In movie_info.text"
            list_tmp = movie_info.text.split(u'\u25ce')            
#            print list_tmp
        else:
            #抓取的p段落，包含很多空行，使用的换行</br>，为无用信息，为了剔除，使用循环判断该内容是否包含字符串，将过滤后的内容加入到新的列表
            if len(movie_info.contents) > 5:
#                print "In movie_info.contents"
                for i in movie_info.contents:
                    if isinstance(i,bs4.element.NavigableString):
                        list_tmp.append(i)

        try:
            
            if len(list_tmp) != 0:
                name1 = "null"
                name2 = "null"
                Movie_time = "null"
                Movie_state = "null"
                Movie_type = "null"
                Movie_mins = "null"
                Movie_name = "null" 
                #分别提取所需的各个字段信息
                #因为此处获取的信息是Unicode编码，如 '片 名' 之间的空白不是空格，是一个字符Unicode编码 \u3000，以空白为分隔符，将字符串序列化，提取最后一个列，即使所需信息
                for element in list_tmp[:20]:
                    if u'译' in element and u'名' in element and len(element):
                        name1 = element.split(u'\u3000')[-1].encode('utf8')
                        continue
                    if u'片' in element and u'名' in element and len(element):
                        name2 = element.split(u'\u3000')[-1].encode('utf8')
                        continue
                    if u'年' in element and u'代' in element:
                        Movie_time = element.split(u'\u3000')[-1].encode('utf8')
                        continue
                    if u'国' in element and u'家' in element and len(element) <20:
                        Movie_state = element.split(u'\u3000')[-1].encode('utf8')
                        continue
                    if u'类' in  element and  u'别' in  element:
                        Movie_type = element.split(u'\u3000')[-1].encode('utf8')
                        continue
                    if u'片' in element and u'长' in element:
                        Movie_mins = element.split(u'\u3000')[-1].encode('utf8')
                        continue
                Movie_name = name1 + "/" + name2
                self.info_list.append((Movie_name,Movie_time,Movie_state,Movie_type,Movie_mins,download_link,index_url[1]))
        except  Exception,err:
            print err
            
    #循环遍历索引页中获取的详细页，并使用self.get_detail_info抓取所需信息
    def detail_info(self):
        self.info_list = []
        for pageurl in self.index_list:
            content = self.get_html(pageurl[1])
            if isinstance(type(content),type(None)):
                print "get html error"
                print pageurl[1]
                time.sleep(3)
                content = self.get_html(pageurl[1])
                self.get_detail_info(content,pageurl)
            else:
                self.get_detail_info(content,pageurl)

    #初始化数据库的表    
    def create_db_tables(self):
        conn = MySQLdb.connect(host = "192.168.210.165", user = "root",passwd = "password",db = "movie_info",charset = "utf8")    
        cursor = conn.cursor()
    
        cursor.execute('DROP TABLE IF EXISTS movies_info')
        cursor.execute('DROP TABLE IF EXISTS movies_overview')    

        create_table1 = """CREATE TABLE `movies_info` (
                        `id` int(10) NOT NULL AUTO_INCREMENT,
                        `movie_name` varchar(120) DEFAULT NULL,
                        `movie_time` varchar(20) DEFAULT NULL,
                        `movie_state` varchar(20) DEFAULT NULL,
                        `movie_type` varchar(20) DEFAULT NULL,
                        `movie_mins` varchar(30) DEFAULT NULL,
                        `download_link` varchar(110) DEFAULT NULL,
                        `movie_index_url` varchar(110) DEFAULT NULL,
                        PRIMARY KEY (`id`)
                        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8
                        """
        cursor.execute(create_table1) 

        create_table2 = """CREATE TABLE `movies_overview` (
                        `id` int(10) NOT NULL AUTO_INCREMENT,
                        `movie_title` varchar(50) DEFAULT NULL,
                        `movie_index_url` varchar(100) DEFAULT NULL,
                        PRIMARY KEY (`id`)
                        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8
                        """
        cursor.execute(create_table2)
            
        conn.commit()
        cursor.close()
        conn.close()        

    def save_detail_info(self,values):
        #创建mysql连接
        conn = MySQLdb.connect(host = "192.168.210.165", user = "root",passwd = "password",db = "movie_info",charset = "utf8")
        #创建游标
        cursor = conn.cursor()
    
        #插入数据
        cursor.executemany("insert into movies_info (movie_name,movie_time,movie_state,movie_type,movie_mins,download_link,movie_index_url) values(%s,%s,%s,%s,%s,%s,%s)",values)
        #提交完成
        conn.commit()
        print "insert detail OK!"
        cursor.close()
        conn.close()
        
    def save_info(self,values):
        #创建mysql连接
        conn = MySQLdb.connect(host = "192.168.210.165", user = "root",passwd = "password",db = "movie_info",charset = "utf8")
        #创建游标1
        cursor = conn.cursor()
    
        #插入数据
        cursor.executemany("insert into movies_overview (movie_title,movie_index_url) values(%s,%s)",values)
        #提交完成
        conn.commit()
        print "insert overview OK!"
        cursor.close()
        conn.close()

    #获取此分类下所有页面的总页数  
    def pagenum(self):
        url = "http://www.ygdy8.net/html/gndy/dyzz/index.html"
        html = self.get_html(url)
        soup = BeautifulSoup(html,'html.parser',from_encoding='utf8')
        num_text = soup.find_all('div',class_="x")
        num = int(num_text[1].text[-5:-1])
        return num
 
if __name__ == '__main__':
    dianying = scrapy_dytt()
    page_num = dianying.pagenum()
    dianying.create_db_tables()
    for num in range(1,page_num+1):
        url = "http://www.ygdy8.net/html/gndy/dyzz/list_23_"+ str(num) + ".html"
        html = dianying.get_html(url)
        dianying.search_url(html)
        time.sleep(1)
        print url
        dianying.save_info(dianying.index_list)
        dianying.detail_info()
        dianying.save_detail_info(dianying.info_list)    



