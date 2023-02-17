# django連携用ライブラリの読み込み
from django.contrib.auth import login as auth_login
from django.shortcuts import render,redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.conf import settings

# view構築ヘルパーライブラリの読み込み
from django.views import View
from django.views.generic import TemplateView

# 自作したモジュールを読み込んで連携
from .models import MediaFiles, MediaGenre, Comics

# Ajaxで使用するライブラリの読み込み
from django.http.response import JsonResponse
import json

# データベース操作で使用するライブラリの読み込み
from django.db.models import Q, Max
from random import randrange

# 汎用ライブラリの読み込み
import os
import shutil
import zipfile
import tempfile
from logging import getLogger
import re


# 頻繁に使う操作をメソッドにし、クラスとしてまとめる

# データベース操作まとめ
class RecordOperation:

    # 重複レコードがなければインサート、見つかったらフラグを返して終了
    def record_save_if_not_exists(self, target_model=None, search_condition=None, will_set_data=None):
        if target_model.objects.filter(search_condition).exists() is False:
            will_set_record = will_set_data
            will_set_record.save()
            return True
        else:
            return False



# 受信データ整形まとめ
class dataCast:
    # 受信した文字列化プライマリキーリストを整数組み込みリストに変換
    def RecievedPkListCast(self, recievedString=None):
        return [int(page) for page in recievedString.split(',')]


    # プライマリキーリストからレコードオブジェクトリストを生成
    def pkListToRecordList(self, pkList=None, model=None):
        # 返送用の空リストを宣言
        recordList = []

        # プライマリキーリストを順番に走査
        for selectPK in pkList:
            # レコードが取得できたら返送用リストに詰めていく
            try:
                record = model.objects.get(pk=selectPK)
            except:
                # レコードの取得に失敗したら詰めずに次へ
                continue
            else:
                recordList.append(record)

        return recordList



# メディアディレクトリ操作まとめ
class mediaDirectory:
    # クラス内で使い回すメンバオブジェクト
    mediaRoot = settings.MEDIA_ROOT + '/'   # メディアファイルのパスを格納する
    logger = getLogger(__name__)            # ログ出力用オブジェクト


    # プライマリキーリストにあるファイルを指定ディレクトリに移動する
    def moveToDirectory(self, pathToMove=None, pkList=None):
        # プライマリキーリストを1件ずつ引き抜いて処理
        for selectPK in pkList:
            try:
                # 対象ファイルのレコードオブジェクトを取り出す
                record = MediaFiles.objects.get(pk=selectPK)

            except:
                # レコードの取得に失敗したらエラーログを残してイテレーションを送る
                self.logger.error('PK{} setting gnere failed'.format(selectPK))
                continue

            else:
                # レコードオブジェクトが取得できたら移動を実行
                # ファイル名単体を格納
                filename = os.path.basename(record.mediafile.name)

                # 移動先パスを事前に条件分岐で構成
                moveTo = None
                if pathToMove is None:
                    # 移動先パスが無指定の場合はルートディレクトリへ戻す
                    moveTo = filename
                else:
                    # 移動先パスが指定されている場合は間に挟む
                    moveTo = pathToMove + '/' + filename
                
                # 実際にファイルを動かす
                shutil.move((self.mediaRoot + record.mediafile.name), self.mediaRoot + moveTo)

                # レコードのnameをサブディレクトリ付きに変更
                record.mediafile.name = moveTo
                # レコードの変更をDBに登録
                record.save()
        
        return 0
        


    # 新規ジャンルを作成する
    def newGenreGenerate(self, genrename=None):
        # ジャンルがDB上に存在していなければ、DBレコードを生成
        if MediaGenre.objects.filter(genrename=genrename).exists() is False:
            genreRecord = MediaGenre(genrename=genrename)
            genreRecord.save()

        # 作成予定のディレクトリパスを格納
        genreDir = self.mediaRoot + genrename
        # ジャンルと同名のサブディレクトリが存在していなければ、ディレクトリを作成
        if os.path.exists(genreDir) is False:
            os.mkdir(genreDir)
        
        # 呼び出し元にレコードオブジェクトを渡す
        try:
            recordReturn = MediaGenre.objects.get(genrename=genrename)
        except:
            # 失敗した場合はnullを返しておく
            recordReturn = None
        return recordReturn
    

    # ファイルのジャンル付けを行う
    def setGenre(self, genrename=None, pkList=None):
        # ジャンルのDBレコードオブジェクトを取得
        genreRecord = self.newGenreGenerate(genrename=genrename)
        if genreRecord is None:
            # このタイミングで失敗していたら何もせずにnullを返しておく
            return None
        
        # DBレコードにジャンル紐付け情報をまとめて付与する
        recordBatch = MediaFiles.objects.filter(pk__in=pkList)
        recordBatch.update(genre=genreRecord)
        
        # ジャンル用サブディレクトリへ移動
        self.moveToDirectory(pathToMove=genreRecord.genrename, pkList=pkList)

        # 呼び出し元にレコードオブジェクトを渡す
        return genreRecord
    

    # 新規漫画を作成する
    def newComicGenerate(self, comicTitle=None, genrename=None):
        # ジャンルのDBレコードオブジェクトを取得
        genreRecord = self.newGenreGenerate(genrename=genrename)
        if genreRecord is None:
            # このタイミングで失敗していたら何もせずにnullを返しておく
            return None

        # 新規生成する漫画のタイトルとジャンルを指定したレコードを生成し、DBに登録する
        if Comics.objects.filter(comicname=comicTitle).exists() is False:
            newComic = Comics(comicname=comicTitle, genre=genreRecord)
            newComic.save()

        # 作成予定のディレクトリパスを格納
        comicDir = self.mediaRoot + genrename + '/' + comicTitle
        # 新規生成する漫画を格納するサブディレクトリを生成
        if os.path.exists(comicDir) is False:
            os.mkdir(comicDir)

        # 呼び出し元にレコードオブジェクトを渡す
        try:
            comicReturn = Comics.objects.get(comicname=comicTitle)
        except:
            # 何故か失敗した場合はnullを返しておく
            comicReturn = None
        return comicReturn


    # ファイルを漫画に登録する
    def setComic(self, comicTitle=None, genrename=None, pkList=None):
        # 登録先漫画のDBレコードオブジェクトを取得
        comicRecord = self.newComicGenerate(comicTitle=comicTitle, genrename=genrename)

        # 登録予定ファイルのDBレコードリストを生成
        targetPages = MediaFiles.objects.filter(pk__in=pkList)
        # DBリストにまとめて漫画とジャンルの紐付けを行う
        targetPages.update(comiclink=comicRecord, genre=comicRecord.genre)

        # ファイルをサブディレクトリに格納する
        self.moveToDirectory(pathToMove=(genrename + '/' + comicTitle), pkList=pkList)

        return 0


