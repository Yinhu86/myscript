
#-*-coding:utf8 -*-
#windows 下使用
#linux 下应导入import MySQLdb 
import pymysql
import requests
import random
import time
from bs4 import BeautifulSoup

def get_html(url):
    headers_list =  [{ 'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'},
            { 'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
            { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'},
            { 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)'},
            { 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)'},
            { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}]
    try:
        #添加代理项proxies={'http':"127.0.0.1:8087"}，本地使用的XX-net代理工具
        html_page = requests.get(url,proxies={'http':"127.0.0.1:8087"},headers=random.choice(headers_list))
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

def search_url(html_content,urls_list):
#    root_url = "http://www.tecmint.com/"
    try:
        soup = BeautifulSoup(html_content,'html.parser',from_encoding='utf8')
        urls = soup.find_all('a',rel="bookmark")
#        print urls
        #获取链接和描述
        for url in urls:
            m_name = url.text
            m_link = url['href']
            #去除重复内容
            if [m_name,m_link] not in urls_list:
                urls_list.append([m_name,m_link])
    except Exception,err:
        pass


def save_info(urls_list):
    #创建mysql连接
    conn = pymysql.connect(host = "192.168.210.165", user = "root",passwd = "password",db = "info_db",charset = "utf8")
    #创建游标
    cursor = conn.cursor()
    #检查表是否存在，存在删除
    cursor.execute('DROP TABLE IF EXISTS tecmint_list')
    #创建表,url创建索引去重
    create_table = """CREATE TABLE `tecmint_list` (
                    `id` int(10) NOT NULL AUTO_INCREMENT,
                    `describe_info` varchar(100) DEFAULT NULL,
                    `url` varchar(100) DEFAULT NULL,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `url` (`url`)
                    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8
                    """
    cursor.execute(create_table)

    #插入命令
    insert_sql = "insert into tecmint_list (describe_info,url) values(%s,%s)"
    #插入数据
    cursor.executemany(insert_sql,urls_list)
    #提交完成
    conn.commit()
    print "insert OK!"
    cursor.close()
    conn.close()

if __name__ == '__main__':
    urls_list = []
    for num in range(1,124):
        url = "http://www.tecmint.com/page/" + str(num) + "/"
        html = get_html(url)
        url_data = search_url(html,urls_list)
#        time.sleep(2)
        print url
    save_info(urls_list)
