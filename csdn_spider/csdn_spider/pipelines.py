# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


def call_func(module, func_name, item=None):
    if hasattr(module, func_name):
        if item is None:
            return getattr(module, func_name)()
        else:
            return getattr(module, func_name)(item)


class FirstPipeline(object):

    def process_item(self, item, spider):
        return call_func(spider, "process_first", item)

    def close_spider(self, spider):
        call_func(spider, "close_first")


class SecondPipeline(object):

    def process_item(self, item, spider):
        return call_func(spider, "process_second", item)

    def close_spider(self, spider):
        call_func(spider, "close_second")


class ThirdPipeline(object):

    def process_item(self, item, spider):
        return call_func(spider, "process_third", item)

    def close_spider(self, spider):
        call_func(spider, "close_third")
