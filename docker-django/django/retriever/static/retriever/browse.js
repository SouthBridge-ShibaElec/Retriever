//ジャンル選択リストで複数選択コントロールを作動させる
//ドラッグ文字選択が誤爆するとウザいので止める
$('#genreList').selectable().disableSelection();


//DOMからCSRFトークンを貰う
var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
//Ajax通信でCSRFトークンを使う設定
//ココから先はコピペコード
//django本より
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
//コピペはココまで


//処理段階問わず横断的に持ちたい値
var genreSelect = [];           //選択したジャンル
var mediaArchive = [];          //閲覧したファイル（巻き戻し機能で使用）
var mediaArchivePointer = -1;    //ファイルリスト中の閲覧中ファイルを示すポインタ(1枚目を引いたときに0を指すよう初期化)


//巻き戻し機能のポインタをコンソールで監視する関数
function printArchivePointer(caption){
    //最新の画像を見ているとき、ポインタの値+1=配列の長さ
    console.log('--' + caption + '--')                              //ポインタ値を確認したタイミングを記録
    console.log('length : ' + mediaArchive.length.toString());      //巻き戻し配列の長さを使おうとしたときに返る値
    console.log('pointer : ' + mediaArchivePointer.toString());     //ポインタの位置を取得しようとしたときに見える値
    console.log(JSON.stringify(mediaArchive));                      //巻き戻し配列の中身をダンプ。処理したタイミングの状態を見るためにJSON.stringify()を噛ましてる
}


//届いたメディアの種類を判定し、表示ボックスに代入する関数
function mediaDisplay(mediaURL){
    //ビデオファイル判定用正規表現オブジェクト
    var videoRegex = /.+\.(mp4|m4a)$/i;
    //ビデオ表示DOMへのショートカット。JS再生制御に使う
    var video = $('.mainArea .videoBox video').get(0);


    //とりあえず全部の画面を非表示化
    //漫画ページ表記も一緒に非表示にする
    $('.mainArea > *, .progress .comicLabel').addClass('disable');
    //ビデオファイルが入っている場合は止める
    video.pause();


    //届いたメディアが動画かどうかを判定
    if(videoRegex.test(mediaURL)){
        //動画の場合は動画ボックスにURLを代入する
        $('.mainArea .videoBox video').attr('src',mediaURL);
        //動画ボックスを可視状態にする
        $('.mainArea .videoBox').removeClass('disable');
        //代入と非表示解除が終わったら再生スタート
        video.play();
    }else{
        //画像の場合は画像ボックスにURLを代入する
        $('.mainArea .imageBox img').attr('src',mediaURL);
        //画像ボックスを可視状態にする
        $('.mainArea .imageBox').removeClass('disable');
    }
}


//プログレスバーを駆動する関数
function proggressbarOverwrite(barObject, labelObject, allLength, proggressLength){
    //プログレスバー表示を更新する
    //bootstrapのprogressbarは進捗表示をwidth直接指定で渡すので、計算が必要
    progress = ( proggressLength / allLength) * 100;
    barObject.css('width', progress.toString() + '%');
    //アクセシビリティ用にaria-に生データを入れる
    barObject.attr('aria-valuemax', allLength);
    barObject.attr('aria-valuenow', proggressLength);
    //生データ数字表示を書き換える
    labelObject.text(proggressLength.toString() + '/' + allLength);

}


//取得したファイルを画面に表示させる関数(Ajax成功時呼び出しを想定)
function mediaRender(getData){
    //届いたメディアを表示させる
    mediaDisplay(getData.src);
    //プログレスバー表示を更新する
    proggressbarOverwrite($('.progress .progress-bar'), $('.progress .progressLabel'), getData.allLength, getData.watchedLength);

    //ファイルが漫画として届いた場合は、ページ表記を駆動する
    if(getData.media_type == 'comic'){
        //漫画内ページ表記を更新する
        //漫画は１まとまりで1コンテンツとするので、プログレスバーはイジらない
        $('.progress .comicLabel .now').text(getData.comicPage);
        $('.progress .comicLabel .all').text(getData.comicLast);
        //プライマリキーは非表示。漫画の次ページを取り寄せるときにJSで値を拾う
        $('.progress .comicLabel .pk').text(getData.comicPK);
        //非表示になっていた漫画ページ表記を可視状態にする
        $('.progress .comicLabel').removeClass('disable');
    }

    //巻き戻し機能用リストにURLとプライマリキーを登録
    var srcDict = {src: getData.src, pk: getData.mediaPK};
    mediaArchive.push(srcDict);
    //ポインタの末尾を指すようインクリメント
    mediaArchivePointer++;
    
}


//プログレスバーの更新のみを行う関数(Ajax成功時呼び出しを想定)
function progressbarDriveAjax(getData){
    //プログレスバー表示を更新する
    proggressbarOverwrite($('.progress .progress-bar'), $('.progress .progressLabel'), getData.allLength, getData.watchedLength);
}


