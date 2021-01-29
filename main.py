'''
This script is for downloading ebook from https://www.books.com.tw/
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
import json
import os

# read config
with open('config.json') as f:
  config = json.load(f)


driver = webdriver.Chrome()
driver.get("https://cart.books.com.tw/member/login")
assert "博客來-會員登入" in driver.title

# enter email
email_elem = driver.find_element_by_id("login_id")
email_elem.clear()
email_elem.send_keys(config['account'])

# enter password
pwd_elem = driver.find_element_by_id("login_pswd")
pwd_elem.clear()
pwd_elem.send_keys(config['password'])

# enter captcha
input_captcha = ''
while len(input_captcha) <= 0:
  input_captcha = input("please enter captcha: ")
  captcha_elem = driver.find_element_by_id("captcha")
  captcha_elem.clear()
  captcha_elem.send_keys(input_captcha)

login_elem = driver.find_element_by_id("books_login")
login_elem.click()

# wait for login then go to my ebook
print("waiting for page ready...")
# driver.implicitly_wait(3000) # seconds
try:
  my_book_btn_elem = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://viewer-ebook.books.com.tw/viewer/index.html?readlist=all&MemberLogout=true']")))
except:
  print("login failed")
  quit()

# go to my ebook
print("going to ebook page...")
driver.get("https://viewer-ebook.books.com.tw/viewer/index.html?readlist=all")
try:
  print("waiting for book ready...")
  book_link_elem = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, config['book_url']))
  )
  book_link_elem.click()
except Exception as e:
  print("cannot load ebook page")
  driver.close()
  exit(0)

#
print("loaded the book")
print("waiting for new tab ready")
time.sleep(5)

print("switching to last opened tab")
driver.switch_to.window(driver.window_handles[-1])
print("switched to page: {}".format(driver.title))

book_container_elem = WebDriverWait(driver, 10).until(
  EC.presence_of_element_located((By.ID, "book_container"))
)
print("closing black web")
book_container_elem.click()


print("loaded book container")
input("please press any key to start...")

# checking out folder
if not os.path.exists(config['output_folder']):
  os.mkdir(config['output_folder'])

end_text = "全書閱畢，更多好書盡在博客來。"
page = 1
while True:
  tmp_img_path = "tmp.png"
  time.sleep(0.5)


  driver.save_screenshot(tmp_img_path)

  # crop image
  left_buff = 35
  right_buff = 25
  top_buff = 0
  bottom_buff = 0
  im = Image.open(tmp_img_path)
  im = im.crop((left_buff, top_buff, im.width - left_buff - right_buff, im.height - top_buff - bottom_buff))
  im.save(os.path.join(config['output_folder'], '{}.png'.format(page)))

  book_container_elem.send_keys(Keys.RIGHT)
  page += 1
  
  try:
    end_elem = driver.find_element_by_xpath('//em[contains(text(), "' + end_text + '")]')
    break
  except:
    pass

if os.path.exists(tmp_img_path):
  os.remove(tmp_img_path)
print("done")
driver.close()
