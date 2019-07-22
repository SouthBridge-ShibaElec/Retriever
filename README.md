# Retriever
![Retrieverアイコン](https://raw.github.com/wiki/SouthBridge-ShibaElec/Retriever/icon-192x192.png)

Docker上で動作する宅内LAN用Webアプリケーションです。
画像ファイルや動画ファイルを収集し、利用しやすいように取り出せるよう管理します。

## アプリケーション紹介

このWebアプリケーションは、収集した画像や動画を集中管理し、閲覧したいときにランダムに配信します。
スマートフォンやタブレット、パソコンにインストールされているWebブラウザに画像を全画面表示し、作品を楽しむことができます。

<img src="https://raw.github.com/wiki/SouthBridge-ShibaElec/Retriever/Digi_face-1140317265860030464-20190617_025636-img3.jpg" width="500px">

作品にはジャンルを設定することができます。
ランダムに閲覧したい作品をジャンルで指定することができ、配信を受ける作品を制御できます。

<img src="https://raw.github.com/wiki/SouthBridge-ShibaElec/Retriever/Digi_face-1140317265860030464-20190617_025636-img1.jpg" width="700px">

複数のファイルを順番付けて、「漫画」という単位で管理することが可能です。

<img src="https://raw.github.com/wiki/SouthBridge-ShibaElec/Retriever/Digi_face-1140317265860030464-20190617_025636-img2.jpg" width="700px">

漫画として登録された作品群は、ランダム配信時にページ順を崩さず配信されます。
漫画作品と単一ファイル作品を、混ぜ込んでランダムに楽しむことができます。

<img src="https://raw.github.com/wiki/SouthBridge-ShibaElec/Retriever/Digi_face-1140317265860030464-20190617_025636-img4.jpg" width="700px">

## デプロイ手順

Retrieverは、Dockerとdocker-compose、jwilder/nginx-proxyに依存しています。
下記リンクの内容に従い、先に環境構築を済ませてください。

[複数のWebアプリを1サーバーのDockerを使ってSSL対応のサブドメインで簡単に運用する | QUARTETCOM TECH BLOG](https://tech.quartetcom.co.jp/2017/04/11/multiple-ssl-apps-on-one-docker-host/)

----

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
nginx-proxyのコンテナが2つ、Retrieverのコンテナが３つが安定して起動していることを確認してください。
```
$docker-compose up -d
$docker ps -a
```
(アプリケーションサーバ用コンテナがrestartを繰り返すことがあります。`docker-compose down`してから、再度`docker-compose up -d`してください。)

----

コンテナが起動したら、Retrieverを動作させるためにDjangoの設定をしていきます。

アプリケーションサーバ用コンテナのシェルに入り、manage.pyが見えることを確認します。
```
$dodcker exec -it docker-django_retriever_django_1 bash
#ls
```
Retrieverで使用するデータベーステーブルを作成します。
```
#python3 manage.py makemigrations retriever
#python3 manage.py migrate
```

nginxから配信する静的ファイルを収集します。
```
#python3 manage.py collectstatic
```

コンテナのシェルを出て、Retrieverシステムを再起動したら使用準備が完了です。
```
$docker-compose down
$docker-compose up -d
```

## 既知の問題点

Retrieverはまだ荒削りです。
現在把握している問題があります。
使用する際は注意してください。

### 「無効なURLです。プログラム設定の反映待ちである可能性があります。しばらく時間をおいて再度アクセスをお試しください。」のエラーが出る

操作画面でのエラー発生後や、作品配信の通信が失敗した後によく発生します。

Webブラウザを完全に閉じてセッションを切り、再接続すると復旧することがあります。

それでも復旧しない場合は、RetrieverのDockerコンテナ群を`docker-compose down`してから、`docker-compose up -d`し直してください。

### 作品をまとめて操作した後、pythonのエラー画面が表示されて登録した作品が見えなくなる

作品を100件以上の単位でアップロードしたり、ジャンル付けをしたりした際にエラー画面が表示され、まとめて操作を加えた作品にアクセスできなくなります。

ファイルをまとめての操作は一度に50件程度に留めてください。

エラーが出た直後はシステムが不安定になっており、まとまった操作をしていなくてもエラーが頻発する恐れがあります。
このエラーに遭遇したら、RetrieverのDockerコンテナ群を`docker-compose down`してから`docker-compose up -d`してから使用を続けてください。
