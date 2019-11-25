import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 抓取电影id
SPIDER_NAME = "movie_subject"

execute(["scrapy", "crawl", SPIDER_NAME])
