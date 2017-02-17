# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class NgameItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    rule_id = scrapy.Field()
    type_id = scrapy.Field()
