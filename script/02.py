import re
import sys
# import winsound
import bs4,requests
from bs4 import BeautifulSoup
from selenium import webdriver

# ------------------------------
# DEBUG・初期 設定
# ------------------------------
# DEBUG=True
DEBUG=False

if DEBUG:
	heroku_login_url='http://127.0.0.1:8000/accounts/login/'
	heroku_bd_url="http://127.0.0.1:8000/dballdata/"
else:
	heroku_login_url='https://camera-shop-alert.herokuapp.com/accounts/login/'
	heroku_bd_url="https://camera-shop-alert.herokuapp.com/dballdata/"

heroku_id="qMCm1rZDDb"
heroku_pass="cWixDU3Kvv"

# ------------------------------
# HerokuサイトからDB内容をrequestsで取得する
# ------------------------------
def get_heroku_db_all_data_requests():
	# https://own-search-and-study.xyz/2017/04/09/djangoで作ったサイトにスクリプトでログインする方/
	session=requests.session()
	session.get(heroku_login_url)
	csrf=session.cookies['csrftoken']
	login_info={"csrfmiddlewaretoken":csrf,
							"username":heroku_id,
							"password":heroku_pass,
							"next":heroku_bd_url}
	response=session.post(heroku_login_url,data=login_info,headers=dict(Referer=heroku_login_url))
	bs4obj=BeautifulSoup(response.text,'html.parser')
	try:
		search_query=eval(bs4obj.select_one('span[id="db_all_data_dict"]').text)
	except:
		search_query=''
	line_token=bs4obj.select_one('span[id="line_token"]').text
	return line_token,search_query

# ------------------------------
# キタムラ
# ------------------------------
# キタムラの商品一覧ページから必要な情報を取得
# サイトがリニューアルされて一覧に詳細も表示されるように変更された
def get_detail_kitamura_selenium(driver):
	items_detail_dict=[]
	add_url='https://shop.kitamura.jp'
	src_url="https://shop.kitamura.jp/ec/list?type=u&sort=update_date&limit=100"
	while items_detail_dict==[]:
		driver.get(src_url)
		bs4obj=bs4.BeautifulSoup(driver.page_source,'html.parser')
		items_list=bs4obj.select('div[class="product-area"]')
		# print(items_list)
		for items in items_list:
			# 商品URL
			items_url=add_url+items.select_one('a[class="product-link"]').get('href')
			# タイトル
			items_title=items.select_one('div[class="product-name"]').text
			# 価格
			items_price=items.select_one('span[class="product-price"]').text
			# 画像URL
			items_imgurl=items.select_one('img[class="product-img"]').get('src')
			# 商品説明文
			items_desc=items.select_one('span[class="product-note-val"]').text
			items_detail_dict.append({'タイトル':items_title,
																'価格':items_price,
																'画像URL':items_imgurl,
																'商品説明文':items_desc,
																'商品URL':items_url,
																})
		if not items_detail_dict:
			print('items_detail_dict が空なので再取得')
		# print(f'items_detail_dict の要素数：{len(items_detail_dict)}')
	# print(items_detail_dict)
	return items_detail_dict
# キタムラの新旧の商品詳細辞書を比較する
def compare_detail_dict_kitamura(old_detail_dict_kitamura,new_detail_dict_kitamura):
	update_detail_dict=[]
	for i in new_detail_dict_kitamura[:50]:
		for j in old_detail_dict_kitamura:
			if i['商品URL'] in j.values():
				break
		else:
			update_detail_dict.append(i)
	return update_detail_dict

# ------------------------------
# ネットモール
# ------------------------------
# 「カメラカテゴリ、更新日順、90件表示」でURLのリストを取得
def get_url_list_netmall():
	items_url_list=[]
	src_url='https://netmall.hardoff.co.jp/cate/00010003/?p=1&s=1&pl=90'
	src_url_parser=requests.get(src_url)
	bs4obj=bs4.BeautifulSoup(src_url_parser.text,'html.parser')
	items_list=bs4obj.find_all("a",attrs={'class':'p-goods__link'})
	for items in items_list:
		# 商品URL
		items_url_list.append(items.get('href'))
	# print(len(items_url_list))
	# print(items_url_list)
	return items_url_list
