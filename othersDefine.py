# -*- coding: utf-8 -*-

import pathlib
import re

from Constants import DDL_REs

def readViewFedine(defPath, tableList):
	assert tableList, 'no table names'
	vl = {}
	p = pathlib.Path(defPath)
	for fp in list(p.glob('**/*.sql')):
		with fp.open(mode='r', encoding='utf-8') as f:
			viewFile = f.read()
			for m in list(re.finditer(DDL_REs['create-view'], viewFile)):
				tables = []
				def_body = m.group('view_def')
				for tn, t_re in tableList.items():
					if re.search(t_re, def_body):
						tables.append(tn)
				vl[m.group('view_name')] = tables
	return vl
#[EOF]