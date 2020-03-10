# -*- coding: utf-8 -*-
from csdn_spider.items import *
from scrapy.exceptions import DropItem
from csdn_spider import db
from csdn_spider import tools


class ZeroSpider(scrapy.Spider):
    name = "zero"
    allowed_domains = ["csdn.net"]
    start_urls = ['https://download.csdn.net/user/zzia615/uploads']

    # static
    max_req_count = 100

    # new
    printer = tools.Printer()
    ids_seen = set()
    req_count = 0
    drop_count = 0
    hit_count = 0
    crawl_count = 0
    fail_count = 0

    # slutroulettelive

    def parse(self, response):
        cards = response.xpath('//div[@class="card clearfix"]')
        domain = 'https://download.csdn.net'

        self.crawl_count += 1
        self.req_count -= 1

        for card in cards:
            score = tools.between(tools.list0(card.xpath('div[@class="content"]/div[@class="score"]').extract()),
                                  '</label>', '</div>').strip()
            if score != '0':
                continue

            _id = tools.tail(tools.list0(card.xpath('div[@class="img"]/a/@href').extract()), '/')
            url = domain + tools.list0(card.xpath('div[@class="img"]/a/@href').extract(), '_error')
            type = tools.rbetween(tools.list0(card.xpath('div[@class="img"]//img/@src').extract()), '/', '.')
            title = tools.list0(card.xpath('div[@class="content"]/h3/a/text()').extract()).strip()
            brief = tools.list0(card.xpath('div[@class="content"]/p[@class="brief"]/text()').extract()).strip()
            tags = tools.list0(
                card.xpath('div[@class="content"]//p[@class="tags clearfix"]/a/text()').extract()).strip()
            date = tools.between(tools.list0(card.xpath('div[@class="content"]//div[@class="date"]').extract()),
                                 '</label>', '</div>').strip()

            item = ZeroSpiderItem()
            item['id'] = _id
            item['title'] = title
            item['type'] = type
            item['tags'] = tags
            item['brief'] = brief
            item['date'] = date
            item['url'] = url

            yield item

        next_page = response.xpath('//a[@class="page" and text()="下一页"]/@href').extract()
        if len(next_page) > 0:
            _url = domain + next_page[0]
            self.req_count += 1
            yield scrapy.Request(_url, callback=self.parse, errback=self.error_back)

        tree_branch = 2
        while self.req_count < self.max_req_count and tree_branch > 0:
            user_id = db.user_get_zero_id()
            if user_id is None:
                break
            _url = f'{domain}/user/{user_id}/uploads'
            self.req_count += 1
            tree_branch -= 1
            yield scrapy.Request(_url, callback=self.parse, errback=self.error_back)

        self.printer.print(['Crawl', 'Hit', 'Repeat', 'Fail'],
                           [self.crawl_count, self.hit_count, self.drop_count, self.fail_count])

    def process_first(self, item):
        if item['url'] in self.ids_seen:
            self.drop_count += 1
            raise DropItem("Duplicate item found: %s" % item['url'])
        else:
            self.ids_seen.add(item['url'])
            return item

    def process_second(self, item):
        if not db.zero_exist(item['id']):
            db.zero_insert(item.to_doc())
            self.hit_count += 1

    def close_second(self):
        print(f'catch: {len(self.ids_seen)}, drop: {self.drop_count}')

    def error_back(self, failure):
        self.req_count -= 1
        self.fail_count += 1
