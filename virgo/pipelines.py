# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pika
import json
import logging
from virgo.spiders.virgo_config import rabbit_mq

class MoviePipeline(object):
    def __init__(self):
        credentials = pika.PlainCredentials(rabbit_mq['user_name'], rabbit_mq['password'])
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_mq['host'],
                                                                       port=rabbit_mq['port'],
                                                                       virtual_host=rabbit_mq['virtual_host'],
                                                                       credentials=credentials))

        self.channel = self.connection.channel()
        # channel.queue_declare(queue='taurus.spider.test.queue')
        logging.info('****** rabbit mq connected ******')

    def process_item(self, item, spider):
        logging.info('send message: {0}'.format(item['link']))
        message = json.dumps(dict(item))

        self.channel.basic_publish(exchange = rabbit_mq['exchange'],
                                   routing_key = rabbit_mq['routing_key'],
                                   body = message,
                                   properties = pika.BasicProperties(content_type='text/plain',
                                                              content_encoding='UTF-8',
                                                              delivery_mode=2,
                                                              priority=0
                                                              ))

        return item

    def open_spider(self, spider):
        logging.info('open_spider called')


    def close_spider(self, spider):
        self.connection.close()
        logging.info('****** rabbit mq closed ******')

