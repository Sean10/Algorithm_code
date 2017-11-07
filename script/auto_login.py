'''
自动打开网页登录
'''

#coding=utf-8
from selenium import webdriver

driver = webdriver.Firefox()
driver.get("http://10.3.8.211")

#print(driver.title)

driver.find_element_by_id("username").send_keys("2014211310")
driver.find_element_by_id("password").send_keys("******")
driver.find_element_by_name("0MKKey").click()
driver.quit()
