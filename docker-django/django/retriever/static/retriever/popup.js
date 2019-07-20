//メディアファイルのサムネイルクリック時ポップアッププレビュー
//popup.cssと合わせて使用すること

;(function($){
    //ページ末尾にプレビュー用DIV箱を設置
    $("<div></div>", {id: "previewLayer"}).hide().appendTo("body");

    //クリックされたサムネイルからメディアURLを回収し、プレビューの準備をする関数
    function previewer(e){
        //イベントが発生した要素からURLを取得する
        var url = $(e.target).parent("a").attr("href") || $(e.target).attr("href") || $(e.target).attr("src");
        //URL取得に失敗したときのガード節、何もさせずに返す
        if(!url){ return false; }

        //プレビュー用DIV箱を初期化し、画像要素を追加、フェードインで表示
        $("#previewLayer").empty()
                          .append($("<img>", {src: url}))
                          .fadeIn('fast');
        
        return false;
    };

    //.popup要素がクリックされたときにプレビューを生成し表示する(静的)
    $(".popup").mousedown(function(e){
        //バックプロパゲーションを抑止し、jquery UIと共存
        e.stopPropagation();
    });
    $(".popup").click(function(e){
        previewer(e);   //クリックされたらプレビューを実施
        return false;
    });
    
    //動的生成された要素にも適用
    $("main").on("mousedown", ".popup", function(e){
        //バックプロパゲーションを抑止し、jquery UIと共存
        e.stopPropagation();
    });
    $("main").on("click", ".popup", function(e){
        previewer(e);   //クリックされたらプレビューを実施
        return false;
    });

    //プレビューエリアがクリックされたらプレビューエリアを閉じる
    $("#previewLayer").click(function(e){
        $("#previewLayer").fadeOut('fast');
    })
})(jQuery);