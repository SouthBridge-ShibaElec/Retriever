//自由入力テキストボックス
//プルダウンメニュー付き

;(function($) {
    //.AutoCompleteWithPullDown({オプションキー:値})で呼び出し
    $.widget( "my.AutoCompleteWithPullDown", {

        //ウィジェットのオプションを設定するオブジェクト
        options: {
            //位置についてのオプションを受け付け、デフォルト値を設定
            position: {my:"left top",at:"left bottom"}
        },
        
        //ウィジェット生成プライベートメソッド
        _create: function() {
            //元要素の直下にウィジェットエリアを生成
            this.wrapper = $( "<span>" )
                .addClass( "custom-combobox" )
                .insertAfter( this.element );
   
            
            this.element.hide();            //元要素を非表示に
            this._createAutocomplete();     //オートコンプリートエリアを生成
            this._createShowAllButton();    //選択候補プルダウンボタンを生成
        },
   
        //オートコンプリートエリアを組み立てる
        _createAutocomplete: function() {
            //ウィジェットインスタンス自身を変数に捕捉
            var self = this;
            /*
            //元select要素の選択済み要素を取得
            var selected = this.element.children( ":selected" ),
            //選択済み要素が存在すれば文字列を取得、無ければnull
            value = selected.val() ? selected.text() : "";
            */
            //選択済みになっているセレクトボックスを未選択にする
            this.element.val("");
            this.element.selectedIndex = -1;
            //テキストボックスの初期値はnullにする
            var value = "";
   
            //テキストボックスを生成
            this.input = $( "<input>" )
                .appendTo( this.wrapper )
                .val( value )
                .addClass( "custom-combobox-input ui-widget ui-widget-content ui-state-default ui-corner-left" )
                //選択候補エリアを作動させる
                //オプションはココに入れる
                .autocomplete({
                    delay: 0,
                    minLength: 0,
                    source: $.proxy( this, "_source" ),
                    //位置についてのオプションを渡している
                    position: self.options.position
                });
            
            //選択候補プルダウンエリアへの設定
            this.input.autocomplete("widget")
                .addClass("overflow");
   
            //選択候補エリアに何らかの操作をしたときの挙動を定義（たぶん）
            this._on( this.input, {
                //選択候補エリアをクリックしたとき
                autocompleteselect: function( event, ui ) {
                    ui.item.option.selected = true;
                    //select要素の選択肢にselectフラグを付けてる
                    this._trigger( "select", event, {
                        item: ui.item.option
                    });
                },
                //テキストボックスの内容が書き換えられたとき
                autocompletechange: "_removeIfInvalid"
            });
        },
   
        //選択候補プルダウンボタンを組み立てる
        _createShowAllButton: function() {
            var input   = this.input;   //操作対象のウィジェットを補足しておく
            var wasOpen = false;        //開閉済みかを示すフラグ
   
            //ボタンはa要素として組み立てる
            $( "<a>" )
                .attr( "tabIndex", -1 )
                //ウィジェット生成エリアの末尾に挿入
                .appendTo( this.wrapper )
                //jqueryUIのボタンウィジェット化している
                .button({
                    //jqueryUI組み込みアイコンの下矢印を表示させている
                    icons: {
                        primary: "ui-icon-triangle-1-s"
                    },
                    //テキストは貼らない
                    text: false
                })
                //角丸めを剥がす
                .removeClass( "ui-corner-all" )
                //プルダウンメニューの一部として認識させ、右側の角を丸める
                .addClass( "custom-combobox-toggle ui-corner-right" )
                //上空をマウスで押された瞬間に、プルダウンメニューの表示状態を確認する
                .on( "mousedown", function() {
                    wasOpen = input.autocomplete( "widget" ).is( ":visible" );
                })
                //マウスクリックが成立したら本番開始
                .on( "click", function() {
                    //入力フォーカスはテキストボックスに移譲
                    input.trigger( "focus" );
   
                    //プルダウンメニューが開いてたときは、閉める
                    if ( wasOpen ) {
                        return;
                    }
   
                    //テキストボックスが空のときにプルダウンメニューを開けたら、全項目を表示するように誤魔化す
                    input.autocomplete( "search", "" );
                });
        },
   
        //テキストボックスの入力に一致する選択肢を検索して返す
        _source: function( request, response ) {
            //テキストボックスの中身から正規表現オブジェクトを生成
            var matcher = new RegExp( $.ui.autocomplete.escapeRegex(request.term), "i" );
            
            //ウィジェット生成元要素にある選択肢からヒットするものを回収する
            response( this.element.children( "option" ).map(function() {
                var text = $( this ).text();
                if ( this.value && ( !request.term || matcher.test(text) ) )
                    return {
                        label: text,
                        value: text,
                        option: this
                    };
                })
            );

            //テキストボックスが空のときは選択肢の選択フラグをクリア
            if(!request.term){
                this.element.val("");
            }
        },
   
        //選択肢にない入力を受けたときの処理
        _removeIfInvalid: function( event, ui ) {
            //選択肢に存在する内容が入力されていたとき用のガード節
            //ui.itemにはウィジェット生成元要素に定義された選択値が入っている
            if ( ui.item ) {
                //何もしなくていいのでさっさと返す
                return;
            }
   
            //大文字小文字を区別しない緩めの条件で選択候補を検索する
            var value = this.input.val(),
            //全部小文字にする
            valueLowerCase = value.toLowerCase(),
            valid = false;
            this.element.children( "option" ).each(function() {
                //選択候補の中にマッチするものがあれば、それを選択状態にして返す
                if ( $( this ).text().toLowerCase() === valueLowerCase ) {
                    this.selected = valid = true;
                    return false;
                }
            });
            //緩め検索で選択肢が見つかったときのガード節
            if ( valid ) {
                //何もしなくて良くなったのでさっさと返す
                return;
            }
   
            //ココから先は妥当な選択肢が見つからなかったときの処理
            
            //テキストボックスの入力が空かどうかを判定
            if (value.length > 0) {
                //ウィジェット生成元要素の選択値は入れようがないのでnullにしておく
                this.element.val( "" );
            } else {
                //テキストボックスの入力が空のとき

                //テキストボックスの中身、ウィジェット生成元要素の選択値をnullにしておく
                this.input.val( "" );
                this.element.val( "" );
            }
        },
   
        //ウィジェット剥がしの命令を受けたとき用のお片付けメソッド
        _destroy: function() {
            this.wrapper.remove();  //ウィジェットは削除
            this.element.show();    //生成元要素を再表示
        }
    });
})(jQuery);