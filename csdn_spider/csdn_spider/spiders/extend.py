# -*- coding: utf-8 -*-
from csdn_spider.items import *
from scrapy.exceptions import DropItem
from csdn_spider import db
from csdn_spider import tools


class ExtendSpider(scrapy.Spider):
    name = "extend"
    allowed_domains = ["csdn.net"]
    start_urls = ['https://download.csdn.net/download/qq_37025561/10658429']

    # static
    max_req_count = 100

    # new
    printer = tools.Printer()
    req_count = 0
    fail_count = 0
    user_hit_count = 0
    zero_hit_count = 0
    user_duplicate_count = 0
    zero_duplicate_count = 0
    crawl_count = 0

    # slutroulettelive

    def parse(self, response):
        self.crawl_count += 1
        self.req_count -= 1
        cards = response.xpath('//dl[@class="detail_list clearfix"]')
        for card in cards:
            url = tools.list0(card.xpath('dd/a/@href').extract())
            user_id = tools.between(url, 'download.csdn.net/download/', '/')
            # cost = tools.list0(card.xpath('dd//em[@class="cost"]/text()').extract()).strip()
            if not db.user_exist(user_id):
                doc = {
                    'id': user_id,
                    'name': None,
                    'state': 0,
                    'zero': 0,
                }
                if db.user_insert(doc):
                    self.user_hit_count += 1
                else:
                    self.user_duplicate_count += 1

            continue
            if cost == '0':
                _id = tools.tail(url, '/')
                if not db.zero_exist(_id):
                    _type = tools.rbetween(tools.list0(card.xpath('dt/a/img/@src').extract()), '/', '.')
                    title = tools.list0(card.xpath('dd/a/text()').extract()).strip()
                    brief = tools.list0(card.xpath('dd/p/a/text()').extract()).strip()
                    date = tools.list0(card.xpath('dd//em[@class="upl_time"]/text()').extract()).strip()
                    tags = ' '.join(card.xpath('dd//label[@class="tags"]//a/text()').extract())
                    doc = {
                        'id': _id,
                        'title': title,
                        'type': _type,
                        'tags': tags,
                        'brief': brief,
                        'date': date,
                        'url': url,
                        'state': 0,
                    }
                    if db.zero_insert(doc):
                        self.zero_hit_count += 1
                    else:
                        self.zero_duplicate_count += 1

        tree_branch = 2
        while self.req_count < self.max_req_count and tree_branch > 0:
            url = db.zero_get_state_url()
            if url is None:
                break

            self.req_count += 1
            tree_branch -= 1
            yield scrapy.Request(url, callback=self.parse, errback=self.error_back)

        self.print_status()

    def print_status(self):
        tags = ['Crawl', 'UHit', 'UTotal', 'ZHit', 'Fail', 'ZDup', 'UDup']
        vals = [self.crawl_count, self.user_hit_count, db.user_count(), self.zero_hit_count, self.fail_count,
                self.zero_duplicate_count, self.user_duplicate_count]
        self.printer.print(tags, vals)

    def error_back(self, failure):
        self.req_count -= 1
        self.fail_count += 1
        self.print_status()
