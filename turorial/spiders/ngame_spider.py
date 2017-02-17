# -*- coding: utf-8 -*-
import scrapy
import codecs
from twisted.enterprise import adbapi
from datetime import datetime
from hashlib import md5
import MySQLdb
import MySQLdb.cursors
from turorial.ngame_items import NgameItem
from turorial.ngame_detail_items import DetailItem
from scrapy.utils.project import get_project_settings
from scrapy.http import Request
import re
from hashlib import md5
import time
from turorial.DB import DB

class NgameSpider(scrapy.Spider, object):
    name = "ngame"
    allowed_domains = ["9game.cn"]
    start_urls = []
    settings = get_project_settings()
    # mysql config
    host=settings['MYSQL_HOST']
    db=settings['MYSQL_DBNAME']
    user=settings['MYSQL_USER']
    passwd=settings['MYSQL_PASSWD']
    cursorclass = MySQLdb.cursors.DictCursor
    # end of mysql config
    # 九游source_id
    ngame_source_id = 1
    # 正则，匹配发布时间
    time_re = re.compile(r'20\d{2}-\d+-\d+\s\d{2}:\d{2}:\d{2}')
    # ua
    #user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2612.0 Safari/537.36"
    # url dict
    url_dict = {}
    # url前缀
    url_prefix = "http://www.9game.cn"

    def __init__(self):
        self.logger.info(time.strftime('%Y-%m-%d %X', time.localtime()) + ":ngame crawl running................")
	self.init_start_urls()

    def init_start_urls(self):
        db = DB()
	sql = "select * from mt_news_rule where 1=1 and is_delete=0 and status=1 and  source_id=%d" % (self.ngame_source_id)
	try:
	    results = db.select(sql)
	    if not results:
		self.logger.warn("WARNING:not crawl url setting")
	    #print results
	    for ret in results:
		# append start_urls
		self.url_dict[md5(ret['fetch_url']).hexdigest()] = ret
		self.start_urls.append(ret['fetch_url'])
        except:
	    self.logger.error("db error, sql:%s", sql)	

	db.close()
    #异常处理
    def _handle_error(failue, item):
        print 'insert failed................'
        log.msg(failue)

    def start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def make_requests_from_url(self, url):
        return scrapy.Request(url)

    def parse(self, response):
	items = []
	db = DB()
        news_url = self.url_dict[md5(response.url).hexdigest()]
	self.logger.info("请求地址是：%s", news_url['fetch_url'])
        # 重复次数，超过3次，退出当前循环
        dup_times = 0 
        for sel in response.xpath('//ul/li/div/p[@class="tit"]'):
            self.logger.info( "dup_times: " + str(dup_times))
            # 超过三次 退出
            if dup_times > 10:
                break
 
            item = NgameItem()
            # from db
            item['rule_id'] = news_url['id']
	    item['type_id'] = news_url['type_id']
            
	    title = sel.xpath('a/text()').extract()
            link = sel.xpath('a/@href').extract()
            item['title'] = title[0].encode('utf-8')
            
            detail_url = link[0].encode('utf-8')
	    if detail_url.find('http') < 0:
                detail_url = self.url_prefix + detail_url

            urlmd5 = md5(detail_url).hexdigest()
            if self._exist_url(db, urlmd5):
                self.logger.info("url[%s] exist" % detail_url)
                dup_times += 1
                continue 

	    item['link'] = detail_url
            # 调用详情页
            item['desc'] = sel.xpath('text()').extract()[0]

            item = Request(detail_url, meta={'item':item}, callback=self.parse_detail)
	    items.append(item)

        # 关闭数据库连接
        db.close()
	return items
	

    def parse_detail(self, response):
	print 'parse_detail running..........................'
	item = response.meta['item']
	summary = response.xpath('//p[@class="summary"]/text()').extract()[0]
	publish_time = self.get_publish_time(summary)
	item['publish_time'] = publish_time	
        #item['content'] = response.xpath('//div[@class="text-con"]/text()').extract()
	yield item
 
    # 判断url是否已经存在数据库
    def _exist_url(self, db, urlmd5):  
        sql = "select * from mt_news where url_code='%s' limit 1" % urlmd5
        results = db.select(sql)
        if results:
            return True
        else:
            return False 	
    # 获取资讯发布时间
    def get_publish_time(self, summary):
	time_str = re.findall(self.time_re, summary)
        publish_time = ""
        if time_str:
	    publish_time = time_str[0]
        return publish_time
