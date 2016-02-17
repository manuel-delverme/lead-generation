import requests

from pycrunchbase import CrunchBase
import json
import time
cb = CrunchBase("4b9035bdef127369659d0562c70ff426")
for funding_round in cb.funding_rounds(starting_page=1164):
    time.sleep(0.03)
    with open("data/{}".format(funding_round['uuid']), "w") as dump:
        json.dump(funding_round, dump)
"""
cookies = {
    #'multivariate_bot': 'false',
    #'D_SID': '93.50.188.12:jor2kyeEQwGSmQknQD1h90/92BBV2RZlbAmcafAc/NA',
    #'D_PID': 'D4FFDF67-36A9-39B2-83D9-4A578825CAC9',
    #'D_IID': '239B9C41-61C2-3A1F-A135-2ADD2411FF01',
    #'D_UID': 'C1237F3D-BBD7-32F5-8574-AF23AE81B005',
    #'D_HID': '8ENue8d/q81aA0XeCbBQAv8rJI4Z19tpQ0OOQCYTt+g',
    #'__uvt': '',
    #'AMCV_6B25357E519160E40A490D44%40AdobeOrg': '1256414278%7CMCMID%7C10337873107626174119203323835477180792%7CMCAID%7CNONE',
    #'s_cc': 'true',
    #'s_pers': '%20s_getnr%3D1452098373296-New%7C1515170373296%3B%20s_nrgvo%3DNew%7C1515170373298%3B',
    #'_px': 'eyJ0IjoxNDUyMDk4Njc0MDIxLCJzIjp7ImEiOjAsImIiOjB9LCJoIjoiZWRkYjk4MDk2ZDkxOGFlNGI4NjAwMWE0MzU0ODAzY2E3MzUxZGYxYjExYjVjNzg3NjE0ZThkNGRlZGM4ODJhMiJ9',
}

headers = {
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,it;q=0.6',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
}
response = requests.get('https://www.crunchbase.com/funding-round/000066459ef68958129a2e225e577eb8', headers=headers, cookies=cookies)
"""
