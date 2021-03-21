import re
import unittest

# ======================================
# テーブル名を検索する（テーブル名例：zzz）
#
_QR01 = re.compile(r'[^\w]zzz[^\w\.]', flags=(re.MULTILINE | re.IGNORECASE))
#_QR01 = re.compile(r'(?<!--)\.*[^\w]zzz[^\w\.]', flags=(re.MULTILINE | re.IGNORECASE))

_QH01 = r'''\
	-- 「Zzz」でヒットする
   select *
   from Zzz as T1, yyy T2
'''

_QH02 = r'''\
-- 「ZzZ」でヒットする
select * from yyy T1, ZzZ as T2
where ...
'''

_QH03 = r'''\
-- 「ZZZ」ヒットする
select zzz.id from yyy T1, ZzZz as T2
,ZZZ
where ...
'''

_QH04 = r'''\
-- 「ZZZ」ヒットする
select id from
ZZZ
where ...
'''

_QH51 = r'''\
-- ヒットしない（「ZzZz」はテーブル名が異なる）
select * from yyy T1, ZzZz as T2
where ...
'''

_QH52 = r'''\
-- ヒットしない（「zzz.」はalias）
select zzz.id from yyy T1, ZzZz as T2
where ...
'''

#コメント（「--」）は、前処理で除去するため対象外とする
_QH53 = r'''\
-- コメントアウトのためヒットしない
select zzz.id from yyy T1, ZzZz as T2
--,ZZZ
where ...
'''

#コメント（「--」）は、前処理で除去するため対象外とする
_QH54 = r'''\
-- コメントアウトのためヒットしない
select zzz.id from yyy T1, ZzZz as T2   -- ZZZ
where ...
'''

# ======================================
# 行コメントを検索する
#
_CR01 = re.compile(r'--.*$', flags=(re.MULTILINE))

_CH01b = r'''\
-- hoge
 --123
  --漢字
  select --
	id,    -- id
    nm,    -- 名称
	b_date--日付
  from table -- xxxテーブル
  where id = #{id}
'''

_CH01a = r'''\

 
  
  select 
	id,    
    nm,    
	b_date
  from table 
  where id = #{id}
'''

class TestCheck20210316(unittest.TestCase):

	def test_H01(self):
		rs = re.search(_QR01, _QH01)
		self.assertIsNotNone(rs)

	def test_H02(self):
		rs = re.search(_QR01, _QH02)
		self.assertIsNotNone(rs)

	def test_H03(self):
		rs = re.search(_QR01, _QH03)
		self.assertIsNotNone(rs)

	def test_H04(self):
		rs = re.search(_QR01, _QH04)
		self.assertIsNotNone(rs)

	def test_N01(self):
		rs = re.search(_QR01, _QH51)
		self.assertIsNone(rs)

	def test_N02(self):
		rs = re.search(_QR01, _QH52)
		self.assertIsNone(rs)

	#def test_N03(self):
	#	rs = re.search(_QR01, _QH53)
	#	self.assertIsNone(rs)

	#def test_N04(self):
	#	rs = re.search(_QR01, _QH54)
	#	self.assertIsNone(rs)

	def test_C01(self):
		rs = re.sub(_CR01, r'', _CH01b)
		self.assertEqual(rs, _CH01a)

if __name__ == '__main__':
	unittest.main()

#[EOF]