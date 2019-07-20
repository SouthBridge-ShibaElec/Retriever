"""
Django settings for retriever_project project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g3w!u4sdm7frtxvh5t11&ksg&o^mej@j7s=@up81aq7r+puy*l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# アクセスを許可するURL指定
# デプロイするサーバのドメインが異なる場合は変更すること。
ALLOWED_HOSTS = [
    'localhost',
]


# Application definition

# 作動させるアプリケーションを列挙する
# ページデザインを良きに計らうbootstrap
# 管理から除外されたファイルを自動削除するdjango_cleanup
# 開発したRetrieverも含む
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap4',
    'django_cleanup',
    'retriever.apps.RetrieverConfig',
]

# 作動させるミドルウェアを列挙する
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 振り分けるURLは別ファイルで定義
ROOT_URLCONF = 'retriever_project.urls'

# テンプレートの利用設定
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGIを作動させる設定
WSGI_APPLICATION = 'retriever_project.wsgi.application'


# データベースの接続設定
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',  #作成時のデフォルト
        'USER': 'postgres',  #作成時のデフォルト
        'PASSWORD' : 'hogemojahogemoja', #作成時にdocker-compose.ymlで設定
        'HOST' : 'retriever_postgres', #コンテナのサーバ名
        'PORT' : 5432,
    }
}


# ログ出力設定
# Logging setting
LOGGING_PATH = '/opt/apps/log/'     # ログファイルの出力先
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {     # ログ出力のフォーマットを定義
        'production': {
            'format': '%(asctime)s [%(levelname)s] %(process)d %(thread)d %(pathname)s:%(lineno)d %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',                                               # それなりに詳細な出力設定
            'class': 'logging.handlers.TimedRotatingFileHandler',           # ログは日付ベースのローテーションをさせて溢れないようにする
            'filename': os.path.join(LOGGING_PATH, 'time_rotation.log'),    # ログファイルのファイル名を指定
            'formatter': 'production',                                      # ログ出力のフォーマット定義を使用
            'when': 'W0',                                                   # 毎週月曜日にローテーション発動
            'backupCount': 5,                                               # 5週間分保管
        },
    },
    'loggers': {                    # ログを仕掛ける対象を列挙
        '': {                       # 全域ログを拾う
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {                 # djangoベースシステムのログを拾う
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {     # データベースのログを拾う
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
}


# 管理画面用CSSのファイルパスを指定
# Admin site css file path
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# パスワード認証関連設定
# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# 地域別設定
# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ja'        # 日本語を使用

TIME_ZONE = 'Asia/Tokyo'    # 東京時間を使用

USE_I18N = True

USE_L10N = True

USE_TZ = True               # 地域時刻を使用する


# 静的ファイル配信元のファイルパス指定
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

# JS、CSSを格納するパス
STATIC_URL = '/static/'
STATIC_ROOT = '/opt/static' #ボリュームマウント先のパス

# メディアファイルを格納するパス
MEDIA_URL = '/media/'
MEDIA_ROOT = '/opt/media'   #ボリュームマウント先のパス