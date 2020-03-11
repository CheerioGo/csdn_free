# -*- coding: utf-8 -*-
from csdn_spider.items import *
from scrapy.exceptions import DropItem
from csdn_spider import db
from csdn_spider import tools


class UserSpider(scrapy.Spider):
    name = "user"
    allowed_domains = ["csdn.net"]
    start_urls = ['https://me.csdn.net/follow/qq_41185868']

    # static
    max_req_count = 100

    # new
    printer = tools.Printer()
    ids_seen = set()
    req_count = 0
    drop_count = 0
    fail_count = 0
    hit_count = 0
    duplicate_count = 0
    crawl_count = 0

    # slutroulettelive

    def parse(self, response):
        follows = response.xpath('//p[@class="user_name"]/a[@class="fans"]')
        domain1 = 'https://me.csdn.net/follow'
        domain2 = 'https://me.csdn.net/fans'

        self.crawl_count += 1
        self.req_count -= 1

        for follow in follows:
            item = UserSpiderItem()
            item['id'] = tools.tail(tools.list0(follow.xpath('@href').extract()), '/')
            item['name'] = tools.list0(follow.xpath('text()').extract()).strip()
            yield item

        tree_branch = 2
        while self.req_count < self.max_req_count and tree_branch > 0:
            user_id = db.user_get_state_id()
            if user_id is None:
                break
            _url = f'{domain1}/{user_id}'
            self.req_count += 1
            tree_branch -= 1
            yield scrapy.Request(_url, callback=self.parse, errback=self.error_back)

            _url = f'{domain2}/{user_id}'
            self.req_count += 1
            tree_branch -= 1
            yield scrapy.Request(_url, callback=self.parse, errback=self.error_back)

        self.print_status()

    def process_first(self, item):
        if item['id'] in self.ids_seen:
            self.drop_count += 1
            raise DropItem("Duplicate item found: %s" % item['id'])
        else:
            self.ids_seen.add(item['id'])
            return item

    def process_second(self, item):
        if not db.user_exist(item['id']):
            success = db.user_insert(item.to_doc())
            if success:
                self.hit_count += 1
            else:
                self.duplicate_count += 1

    def close_second(self):
        print(f'catch: {len(self.ids_seen)}, drop: {self.drop_count}')

    def print_status(self):
        tags = ['Crawl', 'Hit', 'Miss', 'Total', 'Duplicate', 'Fail']
        vals = [self.crawl_count, self.hit_count, self.drop_count, db.user_count(), self.duplicate_count, self.fail_count]
        self.printer.print(tags, vals)

    def error_back(self, failure):
        self.req_count -= 1
        self.fail_count += 1
        self.print_status()
