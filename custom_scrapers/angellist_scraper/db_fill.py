# -*- coding: utf-8 -*-
import psycopg2
from shadowBrowser import ShadowBrowser

connect_string = "dbname={} user={} host={} password={}".format("grepr", "spider", "localhost", "write_only")
_conn = psycopg2.connect(connect_string)

cookies = {
    '_angellist': 'b05ff44e07344842afcf6c8b4bc42bdc',
    'visitor_hash': '60bc521cd38a722e854b20ee56f4fcd7',

}
headers = { 
    'Origin': 'https://angel.co',
    'Accept-Encoding': 'gzip, deflate',
    'X-CSRF-Token': 'A27YmVOFY25xH0dbN6Pk0BicNQuw5yvrZLmMzcZosR8=',
    'Accept-Language': 'en-US,en;q=0.8,it;q=0.6',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': '*/*',
    'Referer': 'https://angel.co/',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'DNT': '1',
}
browser = ShadowBrowser()

def al_login(user, password):
    global browser

    br.open("https://angel.co/login?utm_source=top_nav_home")
    print( "GET","https://angel.co/login?utm_source=top_nav_home")

    form = list(br.forms())[0]

    form.find_control("user_email").value = "manuel@tuamadre.net"
    form.find_control("user_password").value = "asd123asd"

    br.select_form(nr=0) #login
    response = br.submit()


def parse(url):
    global browser
    try:
        browser.open(url, timeout=10)
    except Exception as e:
        with open("ERROR.log", "a") as errorlog:
            errorlog.write("{}: {}".format(url, repr(e)))

    response = browser.response().read()
    soup = BeautifulSoup(response)
    raised_sum = soup.select(".raised")[0].text
    print url, raised_sum


with _conn.cursor() as cursor:
    cursor.execute('select angel_link from "Businesses" where angel_id is not NULL and crawl_time is NULL')
    for url, in cursor:
        # url = url[:4] + url[5:]
        parse(url = url + "/")
