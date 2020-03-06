# -*- coding: utf-8 -*-
import scrapy
from csdn_spider.items import CsdnSpiderItem
from scrapy.exceptions import DropItem
from csdn_spider import db
import time

_last_time = 0


def xprint(_str):
    global _last_time
    if time.time() - _last_time >= 1:
        print(_str)
        _last_time = time.time()


class CsdnSpider(scrapy.Spider):
    name = "csdn"
    allowed_domains = ["csdn.net"]
    start_urls = ['https://download.csdn.net/download/sxscf1988/12229684']

    # new
    ids_seen = set()
    drop_count = 0
    crawl_count = 0
    reqs_set = set()
    begin_time = time.time()

    def parse(self, response):
        self.crawl_count += 1
        if response.request.url in self.reqs_set:
            self.reqs_set.remove(response.request.url)
        titles = response.xpath('//a[@class="dl_block_a"]/@href')
        for tl in titles:
            url = tl.extract()
            if db.raw_exist(url):
                continue
            item = CsdnSpiderItem()
            item['url'] = url
            yield item

        while len(self.reqs_set) < 100:
            _url = db.raw_get_crawl_url()
            if _url is None:
                break
            self.reqs_set.add(_url)
            yield scrapy.Request(_url, callback=self.parse)

        speed = self.crawl_count / (time.time() - self.begin_time)
        xprint(f'count: {self.crawl_count}, speed:{speed:.1f}, '
               f'reqs: {len(self.reqs_set)}, new: {len(self.ids_seen)}')

    def process_first(self, item):
        if item['url'] in self.ids_seen:
            self.drop_count += 1
            raise DropItem("Duplicate item found: %s" % item['url'])
        else:
            self.ids_seen.add(item['url'])
            return item

    def process_second(self, item):
        if not db.raw_exist(item['url']):
            db.raw_insert(item['url'])
        b = item['url'].find('download.csdn.net/download/') + len('download.csdn.net/download/')
        e = item['url'].find('/', b)
        user_id = item['url'][b:e]
        if not db.user_exist(user_id):
            db.user_insert(user_id)

    def close_second(self):
        print(f'catch: {len(self.ids_seen)}, drop: {self.drop_count}')
