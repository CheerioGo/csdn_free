# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UserSpiderItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()

    def to_doc(self):
        doc = {
            'id': self['id'],
            'name': self['name'],
            'state': 0,
            'zero': 0,
        }
        return doc


class ZeroSpiderItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    type = scrapy.Field()
    date = scrapy.Field()
    tags = scrapy.Field()
    brief = scrapy.Field()

    def to_doc(self):
        doc = {
            'id': self['id'],
            'title': self['title'],
            'type': self['type'],
            'tags': self['tags'],
            'brief': self['brief'],
            'date': self['date'],
            'url': self['url'],
            'state': 0,
        }
        return doc
