import pathlib
import unittest
import sys

from daoReader import DaoReader as DR
from crudJudgment import judgment

class TestCurdJudgment(unittest.TestCase):

    def test_sampleMapper01(self):
        mm = sys._getframe().f_code.co_name
        # Mapper XML を読む
        myPath = pathlib.Path(__file__)
        xmlRoot = myPath.parent
        reader = DR()
        r = reader.readXmls(xmlRoot = xmlRoot / 'resources')
        self.assertIsNotNone(r, "%s no read xml" % mm)
        # CRUD を判定する
        judgment(r)

        # 結果を検証する
        self.assertEqual(len(r.keys()), 1, "%s mappers error" % mm)
        mapperNameSpace = 'com.example.mybatisdemo.mapper.SampleMapper'
        self.assertTrue(mapperNameSpace in r, "%s none mapper" % mm)
        mp = r[mapperNameSpace]
        self.assertEqual(mp['mapper']['package'], 'com.example.mybatisdemo.mapper', "%s interface package error" % mm)
        self.assertEqual(mp['mapper']['interface'], 'SampleMapper', "%s interface name error" % mm)
        self.assertIsNotNone(mp['dml'], "%s none dml" % mm)
        # クエリーの数を確認
        dml = mp['dml']
        self.assertEqual(len(dml.keys()), 4, "%s dml num error" % mm)
        # select tag
        queryTag = 'selectUsers'
        self.assertTrue(queryTag in dml, "%s query tag1 error" % mm)
        query = dml[queryTag]
        crudKey = 'crud'
        self.assertTrue(crudKey in query, "%s curd tag1 error" % mm)
        crud = query[crudKey]
        self.assertEqual(len(crud['create']), 0, '%s crud1 - create error' % mm)
        self.assertEqual(len(crud['read']),   1, '%s crud1 - read num error' % mm)
        self.assertEqual(crud['read'][0], 'some_table', '%s crud1 - read table name error' % mm)
        self.assertEqual(len(crud['update']), 0, '%s crud1 - update error' % mm)
        self.assertEqual(len(crud['delete']), 0, '%s crud1 - delete error' % mm)
        # insert tag
        queryTag = 'newdata'
        self.assertTrue(queryTag in dml, "%s query tag2 error" % mm)
        query = dml[queryTag]
        crudKey = 'crud'
        self.assertTrue(crudKey in query, "%s curd tag2 error" % mm)
        crud = query[crudKey]
        self.assertEqual(len(crud['create']), 1, '%s crud2 - create num error' % mm)
        self.assertEqual(crud['create'][0], 'products', '%s crud2 - create table name error' % mm)
        self.assertEqual(len(crud['read']),   0, '%s crud2 - read error' % mm)
        self.assertEqual(len(crud['update']), 0, '%s crud2 - update error' % mm)
        self.assertEqual(len(crud['delete']), 0, '%s crud2 - delete error' % mm)
        # delete tag
        queryTag = 'deleteByIdAndName'
        self.assertTrue(queryTag in dml, "%s query tag3 error" % mm)
        query = dml[queryTag]
        crudKey = 'crud'
        self.assertTrue(crudKey in query, "%s curd tag3 error" % mm)
        crud = query[crudKey]
        self.assertEqual(len(crud['create']), 0, '%s crud3 - create num error' % mm)
        self.assertEqual(len(crud['read']),   0, '%s crud3 - read error' % mm)
        self.assertEqual(len(crud['update']), 0, '%s crud3 - update error' % mm)
        self.assertEqual(len(crud['delete']), 1, '%s crud3 - delete error' % mm)
        self.assertEqual(crud['delete'][0], 'user', '%s crud3 - create table name error' % mm)
        # update tag
        queryTag = 'updateById'
        self.assertTrue(queryTag in dml, "%s query tag4 error" % mm)
        query = dml[queryTag]
        crudKey = 'crud'
        self.assertTrue(crudKey in query, "%s curd tag4 error" % mm)
        crud = query[crudKey]
        self.assertEqual(len(crud['create']), 0, '%s crud4 - create num error' % mm)
        self.assertEqual(len(crud['read']),   0, '%s crud4 - read error' % mm)
        self.assertEqual(len(crud['update']), 1, '%s crud4 - update error' % mm)
        self.assertEqual(crud['update'][0], 'syain', '%s crud4 - create table name error' % mm)
        self.assertEqual(len(crud['delete']), 0, '%s crud4 - delete error' % mm)

if __name__ == '__main__':
	unittest.main()

#[EOF]