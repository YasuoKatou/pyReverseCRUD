# -*- coding: utf-8 -*-
import re

_RS01 = r".+(?<!delete)\s+from\s+(?P<table_name>\w+).?"
_RS02 = r".+\s+join\s+(?P<join_name>\w+).?"

_RI01 = r".?insert\s+into\s+(?P<table_name>\w+).?"

_RU01 = r".?update\s+(?P<table_name>\w+).?"

_RD01 = r".?(?<=delete)\s+from\s+(?P<table_name>\w+).?"

def select_from_table(query):
	'''
	駆動表（from 句）を取得する
	'''
	f = (re.MULTILINE | re.IGNORECASE)
	return list(re.finditer(_RS01, query, flags=f))

def join_table(query):
	'''
	結合表（join 句）を取得する
	'''
	f = (re.MULTILINE | re.IGNORECASE)
	return list(re.finditer(_RS02, query, flags=f))

def insert_table(query):
	'''
	Insert するテーブル名を取得する
	'''
	f = (re.MULTILINE | re.IGNORECASE)
	return re.search(_RI01, query, flags=f)

def update_table(query):
	'''
	Update するテーブル名を取得する
	'''
	f = (re.MULTILINE | re.IGNORECASE)
	return re.search(_RU01, query, flags=f)

def delete_table(query):
	'''
	delete するテーブル名を取得する
	'''
	f = (re.MULTILINE | re.IGNORECASE)
	return re.search(_RD01, query, flags=f)

def judgment(dao_list):
	for dao in dao_list.values():
		for dml in dao['dml'].values():
			crud = {'create': [], 'update': [], 'read': [], 'delete': []}
			query = "".join(dml['query'])
			# from を調べる
			ms = select_from_table(query)
			if len(ms):
				for m in ms:
					tn = m.group("table_name")
					if not tn in crud['read']:
						crud['read'].append(tn)
			# join を調べる
			ms = join_table(query)
			if len(ms):
				for m in ms:
					tn = m.group("join_name")
					if not tn in crud['read']:
						crud['read'].append(tn)
			dmlType = dml['type']
			if dmlType == 'insert':
				# update 対象のテーブルを調べる
				m = insert_table(query)
				if m:
					tn = m.group("table_name")
					if not tn in crud['create']:
						crud['create'].append(tn)
			elif dmlType == 'update':
				# update 対象のテーブルを調べる
				m = update_table(query)
				if m:
					tn = m.group("table_name")
					if not tn in crud['update']:
						crud['update'].append(tn)
			elif dmlType == 'delete':
				# delete 対象のテーブルを調べる
				m = delete_table(query)
				if m:
					tn = m.group("table_name")
					if not tn in crud['delete']:
						crud['delete'].append(tn)

			dml['crud'] = crud
			print(dml)

if __name__ == '__main__':
	import pathlib
	import sys

	from daoReader import DaoReader as DR

	xmlRoot = ''
	argvs = sys.argv
	if len(argvs) > 1:
		xmlRoot = pathlib.Path(argvs[1])
	else:
		myPath = pathlib.Path(__file__)
		xmlRoot = myPath.parent

	reader = DR()
	r = reader.readXmls(xmlRoot = xmlRoot / 'resources' / 'sources')

	judgment(r)
	'''
	引数：DaoReader.readXmlsの戻り値
	出力は、DaoReader.readXmlsの「FQCN_(n).dml.DML_(n)」に下記内容を追加する
    "crud": {
      "create": [],
      "select": [(table_name1)(, table_name2)],
      "update": [],
      "delete": []
    }
	'''
#[EOF]