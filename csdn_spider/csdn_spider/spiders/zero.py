# -*- coding: utf-8 -*-
import scrapy
from csdn_spider.items import ZeroSpiderItem
from scrapy.exceptions import DropItem
from csdn_spider import db
import time

_last_time = 0


def xprint(_str):
    global _last_time
    if time.time() - _last_time >= 1:
        print(_str)
        _last_time = time.time()


def get_between(_str, start, end):
    b = _str.find(start) + len(start)
    e = _str.find(end, b)
    return _str[b:e]


def rget_between(_str, start, end):
    e = _str.rfind(end)
    b = _str.rfind(start, 0, e) + len(start)
    return _str[b:e]


def rget(_str, start):
    return _str[_str.rfind(start) + len(start):]


def list_0(ls, default=''):
    if len(ls) > 0:
        return ls[0]
    return default


class ZeroSpider(scrapy.Spider):
    name = "zero"
    allowed_domains = ["csdn.net"]
    start_urls = ['https://download.csdn.net/user/zzia615/uploads']

    # new
    ids_seen = set()
    drop_count = 0
    reqs_set = set()
    zero_count = 0
    url_count = 0
    crawl_count = 0
    begin_time = time.time()

    def parse(self, response):
        cards = response.xpath('//div[@class="card clearfix"]')
        domain = 'https://download.csdn.net'

        self.crawl_count += 1
        if response.request.url in self.reqs_set:
            self.reqs_set.remove(response.request.url)

        for card in cards:
            url = domain + card.xpath('div[@class="img"]/a/@href').extract()[0]
            if not db.raw_exist(url):
                db.raw_insert(url)
                self.url_count += 1

            score = get_between(card.xpath('div[@class="content"]/div[@class="score"]').extract()[0], '</label>',
                                '</div>').strip()
            if score != '0':
                continue

            _id = rget(list_0(card.xpath('div[@class="img"]/a/@href').extract()), '/')
            type = rget_between(list_0(card.xpath('div[@class="img"]//img/@src').extract()), '/', '.')
            title = list_0(card.xpath('div[@class="content"]/h3/a/text()').extract()).strip()
            brief = list_0(card.xpath('div[@class="content"]/p[@class="brief"]/text()').extract()).strip()
            tags = list_0(card.xpath('div[@class="content"]//p[@class="tags clearfix"]/a/text()').extract()).strip()
            date = get_between(list_0(card.xpath('div[@class="content"]//div[@class="date"]').extract()), '</label>',
                               '</div>').strip()

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
            self.reqs_set.add(_url)
            yield scrapy.Request(_url, callback=self.parse)

        while len(self.reqs_set) < 100:
            user_id = db.user_get_crawl_id()
            if user_id is None:
                break
            _url = f'{domain}/user/{user_id}/uploads'
            self.reqs_set.add(_url)
            yield scrapy.Request(_url, callback=self.parse)

        speed = self.crawl_count / (time.time() - self.begin_time)
        xprint(f'count: {self.crawl_count}, speed:{speed:.1f}, '
               f'reqs: {len(self.reqs_set)}, zero: {self.zero_count}, new: {self.url_count}')

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
            self.zero_count += 1

    def close_second(self):
        print(f'catch: {len(self.ids_seen)}, drop: {self.drop_count}')
