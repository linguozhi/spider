# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DetailItem(scrapy.Item):
    publish_time = scrapy.Field()
    content = scrapy.Field()
