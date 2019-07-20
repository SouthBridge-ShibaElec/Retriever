# 管理画面構成用ライブラリをインポート
from django.contrib import admin
from django.utils.safestring import mark_safe

# 操作対象のDBモデルを列挙する
from .models import MediaFiles, MediaGenre, Comics

# アップロード済みファイルの操作画面をカスタム
class MediaFileAdmin(admin.ModelAdmin):
    # 表示するDBカラムとその並びを定義
    list_display = ["MediaTag", "pk", "filename", "madedate", "genre", "comiclink", "comicpage", "watched"]
    # プライマリキー順にソート
    ordering = ["pk", ]

    # 追加CSSを使用する
    class Media:
        css = {
            'all': ('customAdmin.css', )
        }

    # 画像のサムネイルを表示させるコード
    # 条件分岐で動画も扱えないか検討したい
    def MediaTag(self, obj):
        return mark_safe('<image src="{}" />'.format(obj.mediafile.url))


# 登録済み漫画の操作画面をカスタム
class ComicAdmin(admin.ModelAdmin):
    # 表示するDBカラムとその並びを定義
    list_display = ["comicname", "genre", "pk"]
    # プライマリキー順にソート
    ordering = ["pk"]

# ブラウザに表示するタイトル
admin.site.site_title = 'Retriever管理ページ'
# ページのタイトル部に表示するタイトル
admin.site.site_header = 'Retriever管理ページ'

# DBレコード管理画面を生成
admin.site.register(MediaFiles, MediaFileAdmin)     # アップロード済みファイルのカスタム設定を適用する
admin.site.register(MediaGenre)                     # 登録済みジャンル操作画面はそのまま
admin.site.register(Comics, ComicAdmin)             # 登録済み漫画のカスタム設定を適用する