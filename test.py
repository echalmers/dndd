from bs4 import BeautifulSoup
import requests
import json
import re
import json

r = requests.get('http://www.orcpub.com/dungeons-and-dragons/5th-edition/monsters')
html = r.content.decode()

# get all monster links
links = set(re.findall('/dungeons-and-dragons/5th-edition/monsters/.+?"', html))
links = [x[:-1] for x in links]

# process each monster page
key_re = re.compile(':\S+? ')
comma_re = re.compile('}\s+\{')
for link in ['/dungeons-and-dragons/5th-edition/monsters/couatl']: #links[:40]:
    print(link)
    r = requests.get('http://www.orcpub.com' + link)
    html = r.content.decode()

    # extract the json-ish part
    html = html.split('id="embedded-data">')[1]
    html = html.split('</div>')[0]
    print(html)

    # convert keys
    while True:
        match = key_re.search(html)
        if match is None:
            break
        html = html.replace(match.group(), '"' + match.group()[1:-1] + '": ')
        print(html)

    # add missing commas
    html = comma_re.sub('}, {', html)

    # replace fractional CRs
    html = html.replace('"challenge": 1/8', '"challenge": 0.125') \
        .replace('"challenge": 1/4', '"challenge": 0.25') \
        .replace('"challenge": 1/2', '"challenge": 0.5')

    try:
        print(json.loads(html))
    except Exception as ex:
        print(html)
        raise ex

