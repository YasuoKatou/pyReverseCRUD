# -*- coding: utf-8 -*-
import datetime
import json
import openpyxl
import pathlib
import re

from openpyxl.styles import Border, Side, PatternFill, Font, GradientFill, Alignment

def getExcelBookPath(prefix):
	def getExcelBookName():
		now = datetime.datetime.now()
		return prefix + now.strftime("_%Y%m%d_%H%M%S.xlsx")
	myPath = pathlib.Path(__file__)
	xmlRoot = myPath.parent
	return xmlRoot / 'resources' / getExcelBookName()

def getCrudConfig():
	myPath = pathlib.Path(__file__)
	json_path = myPath.parent / 'resources' / 'crudConfig.json'
	with json_path.open(mode='r', encoding='UTF8') as f:
		return json.load(f)

def formatCrudSheet(sheet, crud_config):
	excel_config = crud_config['Excel']
	start_row = excel_config['start_row']
	start_column = excel_config['start_column']
	crud_width = excel_config['crud_width']
	row = start_row
	col = start_column
	alignment1 = Alignment(horizontal="center", vertical="center")
	table_list = []
	for key, name in excel_config['tables'].items():
		print(key + ': ' + name)
		num = len(crud_config['tables'][key])
		d = sheet.cell(row=row, column=col, value=name)
		d.alignment = alignment1
		sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+num*4-1)
		count = 0
		for table in crud_config['tables'][key]:
			for k, v in table.items():
				table_list.append(k)
				# テーブル名
				r = row + 1
				c = col + count * 4
				d = sheet.cell(row=r, column=c, value='%s\n%s' % (v,k))
				d.alignment = alignment1
				sheet.merge_cells(start_row=r, start_column=c, end_row=r, end_column=col+(count+1)*4-1)
				# insert
				r += 1
				a1 = openpyxl.utils.get_column_letter(c)
				sheet.column_dimensions[a1].width = crud_width
				d = sheet.cell(row=r, column=c,   value='C')
				d.alignment = alignment1
				# select
				c += 1
				a1 = openpyxl.utils.get_column_letter(c)
				sheet.column_dimensions[a1].width = crud_width
				d = sheet.cell(row=r, column=c, value='R')
				d.alignment = alignment1
				# update
				c += 1
				a1 = openpyxl.utils.get_column_letter(c)
				sheet.column_dimensions[a1].width = crud_width
				d = sheet.cell(row=r, column=c, value='U')
				d.alignment = alignment1
				# delete
				c += 1
				a1 = openpyxl.utils.get_column_letter(c)
				sheet.column_dimensions[a1].width = crud_width
				d = sheet.cell(row=r, column=c, value='D')
				d.alignment = alignment1
				count += 1

		col += num * 4
	return table_list

def formatClassMethods(sheet, crud_config, pinfo):
	RE_EXCLUDE_CLASS = r'.+(Dto|Entity)$'
	excel_config = crud_config['Excel']
	start_row = excel_config['start_row']
	row = start_row + excel_config['header_rows']
	#クラス種別順で出力
	for class_type in ['controller', 'service', 'component', 'mapper' ,'other']:
		sheet.cell(row=row, column=1, value=class_type.capitalize())
		#クラスの出力順をFQCNの昇順で出力
		cl = sorted(pinfo[class_type].items(), key=lambda x:x[0])
		for c in cl:
			if re.match(RE_EXCLUDE_CLASS, c[0]):
				continue
			if not c[1]['isClass']:
				continue
			sheet.cell(row=row, column=2, value=c[0])
			#メソッド種別順で出力
			for method_type in ['constructor', 'public-method', 'private-method']:
				#メソッド名の昇順で出力
				ml = sorted(c[1]['methods'][method_type], key=lambda x:x['name'])
				for m in ml:
					sheet.cell(row=row, column=3, value=m['name'])
					row += 1

def setColumnWidth(sheet):
	def _setColumnWidth(col_no):
		max_width = 0
		columns = list(sheet.columns)[col_no-1]
		for cell in columns:
			if len(str(cell.value)) > max_width:
				max_width = len(str(cell.value))
		#adjusted_width = (max_width + 2) * 1.2
		adjusted_width = max_width
		sheet.column_dimensions[columns[0].column_letter].width = adjusted_width
	_setColumnWidth(1)    #クラスタイプ
	_setColumnWidth(2)	  #FQCN
	_setColumnWidth(3)	  #メソッド

def outExcel(r):
	crud_config = getCrudConfig()
	#print(crud_config)

	book = openpyxl.Workbook()
	sheet = book.worksheets[0]

	sheet.title = 'crud methods'
	formatCrudSheet(sheet, crud_config)
	formatClassMethods(sheet, crud_config, r)

	setColumnWidth(sheet)

	book.save(getExcelBookPath(prefix='crud'))
	book.close()

def outMapperInfo(map_info):
	crud_config = getCrudConfig()
	excel_config = crud_config['Excel']
	start_row = excel_config['start_row']
	start_column = excel_config['start_column']
	row = start_row + excel_config['header_rows']
	alignment1 = Alignment(horizontal="center", vertical="center")
	def setCURD(crud_info):
		for crud_type, crud_tables in crud_info.items():
			for table in crud_tables:
				if table not in table_list:
					print('[%s] is not in CRUD list' % table)
					continue
				pos = start_column + table_list.index(table) * 4
				if crud_type == 'create':
					#pos += 0
					crud = 'C'
				elif crud_type == 'read':
					pos += 1
					crud = 'R'
				elif crud_type == 'update':
					pos += 2
					crud = 'U'
				elif crud_type == 'delete':
					pos += 3
					crud = 'D'
				else:
					assert False, "[%s] is not supported by Excel write process" % crud_type
				d = sheet.cell(row=row, column=pos, value=crud)
				d.alignment = alignment1

	book = openpyxl.Workbook()
	sheet = book.worksheets[0]
	sheet.title = 'mapper'
	table_list = formatCrudSheet(sheet, crud_config)
	for dao in sorted(map_info.items(), key=lambda x:x[0]):
		sheet.cell(row=row, column=1, value=dao[0])
		for map_id in sorted(dao[1]['dml'].items(), key=lambda x:(x[1]['type'], x[0])):
			sheet.cell(row=row, column=2, value=map_id[1]['type'])
			sheet.cell(row=row, column=3, value=map_id[0])
			setCURD(map_id[1]['crud'])
			row += 1

	book.save(getExcelBookPath(prefix='mapper'))
	book.close()

if __name__ == '__main__':
	import pathlib

	from daoReader import DaoReader as DR
	from crudJudgment import judgment

	myPath = pathlib.Path(__file__)
	xmlRoot = myPath.parent

	reader = DR()
	r = reader.readXmls(xmlRoot = xmlRoot / 'resources')

	judgment(r)
	outExcel(r)
#[EOF]