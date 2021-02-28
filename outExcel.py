# -*- coding: utf-8 -*-
import datetime
import json
import openpyxl
import pathlib

from openpyxl.styles import Border, Side, PatternFill, Font, GradientFill, Alignment

def getExcelBookPath():
	def getExcelBookName():
		now = datetime.datetime.now()
		return now.strftime("crud_%Y%m%d_%H%M%S.xlsx")
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
	for key, name in excel_config['tables'].items():
		print(key + ': ' + name)
		num = len(crud_config['tables'][key])
		d = sheet.cell(row=row, column=col, value=name)
		d.alignment = alignment1
		sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+num*4-1)
		count = 0
		for table in crud_config['tables'][key]:
			for k, v in table.items():
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

def formatClassMethods(sheet, crud_config, pinfo):
	excel_config = crud_config['Excel']
	start_row = excel_config['start_row']
	row = start_row + excel_config['header_rows']
	#クラス種別順で出力
	for class_type in ['controller', 'service', 'component', 'mapper' ,'other']:
		sheet.cell(row=row, column=1, value=class_type.capitalize())
		#クラスの出力順をFQCNの昇順で出力
		cl = sorted(pinfo[class_type].items(), key=lambda x:x[0])
		for c in cl:
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

	book.save(getExcelBookPath())
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