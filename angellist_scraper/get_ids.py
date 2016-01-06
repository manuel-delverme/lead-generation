import requests
import itertools
import json


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


range_min = 2749360
range_max = 2820445


def request_companies(min_, max_, page):
    data = 'filter_data%5Braised%5D%5Bmin%5D={}&filter_data%5Braised%5D%5Bmax%5D={}&sort=raised&page={}'.format(int(min_), int(max_), page)
    response = requests.post('https://angel.co/company_filters/search_data', headers=headers, cookies=cookies, data=data)
    return response.json()

def decrease(response_data, step):
    global range_min
    global range_max
    cnt = 0
    while response_data['total'] > 20*19:
        cnt += 1
        range_max /= step
        print "lowering max to", range_max
        response_data = request_companies(range_min, range_max, page)
    return response_data, cnt

def increase(response_data, step):
    global range_min
    global range_max
    cnt = 0
    while response_data['total'] < 20*5:
        cnt += 1
        range_max *= step
        print "increasing max to", range_max
        response_data = request_companies(range_min, range_max, page)
    return response_data, cnt

while True:
    page = 1
    response_data = request_companies(range_min, range_max, page)
    if response_data['total'] == 0:
        raise Exception("done")

    # find a good max
    response_data, _ = decrease(response_data, 2)

    iters = 0
    steps = ( (1+1.0/div) for div in itertools.count(1))
    for step in steps:
        # assert max is not too low
        response_data, iters_up = increase(response_data, step)

        # assert max is not too high
        response_data, iters_down = decrease(response_data, step)
        iters = iters_up + iters_down
        if iters == 0:
            break
    
    pages = int(response_data['total'] / 20) + 1
    print "pages:", pages
    for page in range(pages):
        response_data = request_companies(range_min, range_max, page)
        with open("data/ids.linejson","a") as dump:
            json.dump(response_data['ids'], dump)
            dump.write("\n")

    if response_data['page'] != page:
        raise Exception()

    range_min, range_max = range_max, 2*(2*range_max-range_min)
    print "new ranges", range_min, range_max
