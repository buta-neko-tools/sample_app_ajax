$(function(){
	// ページ読み込み時にも描画されるようにする
	updateBlend();
	// スライダーを操作したときにblend画像を更新する
	$('#blend-slider').on('change', function() {
		updateBlend();
	});
});

function updateBlend() {
	// flaskの/blendエンドポイントにリクエストする
	$.ajax({
	// リクエストメソッドはPOSTでいくぜ、という宣言
	type: 'POST',
	// flaskサーバの/blendというエンドポイントにリクエストする
	url: '/blend',
	// flaskのrequest.get_data()で取得できるデータ
	data: $('#blend-slider').val(),
	// よく分からなければおまじないの認識でいい
	contentType: 'application/json',
}).then(
	// flaskとの通信がうまくいったときの処理
	data => $('#blend-image').attr('src', data),
	// flaskとの通信がエラーになったときの処理
	error => console.log(error)
	);
};