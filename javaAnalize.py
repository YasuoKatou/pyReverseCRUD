# -*- coding: utf-8 -*-

class JavaAnalize():
    def analize(self, javaRoot = None):
        print('java root : %s' % str(javaRoot))
        for path in list(javaRoot.glob('**/*.java')):
            print('read : %s' % str(path))

if __name__ == '__main__':
    import pathlib
    import sys

    javaRoot = ''
    argvs = sys.argv
    if len(argvs) > 1:
        javaRoot = pathlib.Path(argvs[1])
    else:
        myPath = pathlib.Path(__file__)
        javaRoot = myPath.parent

    ana = JavaAnalize()
    ana.analize(javaRoot = javaRoot / 'resources')
#[EOF]