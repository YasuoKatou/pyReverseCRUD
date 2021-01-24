# pyReverseCRUD （開発中）
JavaソースとMyBatisのMapperXMLからCRUDを作成する

## リバースエンジニアリングツール
工事中．．．

## モジュール一覧

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

* 【製造】Javaのソースファイルから使用しているDaoを紐づける  
* 【製造】CRUD の Excel 出力
* 【テスト】サンプルのMapperファイルの拡充  
