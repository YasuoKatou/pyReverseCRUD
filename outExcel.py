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
				d = sheet.cell(row=r, column=c, value=k)
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

def outExcel(r):
	crud_config = getCrudConfig()
	#print(crud_config)

	book = openpyxl.Workbook()
	sheet = book.worksheets[0]
	sheet.title = "CRUD"

	formatCrudSheet(sheet, crud_config)

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