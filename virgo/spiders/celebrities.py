# -*- coding: utf-8 -*-

import scrapy
import re
from virgo.items import CelebrityItem
import csv
from virgo.spiders.virgo_config import celebrity_link_path

class CelebritySpider(scrapy.Spider):
    name = "celebrities"
    allowed_domains = ["rottentomatoes.com"]
    custom_settings = {

    }

    def start_requests(self):
        with open(celebrity_link_path, 'r') as file:
            csv_file = csv.reader(file)
            for rows in csv_file:
                    yield scrapy.Request(rows[0])

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
