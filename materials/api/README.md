# 外部販売システム役のローカルAPI
学習者のLaravelアプリとは別のサービスです。教材側が提供し、課題08から利用します。[契約](contract.txt)と[データ](fixtures.json)を読みます。開発専用、外部公開しないでください。

## まずホストから起動（Python 3がある場合）
リポジトリ直下・Macのターミナルで：
```sh
python3 materials/api/server.py
```
別ターミナルで：
```sh
curl -i http://127.0.0.1:8099/health
curl -i -H 'Authorization: Bearer local-training-only' 'http://127.0.0.1:8099/v1/orders?page=1&per_page=2'
```
停止は起動ターミナルでCtrl+C。Pythonがない場合は次のDocker方式を使います。同じポートで両方を同時に起動しない。

## Sailから使うDocker方式
リポジトリ直下（ホスト）で：
```sh
docker compose -p db-study-sales -f materials/api/compose.yaml up -d
```
既に8099番を他の用途で使っている場合はホスト側ポートだけ変更し記録。教材Composeは`db-study-sales`ネットワークを作ります。別学習環境を同時起動する場合はプロジェクト名・ネットワーク名・ホストポートを分けます。

Sail側のサービスとネットワーク名を既存Composeファイルで確認してから、sail-network.override.yamlをapp/compose.sales.yamlへコピー。標準のlaravel.testとsail以外なら合わせます。元のネットワークを残し、salesを追加します。
例えばapp/の基本ファイル名がcompose.yamlの場合、app/（ホスト）で：
```sh
COMPOSE_FILE=compose.yaml:compose.sales.yaml ./vendor/bin/sail up -d
```
基本ファイルがdocker-compose.ymlなら、その名前に置換。同じ設定を使って以後も起動/停止します。アプリのAPI接続先は`http://sales-api:8099`。ホストのcurlは`http://127.0.0.1:8099`。コンテナ内localhostはホストではありません。
Laravel側の.envには接続先と試験トークンを設定し、コードへ直書きしない。.envはコミットしない。設定名は自分のconfig設計で決めます。

ログ/停止（ホスト、リポジトリ直下）：
```sh
docker compose -p db-study-sales -f materials/api/compose.yaml logs sales-api
docker compose -p db-study-sales -f materials/api/compose.yaml stop
```
再開はup -d。Sailが接続している間のネットワーク削除は不要です。

## 障害再現例
URLへ`mode=server_error`、`mode=rate_limit`、`mode=invalid_json`、`mode=invalid_schema`、`mode=timeout`を指定。`fail_page=2`は2ページ目だけ503。`revision=2`は訂正/取消後。復旧試験は同じrevisionでmode=normalとfail_page=0へ戻して再取得。
実アプリでは試験モードを一般利用者に操作させず、環境設定/テスト専用で扱う。

## 教材サービス自体の確認
```sh
python3 -m unittest discover -s materials/api -p 'test_*.py' -v
```
標準ライブラリのみ。これは配布APIの検証です。自分のLaravel連携のテストを代替しません。Python実行の検証と、Docker/Sail接続の検証を別々に記録します。
