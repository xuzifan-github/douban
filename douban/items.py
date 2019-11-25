#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Item, Field


class Subject(Item):
    douban_id = Field()
    type = Field()


class MovieMeta(Item):
    douban_id = Field()
    type = Field()
    cover = Field()
    name = Field()
    directors = Field()
    screenwriter = Field()
    actors = Field()
    genres = Field()
    regions = Field()
    languages = Field()
    release_date = Field()
    mins = Field()
    alias = Field()
    imdb_id = Field()
    douban_score = Field()
    douban_votes = Field()
    storyline = Field()


class Comment(Item):
    douban_id = Field()
    douban_user_nickname = Field()
    douban_user_id = Field()
    comment_time = Field()
    star_level = Field()
    votes = Field()
    content = Field()
    content_md5 = Field()


class Review(Item):
    douban_id = Field()
    review_id = Field()
    douban_user_nickname = Field()
    douban_user_id = Field()
    avatar = Field()
    title = Field()
    url = Field()
    review_time = Field()
    content = Field()
    content_md5 = Field()
    useful_count = Field()
    useless_count = Field()
    reply = Field()
    repost = Field()


class Reply(Item):
    douban_id = Field()
    review_id = Field()
    avatar = Field()
    douban_user_nickname = Field()
    reply_time = Field()
    content = Field()
    content_md5 = Field()
