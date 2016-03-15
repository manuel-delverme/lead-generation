cookies = {
    'D_SID': '93.35.203.116:DjEG0xGGAPeGEzse2OALHSnbrhyDBpXs7Az7vgKx/MI',
    'pgz': 'ODQ1ODg7VG9yaW5vO1RPOzkx',
    '__rtgxg': '105E27E5-00C4-0001-F81B-14F0A9F01E4C',
    '__rtgxh': '1456681089587$1456681089587$1',
    'kpi': 'ef13987b.52cda217ddd8c',
    'mr': '20',
    'sessionid': '1959369162744455383',
    'argo': 'eyJ3aGF0IjoiYXBwYXJlY2NoaWF0dXJlIGVsZXR0cm9uaWNoZSIsIm1yIjoyMH0=',
    'iqhx': '4374382a-5467-4a35-9b32-e82e3eaacfb6',
    'lst': 'cmljZXJjYS9uYXZpZ2EvMDAwNjQ5NjAwL2FwcGFyZWNjaGlhdHVyZV9lbGV0dHJvbmljaGU=',
    'listPositionUrlForCookie': '01_albatron|02_selinsrl-mi|03_craem-to|04_centrorisparmiofrancesconi|05_sipesrl|06_eggtronic|07_marcheelet|08_pieffepivision|09_aglasrl|10_professionalsecurityfirenze|11_saeelectronic|12_lacoel_assemblaggi_elettronici|13_marpossitalia|14_gilbarcoveederrootfirenze|15_eldisnc|16_groupeenergyservice|17_tecnosystemsas|18_pepperlfuchsfaitalia|19_casit|20_centrocommercialejes',
    'refererShiny': 'aHR0cDovL3d3dy5wYWdpbmVnaWFsbGUuaXQvY2F0L2VsZW5jb19hbGZhYmV0aWNvX2EuaHRtbA==',
    'cp_acc': '1',
    's_cc': 'true',
    's_sq': '%5B%5BB%5D%5D',
    '__bclc1': '1249@8E0556A8-6A58-4334-B9CB-C7E28049A976|798@630554F9-5440-43BF-8162-FC912E36FD48|976@7AFFA036-AB08-4DC3-895D-CC728B83981B|777@98A4C623-B812-4B2F-975E-F9AB9C8E748F',
    'D_PID': 'C7A9E137-DBE9-34C8-9F83-E2C9DF26D3AC',
    'D_IID': '4256BE7B-BD96-36E6-ADCB-C5B66C6C4C48',
    'D_UID': 'D9A1BE04-5319-3C97-81C6-68A7EFE7E691',
    'D_HID': 'wSQxlPyH6+BavxItGPiq0TsUmN79xdJL7GANlZfJ+B8',
    's_fid': '70F8CF0AF652A5C9-0E3845D82CA7512E',
    's_lv': '1458072716764',
    's_lv_s': 'Less%20than%201%20day',
    's_nr': '1458072716765-Repeat',
    'gpv_p24': 'PGIT%3AListat%3AConris%3ACatego',
}

headers = {
    'Pragma': 'no-cache',
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,it;q=0.6',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'no-cache',
    'Referer': 'http://www.paginegialle.it/cat/elenco_alfabetico_d.html',
    'Connection': 'keep-alive',
}

from bs4 import BeautifulSoup
import requests
import string

with open("/tmp/outputs.txt", "w") as fout:
    for letter in string.ascii_lowercase:
        response = requests.get('http://www.paginegialle.it/cat/elenco_alfabetico_{}.html'.format(letter), headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.text)
        for link in soup.select('.vertSingleCity'):
            fout.write(link['href'].split("/")[4] + "\n")
        [n.split("-")[0] for n in open("/tmp/outputs.txt")]
        print letter