# 商品URLから必要な情報を取得
def get_detail_netmall(update_url_list):
	items_detail_dict=[]
	add_url='https://netmall.hardoff.co.jp'
	for update_url in update_url_list:
		src_url_parser=requests.get(update_url)
		bs4obj=bs4.BeautifulSoup(src_url_parser.text,'html.parser')
		# タイトル
		try:
			items_title=bs4obj.find("h2",attrs={'class':'p-goodsDetail__name'}).text
		except AttributeError:
			# カテゴリと商品名が同じ場合は商品名が省略されてカテゴリだけになる
			items_title=bs4obj.find("p",attrs={'class':'p-goodsDetail__category'}).text
		# 価格
		items_price=bs4obj.find("p",attrs={'class':'p-goodsDetail__price'}).text.replace('\n','')
		# 画像URL
		items_imgurl=bs4obj.find("img",attrs={'class':'p-goodsDetail__mainImg js-lightbox js-object-fit'}).get('src')
		if items_imgurl=='/images/goods/blankimg_itemphoto_noimage.png':
			items_imgurl=add_url+items_imgurl
		# 商品説明文
		tr_list=bs4obj.find("div",attrs={'class':'p-goodsGuide__body'}).find_all("tr")
		items_desc=''
		for elem in tr_list:
			if '付属レンズ'==elem.find('th').text or '特徴・備考'==elem.find('th').text:
				items_desc+=elem.find('td').text
		items_detail_dict.append({'タイトル':items_title.replace('　',' '),
															'価格':items_price,
															'画像URL':items_imgurl,
															'商品説明文':items_desc.replace('　',' '),
															'商品URL':update_url,
															})
	# print(items_detail_dict)
	# print(items_detail_dict[2]['商品説明文'])
	return items_detail_dict

# ------------------------------
# LINE notify
# ------------------------------
# LINEで通知を送信する、画像サムネイル表示も可能
def send_line_notify(token,message,image):
	line_notify_api = 'https://notify-api.line.me/api/notify'
	headers = {'Authorization': f'Bearer {token}'}
	data = {'message': message,
					'imageFullsize':image,
					'imageThumbnail':image}
	requests.post(line_notify_api, headers=headers, data=data)
# 辞書の内容を整形して通知
def send_alert_content(alert_content_dict,line_token):
	pipe='------------------------------'
	send_line_notify(line_token,pipe,'')
	for alert_content in alert_content_dict:
		messege=f"\n検索条件名：{alert_content['検索条件名']}\n" \
						f"タイトル：{alert_content['タイトル']}\n" \
						f"価格：{alert_content['価格']}\n" \
						f"商品URL：{alert_content['商品URL']}"
						# f"商品説明文：{alert_content['商品説明文']}\n"
		send_line_notify(line_token,messege,alert_content['画像URL'])
	send_line_notify(line_token,pipe,'')
# LINE notify で送信する前処理
def final_process(update_url_list,site_type):
	# print(f'更新されたURL len({len(update_url_list)})\n{update_url_list}\n\n')
	line_token,db_all_data_dict=get_heroku_db_all_data_requests()
	if db_all_data_dict and line_token:
		if site_type=='kitamura':
			items_detail_dict=update_url_list
		elif site_type=='netmall':
			items_detail_dict=get_detail_netmall(update_url_list)
		alert_content_dict=get_filter_judge(db_all_data_dict,items_detail_dict)
		print(f'通知する内容\n{alert_content_dict}\n')
		if alert_content_dict:
			send_alert_content(alert_content_dict,line_token)
	else:
		print(f'通知が全てOFF or LINEトークンが未入力だったので通知しなかった。\n')

# ------------------------------
# その他
# ------------------------------
# selenium設定
def boot_selenium():
	chrome_options=webdriver.ChromeOptions()
	user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
	chrome_options.add_argument(f'user-agent={user_agent}')
	chrome_options.add_experimental_option("excludeSwitches",['enable-automation',
																														'enable-logging'])
	chrome_options.add_experimental_option('useAutomationExtension',False)
	chrome_options.add_argument('--headless')  #ヘッドレスモード
	# chrome_options.add_argument('--incognito')  #シークレットモード
	chrome_options.add_argument('--no-sandbox')
	# chrome_options.add_argument('--single-process')
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--disable-dev-shm-usage')
	# これを追加するとキタムラから何も取得できなくなる
	# chrome_options.add_argument('--disable-application-cache')
	chrome_options.add_argument('--disable-desktop-notifications')
	chrome_options.add_argument("--disable-extensions")
	chrome_options.add_argument('--ignore-certificate-errors')
	chrome_options.add_argument('--ignore-ssl-errors')
	chrome_options.add_argument('--blink-settings=imagesEnabled=false') #画像を非表示
	# chrome_options.page_load_strategy='none' #
	# ↓を参考にしてプロキシを設定したらHerokuでも内容取得できた
	# https://teratail.com/questions/205583
	# http://proxy.moo.jp/ja/?c=jp&f=1&s=r
	proxy_host='203.74.120.79'
	proxy_port='3128'
	chrome_options.add_argument(f"--proxy-server=http://{proxy_host}:{proxy_port}")
	driver=webdriver.Chrome(options=chrome_options)
	return driver
