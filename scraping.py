import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from time import time
start_time = time()

OLD_SONGS_NOTES_URL = 'https://bemaniwiki.com/index.php?beatmania%20IIDX%2029%20CastHour/%B5%EC%B6%CA%C1%ED%A5%CE%A1%BC%A5%C4%BF%F4%A5%EA%A5%B9%A5%C8'
NEW_SONGS_URL = 'https://bemaniwiki.com/index.php?beatmania%20IIDX%2029%20CastHour/%BF%B7%B6%CA%A5%EA%A5%B9%A5%C8'

def fetch_and_parse(url):
    res = requests.get(url)
    if not res.ok:
        raise Exception('fetch error! url:{}, status:{}, reason:{}'.format(url, res.status_code, res.reason))
    utf8_html = res.content.decode('euc-jp', 'replace')
    return BeautifulSoup(utf8_html, 'html.parser')

json_dict = {
    'header': {
        'created_at': str(datetime.now()),
        'iidx_version': 29,
        'format_version': 1
    },
    'songs': []
}
version_dict = {}
notes_dict = {}

types = [('SPB',1),('SPN',2),('SPH',3),('SPA',4),('SPL',5),('DPN',6),('DPH',7),('DPA',8),('DPL',9)]
soup = fetch_and_parse(OLD_SONGS_NOTES_URL)
_ver = -1
for tr in soup.find_all('table')[2].find_all('tr'):
    tds = tr.find_all('td')
    if len(tds)==1: _ver += 1
    if len(tds) != 13: continue
    title = tds[0].string
    version = max(1, _ver) #1st style: 0->1 substream: 1->1
    version_dict[title] = version
    notes = {}
    for _type,i in types:
        if tds[i].string == '-': continue
        notes[_type] = int(tds[i].string)
    notes_dict[title] = notes

soup = fetch_and_parse(NEW_SONGS_URL)
_, new_song_levels, new_song_notes = soup.find_all('table')
category = ''
for tr in new_song_notes.find_all('tr'):
    tds = tr.find_all('td')
    if len(tds)==1: category = tds[0].string
    if len(tds) != 13: continue
    if category == '復活曲': continue
    title = tds[0].string
    version_dict[title] = 29
    notes = {}
    for _type,i in types:
        if tds[i].string is None or tds[i].string == '-': continue
        notes[_type] = int(tds[i].string)
    notes_dict[title] = notes

for title,version in version_dict.items():
    json_dict['songs'].append({
        'version': version,
        'title': title,
        'notes': notes_dict[title]
    })

with open('songs.json', 'w') as f:
    json.dump(json_dict, f, ensure_ascii=False, indent=4)

print('elapsed time = {}'.format(time() - start_time))
