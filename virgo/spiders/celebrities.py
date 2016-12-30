# -*- coding: utf-8 -*-

import scrapy
import re
from virgo.items import CelebrityItem
# import csv
# from virgo.spiders.virgo_config import celebrity_link_path
import pymysql
from scrapy import signals
from virgo.spiders.virgo_config import datasource as ds

from scrapy.crawler import CrawlerProcess

class CelebritySpider(scrapy.Spider):
    name = "celebrities"
    allowed_domains = ["rottentomatoes.com"]
    custom_settings = {
        'COOKIES_ENABLED': False,
    }
    def __init__(self):
        self.conn = pymysql.connect(
            host = ds['host'],
            user = ds['user'],
            password = ds['password'],
            db = ds['db'],
            port = ds['port'],
        )
        self.logger.info('finish init connection.')

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CelebritySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal = signals.spider_closed)
        return spider


    def spider_closed(self, spider):
        self.conn.close()
        spider.logger.info('Spider closed: %s', spider.name)

    def start_requests(self):
        # with open(celebrity_link_path, 'r') as file:
        #     csv_file = csv.reader(file)
        #     for rows in csv_file:
        #             yield scrapy.Request(rows[0])
        cursor = pymysql.cursors.SSCursor(self.conn)
        cursor.execute('select link from celebrity')
        while True:
            row = cursor.fetchone()
            if not row:
                break
            yield scrapy.Request(row[0])

    def parse(self, response):
        self.logger.info('Parse function called on %s', response.url)
        celebrity_reg = '^https?://www\.rottentomatoes\.com/celebrity/[^/]+/?$'

        if re.match(celebrity_reg, response.url) is not None:
            celebrity_item = CelebrityItem()
            celebrity_item['link'] = response.url
            celebrity_item['actorId'] = response.xpath('//meta[@name="actorID"]/@content').extract_first()
            celebrity_item['birthday'] = response.xpath('//td[contains(text(), "Birthday")]/following-sibling::td/time/@datetime').extract_first()
            celebrity_item['birthplace'] = response.xpath('//td[contains(text(), "Birthplace")]/following-sibling::td/text()').extract_first()
            celebrity_item['image'] = response.xpath('//img[@class="posterImage"]/@src').extract_first()
            bio = response.xpath('//div[contains(@class, "celeb_summary_bio")]/node()').extract()
            if bio is not None:
                celebrity_item['bio'] = ''.join(bio).strip()
            celebrity_item['name'] = response.xpath('//meta[@property="og:title"]/@content').extract_first()
            return celebrity_item
