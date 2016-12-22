#!/usr/bin/env python
#-*- coding:utf-8 -*-

import requests
import re
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header

def get_IP(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'}
    req = requests.get(url,headers=headers)
    html = req.content
    ip = re.search(r'\d+.\d+.\d+.\d+',html).group()
    return ip

def sendmail(wan_ip):
    mail_host = "smtp.163.com"
    mail_user = "send@163.com"
    mail_pass = "password"

    subject = "外网地址变更"
    sender = "send@163.com"
    receiver = "receive@163.com"
    info = {"from":"<send@163.com>","to":"<receive@163.com>"}
    
    message = MIMEText('IP now is ' + wan_ip,'plain','utf-8')

    message['from'] = info["from"]
    message['to'] = info["to"]
    message['Subject'] = Header(subject,'utf-8')

    try:
        smtpobj = smtplib.SMTP()
        smtpobj.connect(mail_host,25)
        smtpobj.login(mail_user,mail_pass)
        smtpobj.sendmail(sender,receiver,message.as_string())
        print "发送成功"
        smtpobj.quit()
    except smtplib.SMTPException,e:
        print e[0],e[1]
        print "发送失败"
        smtpobj.quit()



def savetofile(ip):
    check = True
    if os.path.isfile("ip.txt"):
       pass
    else:
       os.system('touch ip.txt')

    with open('ip.txt','rb+') as f:
        if ip not in f:
           check = False   
    if not check:  
        with open('ip.txt','wb+') as f2:
            f2.write(ip)
        print "Sendmail ..."
        sendmail(ip)

if __name__ == "__main__":
    '''测试自动获取拨号上网的外网IP,并发送邮件'''
    url = "http://ip.cn/"
    wanIP = get_IP(url)
    print wanIP
    savetofile(wanIP)

