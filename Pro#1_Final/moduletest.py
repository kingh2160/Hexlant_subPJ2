import re
import sqlite3
import telegram
import datetime
from bs4 import BeautifulSoup
import time

# Find the target string, return list
def FindStrAll( findlist, target ):
    ret = []
    for i in findlist: ret.append( i.get(target) )
    return ret

# Skip할 게시물 개수 Count
def SkipCnt( boardtype, soup ):
    if( boardtype ==  0 ): return len(soup.find_all( "tr", "top" )+soup.find_all("tr", "emBlue"))
    elif( boardtype == 1 ): return len(soup.find_all("tr", style="cursor:pointer;border-top:1px solid #dee2e6;background-color: papayawhip"))
    elif( boardtype == 6 or boardtype == 7 ): return len(soup.select("ul.article-list > li > span"))
    else: return 0

def FindTopId( boardtype ):
    con1 = sqlite3.connect("C:/Users/sunri/notice/test.db") #C:/Users/세환/pythonfile2/SanhakPJ1/Hexlant_subPJ2/Pro#1_Final/test.db   #C:/Users/sunri/notice/test.db
    cur1 = con1.cursor()
    sql1 = "select id from bottest where boardtype=? order by id desc"  # 현재 DB에 들어있는 가장 높은 ID값을 return, 없으면 None
    cur1.execute(sql1, (boardtype,))
    result = cur1.fetchone()                                            # return type: tuple
    con1.close()
    return result

def GetId( boardtype, link, raw_date ):
    if( boardtype == 0 ):
        pos = link.find('id=')
        return link[pos+3:]
    elif( boardtype == 1 ): return link
    elif( boardtype == 3 ): 
        pos = link.find('detail/')
        return link[pos+7:]
    else : return raw_date

def IsDate(date):
    com = re.compile(r'\d{4}\D\d{2}\D\d{2}')
    seek = com.search(date)
    return seek

def BubbleSort(ziplist):
    num = len(ziplist)
    for i in range(num):
        j = 0
        while j < num - 1 - i:
            if ziplist[j][2] < ziplist[j+1][2]:
                temp = ziplist[j]
                ziplist[j] = ziplist[j+1]
                ziplist[j+1] = temp
            j+=1
    return ziplist

def CompareSend(com, con2, cur2, top_id, now_id, boardtype, origin, title, link, date, completed, bot1, chat_id1):
    sql2 = "insert into bottest(boardtype, title, link, date, id, completed) values (?,?,?,?,?,?)"
    sel = 'select * from bottest where id = ? and completed = ?'
    upd = 'update bottest set completed = ?, title = ? where id = ?'
    
    if( top_id == None or str(top_id)[2:-3] < now_id ):
        bot1.sendMessage(chat_id=chat_id1, text=title.text + ' ' + origin+link + ' ' + date )                     
        cur2.execute(sql2,( boardtype, title.text, origin+link, date, now_id, completed ))                            
        con2.commit()
    elif( boardtype < 4 and com.search(title.text) ):
        cur2.execute(sel, (now_id, '0',))
        res = cur2.fetchone()
        if res:
            bot1.sendMessage(chat_id=chat_id1, text=title.text + ' ' + origin+link + ' ' + date )
            cur2.execute(upd, ('1', title.text, now_id,))
            con2.commit()
    
def UpdateMsg( boardtype, title, origin, link, date, skipCnt, soup, raw_date ):
    #1300808127:AAE1bi5_bLGEBRfYWJa3D9J2_SsKcpfkKmo
    bot1 = telegram.Bot(token='1339037346:AAHOFfZQZb5qqRV_xacyyVyhQb9-qaXWIFE')                                    # 채팅방 봇 토근
    chat_id1 = 1034101411                                                                                     # chat_id를 통해 해당 봇에게 메세지를 보내게 할 수 있음.
    #1034101411 #1339037346:AAHOFfZQZb5qqRV_xacyyVyhQb9-qaXWIFE
    con2 = sqlite3.connect("C:/Users/sunri/notice/test.db")
    cur2 = con2.cursor()
    ziplist = list(zip( title, link, date, raw_date ))
    for i in range(skipCnt): ziplist.pop(0)
    ziplist = BubbleSort(ziplist)
    top_id = FindTopId( boardtype )
    com = re.compile("완료")

    for i, (A, B, C, D) in enumerate(ziplist):
        now_id = GetId(boardtype, B, D)
        completed = 1 if com.search(A.text) else 0
        if IsDate(C):
            realdate = re.sub(r'\D', '.', IsDate(C).group())
            CompareSend(com, con2, cur2, top_id, now_id, boardtype, origin, A, B, realdate, completed, bot1, chat_id1)

        else:
            nowtime = datetime.datetime.now().strftime('%H:%M')
            if( C.strip() < nowtime ):
                ymd = datetime.datetime.now().strftime("%Y.%m.%d")
            else:
                yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                ymd = yesterday.strftime('%Y.%m.%d')
            CompareSend(com, con2, cur2, top_id, now_id, boardtype, origin, A, B, ymd, completed, bot1, chat_id1)
    con2.close()

def IterArticle( driver, boardtype, length, article_tag, extra_tag, link ):
    dataset = []
    for i in range(length):
        article=driver.find_elements_by_css_selector(article_tag)
        article[i].click()
        if( boardtype == 4 or boardtype == 6 or boardtype == 7 ):
            subsource=driver.page_source
            subsoup=BeautifulSoup(subsource, 'html.parser')
            data=subsoup.select_one(extra_tag)
        elif( boardtype == 5 ):
            data = driver.current_url
        dataset.append(data)
        driver.get(link)
        time.sleep(1)
    return dataset