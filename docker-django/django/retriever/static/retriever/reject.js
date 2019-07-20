//除外ファイル処理画面のコントロール駆動と送信処理を記述


//ファイル複数選択コントロールを設置
$("#mediaSelector").selectable();
//ラジオボタン駆動コントロールを設置
$("#selectReject").buttonset();

//実行ボタンクリックで設定データを送信
$("#setReject").click(function(e){
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


    //ファイル処遇の選択をラジオボタンから収集
    var selectReject = $("#selectReject > input[name=selectReject]:checked").val();
    

    //収集したデータを隠しフォームに追加する
    $("#hiddenForm").append(hiddenInput('selectMedia', chooseMedia.toString()))
                    .append(hiddenInput('selectReject', selectReject));
    
    //隠しフォームのデータをPOST送信
    $("#hiddenForm").submit();
});