# 以下、ブラウザからのリクエストを受け付けるviewクラスが続く

# トップページ表示処理
class IndexView(TemplateView):
    template_name = 'index.html'


# アップロード済未分類ファイルをジャンル付け処理
class MediaListView(View, RecordOperation, dataCast, mediaDirectory):
    # GETされたときに表示画面のデータを組み立てて詰めるメソッド
    def genContext(self,):
        # rejectジャンルが存在しないときはココで生成
        self.newGenreGenerate(genrename="reject")
        
        # 登録済みジャンルのリストを取得
        genreList = MediaGenre.objects.all().order_by('genrename')

        # 未分類ファイルを取得
        # まずは対象の存在を確認する
        if MediaFiles.objects.filter(genre__isnull=True).exists():
            # 見つかったら登録日が古いのを上にしてまとめる
            recordList = MediaFiles.objects.filter(genre__isnull=True).order_by('madedate')
            # できたらジャンルと一緒に辞書でまとめる
            context = {
                'recordList': recordList,
                'genreList': genreList,
            }
        else:
            # 未分類ファイルがなかったら通知メッセージを入れて返す。
            context = {
                'blankList': "Classify対象ファイルはありません。",
                'genreList': genreList,
            }
        return context
    
    # GETリクエストへの応答メソッド
    def get(self, request, *args, **kwargs):
        # getContext()メソッドで未分類ファイルリストを用意し、classify.htmlテンプレートにレンダリング
        return render(request, 'classify.html', self.genContext())

    # POSTリクエストへの応答メソッド
    def post(self, request, *args, **kwargs):
        # ジャンル名が指定されていない場合をブロックするガード節
        if request.POST.get('genrename') == "new":
            # 未分類ファイル一覧画面の再表示を行うためにファイル一覧を取得
            modifiedContext = self.genContext()
            # エラーメッセージを含んだデータで未分類ファイル一覧画面をレンダリング
            modifiedContext['genreErr'] = "ジャンルが指定されていません"
            return render(request, 'classify.html', modifiedContext)

        # 画像が選択されていない場合をブロックするガード節
        if request.POST.get('selectMedia') == "new":
            # 未分類ファイル一覧画面の再表示を行うためにファイル一覧を取得
            modifiedContext = self.genContext()
            # エラーメッセージを含んだデータで未分類ファイル一覧画面をレンダリング
            modifiedContext['selectErr'] = '設定対象が選択されていません'
            return render(request, 'classify.html', modifiedContext)
        
        # ジャンル付け予定ファイルのプライマリキーリストを使ってジャンル付け処理を実施
        self.setGenre(genrename=request.POST.get('genrename'), pkList=self.RecievedPkListCast(recievedString=request.POST.get('selectMedia')))

        # 操作成功後、未分類ファイル一覧画面へリダイレクト
        return render(request, 'classify.html', self.genContext())


