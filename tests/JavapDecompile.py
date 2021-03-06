import re
import unittest

from Constants import JAVAP_REs

#
# S01：javapでデコンパイルした結果から「コード」ブロック及び「コンストラクタ／メソッド」ブロック抽出確認に使用するデータ
#
S01 = '''\
public class jp.yks.springboot.sample002.controller.HogeController
{
  private jp.yks.sample.controller.HogeController();
    descriptor: ()V
    flags: (0x0001) ACC_PUBLIC

  public void if001();
    descriptor: ()V
    flags: (0x0001) ACC_PUBLIC
}
SourceFile: "HogeController.java"
RuntimeVisibleAnnotations:
  0: #38()
    org.springframework.web.bind.annotation.RestController
'''

#
# S02：javapでデコンパイルした結果から「コンストラクタ」抽出確認に使用するデータ
#
S02 = '''\
{
  public App();
    descriptor: ()V
    flags: (0x0001) ACC_PUBLIC

  private jp.yks.sample.controller.HogeController();
    descriptor: ()V
    flags: (0x0001) ACC_PUBLIC

  public jp.yks.sample.controller.HogeController(java.lang.Integer, java.lang.String, java.lang.String, java.lang.String);
    descriptor: (Ljava/lang/Integer;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    flags: (0x0001) ACC_PUBLIC
    Code:
'''

#
# S03：javapでデコンパイルした結果から「メソッド」抽出確認に使用するデータ
#
S03 = '''\
{
  public java.lang.String getDivisionCode();
    descriptor: ()Ljava/lang/String;
    flags: (0x0001) ACC_PUBLIC
    Code:
      stack=1, locals=1, args_size=1

  public static void main(java.lang.String[]) throws java.lang.Exception;
    descriptor: ([Ljava/lang/String;)V
    flags: (0x0009) ACC_PUBLIC, ACC_STATIC
    Exceptions:
      throws java.lang.Exception
    Code:

  protected void setUp() throws java.lang.Exception;
    descriptor: ()V
    flags: (0x0004) ACC_PROTECTED
    Code:
      stack=0, locals=1, args_size=1
         0: return

  synchronized void waitUntilFinished();
    descriptor: ()V
    flags: (0x0020) ACC_SYNCHRONIZED
    Code:
        11: invokevirtual #12                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
'''

#
# S04_1：javapでデコンパイルした結果からクラス名、パッケージ名およびソースファイル名を取得
#
S04_1 = '''\
Classfile /Z:/junit-4.11/classes/extensions/ActiveTestSuite.class
  Last modified 2012/11/14; size 2071 bytes
  SHA-256 checksum 5aaec6e709e96f38fbe6b539d348ceef4ac88c0ec442120afb88905bd6db31b2
  Compiled from "ActiveTestSuite.java"
public class junit.extensions.ActiveTestSuite extends junit.framework.TestSuite
  minor version: 0
  major version: 49
  flags: (0x0021) ACC_PUBLIC, ACC_SUPER
'''

#
# S04_2：javapでデコンパイルした結果からクラス名、パッケージ名およびソースファイル名を取得
#
S04_2 = '''\
Classfile /Z:/junit-4.11/classes/extensions/ActiveTestSuite$1.class
  Last modified 2012/11/14; size 986 bytes
  SHA-256 checksum 4cb7cea76a72075cfae9ff71cb6f38b1844b6926163da3cc71fd003f0c875243
  Compiled from "ActiveTestSuite.java"
class junit.extensions.ActiveTestSuite$1 extends java.lang.Thread
  minor version: 0
  major version: 49
  flags: (0x0020) ACC_SUPER
'''

#
# S04_3：javapでデコンパイルした結果からクラス名、パッケージ名およびソースファイル名を取得
#
S04_3 = '''\
Classfile /Z:/workspace/java/java_source_analize/junit-4.11/classes/extensions/package-info.class
  Last modified 2012/11/14; size 122 bytes
  SHA-256 checksum 68199e5c4ec5c531c0567593f72352327c017154d53d7be7940f901953c81140
  Compiled from "package-info.java"
interface junit.extensions.package-info
  minor version: 0
  major version: 49
  flags: (0x0200) ACC_INTERFACE
'''

