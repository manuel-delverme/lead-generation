# -*- coding: utf-8 -*-
import json
import psycopg2
import psycopg2.extras
from bs4 import BeautifulSoup
from shadowBrowser import ShadowBrowser

connect_string = "dbname={} user={} host={} password={}".format("grepr", "spider", "tuamadre.net", "write_only")
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

    browser.open("https://angel.co/login?utm_source=top_nav_home")
    print("GET", "https://angel.co/login?utm_source=top_nav_home")

    form = list(browser.forms())[0]

    form.find_control("user_email").value = "manuel@tuamadre.net"
    form.find_control("user_password").value = "asd123asd"

    browser.select_form(nr=0) #login
    response = browser.submit()


def parse(target_url):
    global browser
    try:
        browser.open(target_url)
    except Exception as e:
        with open("ERROR.log", "a") as errorlog:
            errorlog.write("{}: {}".format(target_url, repr(e)))

    response = browser.get_response().read()
    soup = BeautifulSoup(response)
    keywords = {
        "homepage": ".company_url",
        "meta_description": ".high_concept",
        "meta_keys": ".tag",
        "common_name": ".name_holder > .name",
        "total_funding": ".raised",
        # "employee_min": "company_url",
        # "employee_max": "company_url",
        # "revenue": "company_url",
        # "exports": "company_url",
    }
    data = {}
    for k, v in keywords.items():
        data[k] = extract_class_text(soup, v)
    return data

def extract_class_text(soup, selector):
    return list({div.text for div in soup.select(selector)})

with _conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:

    cursor.execute('select * from "Businesses" where angel_id is not NULL and crawl_time is NULL')
    for row in cursor:
        # url = url[:4] + url[5:]
        if None in (row['homepage'], row['meta_description'], row['meta_keywords'], row['common_name'], row['funding']):

            data = parse(target_url=row['angel_link'])
            data['id'] = row['id']
            sql_str = """
              UPDATE "Businesses"
              SET homepage=%(homepage)s,
                  meta_description=%(meta_description)s,
                  meta_keywords=%(meta_keys)s,
                  common_name=%(common_name)s,
                  funding=%(total_funding)s
              WHERE
                id = %(id)s
            """
            print data
            with _conn.cursor() as cur2:
                cur2.execute(sql_str, data)