# アップロード操作受付処理
class UpLoadView(View, RecordOperation, mediaDirectory):
    # クラス内で使い回すメンバオブジェクト
    logger = getLogger(__name__)        # ログ出力用オブジェクト
    uploadErr = []                      # 登録を弾かれたファイルのエラーメッセージを格納


    # エラー扱いのアップロードファイルを記録する関数
    def errorLogging(self, fileName):
        self.logger.error('{} save to database failed.'.format(os.path.basename(fileName)))
        self.uploadErr.append("{}の保存に失敗しました。".format(os.path.basename(fileName)))


    # GETが来たらテンプレートを使ってレンダリング
    def get(self, request, *args, **kwargs):
        # upload.htmlテンプレートにレンダリング
        return render(request, 'upload.html')


    # POSTが来たらフォームモジュールがよしなにしてくれたデータをデータベースに登録
    def post(self, request, *args, **kwargs):
        # エラーメッセージ収集用のリストをクリア
        self.uploadErr.clear()

        # 後で使うオブジェクトを仕込んでおく

        # 重複対策ファイル名除外用Regexオブジェクト
        overlappingRegex = re.compile(r'''(
            ^(.*?)              # 任意のファイル名、後ろを巻き込まないよう非貪欲マッチ
            (                   # --ここから重複よけバリエーションのOR探索
                (                   # --ここから(1)の判定(FireFox用)
                    \(
                        (\d){1,3}      # 3桁まで(Pixivダウンローダで識別子を格納していたため)
                    \)
                )|                  # --ここまで(1)のような重複よけの判定、ORで続く
                (                   # --ここから(hogeのコピー)の判定(ubuntu専用)
                    \(
                        (.*?)           # コピー)まではバラつくので任意マッチ、後ろを巻き込まないよう非貪欲マッチ
                        コピー          # 日本語部分をマッチさせる
                    \)
                )|                  # --ここまで(hogeのコピー)の判定、ORで続く
                (                   # --ここからhoge - コピーの判定(windows専用)
                    コピー              # 日本語丸腰置きをマッチさせる
                )                   # --ここまでhoge - コピーの判定
            )                   # --ここまで重複よけバリエーションのOR探索
            \.                  # 拡張子前ドットをマッチさせる
            (.*)$               # 任意の拡張子
            )''', re.VERBOSE)   # 開業入り文字列でコメントを入れたい場合はre.VERVOSEオプションを入れる
        # ZIPファイルを検出するRegexオブジェクト
        zipDetectRegex = re.compile(r'^(.*?)\.zip$')
        # メディアファイルを判定するRegexオブジェクト
        mediaDetectRegex = re.compile(r'''(
            ^(.*?)          # 任意のファイル名、後ろを巻き込まないよう非貪欲マッチ
            \.              # 拡張子前ドットをマッチさせる
            (               # --ここから拡張子の判定
                (jpe?g)|        # .jqgまたは.jpegにマッチ、ORで続く
                (png)|          # .pngにマッチ、ORで続く
                (gif)|          # .gifにマッチ、ORで続く
                (mp4)|          # .mp4にマッチ、ORで続く
                (m4a)           # .m4aにマッチ、ORで続く
            )$              # --ここまで拡張子の判定
        )''', re.VERBOSE|re.IGNORECASE)     # 大文字でもマッチさせる


        # ファイル本体のまとまりはリクエストデータから持ってくる
        files = request.FILES.getlist('uplode_file')


        # 複数ファイルをひとつずつ引き抜いて処理
        for f in files:
            # 重複対策ファイル名かどうかを判定するガード節
            if overlappingRegex.match(f.name) is not None:
                # 重複対策ファイル名は新規登録させない
                # エラーコードを格納して、さっさと次のイテレーションに移る
                self.errorLogging(f.name)
                continue
            
            # ZIPファイルを別扱いするガード節
            if zipDetectRegex.match(f.name):
                # 受け取ったファイルからZIPオブジェクトを生成する
                with zipfile.ZipFile(f) as targetZIP:
                    # ここからは一時ディレクトリ内で処理
                    with tempfile.TemporaryDirectory() as td:
                        # 含まれるファイルのリストを生成する
                        zippedFileList = targetZIP.namelist()
                        # リストに上がったファイルをひとつずつ引き抜いて処理
                        for zfPath in zippedFileList:
                            # ZIPファイル内パスからファイル名のみを抽出
                            zfname = os.path.basename(zfPath)

                            # ファイルを登録できるかを判定
                            mediaBool = (mediaDetectRegex.match(zfname) is not None)                      # 登録できるファイルかどうかを判定
                            existBool = (MediaFiles.objects.filter(filename=zfname).exists() is False)    # 同名ファイルが存在しないかを判定
                            overlappingBool = (overlappingRegex.match(zfname) is None)                    # 重複対策ファイル名で無いかを判定
                            # ブール値をAND条件で結合し、判定
                            if mediaBool & existBool & overlappingBool:
                                # 対象となったファイルをメディアファイルに登録していく
                                # データを一時ファイルに展開
                                targetZIP.extract(zfPath, path=td)
                                # 展開したデータをメディアディレクトリのルートにコピー
                                shutil.copy2((td + '/' + zfPath), (self.mediaRoot + zfname))
                                # ファイルパスとファイル名をDBに登録する
                                will_set_record = MediaFiles(filename=zfname, mediafile=zfname)
                                will_set_record.save()

                            # ファイルを登録できない場合
                            else:
                                # ファイル名をログに記録する
                                self.errorLogging(os.path.basename(zfname))
                # ZIPファイルの処理が終わったらイテレーションを終了させる
                continue


            # 単体ファイルが流れてくるので、ファイルの登録を試みる
            if self.record_save_if_not_exists(
                    target_model=MediaFiles,
                    search_condition=Q(filename=os.path.basename(f.name)),                                  # 同一ファイル名が登録されていないか判定
                    will_set_data=MediaFiles(filename=os.path.basename(f.name), mediafile=f)) is False:     # ファイル名を別で登録し、ファイル実体はファイルフィールドに登録
                # 同名のファイルが存在したら失敗フラグが返る
                # ファイル名をログに記録。遷移先にもリストを渡す。
                self.errorLogging(f.name)
        
        
        # アップロード処理が終わったらファイル分類画面にリダイレクトする
        context = MediaListView.genContext(self)    # ベースで必要なコンテキストを生成
        context["uploadErr"] = self.uploadErr       # アップロード処理時のエラーを含める
        return render(request, 'classify.html', context)



