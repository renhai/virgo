# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    movieId = scrapy.Field()
    title = scrapy.Field()
    director = scrapy.Field()
    author = scrapy.Field()
    genre = scrapy.Field()
    studio = scrapy.Field()
    year = scrapy.Field()
    mpaaRating = scrapy.Field()
    image = scrapy.Field()
    link = scrapy.Field()
    movieSynopsis = scrapy.Field()
    inTheaters = scrapy.Field()
    onDvd = scrapy.Field()
    runTime = scrapy.Field()
    timestamp = scrapy.Field()
    cast = scrapy.Field()
    rating = scrapy.Field()

class CelebrityItem(scrapy.Item):
    link = scrapy.Field()
    actorId = scrapy.Field()
    birthday = scrapy.Field()
    birthplace = scrapy.Field()
    image = scrapy.Field()
    bio = scrapy.Field()
    name = scrapy.Field()
