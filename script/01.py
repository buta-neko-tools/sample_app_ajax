import bs4
from selenium import webdriver

chrome_options=webdriver.ChromeOptions()
# アダプタエラー、自動テスト…、を非表示
chrome_options.add_experimental_option("excludeSwitches",['enable-automation',
																													'enable-logging'])
chrome_options.add_argument('--headless')  #ヘッドレスモード
chrome_options.add_argument('--incognito')  #シークレットモード
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-desktop-notifications')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--disable-dev-shm-usage')  #/dev/shmを使わないように指定
chrome_options.add_argument('--disable-application-cache')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--single-process')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--user-agent=aheahe')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')  #画像を非表示
chrome_options.page_load_strategy='none'  #
driver=webdriver.Chrome(options=chrome_options)
url="https://www.yoyaku-sports.city.suginami.tokyo.jp/reselve/m_index.do"
driver.get(url)
bs4obj=bs4.BeautifulSoup(driver.page_source,'html.parser')
print(bs4obj.text)