# 管理除外予定ファイルの処遇を決める処理
class RejectView(View, RecordOperation, dataCast, mediaDirectory):
    # 管理除外ファイルのリストを作るメソッド
    def genContext(self,):
        # rejectジャンルが存在しないときはココで生成
        self.newGenreGenerate(genrename="reject")

        # 管理除外予定ファイルのリストを取得
        # まずは管理除外予定ファイルが存在するかを確認
        if MediaFiles.objects.filter(genre__genrename='reject').exists():
            # 管理除外予定ファイルのDBレコードをリストにする。
            recordList = MediaFiles.objects.filter(genre__genrename='reject').order_by('madedate')
            # 管理除外予定ファイルのリストをレンダリングデータとして登録
            context = {
                'recordList': recordList,
            }
        else:
            # 管理除外予定ファイルが無い場合は通知メッセージを入れて返す
            context = {
                'blankList': "Reject指定ファイルはありません。",
            }
        
        return context

    # GETリクエストへの応答メソッド
    def get(self, request, *args, **kwargs):
        # genContext()で管理除外予定ファイルのリストをreject.htmlへレンダリングして、応答とする。
        return render(request, 'reject.html', self.genContext())

    # POSTリクエストへの応答メソッド
    def post(self, request, *args, **kwargs):
        # フィアル処遇が指定されていない場合をブロックするガード節
        if request.POST.get('selectReject') == "new":
            # 未分類ファイル一覧画面の再表示を行うためにファイル一覧を取得
            modifiedContext = self.genContext()
            # エラーメッセージを含んだデータで未分類ファイル一覧画面をレンダリング
            modifiedContext['selectRejectErr'] = "ファイルの処遇が指定されていません"
            return render(request, 'reject.html', modifiedContext)

        # 画像が選択されていない場合をブロックするガード節
        if request.POST.get('selectMedia') == "new":
            # 未分類ファイル一覧画面の再表示を行うためにファイル一覧を取得
            modifiedContext = self.genContext()
            # エラーメッセージを含んだデータで未分類ファイル一覧画面をレンダリング
            modifiedContext['selectMediaErr'] = '処遇対象が選択されていません'
            return render(request, 'reject.html', modifiedContext)
        
        
        # 選択されたメディアファイルのリストから、DBレコードのリストを生成
        selectedList = self.RecievedPkListCast(recievedString=request.POST.get('selectMedia'))


        # ファイルの処遇が再分類だったときの処理
        if request.POST.get('selectReject') == "classify":
            # プライマリキーリストから1件ずつ引き抜いて、ファイルをメディアルートに再配置
            self.moveToDirectory(pathToMove=None, pkList=selectedList)

            # ファイルのジャンル付けを初期化
            # ファイルのDBレコードオブジェクトのリストを取得
            selectedRecords = MediaFiles.objects.filter(pk__in=selectedList)
            # ジャンル付け情報を一括で初期化
            selectedRecords.update(genre=None)

            # 管理除外予定ファイルのリストを生成し直してレンダリング、リダイレクト
            return render(request, 'reject.html', self.genContext())
        
        # ファイルの処遇が削除だったときの処理
        if request.POST.get('selectReject') == "delete":
            # DBレコードオブジェクトのリストを生成
            selectedRecords = MediaFiles.objects.filter(pk__in=selectedList)
            # 対象レコードを削除。紐ついていたメディアファイルはdjango_cleanupによって自動削除される
            selectedRecords.delete()

            # 管理除外予定ファイルのリストを生成し直してレンダリング、リダイレクト
            return render(request, 'reject.html', self.genContext())
        
        # ラジオボタンで指定できないはずの操作IDを送りつけられたときの処理
        # 再表示用のコンテキストを生成
        context = self.genContext()
        # エラーメッセージをコンテキストに追加する
        context['selectRejectErr'] = "無効な操作です"
        # エラーメッセージ入のコンテキストで画面を再表示
        return render(request, 'reject.html', context)



