#!/bin/bash

cd /root/workspace/virgo/ && \
git pull origin master && \
source venv/bin/activate && \
nohup scrapy crawl rottentomatoes --logfile=/var/log/rottentomatoes.log --loglevel=INFO >./nohup.log 2>&1 & \
deactivate