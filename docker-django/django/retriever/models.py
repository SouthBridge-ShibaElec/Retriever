from django.conf import settings
# DBモデル定義用ライブラリのインポート
from django.db import models
# 日本時間利用のためのライブラリをインポート
from django.utils import timezone

# Create your models here.


# 定義済みジャンルを格納するテーブル
class MediaGenre(models.Model):
    """media genre grouping key table"""
    class Meta:
        db_table = 'media_genre'

    # 別テーブルで管理して重複を防ぐ。ファイル管理テーブルからリレーションする
    genrename = models.CharField(verbose_name='mediagenre', unique=True, null=False, max_length=127)

    def __str__(self):
        return self.genrename


# 定義済み連番漫画を格納するテーブル
class Comics(models.Model):
    class Meta:
        db_table = 'comics'

    # 漫画タイトルを別管理にして重複を防ぐ。ファイル管理テーブルからリレーションする
    comicname = models.CharField(verbose_name='comicname', unique=True, null=False, max_length=127)
    # 漫画に対してジャンルを設定する
    genre = models.ForeignKey(MediaGenre, verbose_name='genre', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.comicname


# 管理中ファイル格納テーブル
class MediaFiles(models.Model):
    """media file name and path stocking"""
    class Meta:
        db_table = 'media_files'

    # ファイル名ユニーク定義で同一ファイル登録を防ぐ。
    filename = models.CharField(verbose_name='filename', unique=True, null=False, max_length=254)
    # 登録日時で管理操作時にソートしやすくする。
    madedate = models.DateTimeField(verbose_name='madedate', auto_now_add=True, null=False)
    # imageではなくfileとして登録することで、動画コンテンツにも対応
    mediafile = models.FileField(verbose_name='mediafile', null=False)
    # ジャンルは別テーブルからリレーション。nullで未分類ファイルを示す。ジャンルが消滅したときもnullにして未分類に。
    genre = models.ForeignKey(MediaGenre, verbose_name='genre', null=True, on_delete=models.SET_NULL)
    # 漫画は別テーブルからリレーション。漫画として管理していないファイルはnull。漫画が消滅したときもnullにする。
    comiclink = models.ForeignKey(Comics, verbose_name='comiclink', null=True, on_delete=models.SET_NULL)
    # 漫画として管理しているときはページ順をファイルに持たせる。
    comicpage = models.IntegerField(verbose_name='comicpage', null=True,)
    # 既読マークをブール値として格納。Trueで既読済み
    watched = models.BooleanField(verbose_name='watched', null=False, default=False, )

    def __str__(self):
        return self.filename
