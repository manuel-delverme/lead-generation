import requests
import time
from bs4 import BeautifulSoup


cookies = {
    'visitor_hash': '60bc521cd38a722e854b20ee56f4fcd7',
    '_angellist': 'b05ff44e07344842afcf6c8b4bc42bdc',
}

headers = {
    'Origin': 'https://angel.co',
    'Accept-Encoding': 'gzip, deflate',
    'X-CSRF-Token': 'A27YmVOFY25xH0dbN6Pk0BicNQuw5yvrZLmMzcZosR8=',
    'Accept-Language': 'en-US,en;q=0.8,it;q=0.6',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': '*/*',
    'Referer': 'https://angel.co/companies?raised[min]=10&raised[max]=1000000000000000',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'DNT': '1',
}


with open("data/ids.uniq") as ids_file:

    for _ in range(9200):
        next(ids_file)

    for id_file in ids_file:
        if id_file == '37320\n':
            break

    for id_ in ids_file:
        url = "https://angel.co/follows/tooltip?type=Startup&id={}".format(id_)
        response = requests.get(url, headers=headers, cookies=cookies)
        try:
            name = BeautifulSoup(response.text, 'html.parser').select('.startup-link')[0]['href'].split("/")[-1]
            with open("data/angel.co/{}".format(name), "a") as dump:
                print(name)
                dump.write(response.text)
            time.sleep(1)
        except:
            raise Exception(id_)
