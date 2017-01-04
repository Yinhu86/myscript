#!/usr/bin/env python
#-*- coding:utf-8 -*-
#抓取汽车之家图片 2017.01.04

import requests
import random
import contextlib
import os
import re
import time
import multiprocessing
from bs4 import BeautifulSoup


def get_html(url):
    headers_list =  [{ 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)'},
            { 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)'}]
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

def get_url_list(html_text,class_str,urlist):
    soup = BeautifulSoup(html_text,'html.parser',from_encoding='utf8')
    urls_info = soup.find_all('a',class_=class_str)
    for url_info in urls_info:
        urlist.append([url_info['href'],url_info.text])

def get_url(page_text,label,attr=[]):
    #根据所给标签内容截取html内容
    soup = BeautifulSoup(page_text,'html.parser',from_encoding='utf8')
    if 'id' in attr:
        url_info = soup.find_all(label,id=attr[1])
    elif 'class' in attr:
        url_info = soup.find_all(label,class_=attr[1])
    else:
        url_info = re.findall(label,page_text)
    return url_info

def download_img(img_url):
    #截取url的之后15个字符作为图片的名字
    jpg_name = img_url[-15:]
    
    headers_list =  [{ 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)'},
                     { 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)'}]
    #以二进制流的方式下载图片，自动关闭二进制流
    with contextlib.closing(requests.get(img_url,headers=random.choice(headers_list),stream=True,timeout=10)) as resp:
        with open(jpg_name,'wb') as fj:
            for chunk in resp.iter_content(1024):
                fj.write(chunk)


def geturl_to_next(next_url,img_list,pid):
    end = True
    time.sleep(0.5)
    #获取下载页内容
    page_text = get_html(next_url)
    img_url = get_url(page_text,'img',['id','img'])[0]['src']
    
    re_s = r'nexturl.*(/photo.*.html)'
    next_url = rooturl + get_url(page_text,re_s)[0]
    if len(img_list) < 10:
#    if next_url in  img_list:
        #添加图片url到set()
        img_list.add(img_url)
    else:
        print "PID %s The end,download over!" %pid
        end = False
    return next_url,end

def getall_img_url(page_text,pid):
    time.sleep(0.5)
    img_lists = set()
    try:
        res = True
	#提取图片url
        img_list = get_url(page_text,'img',['id','img'])
        img_url = img_list[0]['src']
	#提取下一页html链接
        re_s = r'nexturl.*(/photo.*.html)'       
        next_url = rooturl + get_url(page_text,re_s)[0]
	img_lists.add(img_url)
	#迭代方式获取同一主题下的所有图片链接
        while res:
            next_url,res = geturl_to_next(next_url,img_lists,pid)
        return img_lists
    except Exception,err:
        #异常时无法正常返回上层目录，此处添加返回
        os.chdir('..')
        print "except err: ",err     
    
def download_main(u_lists,root_dir):
    #获取子进程pid,调试使用
#    pid = os.getpid()
#    print '\033[1;31m',
#    print "PID %s start download main..." %pid
#    print u_lists 
#    print '\033[0m', 
    #获取主题首页信息
    subpage_text = get_html(u_lists[0])
    subpage_title = u_lists[1]
    subpage_title = subpage_title.encode('utf-8').replace(' ','_')
    #根据主题创建目录，并将图片下载到目录中
    if os.path.isdir(subpage_title) and os.getcwd() == root_dir:
        os.chdir(subpage_title)
    else:
        os.chdir(root_dir)
        os.system('mkdir %s' %subpage_title)
        os.chdir(subpage_title)
    img_list = getall_img_url(subpage_text,pid)
    #开始下载图片
    while len(img_list) > 0:
        download_img(img_list.pop())
    
    os.chdir(root_dir)
#    print '\033[1;34m',
#    print "***PID %s : download ok,return dir***" %pid
#    print '\033[0m', 

        
if __name__ == '__main__':
    #初始化索引主页列表
    stime = time.time()
    index_lists = []
    root_dir = os.getcwd()
    rooturl = "http://car.autohome.com.cn"
    #起始页
    url = "http://car.autohome.com.cn/jingxuan/list-2.html#pvareaid=104097"
#    url = "http://car.autohome.com.cn/jingxuan/list-13.html#pvareaid=104098"

    #获取索引页内容
    start_html_text = get_html(url)

    #提取每个主题页的url
    get_url_list(start_html_text,'pictxt',index_lists)
    
    #创建进程池
    process_pool = multiprocessing.Pool(2)
    for index_list in index_lists:
#        download_main(index_list,root_dir)
        process_pool.apply_async(download_main,(index_list,root_dir))

    process_pool.close()
    process_pool.join()
    #计算用时
    etime = time.time()
    use_time = etime - stime
    print "Use time %sm %ss" %(int(use_time)/60,int(use_time)%60)

