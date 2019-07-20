//ファイル分類画面にてUIを駆動する
//かつ、設定データを送信する処理


//複数選択エリアでjquery UIを作動させる
$("#mediaSelector").selectable();
//ジャンル設定セレクトボックスで自由入力付きセレクトボックスを作動させる
$("#genreSelector").AutoCompleteWithPullDown({position:{my:"left bottom",at:"left top"}});


//サブミットボタンを押したときに走るPOST処理
$('#setGenre').click(function(e){
    //選択されたファイルのプライマリキーを格納するリスト
    var chooseMedia = [];
    //選択されたファイルの情報が格納されたカードのjqueryオブジェクトが見えるハズ
    console.log($('#mediaSelector > li.ui-selected'));
    //選択されたファイルカードの集合から一枚ずつ処理
    $('#mediaSelector > li.ui-selected').map(function(){
        //一枚ずつ処理されているかプライマリキーを監視して確認
        console.log($(this).attr('pk'));
        //カードのpk属性からファイルのプライマリキーを取得し、一時保持
        //プライマリキー格納用リストの末尾に突っ込む
        chooseMedia.push($(this).attr('pk'));
    });

    //出来上がったプライマリキーリストをとりあえず参照
    console.log(chooseMedia);
    //リストを文字列化したときにどんなフォーマットになるか確認してた
    console.log(chooseMedia.toString());

    //何も選択せずにサブミットボタンを押したら警告ポップアップを出す
    if (chooseMedia.toString().length == 0){
        alert('追加する画像を選択してください。');
        //処理をココで返してサブミットに進ませない
        return 0;
    }


    //ジャンル設定セレクトボックスから設定値を回収する
    var genrePK = $('.bottomInput select[name=genre_pk]').val();
    var genreName = $('.bottomInput input.custom-combobox-input').val();

    //何も選択せずにサブミットボタンを押したら警告ポップアップを出す
    if (genreName.length == 0){
        alert('設定するジャンルを選択してください。');
        //処理をココで返してサブミットに進ませない
        return 0;
    }
    

    //ファイルのプライマリキーリストを文字列化したデータを隠しフォームに追加する
    $('#hiddenForm').append(hiddenInput('selectMedia', chooseMedia.toString()))
                    .append(hiddenInput('genre_pk', genrePK))
                    .append(hiddenInput('genrename', genreName));

    //隠しフォームのデータを使ってPOST送信
    $('#hiddenForm').submit();
});