# 普段使い用djangoコンテナ定義Dockerfile

# Dockerfile.baseから作ったイメージからビルド開始
FROM django2.1:latest

# djangoアプリケーション配置先パスを環境変数で指定
ENV APP_PATH /opt/apps

# アプリケーションコードをコンテナにコピー
COPY . $APP_PATH/
# 依存アプリケーションをインストール
RUN pip install --no-cache-dir -r $APP_PATH/requirements.txt

# アプリケーションパスに移動
WORKDIR $APP_PATH
# ダミーログデータをコピー
COPY ./time_rotation.log $APP_PATH/log/
# 静的ファイルを収集・移動して、コンテナ起動準備完了とする
RUN python manage.py collectstatic --noinput