class JavapDecompileTest(unittest.TestCase):
	'''
	javapでdecompileした解析に使用する正規表現パターンを検証する
	'''
	def test_001(self):
		'''
		コード部の抽出を確認する
		'''
		m = re.search(JAVAP_REs['code-block'], S01)

		self.assertIsNotNone(m, 'not found code block')
		s = m.group(0)
		self.assertEqual(s[0], '{', 'not found open braces')
		self.assertEqual(s[-1], '}', 'not found close braces')

	def test_002(self):
		'''
		メソッドブロックの抽出を確認する
		'''
		m1 = re.search(JAVAP_REs['code-block'], S01)
		m2 = re.finditer(JAVAP_REs['method-block'], m1.group(0))
		self.assertIsNotNone(m2, 'not method code block')
		ml = list(m2)
		# メソッドブロック数を確認
		self.assertEqual(len(ml), 2, 'method count not equals')

		n = 0
		# 最初のブロックの開始を確認
		wk = ml[n].group(0)
		n += 1
		m = re.match(r'^\{\n  private jp\.yks\..+', wk)
		self.assertIsNotNone(m, 'block #%d start string error' % n)
		# 最初のブロックの終了を確認
		m = re.match(r'.+\n\n', wk, flags=(re.DOTALL))
		self.assertIsNotNone(m, 'block #%d tail string error' % n)
		# ２ブロックの開始を確認
		wk = ml[n].group(0)
		n += 1
		wk = ml[1].group(0)
		m = re.match(r'^  public void .+', wk)
		self.assertIsNotNone(m, 'block #%d start string error' % n)
		# ２ブロックの終了を確認
		m = re.match(r'.+\n\}', wk, flags=(re.DOTALL))
		self.assertIsNotNone(m, 'block #%d tail string error' % n)

	def test_003(self):
		s = ' aaa bbb cc.cc(ddd) eee fff;'
		m = re.search(r'(?P<deco>.*?)(?P<fqcn>[a-zA-Z0-9_\$\.]+)\((?P<args>[^\(\)]*)\).*;$', s)
		self.assertIsNotNone(m, 'test_003 is not match')
		self.assertEqual(m.group('fqcn'), 'cc.cc', 'test_003 fqcn not match')
		deco = [val for val in m.group('deco').split(' ') if val]
		self.assertEqual(len(deco), 2, 'test_003 has decorations')
		self.assertEqual(deco[0], 'aaa', 'test_003 1st decoration error')
		self.assertEqual(deco[1], 'bbb', 'test_003 1st decoration error')

	def test_101(self):
		'''
		コンストラクタの抽出を確認する
		'''
		m1 = re.finditer(JAVAP_REs['method'], S02)
		self.assertIsNotNone(m1, 'none constructor')
		m2 = list(m1)
		self.assertEqual(len(m2), 3, 'constructors not match')

		n = 0
		# １番目のコンストラクタを確認
		m = m2[n]
		n += 1
		self.assertEqual(m.group('fqcn'), 'App', 'constructor #%d FQCN not match' % n)
		self.assertFalse(m.group('args'), 'constructor #%d has no args' % n)
		deco = [val for val in m.group('deco').split(' ') if val]
		self.assertEqual(len(deco), 1, 'constructor #%d has decorations' % n)
		self.assertEqual(deco[0], 'public', 'constructor #%d 1st decoration error' % n)
		# ２番目のコンストラクタを確認
		m = m2[n]
		n += 1
		self.assertEqual(m.group('fqcn'), 'jp.yks.sample.controller.HogeController', 'constructor #%d FQCN not match' % n)
		self.assertFalse(m.group('args'), 'constructor #%d has no args' % n)
		deco = [val for val in m.group('deco').split(' ') if val]
		self.assertEqual(len(deco), 1, 'constructor #%d has decorations' % n)
		self.assertEqual(deco[0], 'private', 'constructor #%d 1st decoration error' % n)
		# ３番目のコンストラクタを確認
		m = m2[n]
		n += 1
		self.assertEqual(m.group('fqcn'), 'jp.yks.sample.controller.HogeController', 'constructor #%d FQCN not match' % n)
		args = m.group('args')
		self.assertTrue(args, 'constructor #%d has args' % n)
		args_conf = ['java.lang.Integer', 'java.lang.String', 'java.lang.String', 'java.lang.String']
		wk = [val.strip() for val in args.split(',')]
		self.assertEqual(len(wk), len(args_conf), 'constructor #%d args not match' % n)
		for index in range(len(args_conf)):
			self.assertEqual(args_conf[index], wk[index], 'constructor #%d arg(%d) type not match' % (n, (index+1)))
		deco = [val for val in m.group('deco').split(' ') if val]
		self.assertEqual(len(deco), 1, 'constructor #%d has decorations' % n)
		self.assertEqual(deco[0], 'public', 'constructor #%d 1st decoration error' % n)

	def test_201(self):
		'''
		メソッドの抽出を確認する
		'''
		m1 = re.finditer(JAVAP_REs['method'], S03)
		self.assertIsNotNone(m1, 'none method')
		m2 = list(m1)
		self.assertEqual(len(m2), 4, 'methods not match')

		n = 0
		# １番目のメソッドを確認
		m = m2[n]
		n += 1
		self.assertEqual(m.group('fqcn'), 'getDivisionCode', 'method #%d return value not match' % n)
		self.assertFalse(m.group('args'), 'method #%d has no args' % n)
		deco_ex = ['public', 'java.lang.String']
		deco = [val for val in m.group('deco').split(' ') if val]
		self.assertEqual(len(deco_ex), len(deco), 'constructor #%d has decorations' % n)
		self.assertEqual(deco[0], 'public', 'constructor #%d 1st decoration error' % n)
		self.assertEqual(deco[1], 'java.lang.String', 'constructor #%d 2nd decoration error' % n)
		# ２番目のメソッドを確認
		m = m2[n]
		n += 1
		self.assertEqual(m.group('fqcn'), 'main', 'method #%d return value not match' % n)
		args = m.group('args')
		self.assertTrue(args, 'method #%d has args' % n)
		args_conf = ['java.lang.String[]']
		wk = [val.strip() for val in args.split(',')]
		self.assertEqual(len(wk), len(args_conf), 'constructor #%d args not match' % n)
		for index in range(len(args_conf)):
			self.assertEqual(args_conf[index], wk[index], 'constructor #%d arg(%d) type not match' % (n, (index+1)))
		deco_ex = ['public', 'static', 'void']
		deco = [val for val in m.group('deco').split(' ') if val]
		self.assertEqual(len(deco_ex), len(deco), 'constructor #%d has decorations' % n)
		self.assertEqual(deco[0], deco_ex[0], 'constructor #%d 1st decoration error' % n)
		self.assertEqual(deco[1], deco_ex[1], 'constructor #%d 2nd decoration error' % n)
		self.assertEqual(deco[2], deco_ex[2], 'constructor #%d 3rd decoration error' % n)
		# ３番目のメソッドを確認
		m = m2[n]
		n += 1
		self.assertEqual(m.group('fqcn'), 'setUp', 'method #%d return value not match' % n)
		self.assertFalse(m.group('args'), 'method #%d has no args' % n)
		deco_ex = ['protected', 'void']
		deco = [val for val in m.group('deco').split(' ') if val]
		self.assertEqual(len(deco_ex), len(deco), 'constructor #%d has decorations' % n)
		self.assertEqual(deco[0], deco_ex[0], 'constructor #%d 1st decoration error' % n)
		self.assertEqual(deco[1], deco_ex[1], 'constructor #%d 2nd decoration error' % n)
		# ４番目のメソッドを確認
		m = m2[n]
		n += 1
		self.assertEqual(m.group('fqcn'), 'waitUntilFinished', 'method #%d return value not match' % n)
		self.assertFalse(m.group('args'), 'method #%d has no args' % n)
		deco_ex = ['synchronized', 'void']
		deco = [val for val in m.group('deco').split(' ') if val]
		self.assertEqual(len(deco_ex), len(deco), 'constructor #%d has decorations' % n)
		self.assertEqual(deco[0], deco_ex[0], 'constructor #%d 1st decoration error' % n)
		self.assertEqual(deco[1], deco_ex[1], 'constructor #%d 2nd decoration error' % n)

	def test_class_001(self):
		# FQCN の確認
		m = re.search(JAVAP_REs['class'], S04_1)
		self.assertIsNotNone(m, 'none class')
		self.assertEqual(m.group('fqcn'), 'junit.extensions.ActiveTestSuite', 'FQCN error')
		# ソースファイル名の確認
		m = re.search(JAVAP_REs['java-source'], S04_1)
		self.assertIsNotNone(m, 'none source file name')
		self.assertEqual(m.group('source_file'), 'ActiveTestSuite', 'FQCN error')

	def test_class_002(self):
		# FQCN の確認
		m = re.search(JAVAP_REs['class'], S04_2)
		self.assertIsNotNone(m, 'none class')
		self.assertEqual(m.group('fqcn'), 'junit.extensions.ActiveTestSuite$1', 'FQCN error')
		# ソースファイル名の確認
		m = re.search(JAVAP_REs['java-source'], S04_2)
		self.assertIsNotNone(m, 'none source file name')
		self.assertEqual(m.group('source_file'), 'ActiveTestSuite', 'FQCN error')

	def test_class_003(self):
		# FQCN の確認
		m = re.search(JAVAP_REs['interface'], S04_3)
		self.assertIsNotNone(m, 'none class')
		self.assertEqual(m.group('fqcn'), 'junit.extensions.package-info', 'FQCN error')
		# ソースファイル名の確認
		m = re.search(JAVAP_REs['java-source'], S04_3)
		self.assertIsNotNone(m, 'none source file name')
		self.assertEqual(m.group('source_file'), 'package-info', 'FQCN error')

if __name__ == '__main__':
	unittest.main()

#[EOF]