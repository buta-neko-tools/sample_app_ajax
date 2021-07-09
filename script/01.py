import re
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

	def updata_old_url(self,old_url_list,id):
		sql_cmd="UPDATE applications_searchquerymodel SET md_old_url = %s WHERE id = %s"
		self.cursor.execute(sql_cmd,(str(old_url_list),id))

	def init_old_url(self):
		sql_cmd="UPDATE applications_searchquerymodel SET md_old_url = %s WHERE id = %s"
		sqm_dict=pg.fetchall_sqm_dict()
		for sqm in sqm_dict:
			self.cursor.execute(sql_cmd,(None,sqm['id']))

class ydata:
	def url_list(self,ori_url):
		bs4obj=BeautifulSoup(requests.get(ori_url).text,'html.parser')
		# ストアとそれ以外で分岐しようとしたけど同じ方法で取得できた
		# self.url_list=[i.get("href") for i in bs4obj.select("h3 a")]
		# print(len(url_list))
		# print(url_list)
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
		# pprint(auc_data_dict)
		return auc_data_dict

	def filter_judge(self,sqm_dict,auc_data_dict):
		alert_content_dict=[]
		for sqm in sqm_dict:
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
				# 自動延長除外フィルタ
				# ------------------------------
				if 'NG' not in filter_judge.values():
					auc_data['検索条件名']=sqm['検索条件名']
					# dict を append するとなぜか 検索条件名 が上書きされるので以下の記事を参考にした
					# https://gist.github.com/dogrunjp/9748789
					alert_content_dict.append(auc_data.copy())
				print(f'sqm\n{sqm}\n'
							f'auc_data\n{auc_data}\n'
							f'filter_judge\n{filter_judge}\n')
		# print(f'alert_content_dict\n{alert_content_dict}\n\n')
		return alert_content_dict

# ------------------------------
# DEBUG・初期 設定
# ------------------------------
# DEBUG=False
DEBUG=True

if DEBUG:
	import winsound
	heroku_login_url='http://127.0.0.1:8000/accounts/login/'
	heroku_bd_url="http://127.0.0.1:8000/dballdata/"
else:
	heroku_login_url='https://camera-shop-alert.herokuapp.com/accounts/login/'
	heroku_bd_url="https://camera-shop-alert.herokuapp.com/dballdata/"

host='ec2-34-202-54-225.compute-1.amazonaws.com'
dbname='d1mm72kta8mglb'
port='5432'
user='bpldtuvfxuwtvc'
password='da41ca9d74c46db9ec8f61cf8d32cf15c4f1c3adeb11cbda314545ad2fd68bc6'

pg=postgres()
yd=ydata()

pg.connection(host=host,port=port,user=user,password=password,dbname=dbname)

def main():
	while_count=0
	pg.init_old_url()
	while True:
		while_count+=1
		sqm_dict=pg.fetchall_sqm_dict()
		for sqm in sqm_dict:
			if sqm['md_old_url']==None:
				old_url_list=yd.url_list(sqm['md_srch_url'])
				pg.updata_old_url(old_url_list,id=sqm['id'])
			else:
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
				auc_data_dict=yd.auc_detail(update_url_list)
			else:
				print(f'{while_count} {sqm["md_query_name"]} の更新前の最新のURL\n{old_url_list[0]}\n')
# main()

# update_url_list=["https://page.auctions.yahoo.co.jp/jp/auction/v810785129",
# 								 "https://page.auctions.yahoo.co.jp/jp/auction/u451641069"]
# auc_data_dict=yd.auc_detail(update_url_list)

sqm_dict=pg.fetchall_sqm_dict()
pprint(sqm_dict)