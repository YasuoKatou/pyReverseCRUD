# -*- coding: utf-8 -*-
import re
import logging

_RI01 = re.compile(r"insert\s+into\s+(?P<table_name>\w+)", flags=(re.MULTILINE | re.IGNORECASE))

_RU01 = re.compile(r"update\s+(?P<table_name>\w+)", flags=(re.MULTILINE | re.IGNORECASE))

_RD01 = re.compile(r"delete\s+from\s+(?P<table_name>\w+)", flags=(re.MULTILINE | re.IGNORECASE))

def insert_table(query, crud):
	'''
	Insert するテーブル名を取得する
	'''
	m = re.search(_RI01, query)
	assert m, 'not found insert table name\n----------------\n%s\n----------------' & query
	tn = m.group("table_name").lower()
	if not tn in crud['create']:
		crud['create'].append(tn)
	return tn, re.sub(_RI01, '', query)

def update_table(query, crud):
	'''
	Update するテーブル名を取得する
	'''
	m = re.search(_RU01, query)
	assert m, 'not found update table name\n----------------\n%s\n----------------' & query
	tn = m.group("table_name").lower()
	if not tn in crud['update']:
		crud['update'].append(tn)
	return tn, re.sub(_RU01, '', query)

def delete_table(query, crud):
	'''
	delete するテーブル名を取得する
	'''
	m = re.search(_RD01, query)
	assert m, 'not found update table name\n----------------\n%s\n----------------' & query
	tn = m.group("table_name").lower()
	if not tn in crud['delete']:
		crud['delete'].append(tn)
	return tn, re.sub(_RD01, '', query)

def findReferencedTable(query, crud, tableRE):
	for tn, searchRE in tableRE.items():
		if re.search(searchRE, query):
			crud['read'].append(tn)

def judgment(dao, tableRE):
	for dml in dao['dml'].values():
		crud = {'create': [], 'update': [], 'read': [], 'delete': []}
		query = "".join(dml['query'])
		dmlType = dml['type']
		if dmlType == 'insert':
			# update 対象のテーブルを調べる
			tn, query = insert_table(query, crud)
			if tn not in tableRE.keys():
				logging.warning('%s is not defined' % tn)
		elif dmlType == 'update':
			# update 対象のテーブルを調べる
			tn, query = update_table(query, crud)
			if tn not in tableRE.keys():
				logging.warning('%s is not defined' % tn)
		elif dmlType == 'delete':
			# delete 対象のテーブルを調べる
			tn, query = delete_table(query, crud)
			if tn not in tableRE.keys():
				logging.warning('%s is not defined' % tn)
		findReferencedTable(query, crud, tableRE)

		dml['crud'] = crud
		del dml['query']
		#print(dml)

#def judgmentAll(dao_list):
#	for dao in dao_list.values():
#		judgment(dao)

	'''
	引数：DaoReader.readXmlsの戻り値
	出力は、DaoReader.readXmlsの「FQCN_(n).dml.DML_(n)」に下記内容を追加する
    "crud": {
      "create": [],
      "read": [(table_name1)(, table_name2)],
      "update": [],
      "delete": []
    }
	また、r[FQCN_1]['dml'][DML_1]['query']要素はCRUDの判定後、削除する
	'''
#[EOF]