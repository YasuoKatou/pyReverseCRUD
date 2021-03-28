# pyReverseCRUD （開発中）
Java のコンパイル結果と MyBatis の Mapper XML から CRUD を作成する  
注意事項  
* DML の構文解析は行っていません。CRUD の種別は Mapper XML の タグから判断します。  
* 参照テーブルは、下記定義ファイルの```tables```で定義します。  
## リバースエンジニアリングツール
* 解析結果は、Excelに次の４種類（シート）を出力する
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

## 定義ファイル（resources/crudConfig.json）について  
* ```analize```  
    * ```debug```  
        * ```decompile```  
        逆アセンブル（javap）を実施する [True]／しない [False] を指定する。初回起動時は、[True] を指定する。  
        * ```mapper-excel```  
        マッパーの CRUD を Exce l出力する [True]／しない [False] を指定する。
    * ```jdk-path```  
        Java JDK（javap） のフォルダをフルパスで指定する。  
    * ```javap-options```  
        javap 起動時のオプションを指定する。（固定）  
    * ```work-path```  
        逆アセンブル（javap）の結果を格納するフォルダをフルパスで指定する。  
    * ```Project```  
        プロジェクトに関する情報を設定する。  
        * ```path```  
            プロジェクトのルートパスをフルパスで指定する。  
        * ```java-src```（未使用）  
            Javaソースファイルのパスを```path```からの相対パスで指定する。  
        * ```classes```  
            .classファイルのパスを```path```からの相対パスで指定する。  
        * ```mapper-xml```  
            mapper xmlファイルのパスを```path```からの相対パスで指定する。  
        * ```view-def-path```  
            ビュー定義ファイルのルートパスをフルパスで指定する。  
    * ```spring```  
        （工事中）  
* ```Excel```  
    * ```start_row```  
        CRUD の出力を開始するシートの行番号。（固定）  
    * ```header_rows```  
        CRUD のヘッダー行数。（固定）  
    * ```start_column```  
        CRUD マトリクス出力開始列番号。（固定）
    * ```crud_width```  
        CRUD のセル幅。（固定）  
    * ```tables```  
        * テーブルグループ名称キー  
            テーブルグループ名を指定する。 このキーは、```tables```にリンクする。 
    * ```exclude-no_mapper_call```  
        マッパー呼び出しを行わないメソッドまたはクラスをマトリクスから除外する [True]／しない [False] を指定する。  
* ```tables```  
    * テーブルグループ名称キー  
        * テーブル名称（物理名）キー  
            テーブル名称の和名を定義する。 
* ```others```  
    * ```views```  
        ビューの一覧を指定する。  

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



