// ----- Ajax前のおまじない start -----
function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
	beforeSend: function (xhr, settings) {
		if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		}
	}
});
// ----- Ajax前のおまじない end -----

// スライダーの操作を検知する
// inputにするとリアルタイムで検知が可能
$('#ajax-slider').on('input', function(e) {
	// フォームでスライダーが操作されたときに、フォーム送信の通信を止めるためにpreventDefault()を使用
	e.preventDefault();
	// サーバに送信するリクエストの設定
	$.ajax({
		// リクエストを送信するURLを指定
		// jsを外部に設置してもpropならformの内容を引き継げるのでDjangoテンプレートは不要
		'url': $('#ajax-number').prop("action"),
		// HTTPメソッドのGET通信かPOST通信を指定
		'method': $('#ajax-number').prop("method"),
		// サーバに送信するデータの指定
		'data': {
			'num': $('#ajax-slider').val(),
		},
		// データ形式（ここではjson）を指定
		'dataType': 'json'
	})
	// 通信成功時の処理
	// views.pyから受け取ったJSONデータをページに表示
	.done(function(response){
		$('.result p').replaceWith('<p>スライダーの値：' + response.num + '</p>');
	})
	// 通信失敗時の処理
	.fail(function(){
		window.alert("error");
	});
});