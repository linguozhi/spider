import scrapy

class MySpider(scrapy.Spider):

    name = 'myspider'
    start_urls = ['http://scrapinghub.com']

    def parse(self, response):
	print 'xxxxxxxxxxxxxxxxxxxxxxx'
        self.logger.info('Parse function called on %s', response.url)
