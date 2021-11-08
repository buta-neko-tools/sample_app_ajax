import pickle
import time
import paho.mqtt.client as mqtt
from time import sleep
import paho.mqtt.publish as publish

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
def main():
	client=mqtt.Client()  # クラスのインスタンス(実体)の作成
	client.username_pw_set(username='dopudopu',password='CrtTex6On76V8M1v')
	client.on_connect=on_connect  # 接続時のコールバック関数を登録
	client.on_disconnect=on_disconnect  # 切断時のコールバックを登録
	client.on_publish=on_publish  # メッセージ送信時のコールバック
	client.connect('dopudopu.cloud.shiftr.io',1883,60)  # 接続先
	# 通信処理スタート
	client.loop_start()  # subはloop_forever()だが，pubはloop_start()で起動だけさせる
	# print(client)
	# print(vars(client))
	# 永久に繰り返す
	while True:
		client.publish("drone/001","Hello, Drone!")  # トピック名とメッセージを決めて送信
		sleep(3)  # 3秒待つ
# main()

# 送信速度テスト
# やはり毎回認証していると1回の送信で0.5秒程度かかっている
# 認証していない方はほぼ遅延無し
def test01():
	client=mqtt.Client()  # クラスのインスタンス(実体)の作成
	client.username_pw_set(username='dopudopu',password='CrtTex6On76V8M1v')
	client.on_connect=on_connect  # 接続時のコールバック関数を登録
	client.on_disconnect=on_disconnect  # 切断時のコールバックを登録
	client.on_publish=on_publish  # メッセージ送信時のコールバック
	client.connect('dopudopu.cloud.shiftr.io',1883,60)  # 接続先
	# 通信処理スタート
	client.loop_start()  # subはloop_forever()だが，pubはloop_start()で起動だけさせる
	perf_start=time.perf_counter()
	for i in range(11):
		client.publish("drone/001","Hello, Drone!")  # トピック名とメッセージを決めて送信
		sleep(0.1)
	perf_end=time.perf_counter()
	print(f"実行時間：{perf_end-perf_start}")
# test01()
def test02():
	perf_start=time.perf_counter()
	for i in range(11):
		publish.single(topic='drone/001',
									 payload='Hello, Drone!',
									 hostname='dopudopu.cloud.shiftr.io',
									 port=1883,
									 auth={'username':'dopudopu','password':'CrtTex6On76V8M1v'})
		# sleep(0.00001)
	perf_end=time.perf_counter()
	print(f"実行時間：{perf_end-perf_start}")
# test02()

# オブジェクトを送信するテスト
def test03():
	client=mqtt.Client()  # クラスのインスタンス(実体)の作成
	client.username_pw_set(username='dopudopu',password='CrtTex6On76V8M1v')
	client.on_connect=on_connect  # 接続時のコールバック関数を登録
	client.on_disconnect=on_disconnect  # 切断時のコールバックを登録
	client.on_publish=on_publish  # メッセージ送信時のコールバック
	client.connect('dopudopu.cloud.shiftr.io',1883,60)  # 接続先
	# 通信処理スタート
	client.loop_start()  # subはloop_forever()だが，pubはloop_start()で起動だけさせる
	# print(pickle.dumps(client))
	print(vars(client))
	client.publish("drone/001","Hello, Drone!")  # トピック名とメッセージを決めて送信
test03()
