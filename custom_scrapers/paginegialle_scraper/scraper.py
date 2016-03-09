resp = requests.get("http://mobile.seat.it/searchpg?client=pgbrowsing&version=5.0.1&device=evo&pagesize=25&output=jsonp&lang=en&what=a")
js = json.loads(resp.text[1:-3])
len(js['results'])