# 検索条件と比較して全てOKなら items_detail_dict に検索条件名を付加して返す
def get_filter_judge(db_all_data_dict,items_detail_dict):
	alert_content_dict=[]
	for db_all_data in db_all_data_dict:
		for items_detail in items_detail_dict:
			filter_judge=[]
			# ORタイトル のフィルタ
			for filter_data in db_all_data['ORタイトル'].split(' '):
				if filter_data in items_detail['タイトル'] or db_all_data['ORタイトル']=='':
					filter_judge.append("OK")
					break
			else:
				filter_judge.append("NG")
			# 除外タイトル のフィルタ
			for filter_data in db_all_data['除外タイトル'].split(' '):
				if db_all_data['除外タイトル']=='':
					filter_judge.append("OK")
					break
				if filter_data in items_detail['タイトル']:
					filter_judge.append("NG")
					break
			else:
				filter_judge.append("OK")
			# OR商品説明文 のフィルタ
			for filter_data in db_all_data['OR商品説明文'].split(' '):
				if filter_data in items_detail['商品説明文'] or db_all_data['OR商品説明文']=='':
					filter_judge.append("OK")
					break
			else:
				filter_judge.append("NG")
			# 除外商品説明文 のフィルタ
			for filter_data in db_all_data['除外商品説明文'].split(' '):
				if db_all_data['除外商品説明文']=='':
					filter_judge.append("OK")
					break
				if filter_data in items_detail['商品説明文']:
					filter_judge.append("NG")
					break
			else:
				filter_judge.append("OK")
			# 価格 のフィルタ
			if db_all_data['最低価格']=='':
				min_price=0
			else:
				min_price=int(db_all_data['最低価格'])
			if db_all_data['最高価格']=='':
				max_price=sys.maxsize
			else:
				max_price=int(db_all_data['最高価格'])
			if min_price <= int(re.sub(r'[(税込)¥円,]','',items_detail['価格'])) <= max_price:
				filter_judge.append("OK")
			else:
				filter_judge.append("NG")
			# filter_judgeにNGが含まれていなければappendする
			if "NG" not in filter_judge:
				items_detail['検索条件名']=db_all_data['検索条件名']
				# dict を append するとなぜか 検索条件名 が上書きされるので以下の記事を参考にした
				# https://gist.github.com/dogrunjp/9748789
				alert_content_dict.append(items_detail.copy())
			print(f'db_all_data\n{db_all_data}\n'
						f'items_detail\n{items_detail}\n'
						f'filter_judge\n{filter_judge}\n')
		# print(f'alert_content_dict\n{alert_content_dict}\n\n')
	return alert_content_dict

# ------------------------------
# 新着を検出して通知を行う
# ------------------------------
# キタムラのリニューアルに合わせて改良
def main_process_v2():
	# selenium を起動
	driver=boot_selenium()
	# エラーで終了しても driver.quit() 出来るように追加
	try:
		print(f'selenium 起動完了')
		# kitamura
		while_count_kitamura=0
		old_detail_dict_kitamura=get_detail_kitamura_selenium(driver)
		# print(f'old_detail_dict_kitamura の要素数：{len(old_detail_dict_kitamura)}')
		# netmall
		while_count_netmall=0
		old_url_list_netmall=get_url_list_netmall()
		# print(f'old_url_list_netmall の要素数：{len(old_url_list_netmall)}')
		while True:
			# kitamura
			while_count_kitamura+=1
			new_detail_dict_kitamura=get_detail_kitamura_selenium(driver)
			# print(f'new_detail_dict_kitamura の要素数：{len(new_detail_dict_kitamura)}')
			update_detail_dict_kitamura=compare_detail_dict_kitamura(old_detail_dict_kitamura,new_detail_dict_kitamura)
			if update_detail_dict_kitamura:
				# winsound.Beep(1500,500)
				# winsound.Beep(1500,500)
				print(f'kitamura で更新されたURLの数：{len(update_detail_dict_kitamura)}\n')
				while_count_kitamura=0
				old_detail_dict_kitamura=new_detail_dict_kitamura
				final_process(update_detail_dict_kitamura,'kitamura')
				# ------------------------------
				# break
				# ------------------------------
			else:
				print(f'{while_count_kitamura} 更新前の最新の kitamura のURL\n{old_detail_dict_kitamura[0]["商品URL"]}\n')
			# netmall
			while_count_netmall+=1
			new_url_list_netmall=get_url_list_netmall()
			# print(f'new_url_list_netmall の要素数：{len(new_url_list_netmall)}')
			update_url_list_netmall=list(set(new_url_list_netmall[:45])-set(old_url_list_netmall))
			if update_url_list_netmall:
				# winsound.Beep(1500,500)
				# winsound.Beep(1500,500)
				print(f'netmall で更新されたURLの数：{len(update_url_list_netmall)}\n')
				while_count_netmall=0
				old_url_list_netmall=new_url_list_netmall
				final_process(update_url_list_netmall,'netmall')
				# ------------------------------
				# break
				# ------------------------------
			else:
				print(f'{while_count_netmall} 更新前の最新の netmall のURL\n{old_url_list_netmall[0]}\n')
	finally:
		print(f'異常終了したので driver.quit()')
		driver.quit()






# main_process(self)
main_process_v2()
# main_process_netmall_only(self)
# main_process_selenium_test(self)

