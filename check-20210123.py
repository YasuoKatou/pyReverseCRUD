import re
import sys
import unittest


verbose_list = []

class TestStringMethods(unittest.TestCase):

	_RS01 = r".+\s+from\s+(?P<table_name>\w+).?"
	_RS02 = r".+\s+join\s+(?P<join_name>\w+).?"

	_RI01 = r".?insert\s+into\s+(?P<table_name>\w+).?"

	_RU01 = r".?update\s+(?P<table_name>\w+).?"

	_RD01 = r".?delete\s+from\s+(?P<table_name>\w+).?"

	def select_from_table(self, query):
		'''
		駆動表（from 句）を取得する
		'''
		f = (re.MULTILINE | re.IGNORECASE)
		return list(re.finditer(self._RS01, query, flags=f))

	def join_table(self, query):
		'''
		結合表（join 句）を取得する
		'''
		f = (re.MULTILINE | re.IGNORECASE)
		return list(re.finditer(self._RS02, query, flags=f))

	def insert_table(self, query):
		'''
		Insert するテーブル名を取得する
		'''
		f = (re.MULTILINE | re.IGNORECASE)
		return re.search(self._RI01, query, flags=f)

	def update_table(self, query):
		'''
		Update するテーブル名を取得する
		'''
		f = (re.MULTILINE | re.IGNORECASE)
		return re.search(self._RU01, query, flags=f)

	def delete_table(self, query):
		'''
		delete するテーブル名を取得する
		'''
		f = (re.MULTILINE | re.IGNORECASE)
		return re.search(self._RD01, query, flags=f)

	@classmethod
	def tearDownClass(cls):
		if any(verbose_list):
			print('\n')
		for s in verbose_list:
			print(s)

	def test_select_01(self):
		mm = sys._getframe().f_code.co_name
		q = "select *   from table1 as T where T.id =	1;"
		# 駆動表（from 句）を確認
		ms = self.select_from_table(q)
		self.assertEqual(len(ms), 1, "%s : none driving table !?" % mm)
		for m in ms:
			tn = m.group("table_name")
			verbose_list.append("%s : table [%s]" % (mm, tn))
			self.assertEqual(tn, "table1", "%s : table name ?" % mm)
		# 結合表（join 句）を確認
		ms = self.join_table(q)
		self.assertEqual(len(ms), 0, "%s : join match !?" % mm)

	def test_select_02(self):
		mm = sys._getframe().f_code.co_name
		q = "select * FROM\n"
		q += "table_2 T where\n"
		q += "T.id = 1"
		# 駆動表（from 句）を確認
		ms = self.select_from_table(q)
		self.assertEqual(len(ms), 1, "%s : none driving table !?" % mm)
		for m in ms:
			tn = m.group("table_name")
			verbose_list.append("%s : table [%s]" % (mm, tn))
			self.assertEqual(tn, "table_2", "%s : table name ?" % mm)
		# 結合表（join 句）を確認
		ms = self.join_table(q)
		self.assertEqual(len(ms), 0, "%s : join match !?" % mm)

	def test_select_03(self):
		'''
		結合の確認
		'''
		mm = sys._getframe().f_code.co_name
		q = "select * FRoM\n"
		q += "table_3 T \n"
		q += "left outer joIN mTable\ns"
		q += "where T.id = 1"
		# 駆動表（from 句）を確認
		ms = self.select_from_table(q)
		self.assertEqual(len(ms), 1, "%s : none driving table !?" % mm)
		for m in ms:
			tn = m.group("table_name")
			verbose_list.append("%s : table [%s]" % (mm, tn))
			self.assertEqual(tn, "table_3", "%s : table name ?" % mm)
		# 結合表（join 句）を確認
		ms = self.join_table(q)
		self.assertEqual(len(ms), 1, "%s : none join table !?" % mm)
		for m in ms:
			tn = m.group("join_name")
			verbose_list.append("%s : join table [%s]" % (mm, tn))
			self.assertEqual(tn, "mTable", "%s : join name ?" % mm)

	def test_select_04(self):
		'''
		副問合せを確認
		駆動表と副問合せのテーブルがマッチする
		'''
		mm = sys._getframe().f_code.co_name
		q = "select * from table_4\n"
		q += "where uriage > (select AVG(uriage) from table_4);"
		e = ["table_4", "table_4"]
		# 駆動表（from 句）を確認
		ms = self.select_from_table(q)
		self.assertEqual(len(ms), len(e), "%s : none driving table !?" % mm)
		ec = 0
		for m in ms:
			tn = m.group("table_name")
			verbose_list.append("%s : table [%s]" % (mm, tn))
			te = e[ec]
			self.assertEqual(tn, te, "%s : table name ?" % mm)
			ec += 1
		# 結合表（join 句）を確認
		ms = self.join_table(q)
		self.assertEqual(len(ms), 0, "%s : join match !?" % mm)

	def test_insert_01(self):
		mm = sys._getframe().f_code.co_name
		q = "  INSERT  into  products (did, dname) VALUES (1, 'Cheese');"
		# insert を確認
		m = self.insert_table(q)
		self.assertIsNotNone(m, "%s : none insert table !?" % mm)
		tn = m.group("table_name")
		verbose_list.append("%s : insert [%s]" % (mm, tn))
		self.assertEqual(tn, "products", "%s : table name ?" % mm)

	def test_update_01(self):
		mm = sys._getframe().f_code.co_name
		q = "  UPDATE films SET kind = 'Dramatic' WHERE kind = 'Drama';"
		# update を確認
		m = self.update_table(q)
		self.assertIsNotNone(m, "%s : none update table !?" % mm)
		tn = m.group("table_name")
		verbose_list.append("%s : update [%s]" % (mm, tn))
		self.assertEqual(tn, "films", "%s : table name ?" % mm)

	def test_delete_01(self):
		mm = sys._getframe().f_code.co_name
		q = "  DELETE FROM Staff WHERE id='0002';"
		# delete を確認
		m = self.delete_table(q)
		self.assertIsNotNone(m, "%s : none delete table !?" % mm)
		tn = m.group("table_name")
		verbose_list.append("%s : delete [%s]" % (mm, tn))
		self.assertEqual(tn, "Staff", "%s : table name ?" % mm)

if __name__ == '__main__':
	unittest.main()

#[EOF]