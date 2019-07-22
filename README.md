# Retriever
![Retrieverアイコン](https://raw.githubusercontent.com/SouthBridge-ShibaElec/Retriever/master/docker-django/django/retriever/static/retriever/icon-192x192.png?token=AMVJJGJ4VFDYNY7P3Z7RZQC5GOOBS)

Docker上で動作する宅内LAN用Webアプリケーションです。
画像ファイルや動画ファイルを収集し、利用しやすいように取り出せるよう管理します。

## デプロイ手順

Retrieverは、Dockerとdocker-compose、jwilder/nginx-proxyに依存しています。
下記リンクの内容に従い、先に環境構築を済ませてください。

[複数のWebアプリを1サーバーのDockerを使ってSSL対応のサブドメインで簡単に運用する | QUARTETCOM TECH BLOG](https://tech.quartetcom.co.jp/2017/04/11/multiple-ssl-apps-on-one-docker-host/)


Retrieverは下記リンクのコードをベースにして開発したため、デプロイ手順は基本的に下記リンクに沿って進めます。

[DjangoをDocker Composeでupしよう！ - Qiita](https://qiita.com/kyhei_0727/items/e0eb4cfa46d71258f1be)


リポジトリをcloneしたら、
```
$cd Retrieverリポジトリのディレクトリ/docker-django
```
に移動します。


Dockerfile.baseが見えることを確認して、アプリケーションサーバ用コンテナイメージをビルドします。
```
$docker build -t django2.1 -f ./django/Dockerfile.base ./django
```
Dockerイメージの順が整ったので、システムをupします。
```
$docker-compose up -d
$docker ps -a
```
nginx-proxyのコンテナが2つ、Retrieverのコンテナが３つが安定して起動していることを確認してください。

(アプリケーションサーバ用コンテナがrestartを繰り返すことがあります。`docker-compose down`してから、再度`docker-compose up -d`してください。)
