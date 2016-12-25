#!/bin/bash

cd /root/workspace/virgo/ && \
git pull origin master && \
nohup /root/workspace/virgo/venv/bin/python2.7 /root/workspace/virgo/venv/bin/scrapy crawl rottentomatoes \
-s JOBDIR=/root/data/scrapy_job \
--logfile=/var/log/rottentomatoes.log --loglevel=INFO >./nohup.log 2>&1 & \