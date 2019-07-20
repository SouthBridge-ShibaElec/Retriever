//アップロード画面のコントロール駆動と送信処理を記述


//ココから先はコピペコードコピペ元は下記URLより
//https://cccabinet.jpn.org/bootstrap4/javascript/forms/file-browser
//一部改変

//ファイル選択エリアにファイル選択時発動のプレビュー表示関数をイベントリスナとして貼り付ける
$('.custom-file-input').on('change', handleFileSelect);

//選択されたファイルのプレビューを作成する関数
function handleFileSelect(evt) {
    //ファイル選択が2回目以降のときは、前回のプレビューを消してお掃除
    $('#preview').remove();

    //プレビューを入れておくDIV箱を生成
    $(this).parents('.input-group').after('<div id="preview"></div>');
    
    //イベント貼り付け元のファイル選択コントロールから、選択されたファイル郡オブジェクトを収集
    var files = evt.target.files;
    //収集したファイルを1つずつ取り出して処理
    for (var i = 0, f; f = files[i]; i++) {
        //ファイル群オブジェクトを操作できるようにしてくれるクラス?をコンストラクト
        var reader = new FileReader();
        //ファイルを一気に走査して処理を貼ってくれるらしい
        reader.onload = (function(theFile) {
            return function(e) {
                //処理対象ファイルが画像か判定
                if (theFile.type.match('image.*')) {
                    //画像では画像のプレビューとファイル名の表示
                    var $html = ['<div class="previewCard"><img class="img-thumbnail popup" src="', e.target.result,'" title="', escape(theFile.name), ' /><div class="text-center">', escape(theFile.name),'</div></div>'].join('');
                } else {
                    //画像以外はファイル名のみの表示
                    var $html = ['<div class="previewCard"><span class="">', escape(theFile.name),'</span></div>'].join('');
                }
                //プレビュー格納DIV箱に挿入
                $('#preview').append($html);
            };
        })(f);
        //これはなんだかわからねぇ…
        reader.readAsDataURL(f);
    }
    //ファイル選択コントロール内ラベルにファイル総数を表示
    $(this).next('.custom-file-label').html(+ files.length + '個のファイルを選択しました');
}

//ファイル選択を取り消したときの処理
$('.reset').click(function(){
    //ファイル選択コントロール内ラベルの表記を元に戻す
    $(this).parent().prev().children('.custom-file-label').html('ファイル選択...');
    //ファイル選択コントロールの入力値(ファイル群)をnullクリア
    $('.custom-file-input').val('');
    //プレビュー格納DiV箱を削除してお掃除
    $('#preview').remove('');
})

//コピペココまで