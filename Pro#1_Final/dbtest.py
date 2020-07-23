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
NumofSite = 4
def Process( boardtype ):
    sql = "select * from address where boardtype=?"
    cur.execute(sql,(boardtype,))
    results = cur.fetchall()
    driver = webdriver.Chrome('C:/Users/sunri/chromedriver', chrome_options=options) #C:/chromedriver_win32/chromedriver  
    #C:/Users/sunri/chromedriver
    driver.get( results[0][1] )
    wait = WebDriverWait(driver, 10)
    if( results[0][8] != None ): element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, results[0][8])))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.select( results[0][2] )
    if not title: return                                                                                                      # Can't Crwaling Case
    origin = results[0][5]
    if( boardtype == 4 or boardtype == 6 or boardtype == 7):
        date = IterArticle( driver, boardtype, len(title), results[0][2], results[0][3] )
    else: date = soup.select( results[0][3] )
    raw_date = []
    for i in range(len(date)):
        raw_date.append(date[i].get_text())
    if( boardtype == 5 ): link = IterArticle( driver, boardtype, len(title), results[0][4], '' )
    else: link = FindStrAll( soup.select(results[0][4]), results[0][6] )
    if( results[0][7] != None ): date = FindStrAll( date, results[0][7] )
    if( boardtype == 1 ): link = list(map(lambda text: text[15:22], link))
    if( boardtype == 8 ): link = list(map(lambda text: text.split('?source')[0], link))
    if( boardtype == 2 or boardtype == 6 or boardtype == 7 or boardtype == 8 ):
        raw_date = date
        date = list(map(lambda text: text[:10].replace("-",".",2), date))
    if( boardtype == 4 ):
        for i in range(len(date)):
            date[i] = date[i].get_text()[:10].replace("-",".",2)
    elif( boardtype == 5 ):
        for i in range(len(date)):
            date[i] = date[i].get_text()[:10].replace("/",".",2)
    skipCnt = SkipCnt( boardtype, soup )
    UpdateMsg(boardtype, title, origin, link, date, skipCnt, soup, raw_date )

while True:
    conn = sqlite3.connect("C:/Users/sunri/notice/test.db") #Pro#1_Final/test.db
    #C:/Users/sunri/notice/test.db
    cur = conn.cursor()
    #for i in range(NumofSite): Process(i)
    Process(8)
    print( 'TEST END ')
    conn.close()
    time.sleep(600)                                                                                                           # 60초(1분)을 쉬어줍니다.
