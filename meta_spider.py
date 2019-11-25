import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 抓取电影元数据
SPIDER_NAME = "movie_meta"

execute(["scrapy", "crawl", SPIDER_NAME])
