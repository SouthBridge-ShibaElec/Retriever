"""retriever_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# 管理画面用ライブラリをインポート
from django.contrib import admin
# URL組み立てライブラリをインポート
from django.urls import path, include

# don't modify, current file is looking on manage.py.
from retriever import views

# URLを定義して紐付けするビューを列挙
urlpatterns = [
    path('admin/', admin.site.urls),# 管理画面
    path('', views.index, name='index'),                    # ドメイン以降を省略した場合はトップページへ
    path('upload/', views.upload, name='upload'),           # ファイルアップロード画面
    path('classify/', views.medialist, name='classify'),    # ファイル分類画面
    path('reject/', views.reject, name='reject'),           # ファイル除外画面
    path('comic/', views.comicedit, name='comic'),          # 連番漫画編集画面
    path('browse/', views.browse, name='browse')            # ファイル閲覧画面
]
