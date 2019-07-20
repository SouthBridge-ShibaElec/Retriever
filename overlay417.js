//画像をポップアッププレビューするコピペコード
//ソース：https://spelunker2.wordpress.com/2014/09/09/jquery%E3%81%A7%E7%94%BB%E5%83%8F%E3%83%9D%E3%83%83%E3%83%97%E3%82%A2%E3%83%83%E3%83%97%E3%82%92%E4%BD%9C%E3%81%A3%E3%81%9F/


$(function(){

$("<div></div>", {id: "overlay417"}).hide().appendTo("body");

$(".popup").click(function(e) {

    //イベントが発生した要素からURLを取得する
    var url = $(e.target).parent("a").attr("href") || $(e.target).attr("href") || $(e.target).attr("src");
    if(!url){ return false; }


    //対象画像を読み込んで、サイズを計算してからポップアップする
    var preload = new Image();
    preload.onload = function() {
        //ウインドウのサイズ
        var windowW   = $(window).width();
        var windowH   = $(window).height();

        //画像の表示大サイズ
        var displayW = $(e.target).width();
        var displayH = $(e.target).height();

        //画像の原寸大サイズ
        var imgW = preload.width;
        var imgH = preload.height;

        //原寸大で表示した時のはみ出る量を計算。正ならはみ出る
        var margin = 80;
        var overW  = imgW - windowW + margin;
        var overH  = imgH - windowH + margin;


        //横も縦もはみ出ない時
        if(overW <= 0 && overH <= 0){
            popupW = imgW;
            popupH = imgH;
        }

        //横だけはみ出る時
        else if(overW > 0 && overH <= 0){
            popupW = windowW - margin;
            popupH = popupW * imgH / imgW;
        }

        //縦だけはみ出る時
        else if(overW <= 0 && overH > 0){
            popupH = windowH - margin;
            popupW = popupH * imgW / imgH;
        }

        //横も縦もはみ出る時
        else{
            if(overW > overH) {
                //横を画面内に収める
                popupW = windowW - margin;
                popupH = popupW * imgH / imgW;
                //まだ縦がはみ出る場合
                if(popupH > (windowH - margin)){
                    var beforeH = popupH;
                    popupH = windowH - margin;
                    popupW = popupH * popupW / beforeH;
                }
            }
            else{
                //縦を画面内に収める
                popupH = windowH - margin;
                popupW = popupH * imgW / imgH;
                //まだ横がはみ出る場合
                if(popupH > (windowH - margin)){
                    var beforeW = popupW;
                    popupW = windowW - margin;
                    popupH = popupW * popupH / beforeW;
                }
            }
        }

        //原寸大よりポップアップの方が大きい場合は、原寸大で表示する(拡大はしない)
        if(popupW > imgW || popupH > imgH){
            popupW = imgW;
            popupH = imgH;
        }

        //表示上よりポップアップの方が小さい場合は、新しいウインドウを開いて終了
        /*if(popupW < displayW || popupH < displayH){ 
            window.open(url);
            return false;
        }*/

        //ポップアップの表示位置を決める
        var popupL = (windowW/2) - (popupW/2) + $(window).scrollLeft();
        var popupT = (windowH/2) - (popupH/2) + $(window).scrollTop();

        //ポップアップの表示位置とサイズを整数にする
        popupL = Math.round(popupL);
        popupT = Math.round(popupT);
        popupW = Math.round(popupW);
        popupH = Math.round(popupH);

        //デバッグ用
        //console.log('画像:' + imgW + '*' + imgH + ', 表示上:' + displayW + '*' + displayH + ', ウインドウ:' + windowW + '*' + windowH + ', ポップアップ画像:' + popupW + '*' + popupH + ', ポップアップ位置:' + popupL + '*' + popupT);

        //レイヤー内を空にする→CSSを適用→imgタグ追加→表示
        $("#overlay417").empty().css({
            'height'    : $(document).height(),
            'position'  : 'absolute',
            'top'       : '0',
            'left'      : '0',
            'width'     : '100%',
            'padding'   : '0',
            'margin'    : '0',
            'z-index'   : '100',
            'cursor'    : 'pointer',
            'background-color': 'rgba(255,255,255,0.4)'
        })
        .append($("<img>", {src: url, width: popupW, height: popupH}))
        .fadeIn('fast');

        //レイヤー内画像にCSSを適用
        $("#overlay417 img").css({
            'left'       : popupL,
            'top'        : popupT,
            'position'   : 'absolute',
            'display'    : 'inline-block',
            'border'     : '7px solid white',
            'box-sizing' : 'content-box',
            'box-shadow' : '0px 0px 10px rgba(0, 0, 0, 0.3)'
        });
    };
    preload.src = url;
    return false;
});


$("#overlay417").click(function() {
    $("#overlay417").hide();
});


});