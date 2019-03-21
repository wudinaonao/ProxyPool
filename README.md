# ProxyPool
## 技术架构

  后端: Python + spring boot
  
  前端: Vue + bootstarp + iView
  
  这个仓库目前只有Python项目, 即代理的搜集以及检测和录入数据库
  
## 使用说明
  Config文件夹里为各项配置
  + DataBase 文件里配置数据库的相关参数
  + GeneralConfig 日志文件记录等级, 以及日志路径等在这里配置
  
  ### Spider文件夹存放爬虫文件
  每个Py文件对应一个爬虫,  目前一共有6个爬虫, 分别爬取6个网站的公开免费代理
  + https://cn-proxy.com/
  + https://free-proxy-list.net/
  + https://hidemyna.me/en/proxy-list/
  + https://www.kuaidaili.com/
  + https://www.proxy-list.download/
  + https://www.xicidaili.com/nn/
  
  可以自己另外增加爬虫, 然后放入Spider文件夹即可
  ### 编写自己的爬虫
  爬虫需要实现ISpider接口, 位于Interface包.
  需要实现的方法为:
  ```
  start                 方法用于启动爬虫, 并写入结果到数据库, 可调用GeneralTool.writeToDatabase方法
  _getHtml              方法用于获取网页的HTML源码
  _getProxyResultList   方法用于获取代理结果, 为一个列表
  ```
  _getProxyResultList 返回结果应为
  ```
  [{}, {}, .....]
  # example
  [
    {
      "ip":"8.8.8.8", 
      "port": "8848", 
      "type":"HTTPS", 
      "location":"USA", 
      "speed":"0.3s", 
      "lastUpdateTime":"2019-0.-21 21:21:21", 
      "md5":"123456789123456789123456789ASDFG", 
      "weight": "0"
    }
  ]
  ```
  每个字典包含键: ip, port, type, location, speed, lastUpdateTime, md5, weight
  
  speed, lastUpdateTime, weight 因为尚未验证, 所以可以给任意值
  
  ### 数据库表结构
  目前共两张表, UnVerified, Verified
  
  UnVerified 表(Verified表相同):
  ```
  CREATE TABLE `UnVerified` (
  `id` bigint(10) NOT NULL AUTO_INCREMENT,
  `ip` varchar(15) NOT NULL,
  `port` varchar(5) NOT NULL,
  `type` varchar(5) CHARACTER SET utf8mb4 NOT NULL,
  `location` varchar(30) CHARACTER SET utf8mb4 NOT NULL,
  `speed` varchar(10) CHARACTER SET utf8mb4 NOT NULL,
  `lastUpdateTime` varchar(30) CHARACTER SET utf8mb4 NOT NULL,
  `md5` char(32) NOT NULL,
  `weight` bigint(10) NOT NULL,
  PRIMARY KEY (`id`,`md5`),
  UNIQUE KEY `md5` (`md5`)
  ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
  ```
  
  下课了, 准备去吃点东西, 回来再写...
  
  
