#!/usr/bin/env python
#-*- coding:utf8 -*-
#测试可用的代理IP
__author__ = 'LYH'

import requests
import lxml
import re
from bs4 import BeautifulSoup
import random
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

class agentIP(object):
    def __init__(self):
        #添加headers信息
        self.headers_list =  [{ 'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'},
            { 'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
            { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'},
            { 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)'},
            { 'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)'},
            { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}]

    def getagentIP(self,agent_web):
        IP_list = []
        agent_html = requests.get(agent_web,headers=random.choice(self.headers_list)).content
        soup = BeautifulSoup(agent_html,'html.parser',from_encoding='utf8')
        info_list = soup.find_all('tr')
        for ip_info in info_list:
            classfiy = ip_info.find_all('td',class_='country')
            if len(classfiy) > 1 and  classfiy[1].text == u'高匿':
                cont = ip_info.find_all('td')
                agentip = cont[1].text + ":" +cont[2].text
                IP_list.append(agentip)
        return IP_list

    def request_url(self,test_url,proxy_ip):
        #测试代理IP是否能正常使用
        print "Test url %s " %test_url
        #获取网站的部分字符串用于测试，获取的页面是否正常
        res = re.findall(r'http[s]?://\w+.(\w+.[cn,com,org]*)',test_url)[0]
        try:
            req = requests.get(test_url,proxies={'http':proxy_ip},headers=random.choice(self.headers_list),timeout=3)
            if req.status_code == 200:
                if res in req.content:
                    return True
        except Exception,err:
            print err
            return False

    def checkagentIP(self,IP_list):
        #2个测试网站都通过则代理IP正常
        curl = "http://cn.bing.com"
        curl2 = "http://httpbin.org"
        verificationIP = []
        for iport in IP_list:
            if self.request_url(curl,iport) and self.request_url(curl2,iport):
                verificationIP.append(iport)
        return verificationIP

if __name__ == '__main__':
    #代理IP网站
    proxy_web = ["http://www.xicidaili.com/wn","http://www.xicidaili.com/nn"]
    getIP = agentIP()
    enableIP = []
    for web in proxy_web:
        IP_list = getIP.getagentIP(web)
        eIP = getIP.checkagentIP(IP_list)
        enableIP = enableIP + eIP
    with open('agentIP.txt','ab+') as f:
        for ip in enableIP:
            print ip
            f.write(ip + '\n')








