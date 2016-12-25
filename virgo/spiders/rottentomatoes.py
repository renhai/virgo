# -*- coding: utf-8 -*-
import scrapy
from virgo.items import MovieItem
from virgo.items import CelebrityItem
import json
import time
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import re


class RottentomatoesSpider(scrapy.Spider):
    name = "rottentomatoes"
    allowed_domains = ["rottentomatoes.com"]
    custom_settings = {
        # 'FEED_URI' : feed['FEED_URI'],
        # 'FEED_FORMAT': feed['FEED_FORMAT'],
        'DEPTH_LIMIT': 5,
    }
    start_urls = [
        'https://www.rottentomatoes.com',
        # 'https://www.rottentomatoes.com/m/ghost-town-gold',
        # 'https://www.rottentomatoes.com/m/soldiers-three',
        # 'https://www.rottentomatoes.com/m/alpha_dog',
        # 'https://www.rottentomatoes.com/m/sully',
        # 'https://www.rottentomatoes.com/m/97_owned',
        # 'https://www.rottentomatoes.com/m/blood_equity',
        # 'https://www.rottentomatoes.com/celebrity/tom_hanks',
        # 'https://www.rottentomatoes.com/celebrity/kashish/',
    ]

    # rules = (
    #     # Rule(LinkExtractor(allow=('.*'), deny=(), ), follow=True),
    #     Rule(LinkExtractor(allow=('/m/[^/]+/?$', )), callback='parse_item', follow=False),
    # )

    def parse(self, response):
        self.logger.info('Parse function called on %s', response.url)
        movie_reg = '.*/m/[^/]+/?$'
        celebrity_reg = '.*/celebrity/[^/]+/?$'
        if re.match(movie_reg, response.url) is not None:
            movie_item = MovieItem()
            movie_item['movieId'] = response.xpath('//meta[@name="movieID"]/@content').extract_first()
            details = response.xpath('//script[@id="jsonLdSchema"]/text()').extract_first()
            details_json = json.loads(details)
            movie_item['title'] = details_json.get('name')
            movie_item['director'] = details_json.get('director')
            movie_item['author'] = details_json.get('author')
            movie_item['genre'] = ','.join(details_json.get('genre', []))
            movie_item['studio'] = details_json.get('productionCompany', {}).get('name')
            movie_item['year'] = details_json.get('datePublished')
            movie_item['mpaaRating'] = details_json.get('contentRating')
            movie_item['image'] = details_json.get('image')
            movie_item['link'] = response.url
            movie_item['movieSynopsis'] = response.xpath('//div[@id="movieSynopsis"]/text()').extract_first()
            movie_item['inTheaters'] = response.xpath('//div[contains(text(), "In Theaters")]/following-sibling::div/time/@datetime').extract_first()
            movie_item['onDvd'] = response.xpath('//div[contains(text(), "On DVD")]/following-sibling::div/time/@datetime').extract_first()
            movie_item['runTime'] = response.xpath('//div[contains(text(), "Runtime")]/following-sibling::div/time/@datetime').extract_first()
            movie_item['timestamp'] = long(time.time() * 1000)

            actors = details_json.get('actors')
            character = details_json.get('character')
            for i in range(len(actors)):
                if len(actors) == len(character):
                    actors[i]['characters'] = character[i]
                else:
                    characterXpath = '//div[contains(@class,"castSection")]//a[@href="' + actors[i]['sameAs'] + '"]/following-sibling::span/@title'
                    characterString = response.xpath(characterXpath).extract_first()
                    if characterString:
                        actors[i]['characters'] = characterString
            movie_item['cast'] = actors

            rating = {}
            if 'aggregateRating' in details_json:
                if 'ratingValue' in details_json['aggregateRating']:
                    rating['criticRatingValue'] = details_json['aggregateRating']['ratingValue']
                if 'reviewCount' in details_json['aggregateRating']:
                    rating['criticReviewsCounted'] = details_json['aggregateRating']['reviewCount']

            criticFresh = response.xpath('//div[@id="all-critics-numbers"]//div[@id="scoreStats"]//span[contains(text(), "Fresh")]/following-sibling::span/text()').extract_first()
            if criticFresh is not None:
                rating['criticFresh'] = int(criticFresh.replace(',', ''))

            criticRotten = response.xpath('//div[@id="all-critics-numbers"]//div[@id="scoreStats"]//span[contains(text(), "Rotten")]/following-sibling::span/text()').extract_first()
            if criticRotten is not None:
                rating['criticRotten'] = int(criticRotten.replace(',', ''))

            criticAverageRating = response.xpath('//div[@id="all-critics-numbers"]//div[@id="scoreStats"]//span[contains(text(), "Average Rating")]/../text()').extract()
            if criticAverageRating:
                rating['criticAverageRating'] = (''.join(criticAverageRating)).strip()

            audienceRatingValue = response.xpath('//div[contains(@class, "audience-panel")]//a[@href="#audience_reviews"]//div[@class="meter-value"]//span/text()').extract_first()
            if audienceRatingValue is not None:
                rating['audienceRatingValue'] = int(audienceRatingValue.replace('%', ''))

            audienceAverageRating = response.xpath('//div[contains(@class, "audience-info")]//span[contains(text(), "Average Rating")]/../text()').extract()
            if audienceAverageRating:
                rating['audienceAverageRating'] = (''.join(audienceAverageRating)).strip()

            audienceRatingCount = response.xpath('//div[contains(@class, "audience-info")]//span[contains(text(), "User Ratings")]/../text()').extract()
            if audienceRatingCount:
                audienceRatingCountString = ''.join(audienceRatingCount).strip()
                rating['audienceRatingCount'] = int(audienceRatingCountString.replace(',', ''))

            criticsConsensus = response.xpath('//div[@id="all-critics-numbers"]//p[contains(@class, "critic_consensus")]/text()').extract()
            if criticsConsensus:
                rating['criticsConsensus'] = ''.join(criticsConsensus).strip()

            movie_item['rating'] = rating
            yield movie_item

            for person in movie_item['cast']:
                yield scrapy.Request(response.urljoin(person['sameAs']), callback=self.parse, priority=99)
            for person in movie_item['director']:
                yield scrapy.Request(response.urljoin(person['sameAs']), callback=self.parse, priority=99)
            for person in movie_item['author']:
                yield scrapy.Request(response.urljoin(person['sameAs']), callback=self.parse, priority=99)

        elif re.match(celebrity_reg, response.url) is not None:
            celebrity_item = CelebrityItem()
            celebrity_item['link'] = response.url
            celebrity_item['actorId'] = response.xpath('//meta[@name="actorID"]/@content').extract_first()
            celebrity_item['birthday'] = response.xpath('//td[contains(text(), "Birthday")]/following-sibling::td/time/@datetime').extract_first()
            celebrity_item['birthplace'] = response.xpath('//td[contains(text(), "Birthplace")]/following-sibling::td/text()').extract_first()
            celebrity_item['image'] = response.xpath('//img[@class="posterImage"]/@src').extract_first()
            bio = response.xpath('//div[contains(@class, "celeb_summary_bio")]/node()').extract()
            if bio is not None:
                celebrity_item['bio'] = ''.join(bio).strip()
            yield celebrity_item


        for url in response.xpath('//a/@href').extract():
            full_url = response.urljoin(url)
            if re.match(movie_reg, full_url) is not None:
                yield scrapy.Request(full_url, callback=self.parse, priority=100)
            else:
                yield scrapy.Request(full_url, callback=self.parse, priority=0)