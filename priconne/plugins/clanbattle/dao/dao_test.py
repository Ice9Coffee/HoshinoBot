import os
import logging
from sqlitedao import DB_PATH
from sqlitedao import ClanDao, MemberDao
import datetime
import sqlite3

def testadd(dao, item):
    print('testadd:', item)
    ret = dao.add(item)
    print('ret =', ret)

def testdelete(dao, *args):
    print('testdelete:', args)
    ret = dao.delete(*args)
    print('ret =', ret)

def testmodify(dao, item):
    print('testmodify:', item)
    ret = dao.modify(item)
    print('ret =', ret)

def testfindone(dao, *args):
    print('testfindone:', args)
    ret = dao.find_one(*args)
    print('ret =', ret)

def testfindall(dao):
    print('testfindall:')
    ret = dao.find_all()
    print('ret =', ret)

def testfind_by_gid(dao, gid):
    print('testfind_by_gid:')
    ret = dao.find_by_gid(gid)
    print('ret =', ret)

def testfind_by_uid(dao, uid):
    print('testfind_by_uid:')
    ret = dao.find_by_uid(uid)
    print('ret =', ret)


def testclandao():
    print('-'*10, 'testclandao', '-'*10)
    clandao = ClanDao()
    clan1 = {'gid':123456789, 'cid':1, 'name':'凯留同好会'}
    clan2 = {'gid':123456789, 'cid':2, 'name':'可可罗同好会'}
    clan3 = {'gid':123456789, 'cid':3, 'name':'佩可同好会'}
    clan4 = {'gid':987654321, 'cid':1, 'name':'克里斯同好会'}
    clan5 = {'gid':987654321, 'cid':2, 'name':'矛依未同好会'}
    clan6 = {'gid':987654321, 'cid':3, 'name':'似似花同好会'}
    testadd(clandao, clan1)
    testadd(clandao, clan2)
    testadd(clandao, clan3)
    testadd(clandao, clan4)
    testadd(clandao, clan5)
    testadd(clandao, clan6)
    testfindall(clandao)
    testdelete(clandao, clan5['gid'], clan5['cid'])
    testfind_by_gid(clandao, 987654321)
    clan6['name'] = '华哥同好会'
    testmodify(clandao, clan6)
    testfind_by_gid(clandao, 987654321)
    testfindall(clandao)
    print('-'*10, 'test end', '-'*10)

def testmemberdao():
    print('-'*10, 'testmemberdao', '-'*10)
    mbdao = MemberDao()
    mb1 = {'uid':111, 'alt':0, 'gid':123456789, 'cid':1, 'name':'凯留'}
    mb2 = {'uid':111, 'alt':1, 'gid':123456789, 'cid':1, 'name':'可可罗'}
    mb3 = {'uid':333, 'alt':0, 'gid':123456789, 'cid':1, 'name':'佩可'}
    mb4 = {'uid':444, 'alt':0, 'gid':123456789, 'cid':2, 'name':'克里斯提娜'}
    mb5 = {'uid':555, 'alt':0, 'gid':123456789, 'cid':2, 'name':'矛依未'}
    mb6 = {'uid':666, 'alt':0, 'gid':123456789, 'cid':2, 'name':'似似花'}
    testadd(mbdao, mb1)
    testadd(mbdao, mb2)
    testadd(mbdao, mb3)
    testadd(mbdao, mb4)
    testadd(mbdao, mb5)
    testadd(mbdao, mb6)
    testfindall(mbdao)
    testfind_by_uid(mbdao, 111)
    testdelete(mbdao, mb5['uid'], mb5['alt'])
    testfind_by_gid(mbdao, 123456789)
    mb1['name'] = '华哥'
    testmodify(mbdao, mb1)
    testfind_by_uid(mbdao, 111)
    testfind_by_gid(mbdao, 123456789)
    testfindall(mbdao)
    print('-'*10, 'test end', '-'*10)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print(DB_PATH)
    testclandao()
    testmemberdao()


'''
    con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cur.execute("create table test(d date, ts timestamp)")

    today = datetime.date.today()
    now = datetime.datetime.now()

    cur.execute("insert into test(d, ts) values (?, ?)", (today, now))
    cur.execute("select d, ts from test")
    row = cur.fetchone()
    print(today, "=>", row[0], type(row[0]))
    print(now, "=>", row[1], type(row[1]))

    cur.execute('select current_date as "d [date]", current_timestamp as "ts [timestamp]"')
    row = cur.fetchone()
    print("current_date", row[0], type(row[0]))
    print("current_timestamp", row[1], type(row[1]))
'''