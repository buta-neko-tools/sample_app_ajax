import re

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

	def fetchall_dict(self,sql):
		self.dictcur.execute(sql)
		return [dict(r) for r in self.dictcur.fetchall()]

	def updata_old_url(self,oldurl,id):
		pg_update="UPDATE applications_searchquerymodel SET md_old_url = %s WHERE id = %s"
		self.cursor.execute(pg_update,(str(oldurl),id))

	def updata_newurl(self,newurl,id):
		pg_update="UPDATE applications_searchquerymodel SET md_newurl = %s WHERE id = %s"
		self.cursor.execute(pg_update,(str(newurl),id))

class ydata:
	def url_list(self,ori_url):
		bs4obj=BeautifulSoup(requests.get(ori_url).text,'html.parser')
		# ストアとそれ以外で分岐しようとしたけど同じ方法で取得できた
		# self.url_list=[i.get("href") for i in bs4obj.select("h3 a")]
		# print(len(url_list))
		# print(url_list)
		return [i.get("href") for i in bs4obj.select("h3 a")]

def tame():
	host='ec2-34-202-54-225.compute-1.amazonaws.com'
	dbname='d1mm72kta8mglb'
	port='5432'
	user='bpldtuvfxuwtvc'
	password='da41ca9d74c46db9ec8f61cf8d32cf15c4f1c3adeb11cbda314545ad2fd68bc6'

	pg = postgres()
	pg.connection(host=host,port=port,user=user,password=password,dbname=dbname)
	sqm_dict = pg.fetchall_dict('SELECT * FROM applications_searchquerymodel')
	print(sqm_dict)
	# udm_dict = pg.fetchall_dict('SELECT * FROM applications_userdatamodel')
	# print(udm_dict)

	oldurl=["aa","bb","cc"]
	pg.updata_oldurl(oldurl,id=1)

	newurl=["a1","v4","6n"]
	pg.updata_newurl(newurl,id=1)

	sqm_dict = pg.fetchall_dict('SELECT * FROM applications_searchquerymodel')
	print(sqm_dict)

	print(sqm_dict[1]['md_oldurl'])
	for i in eval(sqm_dict[1]['md_oldurl']):
		print(i)

	print(sqm_dict[1]['md_newurl'])
	for i in eval(sqm_dict[1]['md_newurl']):
		print(i)

host='ec2-34-202-54-225.compute-1.amazonaws.com'
dbname='d1mm72kta8mglb'
port='5432'
user='bpldtuvfxuwtvc'
password='da41ca9d74c46db9ec8f61cf8d32cf15c4f1c3adeb11cbda314545ad2fd68bc6'

pg=postgres()
pg.connection(host=host,port=port,user=user,password=password,dbname=dbname)
sqm_dict=pg.fetchall_dict('SELECT * FROM applications_searchquerymodel')

yd=ydata()
for sqm in sqm_dict:
	if sqm['md_old_url']==None:
		old_url=yd.url_list(sqm['md_srch_url'])
		pg.updata_old_url(old_url,id=sqm['id'])
	else:
		old_url=sqm['md_old_url']