# 連番管理漫画ファイル設定処理
class ComicEditView(View, dataCast, RecordOperation, mediaDirectory):

    # 画面表示に使うためのデータリストを生成する
    def getList(self,):
        # データリストを種別ごとに取得し保持。
        comicList = Comics.objects.all().order_by('-pk')                                # 新規作成漫画がなるべく先頭になるように
        genreList = MediaGenre.objects.all().order_by('genrename')                      # 文字コード順に並べてジャンル名から調べやすく
        mediaList = MediaFiles.objects.filter(genre__isnull=True).order_by('madedate')  # 登録日順に並べて古いファイルから処理させる
        
        # 連番管理漫画のサンプル画像のURLを保持するリスト。並び順をcomicListと同じにして、同時に順繰りに取り出して整合性を保つ
        comicSumb = []
        for comic in comicList:
            # comicListを順繰りに調べ、1ページ目の画像URLの取得を試みる
            try:
                image = MediaFiles.objects.get(comiclink=comic, comicpage=1)
            except:
                # なぜかURLを取得できなかったら、リストにnullを詰めてリスト順の整合性を保つ
                comicSumb.append(None)
            else:
                # 何事もなくURLを取得できたら、リストに詰める
                comicSumb.append(image.mediafile.url)
        
        # 連番管理漫画を表示しやすいように、漫画のレコードとサンプル画像URLを辞書でひとまとめにして、リストに詰める
        comicRecord = [
            {'comicList': comic, 'comicSumb': sumb}
            for comic,sumb
            in zip(comicList, comicSumb)
        ]

        # 各リストを辞書でひとまとめにして、キーでアクセスできるようにしてから呼び出し元に渡す
        context = {
                'comicRecord': comicRecord,
                'genreList': genreList,
                'mediaList': mediaList,
                'comicSumb': comicSumb,
            }
        return context
    
    # 編集中漫画の情報をコンテキストに与える
    def getEdittingComicContext(self, targetComic=None):
        # まずは普通にコンテキストを作る
        context = self.getList()

        # 編集中漫画のDBレコードを貰っておいて、プライマリキーとページリストを格納する
        if targetComic is not None:
            context['comicPK'] = targetComic.pk
            context['pageList'] = MediaFiles.objects.filter(comiclink=targetComic).order_by('comicpage')
        
        # 加工が終わったコンテキストを返す
        return context

    # 漫画登録ファイルのページ番号を連番に振り直す
    def comicPageSort(self, pageRecordList=None):
        # メディアファイルのレコードリストを順繰りに取り出し、リスト順iと対象レコードpageを抜き出して処理
        for i,page in enumerate(pageRecordList, 1):
            # ページ番号をリスト順で上書きし、歯抜け番号を除去
            page.comicpage = i
            # レコード毎にDBへ変更を書き込む
            page.save()
        return 0
    
    # 漫画登録ファイルを除外し、ページを振り直す
    def comicPageReject(self, pagePK=None):
        # プライマリキーから対象のファイルレコードを取得
        try:
            targetRecord = MediaFiles.objects.get(pk=pagePK)
        except:
            # 取得できなかったら処理をやめる
            return 0
        else:
            # 漫画との関連をnullで上書きし切り離す
            targetRecord.comiclink = None
            # 漫画ページの指定をnullで上書きし、再利用時に支障が無いようにする
            targetRecord.comicpage = None
            # レコードの変更をDBに書き込む
            targetRecord.save()

            # 除外対象メディアファイルにリジェクトジャンルを設定し、ファイル実体も移動
            self.setGenre(genrename='reject', pkList=[pagePK])

        return 0

    # GETリクエストへの応答メソッド
    def get(self, request, *args, **kwargs):
        # 漫画を指定しない丸腰リクエストだった場合
        if request.GET.get('comic_pk') is None:
            # 生成したリスト群とcomic.htmlテンプレートを使ってリクエストをレンダリングし、送り返す
            return render(request, 'comic.html', self.getList())

        # GETリクエストで漫画を指定していて、指定された漫画が存在するとき
        elif Comics.objects.filter(pk=request.GET['comic_pk']).exists() is True:
            # 編集指定漫画のDBレコードを取得
            try:
                targetComic = Comics.objects.get(pk=int(request.GET.get('comic_pk')))
            except:
                # 指定された漫画の取得に失敗したときは、丸腰リクエストと同様のレンダリングを行う
                return render(request, 'comic.html', self.getList())
            # 編集指定漫画の情報を詰めて応答
            return render(request, 'comic.html', self.getEdittingComicContext(targetComic=targetComic))

        # GETリクエストで漫画を指定したが、存在しなかった場合を想定
        else:
            # とりあえずgetList()で画面表示用リスト群を生成
            context = self.getList()
            # 指定された漫画が見つからなかった旨のエラーメッセージをコンテキストに追加
            context['comicError'] = '指定された漫画は存在しません。新たに作成してください。'
            # エラーメッセージ入りのコンテキストで画面をレンダリングし、送り返す
            return render(request, 'comic.html', context)

    # POSTリクエストへの応答メソッド
    def post(self, request, *args, **kwargs):
        # POSTリクエストは画面中のサブミットボタンごとにrequestキーの値を入れ分けて、処理を振り分けている

        # 漫画の新規生成を受け付ける処理の分岐
        if request.POST.get('request') == 'makecomic':
            # ジャンル名を格納
            genrename = request.POST.get('genrename')
            # 漫画タイトルを格納
            title = request.POST.get('title')

            # ジャンルが未指定の場合を弾くガード節
            if genrename == "new":
                # ベースとなるコンテキストを作成
                context = self.getList()
                # エラーメッセージを格納
                context['comicError'] = "ジャンルを指定してください"
                # エラーメッセージ入りコンテキストで返答し、先に進ませない
                return render(request, 'comic.html', context)
            
            # 漫画タイトルが未指定の場合を弾くガード節
            if title == "new":
                # ベースとなるコンテキストを作成
                context = self.getList()
                # エラーメッセージを格納
                context['comicError'] = "タイトルを指定してください"
                # エラーメッセージ入りコンテキストで返答し、先に進ませない
                return render(request, 'comic.html', context)
            
            # 漫画を新規作成する
            newComic = self.newComicGenerate(comicTitle=title, genrename=genrename)

            # 漫画編集画面へ、新規生成した漫画を指定した状態でリダイレクト
            return render(request, 'comic.html', self.getEdittingComicContext(targetComic=newComic))


        # ページ追加を受け付ける処理の分岐
        elif request.POST.get('request') == 'addpage':
            # 追加予定メディアファイルのプライマリキーリストを格納
            pages = self.RecievedPkListCast(recievedString=request.POST.get('pages'))
            # 登録先漫画のDBレコードを取得
            try:
                targetComic = Comics.objects.get(pk=int(request.POST.get('comicpk')))
            except:
                # 取得に失敗した場合は何もせず、ページを再レンダリング
                return render(request, 'comic.html', self.getList())
            
            # 指定されたファイルを漫画に登録
            self.setComic(comicTitle=targetComic.comicname, genrename=targetComic.genre.genrename, pkList=pages)
            
            # 編集中漫画の情報を詰めてリダイレクト
            return render(request, 'comic.html', self.getEdittingComicContext(targetComic=targetComic))


        # 漫画内ページの並び替えを受け付ける処理の分岐
        elif request.POST.get('request') == 'sortpage':
            # ページリストが空の場合を弾くガード節
            if request.POST.get('pages') == "new":
                # ベースのコンテキストを取得
                context = self.getList()
                # コンテキストにエラーメッセージを格納
                context['pageError'] = "ページが存在しません"
                # エラーメッセージ入りコンテキストで返答し先へ進ませない
                return render(request, 'comic.html', context)

            # ページ順文字列リストからプライマリキーリストを生成
            pages = self.RecievedPkListCast(recievedString=request.POST.get('pages'))
            # ページ順プライマリキーリストからページレコードリストを生成
            pageRecords = self.pkListToRecordList(pkList=pages, model=MediaFiles)

            # 操作対象漫画のプライマリキーをキャストして保持
            try:
                targetComic = Comics.objects.get(pk=int(request.POST.get('comicpk')))
            except:
                targetComic = None

            # ページ順を指定したリストを参照してDB更新処理を実行
            self.comicPageSort(pageRecordList=pageRecords)
            
            # 編集中漫画の情報を詰めてリダイレクト
            return render(request, 'comic.html', self.getEdittingComicContext(targetComic=targetComic))


        # 漫画内ページの除外を受け付ける処理の分岐
        elif request.POST.get('request') == 'rejectpage':
            # 対象ページファイルのプライマリキーを格納
            targetPK = int(request.POST.get('pages'))
            # 処理対象漫画のプライマリキーを保持
            try:
                targetComic = Comics.objects.get(pk=int(request.POST.get('comicpk')))
            except:
                # 処理対象漫画レコードの取得に失敗した場合は、画面をレンダリングし直す。
                return render(request, 'comic.html', self.getList())


            # ページの除外操作を行う
            self.comicPageReject(pagePK=targetPK)

            # ページを除外したことでページ番号が歯抜けになるので、連番になるように振り直す
            # 漫画に登録されているメディアファイルのレコードをDBから抽出し、ページ番号順にソートする
            comicPage = MediaFiles.objects.filter(comiclink=targetComic).order_by('comicpage')
            # メディアファイルのレコードリストを順繰りに取り出し、リスト順iと対象レコードpageを抜き出して処理
            self.comicPageSort(pageRecordList=comicPage)
            
            # 編集中漫画の情報を詰めてリダイレクト
            return render(request, 'comic.html', self.getEdittingComicContext(targetComic=targetComic))

        # 予期せぬ処理キーワードが飛んできた場合の処理
        else:
            # エラーメッセージと共にリダイレクト
            context = self.getList()
            context['commandError'] = "無効な操作です"
            return render(request, 'comic.html', context)



