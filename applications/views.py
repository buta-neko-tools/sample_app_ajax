from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .models import AjaxSliderModel
import json
#import paho.mqtt.client as mqtt
from time import sleep
#import paho.mqtt.publish as publish

def index(request):
	return render(request, 'applications/index.html', {})

def ajax_number(request):
	num = request.POST.get('num')
	print(num)
	AjaxSliderModel.objects.update_or_create(md_name='AjaxSliderNum',
																					 defaults={'md_num':num})
	d = {'num': num}
	return JsonResponse(d)

def dballdata(request):
	try:
		dballdata=AjaxSliderModel.objects.get(md_name='AjaxSliderNum')
		db_num=dballdata.md_num
	except:
		db_num='50'
	dt_data={'db_num':db_num}
	conv_json=json.dumps(dt_data)
	return render(request,'applications/dballdata.html',{'conv_json':conv_json})

"""
def mqtt_test01(request):
	# ブローカーに接続できたときの処理
	def on_connect(client,userdata,flag,rc):
		print("Connected with result code "+str(rc))
	# ブローカーが切断したときの処理
	def on_disconnect(client,userdata,flag,rc):
		if rc!=0:
			print("Unexpected disconnection.")
	# publishが完了したときの処理
	def on_publish(client,userdata,mid):
		print("publish: {0}".format(mid))
	# メイン関数   この関数は末尾のif文から呼び出される
	client=mqtt.Client()  # クラスのインスタンス(実体)の作成
	client.username_pw_set(username='dopudopu',password='CrtTex6On76V8M1v')
	client.on_connect=on_connect  # 接続時のコールバック関数を登録
	client.on_disconnect=on_disconnect  # 切断時のコールバックを登録
	client.on_publish=on_publish  # メッセージ送信時のコールバック
	client.connect('dopudopu.cloud.shiftr.io',1883,60)  # 接続先
	# 通信処理スタート
	client.loop_start()  # subはloop_forever()だが，pubはloop_start()で起動だけさせる
	client.publish("drone/001","Hello, Drone!")  # トピック名とメッセージを決めて送信
	return render(request, 'applications/mqtt_test01.html', {'client_obj':client})
def mqtt_ajax(request):
	client_obj = request.POST.get('client_obj')
	slider_num = request.POST.get('slider_num')
	#print(f'client_obj:{client_obj},slider_num:{slider_num}')
	d = {'client_obj': client_obj,
			 'slider_num': slider_num,
			 }
	print(d)
	client_obj.publish("drone/001","Hello, Drone!")
	return JsonResponse(d)
def mqtt_ajax(request):
	slider_num = request.POST.get('slider_num')
	d = {'slider_num': slider_num,
			 }
	print(d)
	publish.single(topic='aaa',
								 payload=slider_num,
								 hostname='dopudopu.cloud.shiftr.io',
								 port=1883,
								 client_id='Django',
								 auth={'username':'dopudopu','password':'CrtTex6On76V8M1v'},
								 )
	return JsonResponse(d)

"""

def mqtt_test01(request):
	return render(request, 'applications/mqtt_test01.html', {})

def mqtt_test02(request):
	return render(request, 'applications/mqtt_test02.html', {})

# ajaxの解説用
def ajax_index(request):
	return render(request, 'applications/ajax_index.html', {})
# ajaxの解説用
def ajax_proc(request):
	slider_num = request.POST.get('slider_num')
	print(slider_num)
	json_data = {'slider_num': slider_num}
	return JsonResponse(json_data)