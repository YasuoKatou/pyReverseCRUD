import re

DML_REs = {
	'insert': re.compile(r"insert\s+into\s+(?P<table_name>\w+)", flags=(re.MULTILINE | re.IGNORECASE)),
	'update': re.compile(r"update\s+(?P<table_name>\w+)", flags=(re.MULTILINE | re.IGNORECASE)),
	'delete': re.compile(r"delete\s+from\s+(?P<table_name>\w+)", flags=(re.MULTILINE | re.IGNORECASE)),
}

DDL_REs = {
	'create-view' : re.compile(r'CREATE\s+(OR\s+REPLACE\s+)?(TEMP\s+|TEMPORARY\s+)?(RECURSIVE\s+)?VIEW\s+(?P<view_name>\S+)(?P<view_def>.*?);', flags=(re.DOTALL | re.IGNORECASE)),
}

SQL_REs = {
	'comment1' : re.compile(r'--.*$', flags=(re.MULTILINE)),
}

WORD_REs = {

}

JAVAP_REs = {
	# コード部分を抽出する正規表現
	'code-block': re.compile(r'\{.+\}', flags=(re.DOTALL)),
	# １メソッドを抽出する正規表現
	'method-block': re.compile(r'.+?\n(\n|\})', flags=(re.DOTALL)),
	# コンストラクタ及びメソッドを抽出する正規表現
	'method': re.compile(r'(?P<deco>.*?)(?<!\/\/ Method )(?P<fqcn>[a-zA-Z0-9_\$\.]+)\((?P<args>[^\(\)]*)\).*;$', flags=(re.MULTILINE)),
	'interface-method-ref': re.compile(r'\s*(?P<ref_no>#\d+)\s*=\s*InterfaceMethodref\s*\S+\s*\/\/\s*(?P<fqcn_method>[^\.]+\.\w+)'),

	# クラス名を抽出する正規表現
	'class': re.compile(r'^(public|private)?\s*(final\s+)?(abstract\s+)?class\s+(?P<fqcn>\S+)', flags=(re.MULTILINE)),
	# インターフェース名を抽出する正規表現
	'interface': re.compile(r'^(public|private)?\s*interface\s+(?P<fqcn>\S+)', flags=(re.MULTILINE)),
	# 継承元を抽出する正規表現
	'implements': re.compile(r'public\s+class\s+\S+\s+implements\s+(?P<impl>\S+)', flags=(re.MULTILINE)),
	# ソースファイルを抽出する正規表現
	'java-source': re.compile(r'Compiled\s+from\s+"(?P<source_file>\S+)\.java"', flags=(re.MULTILINE)),
	'ref-no': re.compile(r'\d+:\s*invokeinterface\s*(?P<ref_no>#\d+)', flags=(re.MULTILINE)),
}

def getWordRE(word):
	return re.compile(r'[^\w]%s[^\w\.]' % word, flags=(re.MULTILINE | re.IGNORECASE))

#[EOF]