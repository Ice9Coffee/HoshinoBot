# -*- coding:utf-8 -*-
import os
import time
import urllib3
from peewee import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

dbName = 'data.db'
db = SqliteDatabase(os.path.join(os.path.dirname(__file__), dbName))


class Coser(Model):
    id = AutoField(primary_key=True)
    pic_hash = CharField(unique=True)
    uid = IntegerField()
    name = CharField()
    doc_id = IntegerField()
    title = CharField()
    url = CharField()
    category = CharField()
    upload_at = DateTimeField()
    created_at = DateTimeField()

    class Meta:
        database = db


def saveToDb(uid, name, doc_id, title, url, c, picHash, upload_time):
    Coser.replace(
        pic_hash=picHash,
        uid=uid,
        name=name,
        doc_id=doc_id,
        title=title,
        url=url,
        category=c,
        upload_at=upload_time,
        created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    ).execute()
