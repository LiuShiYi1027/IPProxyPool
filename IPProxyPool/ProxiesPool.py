# -*- coding:utf-8 -*-

import requests
import random
from bs4 import BeautifulSoup
import sqlite3
import time


########################################################################
class ProxiesPool:
    """
    IP代理池
    """
    # test
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        # >>>>>>>>>>>数据库相关<<<<<<<<<<<<<
        self.conn = sqlite3.connect('IPPool') # 连接这个数据库,假如不存在会自动创建
        self.cursor = self.conn.cursor()
        self.cursor.execute("""create table if not exists IPList(ip varchar(40) not null primary key,
            port varchar(10) not null,
            address varchar(20) not null,
            type varchar(10) not null,
            livetime varchar(10) not null,
            prooftime varchar(30) not null)""")    
        # >>>>>>>>>>>获取代理相关<<<<<<<<<<<<<
        self.check_url = 'http://ip.chinaz.com/getip.aspx' # 检验url
        self.proxy_url = 'http://www.xicidaili.com/wt/'
        self.proxies_urlList = []
        self.headers_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
           ]
    
    def request(self, url):
        '''
        请求网页函数
        :param url: 请求链接
        :return: 请求响应
        '''
        UA = random.choice(self.headers_list)
        headers = {'User-Agent':UA}
        response = requests.get(url, headers=headers)

        if 200 <= response.status_code < 400:
            return response
        else:
            return None
        
    def get_proxies(self, page=10):
        '''
        获得代理
        :param page:获得代理的页数，默认为10
        :return: None
        '''
        self.proxies_urlList = [self.proxy_url + str(i) for i in range(1, int(page) + 1)] # 存储所要抓取的链接
        
        for url in self.proxies_urlList:
            print(url)
            response = self.request(url)
            print(response.status_code)
            soup = BeautifulSoup(response.text, 'lxml')

            tr_list = soup.find_all('tr')

            for i in range(1, len(tr_list)):
                tr = tr_list[i]
                ip = tr.find_all('td')[1].get_text()
                port = tr.find_all('td')[2].get_text()
                address = tr.find_all('td')[3].get_text().replace('\n','')
                type = tr.find_all('td')[5].get_text()
                livetime = tr.find_all('td')[8].get_text()
                prooftime = tr.find_all('td')[9].get_text()
                
                proxy = {str(type).lower() : 'http://' + str(ip + ':' + port)}                
                print('发现了一个代理，正在检测其可用性...')

                # 检测爬取到的代理的可用性
                if self.check_proxy(proxy):
                    print(proxy,'可用!，插入数据库。')
                    self.push_proxy(ip, port, address, type, livetime, prooftime)
                else:
                    print(proxy,'不可用，丢弃。')

            time.sleep(5) #  睡眠5s，防止被检测
            
    def check_proxy(self,proxy):
        '''
        检查代理的可用性
        '''        
        try:
            response = requests.get(self.check_url, proxies=proxy, timeout=5)
            if 200 <= response.status_code < 300:
                return True
            else:
                return False
        except:
            return False
    
    def push_proxy(self, ip, port, address, type, liveTime, proofTime):
        '''
        向数据库中插入一个IP
        :param ip:ip地址
        :param port:端口号
        :param address:ip来源地
        :param type:IP类型(HTTP or HTTPS)
        :param liveTime:生存时间
        :param proofTime:验证时间
        :return:None
        '''
        try:
            self.cursor.execute('insert into IPList(ip, port, address, type, livetime, prooftime) values("%s","%s","%s","%s","%s","%s")' %
                                (ip, port, address, type, liveTime, proofTime))
            self.conn.commit()
        except:
            self.conn.rollback()

    def find_all_proxies(self):
        '''
        查询数据库中的所有IP
        :return: list形式(数据库中的所有IP)
        '''
        self.cursor.execute('select * from IPList')
        values = self.cursor.fetchall()
        return values

    def find_one_proxy(self, ip):
        '''
        查询数据库中是否存在某个ip
        :param ip:
        :return: 查询到的IP的具体的信息
        '''
        self.cursor.execute("select * from IPList where ip = '%s'" % ip)
        value = self.cursor.fetchone()
        return value

    def delete_one_proxy(self, ip):
        '''
        删除某个指定的proxy
        :param ip:
        :return:
        '''
        try:
            self.cursor.execute("delete from IPList where ip = '%s'" % ip)
            self.conn.commit()
        except:
            self.conn.rollback()
            
    def check_all_proexies(self):
        '''
        检查数据库中全部代理的可用性
        '''
        proxyList = self.find_all_proxies()
        
        for proxy in proxyList: 
            ip = proxy[0]
            proxy = self.change_proxy(proxy)            
            if self.check_proxy(proxy):
                print(proxy,'可用。')
            else:
                self.delete_one_proxy(ip)
                print(proxy,'不可用，已将其删除！')
                
    def change_proxy(self,proxy):
        '''
        修改代理的格式(内部用，外部调用无意义)
        '''
        ip = proxy[0]
        port = proxy[1]
        proxyType = proxy[3].lower() 
        proxy = {proxyType:'http://' + ip + ':' + port}        
        return proxy        
        
        
    def find_valued_proxy(self):
        '''
        查找一个可用的代理
        '''
        proxyList = self.find_all_proxies()
        proxy = random.choice(proxyList)
        proxy = self.change_proxy(proxy)
        if self.check_proxy(proxy):
            return proxy
        else:
            self.find_valued_proxy()
        
    
