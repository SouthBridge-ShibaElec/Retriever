//漫画編集画面の操作データを収集して送信するJS


// コンボボックスをコピペコードの力で自由入力付きに拡張
$("#genreSelector").AutoCompleteWithPullDown();

//漫画新規作成用サブミットボタンを押されたときの送信処理
$('#makeComic').click(function(e){
   //送信に必要なデータを集める
    var title = $('.new_comic input[name=make_comic_name]').val();
    var genrePK = $('.new_comic select[name=genre_pk]').val();
    var genreName = $('.new_comic input.custom-combobox-input').val();

    console.log('makeComic : ' + title + ',' + genrePK + ',' + genreName);

    //漫画タイトルが未入力のときにエラーを出すガード節
    if(title == ''){
        alert('漫画のタイトルを設定してください。');
        return 0;
    }
    //漫画ジャンルが未指定のときにエラーを出すガード節
    if(genreName === ""){
        alert('漫画のジャンルを指定してください');
        return 0;
    }


    //送信用隠しフォームにデータを乗せる
    $('#hiddenForm').append(hiddenInput('request', 'makecomic'))
                    .append(hiddenInput('title', title))
                    .append(hiddenInput('genre_pk', genrePK))
                    .append(hiddenInput('genrename', genreName));
    
    //隠しフォームにサブミットさせる
    $('#hiddenForm').submit();
});


//複数選択エリアで複数選択コントロールを作動させる
$("#mediaSelector").selectable();
//ファイル登録ボタンを押されたときの送信処理
$('#setMedia').click(function(e){
    //選択ファイルのプライマリキー格納用配列を宣言
    var chooseMedia = [];

    //選択済みマークがされたカードを走査してプライマリキーを収集
    console.log($('.mediaBox .media_list li.ui-selected'));
    $('.mediaBox .media_list li.ui-selected').map(function(){
        console.log($(this).attr('pk'));
        var mediaPK = $(this).attr('pk');
        //格納用配列に取得したプライマリキーをプッシュ登録
        //一時変数、いらなくない?
        chooseMedia.push(mediaPK);
    });
    console.log(chooseMedia);
    console.log(chooseMedia.toString());

    //編集対象漫画が選択されていないときのガード節
    //データを集める前に出すべきでは?
    if ($('.comicBox .comic_list li.comic_record.active').length == 0){
        alert('追加先の漫画を選択してください。');
        return 0;
    }

    //ファイルが選択されていないときのガード節
    //toStringしなくても良くない?
    if (chooseMedia.toString().length == 0){
        alert('追加する画像を選択してください。');
        return 0;
    }

    console.log($('.comicBox .comic_list li.comic_record.active').attr('pk'))

    //集めたデータを送信用隠しフォームに登録
    $('#hiddenForm').append(hiddenInput('request', 'addpage'))
                    .append(hiddenInput('comicpk', $('.comicBox .comic_list li.comic_record.active').attr('pk')))
                    .append(hiddenInput('pages', chooseMedia.toString()));
    
    //隠しフォームにサブミットさせる
    $('#hiddenForm').submit();
});


//ページ順設定エリアでソートコントロールを作動させる
$("#pageSorter").sortable({placeholder:"ui-state-highlight"});
//ドラッグ文字選択が誤爆するとウザいので止める
$("#pageSorter").disableSelection();
//ページ順更新ポタンが押されたときの送信処理
$('#setPage').click(function(e){
    //ページ順設定エリアのコントロールから配列でデータを収集
    var pageList = $('#pageSorter').sortable('toArray', {attribute: "pk"});
    console.log(pageList);

    //ページが存在しないときのガード節
    if(pageList.length === 0){
        alert("ページ付け対象のファイルがありません");
        return 0
    }

    //この行何やってんだっけ…
    pageList = pageList.map(Number);
    console.log(pageList);

    //集めたデータを送信用隠しフォームに登録
    $('#hiddenForm').append(hiddenInput('request', 'sortpage'))
                    .append(hiddenInput('comicpk', $('.comicBox .comic_list li.comic_record.active').attr('pk')))
                    .append(hiddenInput('pages', pageList.toString()));
    
    //隠しフォームにサブミットさせる
    $('#hiddenForm').submit();
});


//ページ順設定エリアのページ除外ボタンが押されたときの送信処理
//いっぱいあるのでmapで全てのボタンに処理を貼り付け
$('.pageBox #pageSorter li .pageReject').map(function(){
    console.log(this);
    //thisで各々の場所での処理に適応させる
    $(this).click(function(e){
        //データを送信用隠しフォームに登録
        $('#hiddenForm').append(hiddenInput('request', 'rejectpage'))
                        .append(hiddenInput('comicpk', $('.comicBox .comic_list li.comic_record.active').attr('pk')))
                        .append(hiddenInput('pages', $(this).attr('pk')));
        
        //隠しフォームにサブミットさせる
        $('#hiddenForm').submit();
    });
});