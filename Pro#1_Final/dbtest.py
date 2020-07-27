import os
import time
import telegram
import sqlite3
import datetime
from moduletest import FindStrAll, FindTopId, UpdateMsg, SkipCnt, IterArticle
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument('headless')                                                                                              # 크롬창을 새롭게 켜지 않고 크롤링을 진행하는 옵션
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")                                                                                           # GPU 가속 방지

#1300808127:AAE1bi5_bLGEBRfYWJa3D9J2_SsKcpfkKmo
#bot = telegram.Bot(token='1241503130:AAE4OoAaUKdJ8SRRR5CHYFjPqc05slveQWo')                                                   # 채팅방 봇 토근
#chat_id = -1001442438142                                                                                                     # chat_id를 통해 해당 봇에게 메세지를 보내게 할 수 있음.
#bot = telegram.Bot(token='1300808127:AAE1bi5_bLGEBRfYWJa3D9J2_SsKcpfkKmo')
#chat_id = 843508374

# boardtype: 
#     0-upbit, 1-bithumb, 2-korbit, 3-coinone, 4-binance, 5-kucoin, 6-bittrex(announcement), 7-bittrex(coin_info), 8-bittrex(medium)
# Crawling Function
# boardtype = results[0], url = results[1], title = results[2], date = results[3], link = results[4], origin = results[5], link_tail = results[6], date_tail = results[7], extra = results[8]
NumofSite = 9
def Process( boardtype ):
    sql = "select * from address where boardtype=?"
    cur.execute(sql,(boardtype,))
    results = cur.fetchone()
    driver = webdriver.Chrome('C:/chromedriver_win32/chromedriver',chrome_options = options) #C:/chromedriver_win32/chromedriver  
    #C:/Users/sunri/chromedriver
    driver.get( results[1] )
    wait = WebDriverWait(driver, 10)
    if( results[8] != None ): element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, results[8])))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    origin = results[5]
    title = soup.select( results[2] )
    if not title: return                                                                                     # Can't Crwaling Case
    
    if( boardtype == 5 ): link = IterArticle( driver, boardtype, len(title), results[4], '', results[1] )
    else: link = FindStrAll( soup.select(results[4]), results[6] )
    if( boardtype == 1 ): link = list(map(lambda text: text[15:22], link))
    elif( boardtype == 8 ): link = list(map(lambda text: text.split('?source')[0], link))

    if( boardtype == 4 or boardtype == 6 or boardtype == 7):
        date = IterArticle( driver, boardtype, len(title), results[2], results[3], results[1] )
    else: date = soup.select( results[3] )
    if( results[7] != None ): 
        date = FindStrAll( date, results[7] )
    else:
        date = list(map(lambda text: text.get_text(), date))
    if( len(title) > len(date) ):
        for i in range(len(title) - len(date)):
            date.insert(0, ' ')
    raw_date = date

    skipCnt = SkipCnt( boardtype, soup )
    UpdateMsg(boardtype, title, origin, link, date, skipCnt, soup, raw_date )

while True:
    conn = sqlite3.connect("C:/Users/세환/pythonfile2/SanhakPJ1/Hexlant_subPJ2/Pro#1_Final/test.db") #C:/Users/세환/pythonfile2/SanhakPJ1/Hexlant_subPJ2/Pro#1_Final/test.db
    #C:/Users/sunri/notice/test.db
    cur = conn.cursor()
    for i in range(NumofSite): Process(i)
    print( 'TEST END ')
    conn.close()
    time.sleep(600)                                                                                                           # 60초(1분)을 쉬어줍니다.
