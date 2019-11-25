#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import requests
from hashlib import md5

from lxml import etree

import douban.database as db
from douban.items import Review, Reply
from scrapy import Request, Spider

cursor = db.connection.cursor()


class MovieCommentSpider(Spider):
    name = 'movie_review'
    allowed_domains = ['movie.douban.com']
    sql = 'SELECT douban_id FROM movies WHERE douban_id NOT IN \
           (SELECT douban_id FROM reviews GROUP BY douban_id) ORDER BY douban_id DESC'
    cursor.execute(sql)
    movies = cursor.fetchall()
    start_urls = {
        str(i['douban_id']): 'https://movie.douban.com/subject/%s/reviews?start=0' % i['douban_id'] for i in movies
    }

    def start_requests(self):
        for douban_id, url in self.start_urls.items():
            yield Request(url, meta={'douban_id': douban_id})

    def parse(self, response):
        douban_id = int(response.meta['douban_id'])
        div_list = response.xpath('//div[@class="review-list  "]/div')
        for div in div_list:
            title = div.xpath('.//h2/a/text()').extract_first()
            review_id = int(div.xpath('./@data-cid').extract_first())
            url = f'https://movie.douban.com/review/{review_id}/'
            douban_user_nickname = div.xpath('.//a[@class="name"]/text()').extract_first()
            avatar = div.xpath('.//a[@class="avator"]/img/@src').extract_first()
            try:
                douban_user_id = int(re.findall('icon/u(.*?)-', avatar)[0])
            except:
                user_url = div.xpath('.//a[@class="avator"]/@href').extract_first()
                try:
                    douban_user_id = int(re.findall('\d+', user_url)[0])
                except:
                    douban_user_id = self.get_user_id(user_url)
            review_time = div.xpath('.//span[@class="main-meta"]/text()').extract_first()
            try:
                useful_count = int(
                    div.xpath(f'.//span[@id="r-useful_count-{review_id}"]/text()').extract_first().strip())
            except:
                useful_count = 0
            try:
                useless_count = int(
                    div.xpath(f'.//span[@id="r-useless_count-{review_id}"]/text()').extract_first().strip())
            except:
                useless_count = 0
            reply = int(div.xpath('.//a[@class="reply "]/text()').extract_first()[:-2])
            review = Review()
            review['douban_id'] = douban_id
            review['review_id'] = review_id
            review['douban_user_nickname'] = douban_user_nickname
            review['douban_user_id'] = douban_user_id
            review['avatar'] = avatar
            review['title'] = title
            review['url'] = url
            review['review_time'] = review_time
            review['useful_count'] = useful_count
            review['useless_count'] = useless_count
            review['reply'] = reply
            yield Request(url, callback=self.parse_detail, meta={'review': review})
        if div_list:
            cur_page_start = int(re.findall('start=(.*)', response.url)[0])
            next_page_start = cur_page_start + 20
            next_page_url = f'https://movie.douban.com/subject/{douban_id}/reviews?start={next_page_start}'
            yield Request(next_page_url, callback=self.parse, meta={'douban_id': douban_id})

    def parse_detail(self, response):
        content = ''.join(response.xpath('//div[@class="review-content clearfix"]//text()').extract()).strip()
        content_md5 = md5(content.encode('utf-8')).hexdigest()
        repost = response.xpath('//span[@class="rec-num"]/text()').extract_first()
        repost = int(repost) if repost else 0
        review = response.meta['review']
        review['content'] = content
        review['content_md5'] = content_md5
        review['repost'] = repost
        yield review
        comment_list = json.loads(re.findall(r"'comments': (.*?)'total'", response.text, re.S)[0].strip()[:-1])
        for comment in comment_list:
            content = comment['text']
            if len(content) <= 15:
                continue
            avatar = comment['author']['avatar']
            douban_user_nickname = comment['author']['name']
            reply_time = comment['create_time']
            content_md5 = md5(content.encode('utf-8')).hexdigest()
            reply = Reply()
            reply['douban_id'] = review['douban_id']
            reply['review_id'] = review['review_id']
            reply['avatar'] = avatar
            reply['douban_user_nickname'] = douban_user_nickname
            reply['reply_time'] = reply_time
            reply['content'] = content
            reply['content_md5'] = content_md5
            yield reply
            for i in comment['replies']:
                if len(i['text']) <= 15:
                    continue
                avatar1 = i['author']['avatar']
                douban_user_nickname1 = i['author']['name']
                reply_time1 = i['create_time']
                content_md51 = md5(i['text'].encode('utf-8')).hexdigest()
                reply1 = Reply()
                reply1['douban_id'] = review['douban_id']
                reply1['review_id'] = review['review_id']
                reply1['avatar'] = avatar1
                reply1['douban_user_nickname'] = douban_user_nickname1
                reply1['reply_time'] = reply_time1
                reply1['content'] = i['text']
                reply1['content_md5'] = content_md51
                yield reply1

    @staticmethod
    def get_user_id(user_url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        }
        r = requests.get(user_url, headers=headers)
        html_tree = etree.HTML(r.text)
        try:
            user_id = int(html_tree.xpath('//div[@class="user-info"]/div[@class="pl"]/text()')[0].strip())
        except:
            user_id = None
        return user_id
