# pyReverseCRUD （開発中）
JavaソースとMyBatisのMapperXMLからCRUDを作成する

## リバースエンジニアリングツール
* 解析結果は、Excelに出力する
* 出力タイプは、次の３種類用意する
    * メソッド単位（完成）
    * javaソース単位（着手）
    * サービス単位
    * コントローラ単位 

## モジュール一覧
* javaAnalize  
    javaのclassファイルをデコンパイルし、crudをExcelファイルに出力する

* daoReader  
    MyBatisのマッパーファイル（XML）形式を読込み、各クエリーのCRUDの判定の準備を行う

* curdJudgment  
    DML の内容から CRUD を判定する

## MyBatis の Mapper タグ

* if タグ  
  True として展開する

* include タグ  
  同Mapperファイル内の sql タグを展開する

## 開発メモ  
* 【製造】デコンパイル結果からjavaのソースファイル単位でcrudを作成
* 【製造】Javaのソースファイルから使用しているDaoを紐づける  
　　* 完成。デコンパイル後のファイルを解析
* 【製造】メソッドのつながり
* 【製造】CRUD の Excel 出力  
　　* 完成。[openpyxl]を利用
* 【テスト】サンプルのMapperファイルの拡充  

### メソッドのつながり  
* 外部クラスの(public)メソッドを呼び出す
* クラス内の(public/private)メソッドを呼び出す
* ラムダ式
* インターフェースメソッドを実装メソッドに変換
* リエントラントに注意
* オーバーロード（引数違いの同名メソッド）に注意

### その他メモ
* コントローラは、「RequestMapping」アノテーションを解釈すること（Excel出力に使用する）

### 外部メソッド（インタフェースされたメソッド）呼び出し
* キーワード：invokeinterface  
    4: invokeinterface #25,  1           // InterfaceMethod {FQCN}.{method}:()Ljava/lang/String;  
    {FQCN}：完全限定クラス名（実装クラスに変換が必要）  
    {method}：メソッド名  
    ※Daoクラスの呼び出しはこのカテゴリに該当するが、Daoクラスはマッパークラスとなる  
### 外部メソッド（コンポーネントメソッド）呼び出し
* キーワード：invokevirtual  
    4: invokevirtual #27                 // Method {FQCN}.{method}:()Ljava/lang/String;  
    {FQCN}：完全限定クラス名  
    {method}：メソッド名  
### クラス内(private)メソッド呼び出し 
* キーワード：invokevirtual  
    1: invokevirtual #20                 // Method {method}:()Ljava/lang/String; 
    {method}：メソッド名  
    FQCNは「#20」より、  
    #20 = Methodref          #1.#21         // {FQCN}.{method}:()Ljava/lang/String;  
    引き出せる。  



