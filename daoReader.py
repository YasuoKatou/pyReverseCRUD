# -*- coding: utf-8 -*-

import re
import xml.etree.ElementTree as ET

class DaoReader():
    def __init__(self, resourceRoot = None):
        self.resourceRoot = resourceRoot

    def getMapperInterface(self, mapper):
        wk = mapper.split('.')
        r = {}
        r['interface'] = wk.pop(len(wk)-1)
        if len(wk) > 0:
            r['package'] = '.'.join(wk)
        else:
            r['package'] = ''
        return r

    def removeCRFL(self, source):
        def removeComment(_line):
            _w = _line.split('--', 1)
            return _w[0].strip()
            
        r = []
        for line in re.split(r'[\n\r]', source):
            wk = line.strip()
            if wk:
                wk = removeComment(wk)
                if wk:
                    r.append(wk + '\n')
        return r

    def expandDml(self, dmlType, xml, sqlIncludes):
        r = {'type': dmlType}
        wk = ''
        for v in list(xml.iter()):
            if v.tag == 'include':
                wk += sqlIncludes[v.attrib['refid']]
            if v.text:
                wk += v.text
            if v.tail:
                wk += v.tail
        r['query'] = self.removeCRFL(wk)
        return r

    def readXmls(self, xmlRoot = None):
        if not xmlRoot:
            xmlRoot = self.resourceRoot
        print('xml root : %s' % str(xmlRoot))
        rr = {}
        for path in list(xmlRoot.glob('**/*.xml')):
            print('read : %s' % str(path))
            dmlChildren = []
            sqlIncludes = {}
            r = {'mapper': None, 'dml': {}}
            root = ET.parse(str(path))
            for child in root.iter():
                print(child.tag, child.attrib)
                tagName = child.tag.lower()
                if tagName == 'mapper':
                    ns = child.attrib['namespace']
                    r['mapper'] = self.getMapperInterface(ns)
                    rr[ns] = r
                elif tagName in ('select', 'insert', 'update'):
                    dmlChildren.append(child)
                elif tagName == 'sql':
                    sqlIncludes[child.attrib['id']] = "".join(child.itertext())
            for child in dmlChildren:
                tagName = child.tag.lower()
                if tagName in ('select', 'insert', 'update'):
                  r['dml'][child.attrib['id']] = self.expandDml(tagName, child, sqlIncludes)
        return rr

if __name__ == '__main__':
    import pathlib
    import sys

    xmlRoot = ''
    argvs = sys.argv
    if len(argvs) > 1:
        xmlRoot = pathlib.Path(argvs[1])
    else:
        myPath = pathlib.Path(__file__)
        xmlRoot = myPath.parent

    reader = DaoReader()
    reader.readXmls(xmlRoot = xmlRoot / 'resources')
#[EOF]