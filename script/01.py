import time
from pprint import pprint
import psycopg2
import requests
from bs4 import BeautifulSoup
from psycopg2.extras import DictCursor

class postgres:
	def connection(self,host,user,password,dbname,port):
		self.conn=psycopg2.connect(host=host,dbname=dbname,user=user,password=password,port=port)
		self.conn.autocommit=True
		self.cursor=self.conn.cursor()
		self.dictcur=self.conn.cursor(cursor_factory=DictCursor)

	def fetchall_sqm_dict(self):
		self.dictcur.execute('SELECT * FROM applications_searchquerymodel')
		return [dict(r) for r in self.dictcur.fetchall()]

	def fetch_udm_dict(self,value):
		self.dictcur.execute('SELECT * FROM applications_userdatamodel')
		self.udm_dict=[dict(r) for r in self.dictcur.fetchall()][0]
		return self.udm_dict[value]

	def updata_old_url(self,old_url_list,id):
		sql_cmd="UPDATE applications_searchquerymodel SET md_old_url = %s WHERE id = %s"
		self.cursor.execute(sql_cmd,(str(old_url_list),id))

	def init_old_url(self):
		sql_cmd="UPDATE applications_searchquerymodel SET md_old_url = %s WHERE id = %s"
		self.sqm_dict=pg.fetchall_sqm_dict()
		for sqm in self.sqm_dict:
			self.cursor.execute(sql_cmd,(None,sqm['id']))

class ydata:
	def url_list(self,ori_url):
		bs4obj=BeautifulSoup(requests.get(ori_url).text,'html.parser')
		# ストアとそれ以外で分岐しようとしたけど同じ方法で取得できた
		# self.url_list=[i.get("href") for i in bs4obj.select("h3 a")]
		# print(len(url_list))
		# print(url_list)
		time.sleep(0.5)
		return [i.get("href") for i in bs4obj.select("h3 a")]

	def auc_detail(self,update_url_list):
		auc_data_dict=[]
		for update_url in update_url_list:
			bs4obj=BeautifulSoup(requests.get(update_url).text,'html.parser')
			# オークション名
			auc_title=bs4obj.select_one("h1.ProductTitle__text").text
			# URL
			auc_url=update_url
			# 画像URL
			auc_imgurl=bs4obj.select_one("li.ProductImage__image > div > img").get('src')
			# 出品者ID
			auc_seller=bs4obj.select_one("span.Seller__name > a").text
			# 自動延長
			auc_autoex=bs4obj.select_one("ul.ProductDetail__items.ProductDetail__items--primary").select("dd.ProductDetail__description")[3].text.replace("：","")
			# 即決設定
			if bs4obj.select_one("div.Price.Price--buynow"):
				auc_buynow="あり"
			else:
				auc_buynow="なし"
			auc_data_dict.append({'タイトル':auc_title,
														'商品URL':auc_url,
														'画像URL':auc_imgurl,
														'出品者ID':auc_seller,
														'自動延長':auc_autoex,
														'即決設定':auc_buynow,
														})
			time.sleep(0.5)
		# pprint(auc_data_dict)
		return auc_data_dict

	def filter_judge(self,sqm,auc_data_dict):
		alert_content_dict=[]
		for auc_data in auc_data_dict:
			filter_judge={}
			# ------------------------------
			# タイトルの部分一致除外
			# ------------------------------
			# 入力が空の場合はOK
			if sqm['md_ex_title']=="":
				filter_judge['タイトルの部分一致除外']='OK'
			else:
				for filter_data in sqm['md_ex_title'].split(' '):
					# スペースが2つ入っている場合は''なのでスキップ
					if filter_data=='': continue
					if filter_data in auc_data['タイトル']:
						filter_judge['タイトルの部分一致除外']='NG'
						break
				else:
					filter_judge['タイトルの部分一致除外']='OK'
			# ------------------------------
			# 除外出品者
			# ------------------------------
			# 入力が空の場合はOK
			if sqm['md_ex_seller']=="":
				filter_judge['除外出品者']='OK'
			else:
				for filter_data in sqm['md_ex_seller'].split(' '):
					# スペースが2つ入っている場合は''なのでスキップ
					if filter_data=='': continue
					if filter_data==auc_data['出品者ID']:
						filter_judge['除外出品者']='NG'
						break
				else:
					filter_judge['除外出品者']='OK'
			# ------------------------------
			# 即決設定除外フィルタ
			# ------------------------------
			if sqm['md_buynow_sw']=="nocheck":
				filter_judge['即決設定除外フィルタ']='OK'
			else:
				if auc_data['即決設定']=="なし":
					filter_judge['即決設定除外フィルタ']='OK'
				else:
					filter_judge['即決設定除外フィルタ']='NG'
			# ------------------------------
			# 自動延長除外フィルタ
			# ------------------------------
			if sqm['md_autoex_sw']=="nocheck":
				filter_judge['自動延長除外フィルタ']='OK'
			else:
				if auc_data['自動延長']=="なし":
					filter_judge['自動延長除外フィルタ']='OK'
				else:
					filter_judge['自動延長除外フィルタ']='NG'
			# ------------------------------
			# 判定結果確認
			# ------------------------------
			if 'NG' not in filter_judge.values():
				auc_data['検索条件名']=sqm['md_query_name']
				# dict を append するとなぜか 検索条件名 が上書きされるので以下の記事を参考にした
				# https://gist.github.com/dogrunjp/9748789
				alert_content_dict.append(auc_data.copy())
			print(f'sqm\n'
						f'タイトルの部分一致除外：{sqm["md_ex_title"]}\n'
						f'除外出品者：{sqm["md_ex_seller"]}\n'
						f'即決設定除外フィルタ：{sqm["md_buynow_sw"]}\n'
						f'自動延長除外フィルタ：{sqm["md_autoex_sw"]}\n')
			print(f'auc_data')
			pprint(auc_data)
			print(f'filter_judge')
			pprint(filter_judge)
		print(f'alert_content_dict\n{alert_content_dict}\n\n')
		return alert_content_dict