# 管理中ファイル閲覧処理
class BrowsingView(View, dataCast, RecordOperation, mediaDirectory):
    # GETリクエストへの応答メソッド
    def get(self, request, *args, **kwargs):
        # ジャンル選択用のジャンルリストをDBから取得
        # reject以外のジャンルを全て収集する
        genreList = MediaGenre.objects.exclude(genrename="reject").order_by('genrename')
        # コンテキスト辞書を作成し、閲覧開始画面をレンダリングして返送
        context = {}
        context['genreList'] = genreList
        return render(request, 'browse.html', context)


    # レコード抽出用フィルター関数生成メソッド
    def genFilter(self, genreList=None):
        # 既読排除なしのブロック
        allFilter = (
            Q(genre__pk__in=genreList)# ジャンルリストに該当するかつ、
            & (Q(comicpage__isnull=True) | Q(comicpage=1))# 漫画登録なし　または　漫画の1ページ目
        )
        # 既読排除を含めたブロック
        candidateFilter = (allFilter & Q(watched=False))# かつ、既読マークが付いていないもの

        # 各フィルターブロックを渡す
        return allFilter, candidateFilter


    # 既読ファイルマーク付け括り出しメソッド
    def watchedMark(self, watchedRecord=None, candidateFilter=None):
        # 既読マークを付与
        watchedRecord.watched = True
        # すぐにDBへ反映
        watchedRecord.save()
        # 操作後、次回乱択候補が残っているか検証
        if MediaFiles.objects.filter(candidateFilter).exists() is False:
            # 未読が残っていなかったら既読マークをリセット
            MediaFiles.objects.all().update(watched=False)
            # 一旦全消ししたので今回配信ファイルの既読マークを改めて付ける
            watchedRecord.watched = True
            # DBに反映
            watchedRecord.save()
        # 特に渡すものはないので処理を返す
        return 0

    # 乱択したメディアファイルが連番漫画か否かを判定するメソッド
    def mediaTypeDetect(self, targetRecord=None):
        # 漫画ページの設定がされているかどうかで判定
        if targetRecord.comicpage is None:
            # 単発メディアであればその旨のフラグを返す
            # # 漫画関連の返し値はnullにしておく
            media_type = "image"
            comic_page = None
            comic_last_page = None
        else:
            # 漫画ページが設定されていたら漫画の一部を引いたとみなす
            # 漫画のページ番号と、ページ総数を渡す
            media_type = "comic"
            comic_page = targetRecord.comicpage
            comic_last_page = MediaFiles.objects.filter(Q(comiclink=targetRecord.comiclink)).aggregate(Max('comicpage'))['comicpage__max']
        # メディア情報を並べて返す
        return media_type, comic_page, comic_last_page


    # Ajaxリクエスト対応メソッド(POSTリクエストで飛んでくる)
    def post(self, request, *args, **kwargs):
        # メディアファイル取得シリーズのリクエストが来たときの分岐
        if (request.POST.get('request') == 'pull') | (request.POST.get('request') == 'pull_comic'):
            # DBレコード抽出用Q関数を組み立て
            allFilter, candidateFilter = self.genFilter(genreList=self.RecievedPkListCast(recievedString=request.POST.get('genre')))

            # メディアファイル丸腰取得のとき
            if request.POST.get('request') == 'pull':
                # 配信候補のレコードリストを取得
                candidateRecordList = MediaFiles.objects.filter(candidateFilter)

                # 配信ファイルの乱択を行う
                # start=0, step=1, 末尾候補はsummaryLength-1
                pullMedia = candidateRecordList[randrange(candidateRecordList.count())]
                # 乱択で引いたメディアファイルに既読マークをつける
                self.watchedMark(watchedRecord=pullMedia, candidateFilter=candidateFilter)

                # 乱択で引いたメディアファイルが漫画かどうかを判定
                media_type, comic_page, comic_last_page = self.mediaTypeDetect(targetRecord=pullMedia)


            # 連番漫画の次ページメディアファイル取得のとき
            elif request.POST.get('request') == 'pull_comic':
                # DBから、与えられた漫画のプライマリキーに合致する、現表示中ページの次ページを取得
                try:
                    pullMedia = MediaFiles.objects.get(
                        comiclink__pk=int(request.POST.get('comic_pk')),
                        comicpage=int(request.POST.get('now')) + 1,
                    )
                except:
                    # ファイルレコードの取得に失敗したときは何もしない
                    pass
                else:
                    # 漫画の次ページを取得できたら、次ページを表示するための情報を集める
                    # 送信する漫画のページ番号と、漫画の最終ページ番号を与える
                    comic_page = pullMedia.comicpage
                    comic_last_page = MediaFiles.objects.filter(Q(comiclink=pullMedia.comiclink)).aggregate(Max('comicpage'))['comicpage__max']
                # media_typeはcomicをベタ打ち
                media_type = 'comic'

            # プログレスバー用データを生成する
            # 配信可能ファイル全件の数を取得
            allLength = MediaFiles.objects.filter(allFilter).count()
            # 既読ファイルの数を取得
            watchedLength = allLength - MediaFiles.objects.filter(candidateFilter).count()

            # 集めた情報でAjaxレスポンスを組み立てる
            response = {
                'callback': request.POST.get('genre'),  # 指定ジャンルをとりあえず送り返す
                'media_type': media_type,               # 引いたファイルが漫画か否かを通知
                'src': pullMedia.mediafile.url,         # 引いたメディアファイルをNginxから持ってくるためのURLを渡す
                'mediaPK': pullMedia.pk,                # 引いたメディアのプライマリキーを渡す(バック機能で使う)
                'allLength': allLength,                 # 乱択候補の母数を通知(プログレスバーで使う)
                'watchedLength': watchedLength,         # 既読ファイル数を通知(プログレスバーで使う)
                'comicPK': pullMedia.comiclink_id,      # 漫画のプライマリキーを通知(次のページを引くために使う)
                'comicPage': comic_page,                # 漫画の今のページ(1ページ目)を通知(漫画のページ数表示で使う)
                'comicLast': comic_last_page,           # 漫画の総ページ数を通知(漫画のページ数表示で使う)
            }
            # Ajaxレスポンスとしてユーザに送信
            return JsonResponse(response)


        # メディアファイルのリジェクト司令が来たときの分岐
        elif request.POST.get('request') == 'reject':
            # 除外指定されたファイルのレコード取得を試みる
            try:
                taergetMedia = MediaFiles.objects.get(pk=int(request.POST.get('media_pk')))
            except:
                # 取得に失敗した場合は何もしない
                pass
            else:
                # 漫画のページなのか単体ファイルなのかで処理を分ける
                if taergetMedia.comiclink is None:
                    # 漫画ページでない場合、対象ファイルをrejectジャンルに入れる
                    self.setGenre(genrename='reject', pkList=[int(request.POST.get('media_pk'))])
                else:
                    # 漫画ページの場合、ページの除去操作の後ページ順を振り直す
                    targetComic = taergetMedia.comiclink
                    ComicEditView.comicPageReject(self, pagePK=taergetMedia.pk)
                    ComicEditView.comicPageSort(self, pageRecordList=MediaFiles.objects.filter(comiclink=targetComic))

            # プログレスバーの表記を更新するためのデータを生成
            # DBレコード抽出用Q関数を組み立て
            allFilter, candidateFilter = self.genFilter(genreList=self.RecievedPkListCast(recievedString=request.POST.get('genre')))
            # 配信可能ファイル全件の数を取得
            allLength = MediaFiles.objects.filter(allFilter).count()
            # 既読ファイルの数を取得
            watchedLength = allLength - MediaFiles.objects.filter(candidateFilter).count()

            # プログレスバー更新情報をAjaxレスポンスとして送信する
            response = {
                'allLength' : allLength,            # 配信予定ファイル全件数を通知
                'watchedLength' : watchedLength,    # 既読済み配信予定ファイル件数を通知
            }
            return JsonResponse(response)


        # 得体のしれない分岐キーワードが来たときの分岐
        else:
            # エラーコードらしきものを送信しておく
            response = {
                'callback': "request is not arrowed."
            }
            return JsonResponse(response)



# クラスとして定義したviewを関数化して利用できるようにする
index = IndexView.as_view()
upload = UpLoadView.as_view()
medialist = MediaListView.as_view()
reject = RejectView.as_view()
comicedit = ComicEditView.as_view()
browse = BrowsingView.as_view()
