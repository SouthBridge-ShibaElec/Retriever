//隠しフォームへのデータ登録用関数

//キーバリュー形式でデータを受け取る
function hiddenInput(key, value){
    //valueがnullだと困るのでダミーデータを入れておく
    //空文字列が来ても同様に対処
    if(value == null || value == ""){
        value = "new";
    }
    //隠しフォーム登録用レコードをjqueryオブジェクトとして組み立てる
    var record = $('<input>').attr({
        'type': 'hidden',
        'name': key,
        'value': value,
   });
   //登録したデータを格納したjqueryオブジェクトを返す
   return record;
}
