# IPProxyPool
爬虫代理池

## V1
### 项目依赖
- 安装sqlite3数据库
- 安装requests请求包
- 安装BeatifullSoup HTML/XML文档解析包
### 综述
代理池从西刺代理网站 http://www.xicidaili.com/nn/ 获取国内高匿代理，利用 http://ip.chinaz.com/getip.aspx 检测代理的有效性。
### 主要方法介绍
1. __init__()

- 代理池的构造方法。
- 连接IPPool数据库，假如数据库不存在会自动创建
- 初始化属性

2. request(url)

- 网页请求函数

3. get_proxies(page=10)

- 获得代理，默认获取10页代理

4. check_proxy(proxy)

- 检查代理的可用性

5. push_proxy(ip, port, address, type, liveTime, proofTime)

- 将代理的详细信息插入数据库

6. find_all_proxies()

- 获取数据库中的全部代理

7.find_one_proxy(ip)

- 获取一个指定的代理

8. delete_one_proxy(ip)

- 删除一个指定的代理

9. check_all_proexies()

- 检查数据库中全部代理的可用性

10. find_valued_proxy

- 获取一个可用代理 
