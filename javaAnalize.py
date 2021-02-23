# -*- coding: utf-8 -*-
import json
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
        # ワークフォルダを初期化する
        if self._debug['decompile']:
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

        javap = self._jdkPath + '\\javap' + ' ' + self._javapOptions
        pos = len(str(classes))
        for path in list(classes.glob('**/*.class')):
            print('java class : %s' % str(path))
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
                    r += r'.*'.join(v)
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
        # クラスの判定(public class xxxx {)
        key = r'public\s+class\s+(?P<fqcn>\S+)'
        m = re.search(key, file)
        if m:
            fqcn = m.group('fqcn')
        else:
            # インターフェースの判定（public interface xxx {)
            key = r'public\s+interface\s+(?P<fqcn>\S+)'
            m = re.search(key, file)
            if m:
                fqcn = m.group('fqcn')

        impl = None
        # implementsを判定
        key = r'public\s+class\s+\S+\s+implements\s+(?P<impl>\S+)'
        m = re.search(key, file)
        if m:
            impl = m.group('impl')

        return fqcn, impl

    def findMethods(self, file):
        r = r'\{(?P<code>.+)\}'
        m = re.search(r, file, flags=(re.MULTILINE | re.DOTALL))
        assert m, 'javaのコードが見つかりません.'
        code = m.group('code')
        #print(code)

        ret = {'constructor':[], 'public-method': [], 'private-method': []}
        #コンストラクタの判定
        r = r'(public|private)\s+(?P<fqcn>\S+)\((?P<args>\S*)\);$'
        for m in list(re.finditer(r, code, flags=(re.MULTILINE))):
            #print(m.group('fqcn'))
            nm = m.group('fqcn').split('.')[-1]
            #print(nm)
            ret['constructor'].append({'name': nm, 'args': m.group('args')})
        #メソッドの判定
        r = r'(?P<scope>(public|private))\s+(?P<ret>\S+)\s+(?P<method_name>\S+)\((?P<args>\S*)\);$'
        for m in list(re.finditer(r, code, flags=(re.MULTILINE))):
            #print(m.group('scope') + ' ' + m.group('method_name'))
            scope = 'public-method' if m.group('scope') == 'public' else 'private-method'
            ret[scope].append({'name': m.group('method_name'), 'args': m.group('args')})
        #メソッドの判定(インターフェース用)
        r = r'(?P<scope>(public|private))\s+abstract\s+(?P<ret>\S+)\s+(?P<method_name>\S+)\((?P<args>\S*)\);$'
        for m in list(re.finditer(r, code, flags=(re.MULTILINE))):
            #print(m.group('scope') + ' ' + m.group('method_name'))
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

    def _analize_1(self):
        '''
        ソースファイルをアノテーションから分類する.
        分類：コントローラ、サービス、コンポーネント、マッパー、その他
        '''
        if self._debug['decompile']:
            self.decompile()
        classes = pathlib.Path(self._workPath)
        # クラスの種別（コントローラ、サービス、コンポーネント）を判定
        for path in list(classes.glob('**/*.class')):
            with path.open(mode='r') as f:
                buf = f.read()
                spring_type = self.checkSpringType(buf)
                cn, impl = self.getClass(buf)
                #print('%s(implements %s) is %s' % (cn, impl, spring_type))
                java_info = {'decompile_path': path, 'implements': impl}
                if spring_type:
                    self._project[spring_type][cn] = java_info
                else:
                    self._project['other'][cn] = java_info
                java_info['methods'] = self.findMethods(buf)

    def analize(self):
        self._analize_1()
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
    from crudJudgment import judgment
    from outExcel import outExcel

    ana = JavaAnalize()
    dao = DaoReader(ana.getMapperXMLPath())
    r = dao.readXmls()
    judgment(r)
    ana.analize()
    outExcel(ana._project)
    print('解析終了')
#[EOF]