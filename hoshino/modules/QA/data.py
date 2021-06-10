import os.path

import peewee as pw

db = pw.SqliteDatabase(
    os.path.join(os.path.dirname(__file__), 'qa.db')
)


class Question(pw.Model):
    quest = pw.TextField()
    answer = pw.TextField()
    rep_group = pw.IntegerField(default=0)  # 0 for none and 1 for all
    rep_member = pw.IntegerField(default=0)
    allow_private = pw.BooleanField(default=False)
    creator = pw.IntegerField()
    create_time = pw.TimestampField()

    class Meta:
        database = db
        primary_key = pw.CompositeKey('quest', 'rep_group', 'rep_member')


def init():
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'qa.db')):
        db.connect()
        db.create_tables([Question])
        db.close()


init()
