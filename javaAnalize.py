# -*- coding: utf-8 -*-
import json
import pathlib
import re
import shutil
import subprocess
import sys

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
        self._spring = analize['spring']
        self._springController = []
        self._springService = []
        self._springComponent = []
        self._springMapper = []
        # ワークフォルダを初期化する
        if self._debug['decompile']:
            wp = pathlib.Path(self._workPath)
            if wp.exists():
                shutil.rmtree(str(wp))
            wp.mkdir()

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

    def checkSpringType(self, keys, file):
        r = ''
        for k, v in keys.items():
            r = r + k + r'.*'
            if isinstance(v, list):
                r += r'.*'.join(v)
            else:
                r += v
        return re.search(r, file, flags=re.MULTILINE | re.DOTALL)

    def getClass(self, file):
        '''
        クラス(インターフェース)ファイルのFQCNとimplementsを取得する
        '''
        fqcn = None
        key = r'public\s+class\s+(?P<fqcn>\S+)'
        m = re.search(key, file)
        if m:
            fqcn = m.group('fqcn')
        else:
            key = r'public\s+interface\s+(?P<fqcn>\S+)'
            m = re.search(key, file)
            if m:
                fqcn = m.group('fqcn')

        impl = None
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

        r = r'.+public\s+(?P<aaa>.+);$'
        ms = list(re.finditer(r, code, flags=(re.MULTILINE)))
        if len(ms):
            for m in ms:
                print(m.group("aaa"))

    def analize(self):
        if self._debug['decompile']:
            self.decompile()
        classes = pathlib.Path(self._workPath)
        # クラスの種別（コントローラ、サービス、コンポーネント）を判定
        for path in list(classes.glob('**/*.class')):
            with path.open(mode='r') as f:
                buf = f.read()
            for k, v in self._spring.items():
                if self.checkSpringType(v['checkAnnotations'], buf):
                    cn, impl = self.getClass(buf)
                    print('%s(implements %s) is %s' % (cn, impl, k))
                    self.findMethods(buf)

if __name__ == '__main__':
    ana = JavaAnalize()
    ana.analize()
#[EOF]