class line_notify:
	def send(self,alert_content_dict):
		pipe='------------------------------'
		line_token=pg.fetch_udm_dict('md_line_token')
		if alert_content_dict and line_token:
			print(f'alert_content_dict と line_token が有るので通知する')
			self.api_post(line_token,pipe,'')
			for alert_content in alert_content_dict:
				messege=f"\n検索条件名：{alert_content['検索条件名']}\n"\
					f"タイトル：{alert_content['タイトル']}\n"\
					f"商品URL：{alert_content['商品URL']}"
					# f"価格：{alert_content['価格']}\n"\
					# f"商品説明文：{alert_content['商品説明文']}\n"
				self.api_post(line_token,messege,alert_content['画像URL'])
			self.api_post(line_token,pipe,'')
		else:
			if alert_content_dict:
				print(f'line_token が空だったので通知しなかった')
			if line_token:
				print(f'alert_content_dict が空だったので通知しなかった')

	def api_post(self,token,message,image):
		line_notify_api = 'https://notify-api.line.me/api/notify'
		headers = {'Authorization': f'Bearer {token}'}
		data = {'message': message,
						'imageFullsize':image,
						'imageThumbnail':image}
		requests.post(line_notify_api, headers=headers, data=data)




# ------------------------------
# DEBUG・初期 設定
# ------------------------------
# DEBUG=False
DEBUG=True

if DEBUG:
	import winsound

host='ec2-34-202-54-225.compute-1.amazonaws.com'
dbname='d1mm72kta8mglb'
port='5432'
user='bpldtuvfxuwtvc'
password='da41ca9d74c46db9ec8f61cf8d32cf15c4f1c3adeb11cbda314545ad2fd68bc6'

pg=postgres()
yd=ydata()
ln=line_notify()

pg.connection(host=host,port=port,user=user,password=password,dbname=dbname)

def main():
	while_count=0
	pg.init_old_url()
	while True:
		while_count+=1
		sqm_dict=pg.fetchall_sqm_dict()
		for sqm in sqm_dict:
			if sqm['md_old_url']==None:
				print(f'{sqm["md_query_name"]} の md_old_url が空なので新規に取得\n')
				old_url_list=yd.url_list(sqm['md_srch_url'])
				pg.updata_old_url(old_url_list,id=sqm['id'])
			else:
				print(f'{sqm["md_query_name"]} の md_old_url が有るのでDBから取得\n')
				old_url_list=eval(sqm['md_old_url'])
			new_url_list=yd.url_list(sqm['md_srch_url'])
			update_url_list=list(set(new_url_list[:50])-set(old_url_list))
			if update_url_list:
				if DEBUG:
					winsound.Beep(1500,500)
					winsound.Beep(1500,500)
				print(f'{sqm["md_query_name"]} で更新されたURLの数：{len(update_url_list)}\n')
				while_count=0
				pg.updata_old_url(new_url_list,id=sqm['id'])
				if sqm['md_alert_sw']=="checked":
					print(f'{sqm["md_query_name"]} の md_alert_sw が checked なので、オク詳細を取得して、フィルタ判定\n')
					auc_data_dict=yd.auc_detail(update_url_list)
					alert_content_dict=yd.filter_judge(sqm=sqm,auc_data_dict=auc_data_dict)
					ln.send(alert_content_dict)
				else:
					print(f'{sqm["md_query_name"]} の md_alert_sw が nocheck なので pass\n')
			else:
				print(f'{while_count} {sqm["md_query_name"]} の更新前の最新のURL\n{old_url_list[0]}\n')
main()