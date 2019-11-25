import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 抓取影评和回应
SPIDER_NAME = "movie_review"

execute(["scrapy", "crawl", SPIDER_NAME])
