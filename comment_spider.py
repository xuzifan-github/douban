import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 抓取短评
SPIDER_NAME = "movie_comment"

execute(["scrapy", "crawl", SPIDER_NAME])
