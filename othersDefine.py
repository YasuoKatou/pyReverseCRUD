# -*- coding: utf-8 -*-

import pathlib
import re

from Constants import DDL_REs, getWordRE


def _checkView2View(defPath, viewTable):
	'''
	ビューからビューの呼び出しを解決する.
	-----------------------
	defPath   : ビュー定義ファイルが配置されたフォルダーのルートパス
	viewTable : キーがビュー名、値が参照テーブルリストで構成する辞書型の値
	-----------------------
	戻り値    : viewTable
	'''
	# ビュー名を判定する正規表現一覧を作成
	wk = {}
	for vn in viewTable.keys():
		wk[vn] = getWordRE(vn)
	# ビュー定義を読出
	p = pathlib.Path(defPath)
	for fp in list(p.glob('**/*.sql')):
		with fp.open(mode='r', encoding='utf-8') as f:
			viewFile = f.read()
			# create view 定義のブロックを取得
			for m in list(re.finditer(DDL_REs['create-view'], viewFile)):
				create_view_name = m.group('view_name').lower()
				def_body = m.group('view_def')

				for vn, v_re in wk.items():
					if vn == create_view_name:
						# create view するビュー内に自身の参照はあり得ない
						continue
					# ビューからビューの呼出しを確認
					if re.search(v_re, def_body):
						for tn in viewTable[vn]:
							if tn not in viewTable[create_view_name]:
								viewTable[create_view_name].append(tn)
	return viewTable

def readViewDedine(defPath, tableList):
	'''
	ビュー定義ファイルから参照テーブルを抽出する.
	-----------------------
	defPath   : ビュー定義ファイルが配置されたフォルダーのルートパス
	tableList : テーブル一覧（辞書型）
	            キー：テーブル名、値：テーブル名を判定する正規表現
	-----------------------
	戻り値    : キーがビュー名、値が参照テーブルリストで構成する辞書型の値
	'''
	assert tableList, 'no table names'
	vl = {}
	p = pathlib.Path(defPath)
	# 指定フォルダ配下のビュー定義ファイル（*.sql）を読込む
	for fp in list(p.glob('**/*.sql')):
		with fp.open(mode='r', encoding='utf-8') as f:
			# ファイルの内容を全読み
			viewFile = f.read()
			# DDL（create view xxx ....）文を取得
			for m in list(re.finditer(DDL_REs['create-view'], viewFile)):
				tables = []
				# DDL文の「reate view xxx」より後ろを取得
				def_body = m.group('view_def')
				# 引数のテーブル一覧の参照を確認
				for tn, t_re in tableList.items():
					if re.search(t_re, def_body):
						tables.append(tn.lower())
				vl[m.group('view_name').lower()] = tables
	return _checkView2View(defPath, vl)
#[EOF]