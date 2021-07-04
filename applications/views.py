from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import SearchQueryModel,UserDataModel



def input_v1(request):
	if request.user.is_authenticated:
		# ここで初期化しないとリロードしても検索条件消えない
		read_db=[]
		# DBに保存されている全ての内容を取得
		exists_db=SearchQueryModel.objects.all()
		# 検索条件保存ボタンか検索条件呼び出しボタンが押されたときの処理
		# これを付けないとリロードしたときにも保存処理が行われる
		if request.method=='POST':
			# ボタンを押したときnameでボタンを判定
			if request.POST["db_action_btn"]=="save":
				# idを指定しないと最後に追加される
				SearchQueryModel.objects.create(
					md_query_name	=request.POST['query_name'],
					md_srch_url		=request.POST['srch_url'],
					md_ex_title		=request.POST['ex_title'],
					md_ex_seller	=request.POST['ex_seller'],
					md_sokketu_sw	=request.POST['sokketu_sw'],
					md_autoex_sw	=request.POST['autoex_sw'],
					md_alert_sw		=request.POST['alert_sw_first'],
				)
				# 登録後は最新のDBの内容を読み込んでDjangoテンプレートに渡す
				read_db=SearchQueryModel.objects.order_by("id").last()
			elif request.POST["db_action_btn"]=="read":
				read_db=SearchQueryModel.objects.get(id=request.POST["select_db_data"])
			elif request.POST["db_action_btn"]=="delete":
				SearchQueryModel.objects.filter(id=request.POST["select_db_data"]).delete()
			elif request.POST["db_action_btn"]=="all_delete":
				SearchQueryModel.objects.all().delete()
			# alert_sw の更新、exists_db 更新してないのに何でボタンクリックしたら変更反映されてる？
			elif request.POST["db_action_btn"]=="alert_sw":
				for sqm_obj in SearchQueryModel.objects.all():
					tmp_db=SearchQueryModel.objects.get(id=sqm_obj.id)
					if str(sqm_obj.id) in request.POST.getlist('alert_sw_all'):
						tmp_db.md_alert_sw='checked'
					else:
						tmp_db.md_alert_sw='nocheck'
					tmp_db.save()
		dt_data={'exists_db':exists_db,
						 'read_db':read_db,
						 }
		return render(request, 'applications/input_v1.html', dt_data)
	else:
		return HttpResponseRedirect('/accounts/login/')

def userdata(request):
	if request.user.is_authenticated:
		try:
			userdata=UserDataModel.objects.get(md_name='user data')
			db_line_token=userdata.md_line_token
		except:
			db_line_token=''
		if request.method=='POST':
			UserDataModel.objects.update_or_create(
				md_name='user data',
				defaults={'md_line_token':request.POST['line_token']}
			)
			userdata=UserDataModel.objects.get(md_name='user data')
			db_line_token=userdata.md_line_token
		dt_data={'db_line_token':db_line_token}
		return render(request, 'applications/userdata.html',dt_data)
	else:
		return HttpResponseRedirect('/accounts/login/')

def dballdata(request):
	if request.user.is_authenticated:
		db_all_data_dict=[]
		for sqm_obj in SearchQueryModel.objects.all():
			db_all_data_dict.append({'検索条件名':sqm_obj.md_query_name,
															 '検索元URL':sqm_obj.md_srch_url,
															 '部分一致除外タイトル':sqm_obj.md_ex_title,
															 '除外出品者':sqm_obj.md_ex_seller,
															 '通知':sqm_obj.md_alert_sw,
															 '即決価格':sqm_obj.md_sokketu_sw,
															 '自動延長':sqm_obj.md_autoex_sw})
		try:
			user_data=UserDataModel.objects.get(md_name='user data')
			line_token=user_data.md_line_token
		except:
			line_token=''
		dt_data={'db_all_data_dict':db_all_data_dict,
						 'line_token':line_token}
		return render(request, 'applications/dballdata.html',dt_data)
	else:
		return HttpResponseRedirect('/accounts/login/')