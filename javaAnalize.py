# -*- coding: utf-8 -*-
import json
import logging
import pathlib
import re
import shutil
import subprocess
import sys

from daoReader import DaoReader

class JavaAnalize():
    def __init__(self):
        # 定義情報の読込み
        myPath = pathlib.Path(__file__)
        json_path = myPath.parent / 'resources' / 'crudConfig.json'
        with json_path.open(mode='r', encoding='UTF8') as f:
            config = json.load(f)
        analize = config['analize']
        self._debug = analize['debug']
        self._jdkPath = analize['jdk-path']
        self._javapOptions = analize['javap-options']
        self._workPath = analize['work-path']
        self._projectRoot = analize['Project']['path']
        self._javaSrc = self._projectRoot + analize['Project']['java-src']
        self._projectClasses = self._projectRoot + analize['Project']['classes']
        self._mapperXMLPath = self._projectRoot + analize['Project']['mapper-xml']
        self._spring = analize['spring']
        self._project = {
            "controller": {},    # = analize.spring.controller in crudConfig.json
            "service": {},       # = analize.spring.service in crudConfig.json
            "component": {},     # = analize.spring.component in crudConfig.json
            "mapper": {},        # = analize.spring.mapper in crudConfig.json
            "other": {},         # else
        }
        self._java_re = {
            'class-re': re.compile(r'^(public|private)?\s*(final\s+)?(abstract\s+)?class\s+(?P<fqcn>\S+)', flags=(re.MULTILINE)),
            'interface-re': re.compile(r'^(public|private)?\s*interface\s+(?P<fqcn>\S+)', flags=(re.MULTILINE)),
            'implements-re': re.compile(r'public\s+class\s+\S+\s+implements\s+(?P<impl>\S+)', flags=(re.MULTILINE)),
            'constructor-re': re.compile(r'(public|private)\s+(?P<fqcn>\S+)\((?P<args>[^\(\)]*)\);$', flags=(re.MULTILINE)),
            'method1-re': re.compile(r'(?P<scope>(public|private))\s+(?P<ret>\S+)\s+(?P<method_name>\S+)\((?P<args>[^\(\)]*)\);$', flags=(re.MULTILINE)),
            'method2-re': re.compile(r'(?P<scope>(public|private))\s+abstract\s+(?P<ret>\S+)\s+(?P<method_name>\S+)\((?P<args>[^\(\)]*)\);$', flags=(re.MULTILINE)),
            'InterfaceMethodref-re': re.compile(r'\s*(?P<ref_no>#\d+)\s*=\s*InterfaceMethodref\s*\S+\s*\/\/\s*(?P<fqcn_method>[^\.]+\.\w+)'),
            'code-block-re': re.compile(r'\{(?P<code>.+)\}', flags=(re.MULTILINE | re.DOTALL)),
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
                for line in self.command(javap + ' ' + str(path)):
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
        m = re.search(self._java_re['class-re'], file)
        if m:
            fqcn = m.group('fqcn')
            isClass = True
        else:
            # インターフェースの判定（public interface xxx {)
            m = re.search(self._java_re['interface-re'], file)
            if m:
                fqcn = m.group('fqcn')

        impl = None
        # implementsを判定
        m = re.search(self._java_re['implements-re'], file)
        if m:
            impl = m.group('impl')

        return fqcn, impl, isClass

    def prepare(self, map_info):
        '''
        javapで参照するマッパーのキーワードを作成
        '''
        for fqcn, v1 in map_info.items():
            for method_name, v2 in v1['dml'].items():
                v2['javap'] = '%s.%s' % (fqcn.replace('.', '/'), method_name)

    def findMethods(self, file):
        m = re.search(self._java_re['code-block-re'], file)
        assert m, 'javaのコードが見つかりません.'
        code = m.group('code')
        #print(code)

        ret = {'constructor':[], 'public-method': [], 'private-method': []}
        #コンストラクタの判定
        for m in list(re.finditer(self._java_re['constructor-re'], code)):
            #print(str(m.string))
            nm = m.group('fqcn').split('.')[-1]
            ret['constructor'].append({'name': nm, 'args': m.group('args')})
        #メソッドの判定
        for m in list(re.finditer(self._java_re['method1-re'], code)):
            #print(str(m.string))
            scope = 'public-method' if m.group('scope') == 'public' else 'private-method'
            ret[scope].append({'name': m.group('method_name'), 'args': m.group('args')})
        #メソッドの判定(インターフェース用)
        for m in list(re.finditer(self._java_re['method2-re'], code)):
            #print(str(m.string))
            scope = 'public-method' if m.group('scope') == 'public' else 'private-method'
            ret[scope].append({'name': m.group('method_name'), 'args': m.group('args')})
        ##r = r'.+public\s+(?P<aaa>.+);$'
        #r = r'.+(public|private)\s+(?P<aaa>.+);$'
        #ms = list(re.finditer(r, code, flags=(re.MULTILINE)))
        #num = len(ms)
        #if num:
        #    for idx in range(num):                    
        #        #print(ms[idx].group("aaa"))
        #        if idx < num - 1:
        #            print(code[ms[idx].start():ms[idx+1].start()])
        #        else:
        #            print(code[ms[idx].start():])
        return ret

    def _getDaoInterfaceMethodref(self, file, map_info):
        '''
        デコンパイルの結果からDao呼び出しの一覧を作成
        '''
        ret = {}
        for m in list(re.finditer(self._java_re['InterfaceMethodref-re'], file)):
            fqcn_method = m.group('fqcn_method')
            #print('%s - %s' % (m.group('ref_no'), fqcn_method))
            for v1 in map_info.values():
                for v2 in v1['dml'].values():
                    if fqcn_method == v2['javap']:
                        ref_no = m.group('ref_no')
                        #print('%s - %s' % (ref_no, fqcn_method))
                        ret[ref_no] = fqcn_method
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
            logging.debug('java decompile source : %s' % str(path))
            with path.open(mode='r', encoding='utf-8') as f:
                buf = f.read()
                spring_type = self.checkSpringType(buf)
                cn, impl, isClass = self.getClass(buf)
                assert cn, 'no class/interface [%s]' % str(path)
                #print('%s(implements %s) is %s' % (cn, impl, spring_type))
                java_info = {'decompile_path': path, 'implements': impl, "isClass": isClass}
                if spring_type:
                    self._project[spring_type][cn] = java_info
                else:
                    self._project['other'][cn] = java_info
                java_info['mapper-refs'] = self._getDaoInterfaceMethodref(buf, map_info)
                java_info['methods'] = self.findMethods(buf)

    def analize(self, map_info):
        self.prepare(map_info)
        self._analize_1(map_info)
        '''
        self._project = {
          "controller": {    -- コントローラクラス一覧
            FQCN_1: {
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
    from outExcel import outMapperInfo

    log_format = '%(levelname)s : %(asctime)s : %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    #logging.basicConfig(level=logging.INFO, format=log_format)

    ana = JavaAnalize()
    dao = DaoReader(ana.getMapperXMLPath())
    map_info = dao.readXmls()
    if ana._debug['mapper-excel']:
        outMapperInfo(map_info)
    ana.analize(map_info)
    outExcel(ana._project)
    logging.info('解析終了')
#[EOF]