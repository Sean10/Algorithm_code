'''
自动打开网页登录
'''

#coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Firefox()
driver.get("http://10.3.8.211")

#print(driver.title)

driver.find_element_by_id("username").send_keys("2014211310")
driver.find_element_by_id("password").send_keys("******")
driver.find_element_by_name("0MKKey").click()

element = WebDriverWait(driver,5,0.5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR,"body > div > div > div.b_cernet > form > table > tbody > tr:nth-child(3) > td > p:nth-child(2) > input"))
)

driver.quit()
