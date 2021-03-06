# -*- coding: utf-8 -*-

import json
import logging
import pathlib
import re
import shutil
import subprocess
import sys

from Constants import JAVAP_REs, getWordRE

class JavaAnalize():
    def __init__(self):
        # 定義情報の読込み
        myPath = pathlib.Path(__file__)
        json_path = myPath.parent / 'resources' / 'crudConfig.json'
        with json_path.open(mode='r', encoding='UTF8') as f:
            config = json.load(f)
        self._tables = config['tables']
        self._others = config['others']
        analize = config['analize']
        self._debug = analize['debug']
        self._jdkPath = analize['jdk-path']
        self._javapOptions = analize['javap-options']
        self._workPath = analize['work-path']
        self._projectRoot = analize['Project']['path']
        self._javaSrc = self._projectRoot + analize['Project']['java-src']
        self._projectClasses = self._projectRoot + analize['Project']['classes']
        self._mapperXMLPath = self._projectRoot + analize['Project']['mapper-xml']
        self._viewDefPath = analize['Project']['view-def-path']

        self._spring = analize['spring']
        self._project = {
            "controller": {},    # = analize.spring.controller in crudConfig.json
            "service": {},       # = analize.spring.service in crudConfig.json
            "component": {},     # = analize.spring.component in crudConfig.json
            "mapper": {},        # = analize.spring.mapper in crudConfig.json
            "other": {},         # else
        }
        # ワークフォルダを初期化する
        if self._debug['decompile']:
            logging.info('init java decompile workspace')
            wp = pathlib.Path(self._workPath)
            if wp.exists():
                shutil.rmtree(str(wp))
            wp.mkdir()

    def getMapperXMLPath(self):
        return self._mapperXMLPath

    def getTablesRE(self):
        r = {}
        for table_group in self._tables.values():
            for tables in table_group:
                for t in tables.keys():
                    tn = t.lower()
                    if tn not in r.keys():
                        r[tn] = getWordRE(tn)
                    else:
                        logging.info('[%s] is duplicated' % tn)
        return r

    def getViewsRE(self):
        r = {}
        for vn in self._others['views']:
            if vn not in r.keys():
                r[vn.lower()] = getWordRE(vn.lower())
            else:
                logging.info('[%s] is duplicated' % vn)
            
        return r

    def command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, check=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True)
            for line in result.stdout.splitlines():
                yield line
        except subprocess.CalledProcessError:
            print('外部プログラムの実行に失敗しました [' + cmd + ']', file=sys.stderr)
            sys.exit(1)

    def decompile(self):
        classes = pathlib.Path(self._projectClasses)
        if not classes.exists():
            print('java class のルートパスが見つかりません(' + self._projectClasses +')')
            sys.exit(1)
        logging.info('java class file path : %s' % classes)

        javap = "\"%s\\javap\" %s" % (self._jdkPath, self._javapOptions)
        pos = len(str(classes))
        for path in list(classes.glob('**/*.class')):
            logging.debug('java class : %s' % str(path))
            decompPath = pathlib.Path(self._workPath + str(path)[pos:])
            #if not decompPath.exists():
            decompPath.parent.mkdir(parents=True, exist_ok=True)
            with decompPath.open(mode='w', encoding='utf-8') as f:
                for line in self.command(javap + ' \"' + str(path) + '\"'):
                    f.write(line + '\n')

    def checkSpringType(self, file):
        for spring_type, type_info in self._spring.items():
            r = ''
            for k, v in type_info['checkAnnotations'].items():
                r = r + k + r'.*'
                if isinstance(v, list):
                    r = '(%s)' % '|'.join(v)
                else:
                    r += v
                if re.search(r, file, flags=re.MULTILINE | re.DOTALL):
                    return spring_type
        return None

    def getClass(self, file):
        '''
        クラス(インターフェース)ファイルのFQCNとimplementsを取得する
        '''
        fqcn = None
        isClass = False
        # クラスの判定(public class xxxx {)
        m = re.search(JAVAP_REs['class'], file)
        if m:
            fqcn = m.group('fqcn')
            isClass = True
        else:
            # インターフェースの判定（public interface xxx {)
            m = re.search(JAVAP_REs['interface'], file)
            if m:
                fqcn = m.group('fqcn')

        impl = None
        # implementsを判定
        m = re.search(JAVAP_REs['implements'], file)
        if m:
            impl = m.group('impl')

        # javaソースファイル
        source_file = None
        m = re.search(JAVAP_REs['java-source'], file)
        if m:
            source_file = m.group('source_file')

        return fqcn, impl, isClass, source_file

    def prepare(self, map_info):
        '''
        javapで参照するマッパーのキーワードを作成
        '''
        for fqcn, v1 in map_info.items():
            for method_name, v2 in v1['dml'].items():
                v2['javap'] = '%s.%s' % (fqcn.replace('.', '/'), method_name)

    def findMethods(self, class_name, mapper_refs, file):
        m = re.search(JAVAP_REs['code-block'], file)
        assert m, 'javaのコードブロックが見つかりません.'
        code = m.group(0)
        #print(code)
        ret = {'constructor':[], 'public-method': [], 'private-method': []}
        for mb in list(re.finditer(JAVAP_REs['method-block'], code)):
            method_code = mb.group(0)
            #コンストラクタ／メソッドの判定
            for m in list(re.finditer(JAVAP_REs['method'], method_code)):
                #print(str(m.string))
                fqcn = m.group('fqcn')
                if fqcn == class_name:
                    #コンストラクタ
                    nm = fqcn.split('.')[-1]
                    item = {'name': nm, 'args': m.group('args'), 'mapper': []}
                    ret['constructor'].append(item)
                else:
                    #メソッド
                    deco = [val for val in m.group('deco').split(' ') if val]
                    scope = 'private-method' if 'private' in deco else 'public-method'
                    item = {'name': fqcn, 'args': m.group('args'), 'mapper': []}
                    ret[scope].append(item)
            #マッパー参照の確認
            for m in list(re.finditer(JAVAP_REs['ref-no'], method_code)):
                ref_no = m.group('ref_no')
                if ref_no in mapper_refs.keys():
                    mp = mapper_refs[ref_no]
                    item['mapper'].append(mp)
                #else:
                #    logging.error('mapper(%s) not found \n===\n%s\n---\n' % (ref_no, method_code))
                #    assert False, 'mapper not found'
                # マッパー以外もあり得るのでここではエラーとできない
        return ret

    def _searchMapperRefs(self, file, map_info):
        '''
        デコンパイルの結果からDao呼び出しの一覧を作成
        '''
        ret = {}
        for m in list(re.finditer(JAVAP_REs['interface-method-ref'], file)):
            fqcn_method = m.group('fqcn_method')
            #print('%s - %s' % (m.group('ref_no'), fqcn_method))
            for v1 in map_info.values():
                for v2 in v1['dml'].values():
                    if fqcn_method == v2['javap']:
                        ref_no = m.group('ref_no')
                        #print('%s - %s' % (ref_no, fqcn_method))
                        ret[ref_no] = v2
        return ret

    def _analize_1(self, map_info):
        '''
        ソースファイルをアノテーションから分類する.
        分類：コントローラ、サービス、コンポーネント、マッパー、その他
        '''
        if self._debug['decompile']:
            self.decompile()
        classes = pathlib.Path(self._workPath)
        logging.info('java analize root : %s' % str(classes))
        # クラスの種別（コントローラ、サービス、コンポーネント）を判定
        for path in list(classes.glob('**/*.class')):
            logging.debug('java decompile read : %s' % str(path))
            with path.open(mode='r', encoding='utf-8') as f:
                buf = f.read()
                spring_type = self.checkSpringType(buf)
                cn, impl, isClass, source_name = self.getClass(buf)
                assert cn, 'no class/interface [%s]' % str(path)
                #print('%s(implements %s) is %s' % (cn, impl, spring_type))
                wk = cn.split('.')
                p = '' if len(wk) == 1 else '.'.join([wk[i] for i in range(0, len(wk)-1)])
                java_info = {'source_path': '%s.%s.java' % (p, source_name)
                    ,'decompile_path': path, 'implements': impl, "isClass": isClass}
                if spring_type:
                    self._project[spring_type][cn] = java_info
                else:
                    self._project['other'][cn] = java_info
                mapper_refs = self._searchMapperRefs(buf, map_info)
                java_info['methods'] = self.findMethods(cn, mapper_refs, buf)

    def analize(self, map_info):
        self.prepare(map_info)
        self._analize_1(map_info)
        '''
        self._project = {
          "controller": {    -- コントローラクラス一覧
            FQCN_1: {
              "source_path": (path)
              "decompile_path": (full path),
              "implements": (= interface FQCN),
              "methods": (*1)
            }
          },
          "service": {},     -- サービスクラス一覧
          "component": {},   -- コンポーネントクラス一覧
          "mapper": {},      -- マッパークラス一覧
          "other": {},       -- その他クラス一覧
        }
        (*1)
        "methods": {
            "constructor": [{"name": xxxx, "args": yyyy},],
            "public-method": [{"name": xxxx, "args": yyyy},],
            "private-method": [{"name": xxxx, "args": yyyy},]
        }
        '''
if __name__ == '__main__':
    from outExcel import outExcel
    from outExcel import outMapperInfo, view2table
    from daoReader import DaoReader
    from othersDefine import readViewDedine

    log_format = '%(levelname)s : %(asctime)s : %(message)s'
    #logging.basicConfig(level=logging.DEBUG, format=log_format)
    logging.basicConfig(level=logging.INFO, format=log_format)

    ana = JavaAnalize()
    dao = DaoReader(ana.getMapperXMLPath())
    tableRE = ana.getTablesRE()
    viewRE  = ana.getViewsRE()
    map_info = dao.readXmls(tableRE=tableRE, viewRE=viewRE)
    view_info = readViewDedine(ana._viewDefPath, tableRE)
    view2table(map_info, view_info)
    if ana._debug['mapper-excel']:
        outMapperInfo(map_info, view_info)
    ana.analize(map_info)
    outExcel(ana._project, view_info)
    logging.info('解析終了')
#[EOF]