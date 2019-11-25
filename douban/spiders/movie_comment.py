#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from hashlib import md5
import douban.database as db
from douban.items import Comment
from scrapy import Request, Spider

cursor = db.connection.cursor()


class MovieCommentSpider(Spider):
    name = 'movie_comment'
    allowed_domains = ['movie.douban.com']
    sql = 'SELECT douban_id FROM movies WHERE douban_id NOT IN \
           (SELECT douban_id FROM comments GROUP BY douban_id) ORDER BY douban_id DESC'
    cursor.execute(sql)
    movies = cursor.fetchall()
    start_urls = {
        str(i['douban_id']): [
            f'https://movie.douban.com/subject/%s/comments?start={start}&limit=20&sort=new_score&status=P' % i[
                'douban_id'] for start in range(0, 201, 20)] for i in movies
    }

    def start_requests(self):
        for douban_id, url_list in self.start_urls.items():
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
                'Referer': f'https://movie.douban.com/subject/{douban_id}/',
            }
            for url in url_list:
                yield Request(url, headers=headers, meta={'douban_id': douban_id})

    def parse(self, response):
        douban_id = int(response.meta['douban_id'])
        div_list = response.xpath('//div[@class="comment-item"]')
        for div in div_list:
            content = div.xpath('.//span[@class="short"]/text()').extract_first()
            if len(content) <= 15:
                continue
            douban_user_nickname = div.xpath('.//span[@class="comment-info"]/a/text()').extract_first()
            avatar_src = div.xpath('./div[@class="avatar"]/a/img/@src').extract_first()
            douban_user_id = int(re.findall('icon/u(.*?)-', avatar_src)[0])
            comment_time = div.xpath('.//span[@class="comment-time "]/text()').extract_first().strip()
            span_class = div.xpath('.//span[@class="comment-info"]/span[2]/@class').extract_first()
            if 'rating' in span_class:
                star_level = int(re.findall('\d+', span_class)[0][0])
            else:
                star_level = None
            votes = int(div.xpath('.//span[@class="votes"]/text()').extract_first())
            content_md5 = md5(content.encode('utf-8')).hexdigest()
            comment = Comment()
            comment['douban_id'] = douban_id
            comment['douban_user_nickname'] = douban_user_nickname
            comment['douban_user_id'] = douban_user_id
            comment['comment_time'] = comment_time
            comment['star_level'] = star_level
            comment['votes'] = votes
            comment['content'] = content
            comment['content_md5'] = content_md5
            yield comment
