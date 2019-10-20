from selenium import webdriver


'''
bilibili cookie
{'ts': 1521104898, 'code': 0, 'data': {'mid': 4771256, 'access_token': '308687586987e4a23d52e74599df05a3', 'refresh_token': 'b377ae20741aa74041c99e65d0bb150b', 'expires_in': 2592000}}
'''
driver = webdriver.PhantomJS()
url = "http://live.bilibili.com/918269"
access_key = 'f552568591102acab72a1809ccc6563f'    # 示例：5dd42a8149a8799b809b700298483f5e
cookies = 'DedeUserID=4771256;DedeUserID__ckMd5=8b58a5d0a8ba7184;LIVE_LOGIN_DATA=;LIVE_LOGIN_DATA__ckMd5=;SESSDATA=035633b2%2C1520411314%2C3f76c805;sid=acchj6ds;bili_jct=a0c56f36d0696aa43459821aec4f838c;'

# 底下这些都是固定值，一时不会变
appkey = '1d8b6e7d45233436'
actionKey = 'appkey'
build = '520001'
device = 'android'
mobi_app = 'android'
platform = 'android'

if __name__ == "__main__":
    driver.get(url)
    # drvier.add_cookie({''})
