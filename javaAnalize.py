# -*- coding: utf-8 -*-
import json
import pathlib
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
        self._jdkPath = config['analize']['jdk-path']
        self._javapOptions = config['analize']['javap-options']
        self._workPath = config['analize']['work-path']
        self._projectRoot = config['analize']['Project']['path']
        self._javaSrc = self._projectRoot + config['analize']['Project']['java-src']
        self._projectClasses = self._projectRoot + config['analize']['Project']['classes']
        # ワークフォルダを初期化する
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

    def analize(self):
        #print('java root : %s' % str(self._javaSrc))
        #javaRoot = pathlib.Path(self._javaSrc)
        #for path in list(javaRoot.glob('**/*.java')):
        #    print('read : %s' % str(path))
        self.decompile()

if __name__ == '__main__':
    ana = JavaAnalize()
    ana.analize()
#[EOF]