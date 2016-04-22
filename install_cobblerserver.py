#!/usr/bin/env python
#Author: Yinhu
#Date: 2016-4-22
#Notice:Support Centos 6 and 7

import re
import urllib2
import subprocess
import os

url = "http://mirrors.aliyun.com"

def check_network():
    ping_res = subprocess.call("ping -c 2 mirrors.aliyun.com",shell=True,stdout=open('/dev/null','w'))
    return ping_res

def version_check():
    version_str = 'cat /etc/redhat-release|egrep -o "([6,7]).[^ ]"|cut -d"." -f1'
    version = os.popen(version_str).read().strip('\n')
    return version

def check_epel():
    epel_res = subprocess.call('rpm -qa|grep epel',shell=True,stdout=open('/dev/null','w'))
    return epel_res

def check_cobbler():
    cobbler_res = subprocess.call('rpm -qa|grep cobbler',shell=True,stdout=open('/dev/null','w'))
    return cobbler_res

def disable_selinux():
    print "Selinux is enable,service will be wrong!"
    i_res = raw_input("Disable selinux now ?(Y/N): ")
    if i_res in ['Y','y']:
        subprocess.call('setenforce 0',shell=True)
        subprocess.call("sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config",shell=True)
        print "Ok,selinux deploy done "
    else:
        print "Ok,do it youerself"
          
def start_server(cmd):
    vc = version_check()
    if vc == '7':
        if cmd == 'start':
            service_cmd = "systemctl restart cobblerd httpd rsyncd dnsmasq xinetd"
        elif cmd == 'autostart':
            service_cmd = "systemctl enable cobblerd httpd rsyncd dnsmasq xinetd"
        subprocess.call(service_cmd,shell=True)
    elif vc == '6':
        for server_name in ['cobblerd','httpd','rsyncd','dnsmasq','xinetd']:
            if cmd == 'start':
                service_cmd = "service " + server_name + " restart"
                print service_cmd
            elif cmd == 'autostart':
                service_cmd = "chkconfig " + server_name +" on"
            subprocess.call(service_cmd,shell=True)

def install_epel_release(url):
    vc = version_check()
    if vc == '7':
        url_epel = url + "/epel/7/x86_64/e/"
    elif vc == '6':
        url_epel = url + "/epel/6Server/x86_64/"
    str_epel = r'>(epel-release.*.rpm)'
    html = urllib2.urlopen(url_epel).read()
    rpm_name = re.findall(str_epel,html)[0]
    url_rpm = url_epel + rpm_name
    
    d_epel_release = "wget " + url_rpm
    i_epel_release = "rpm -ivh " + rpm_name
    wget_check = subprocess.call('rpm -qa|grep wget',shell=True,stdout=open('/dev/null','w'))
    if wget_check != 0:
        subprocess.call('yum install wget -y',shell=True,stdout=open('/dev/null','w'))
    subprocess.call(d_epel_release,shell=True,stdout=open('/dev/null','w'))
    subprocess.call(i_epel_release,shell=True,stdout=open('/dev/null','w'))
    
    subprocess.call("sed -i 's@#baseurl=http://download.fedoraproject.org/pub/@baseurl=http://mirrors.aliyun.com/@g' /etc/yum.repos.d/epel.repo",shell=True)
    subprocess.call("sed -i 's@mirrorlist@#mirrorlist@g' /etc/yum.repos.d/epel.repo",shell=True)
    subprocess.call('rm -f epel-release*.rpm',shell=True) 

def install_cobblerserver():
    yum_p = "yum install cobbler cobbler-web httpd pykickstart xinetd dnsmasq rsync -y"
    subprocess.call(yum_p,shell=True,stdout=open('/dev/null','w'))
    selinux_res = subprocess.call("sestatus|grep enabled",shell=True,stdout=open('/dev/null','w'))

    if selinux_res != 0:
        start_server('start')
    else:
        disable_selinux()
        start_server('start')
    start_server('autostart')
    
def config_cobbler():
    local_ip = 'ip addr|grep -v "127.0.0.1"|egrep -o "inet [1-9].*[$/]"|grep -o "[0-9].*.[0-9]"'
    dns_ip = "cat /etc/resolv.conf |grep nameserver|head -1|awk '{print  $2}'"
    hostip = os.popen(local_ip).read().strip('\n')
    dnsip = os.popen(dns_ip).read().strip('\n')
    ip_setting = "sed -i " + "'270,390s/127.0.0.1/" + hostip + "/g'" + " /etc/cobbler/settings"
    dns_setting = "sed -i " + "'250,260s/127.0.0.1/" + dnsip + "/g'" + " /etc/cobbler/settings"
    subprocess.call("sed -i '13,$s/yes/no/g' /etc/xinetd.d/tftp",shell=True)
    subprocess.call(ip_setting,shell=True) 
    subprocess.call(dns_setting,shell=True)
    subprocess.call("sed -i 's/#ServerName www.example.com:80/ServerName 127.0.0.1:80/g' /etc/httpd/conf/httpd.conf",shell=True) 
    subprocess.call("sed -i 's/= manage_isc/ = manage_dnsmasq/g;s/= manage_bind/= manage_dnsmasq/' /etc/cobbler/modules.conf",shell=True)
    subprocess.call("sed -i 's/manage_dhcp: 0/manage_dhcp: 1/g;s/manage_dns: 0/manage_dns: 1/g' /etc/cobbler/settings",shell=True)
    start_server('start')
    subprocess.call("cobbler sync",shell=True,stdout=open('/dev/null','w'))    

if __name__ == "__main__":
    ce = check_epel()
    cn = check_network()
    cc = check_cobbler()
    print "Please waiting ..."
    if cn == 0:
        if ce == 0:
            print "epel installd"
        else:
            print "will install epel"
            install_epel_release(url)
        if cc != 0:
            install_cobblerserver()
        else:
            print "Cobbler server installd !"
    else:
        print "Please check network or DNS"
    print "Install done ! "
    print "Config cobbler ..."
    config_cobbler()
    print "All done !"
    print "Please modify dhcp pool in /etc/cobbler/dnsmasq.template,and execute 'cobbler sync' ,reboot cobblerd,dnamsq service"
