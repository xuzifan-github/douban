#!/usr/bin/env python
# -*- coding: utf-8 -*-


import douban.database as db
from douban.items import Comment, MovieMeta, Subject, Review, Reply

cursor = db.connection.cursor()


class DoubanPipeline(object):
    def get_subject(self, item):
        sql = 'SELECT id FROM subjects WHERE douban_id=%s' % item['douban_id']
        cursor.execute(sql)
        return cursor.fetchone()

    def save_subject(self, item):
        keys = item.keys()
        values = tuple(item.values())
        fields = ','.join(keys)
        temp = ','.join(['%s'] * len(keys))
        sql = 'INSERT INTO subjects (%s) VALUES (%s)' % (fields, temp)
        cursor.execute(sql, values)
        return db.connection.commit()

    def get_movie_meta(self, item):
        sql = 'SELECT id FROM movies WHERE douban_id=%s' % item['douban_id']
        cursor.execute(sql)
        return cursor.fetchone()

    def save_movie_meta(self, item):
        keys = item.keys()
        values = tuple(item.values())
        fields = ','.join(keys)
        temp = ','.join(['%s'] * len(keys))
        sql = 'INSERT INTO movies (%s) VALUES (%s)' % (fields, temp)
        cursor.execute(sql, tuple(i.strip() for i in values))
        return db.connection.commit()

    def update_movie_meta(self, item):
        douban_id = item.pop('douban_id')
        keys = item.keys()
        values = tuple(item.values())
        values.append(douban_id)
        fields = ['%s=' % i + '%s' for i in keys]
        sql = 'UPDATE movies SET %s WHERE douban_id=%s' % (','.join(fields), '%s')
        cursor.execute(sql, tuple(i.strip() for i in values))
        return db.connection.commit()

    def get_comment(self, item):
        sql = 'SELECT * FROM comments WHERE content_md5="%s"' % item['content_md5']
        cursor.execute(sql)
        return cursor.fetchone()

    def save_comment(self, item):
        keys = item.keys()
        values = tuple(item.values())
        fields = ','.join(keys)
        temp = ','.join(['%s'] * len(keys))
        sql = 'INSERT INTO comments (%s) VALUES (%s)' % (fields, temp)
        cursor.execute(sql, values)
        return db.connection.commit()

    def get_review(self, item):
        sql = 'SELECT * FROM reviews WHERE content_md5="%s"' % item['content_md5']
        cursor.execute(sql)
        return cursor.fetchone()

    def save_review(self, item):
        keys = item.keys()
        values = tuple(item.values())
        fields = ','.join(keys)
        temp = ','.join(['%s'] * len(keys))
        sql = 'INSERT INTO reviews (%s) VALUES (%s)' % (fields, temp)
        cursor.execute(sql, values)
        return db.connection.commit()

    def get_reply(self, item):
        sql = 'SELECT * FROM replies WHERE content_md5="%s"' % item['content_md5']
        cursor.execute(sql)
        return cursor.fetchone()

    def save_reply(self, item):
        keys = item.keys()
        values = tuple(item.values())
        fields = ','.join(keys)
        temp = ','.join(['%s'] * len(keys))
        sql = 'INSERT INTO replies (%s) VALUES (%s)' % (fields, temp)
        cursor.execute(sql, values)
        return db.connection.commit()

    def process_item(self, item, spider):
        if isinstance(item, Subject):
            '''
            subject
            '''
            exist = self.get_subject(item)
            if not exist:
                self.save_subject(item)
        elif isinstance(item, MovieMeta):
            '''
            meta
            '''
            exist = self.get_movie_meta(item)
            if not exist:
                try:
                    self.save_movie_meta(item)
                except Exception as e:
                    print(item)
                    print(e)
            else:
                self.update_movie_meta(item)
        elif isinstance(item, Comment):
            '''
            comment
            '''
            exist = self.get_comment(item)
            if not exist:
                try:
                    self.save_comment(item)
                except Exception as e:
                    print(item)
                    print(e)
        elif isinstance(item, Review):
            '''
            review
            '''
            exist = self.get_review(item)
            if not exist:
                try:
                    self.save_review(item)
                except Exception as e:
                    print(item)
                    print(e)
        elif isinstance(item, Reply):
            '''
            reply
            '''
            exist = self.get_reply(item)
            if not exist:
                try:
                    self.save_reply(item)
                except Exception as e:
                    print(item)
                    print(e)
        return item
