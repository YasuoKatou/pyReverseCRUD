# -*- coding: utf-8 -*-

import logging
import pathlib
import re
import xml.etree.ElementTree as ET

from crudJudgment import judgment

from Constants import SQL_REs

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
        r['query'] = re.sub(SQL_REs['comment1'], r'', wk)
        return r

    def readXmls(self, xmlRoot = None, tableRE = []):
        if not xmlRoot:
            xmlRoot = pathlib.Path(self.resourceRoot)
        logging.info('Mapper xml root : %s' % str(xmlRoot))
        rr = {}
        for path in list(xmlRoot.glob('**/*.xml')):
            logging.debug('read : %s' % str(path))
            dmlChildren = []
            sqlIncludes = {}
            r = {'mapper': None, 'dml': {}}
            root = ET.parse(str(path))
            for child in root.iter():
                #print(child.tag, child.attrib)
                tagName = child.tag.lower()
                if tagName == 'mapper':
                    ns = child.attrib['namespace']
                    r['mapper'] = self.getMapperInterface(ns)
                    rr[ns] = r
                elif tagName in ('select', 'insert', 'update', 'delete'):
                    dmlChildren.append(child)
                elif tagName == 'sql':
                    sqlIncludes[child.attrib['id']] = "".join(child.itertext())
            for child in dmlChildren:
                tagName = child.tag.lower()
                if tagName in ('select', 'insert', 'update', 'delete'):
                  r['dml'][child.attrib['id']] = self.expandDml(tagName, child, sqlIncludes)
            judgment(r, tableRE)
        return rr

    '''
    {
      FQCN_1 (= tag:mapper attribute:namespace): {
        "mapper" {
          "interface": (interface name of FQCN_1)
          "package":   (package name of FQCN_1)
        },
        "dml" {
          DML_1 (= tag:select attribute:id): {
            "type": (= tag:insert/select/update/delete),
            "query": [
              query source  (次のステップで対象テーブルを判定する)
            ]
          }
        }
      }
    },{
      FQCN_2 (= tag:mapper attribute:namespace): {
        :
        :
    }
    '''
#[EOF]