//ジャンル選択画面の「閲覧開始」ボタンをクリックされた場合の処理
$('#startBrowse').click(function(e){
    //選択されたファイルのプライマリキーを集め、リストに格納しておく
    $('#genreList li.ui-selected').map(function(){
        var genrePK = $(this).val();
        genreSelect.push(genrePK);
    });
    //ジャンルを選択しなかったときのガード節
    if(genreSelect.length == 0){
        alert("ジャンルを設定してください。");
        return 0;
    }
    console.log(genreSelect);

    //Ajax通信でメディア配信を要求
    $.post(
        '/browse/',
        {
            request: "pull",                //リクエストの種類を通知
            genre: genreSelect.toString(),  //取得予定ファイルのジャンルを通知
        },
        mediaRender,
        "json"
    );

    printArchivePointer('閲覧開始直後');
});


//次のファイルボタンを押されたときの処理
$('.next').click(function(e){
    printArchivePointer('次へ押下直後');

    //巻き戻し機能を使用中かどうかを判定するガード節
    //最新の画像を見ているとき、ポインタの値+1=配列の長さ
    if((mediaArchivePointer+1) < mediaArchive.length){
        //ポインターを新しい方へ送る
        mediaArchivePointer++;

        //巻き戻しリストから取り出したデータを表示する
        mediaDisplay(mediaArchive[mediaArchivePointer].src);

        //巻き戻し利用のときはAjax使わないのですぐに返しちゃう
        return 0;
    }

    //巻き戻しポインタが配列の末尾を指しているとき、Ajaxで別ファイルを取り寄せる
    //漫画ページ表記の現在・最大が同じ値だったら新しいファイルを取り寄せる
    //ページロード初期値はNone/Noneなので、やはり新ファイル取り寄せになる
    if($('.progress .comicLabel .now').text() != $('.progress .comicLabel .all').text()){
        //ページ表記が別の値だったときは漫画閲覧中
        //漫画の次ページを取り寄せる
        $.post(
            '/browse/',
            {
                request: "pull_comic",                              //リクエストの種類を通知
                genre: genreSelect.toString(),                      //取り寄せ予定のジャンル一覧を渡す
                comic_pk: $('.progress .comicLabel .pk').text(),    //取り寄せる漫画のプライマリキーを渡す
                now: $('.progress .comicLabel .now').text(),        //現在閲覧中のページ番号を渡す
            },
            //Ajaxが成功したらメディア表示処理を走らせる
            mediaRender,
            'json'
        );
    }else{
        //漫画閲覧中ではないOR漫画の閲覧が終わったとき
        //メディアを乱択で取り寄せる
        $.post(
            '/browse/',
            {
                request: "pull",                //リクエストの種類を通知
                genre: genreSelect.toString(),  //取り寄せ予定のジャンル一覧を渡す
            },
            //Ajaxが成功したらメディア表示処理を走らせる
            mediaRender,
            'json'
        );
    }

    printArchivePointer('次へ処理後');
});


//巻き戻しボタンを押されたときの処理
$('.prev').click(function(e){
    printArchivePointer('戻る押下直後');

    //巻き戻しポインタが最後を指しているかを判定
    if(mediaArchivePointer >= 1){
        //最後の一個手前までなら表示処理
        //この一押しでポインタがリストの最後を指す
        mediaArchivePointer--;

        //巻き戻しリストからURLを取り出して、メディアを表示させる
        mediaDisplay(mediaArchive[mediaArchivePointer].src);

    }else{
        //巻き戻しポインタが最後を指しているので、巻き戻せなさそうな表示をする
        $('.prev > span').addClass('error');
        //CSSと連動して、ボタンを一瞬赤くする
        setTimeout(function(){$('.prev > span').removeClass('error');},500);
    }

    printArchivePointer('戻る処理後');
});


//ファイルの除外ボタンを押されたときの処理
$('.reject').click(function(e){
    //表示中ファイルのプライマリキーを除外対象としてAjax送信
    //Ajax成功時点でプログレスバー表示を更新
    $.post(
        '/browse/',
        {
            request: "reject",                                  //リクエストの種類を通知
            genre: genreSelect.toString(),                      //取り寄せ予定のジャンル一覧を渡す
            media_pk: mediaArchive[mediaArchivePointer].pk,     //リジェクト対象ファイルのプライマリキーを通知
        },
        progressbarDriveAjax,
        'json'
    );
    //除外したファイルを巻き戻しリストからも取り除く
    mediaArchive.splice(mediaArchivePointer, 1);
    
    //ファイルを取り除いた結果、巻き戻しリストにファイルが残っているかを判定
    if(mediaArchive.length >= 1){
        //残っている場合は除外したファイルの手前のファイルを表示
        //巻き戻しリストからURLを取り出し、メディアを表示する
        printArchivePointer('ファイルリジェクト直後');
        if(mediaArchivePointer >= 1){
            //リストのケツ以外を消したときは、消したファイルの一つ過去のファイルを表示
            mediaArchivePointer--;
            mediaDisplay(mediaArchive[mediaArchivePointer].src);
        }else{
            //リストのケツを消したときは、ケツから2番目(削除後のケツ)を表示
            mediaDisplay(mediaArchive[mediaArchivePointer].src);
        }
        
    }else{
        //巻き戻しリストにファイルが残っていない場合は、次へボタンを強制発火させてAjax通信のくだりを流用する
        console.log('巻き戻しリスト枯渇により再取得');
        //ファイルを取得していない状態にポインタを初期化
        mediaArchivePointer = -1;
        $('.next').click();
    }
});