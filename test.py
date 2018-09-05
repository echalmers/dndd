from bs4 import BeautifulSoup
import requests
import json
import re
import json

r = requests.get('http://www.orcpub.com/dungeons-and-dragons/5th-edition/monsters')
html = r.content.decode()

# get all monster links
# links = set(re.findall('/dungeons-and-dragons/5th-edition/monsters/.+?"', html))
# links = [x[:-1] for x in links]
links = ['/dungeons-and-dragons/5th-edition/monsters/ancient-brass-dragon']

# process each monster page
key_re = re.compile(':\S+? ')
comma_re = re.compile('}\s+\{')
for i in range(0, len(links)):
    link = links[i]
    print(link + ' ({num}/{total})'.format(num=i+1, total=len(links)))
    r = requests.get('http://www.orcpub.com' + link)
    html = r.content.decode()

    # extract the json-ish part
    html = html.split('id="embedded-data">')[1]
    html = html.split('</div>')[0]

    # replace newlines
    html = html.replace('\\n', '\n')

    # convert keys
    num = 0
    while True:
        match = key_re.search(html)
        if match is None:
            break

        html = html.replace(match.group(), '"' + match.group()[1:-1] + '": ')

    # add missing commas
    html = comma_re.sub('}, {', html)

    # replace fractional CRs
    html = html.replace('"challenge": 1/8', '"challenge": 0.125') \
        .replace('"challenge": 1/4', '"challenge": 0.25') \
        .replace('"challenge": 1/2', '"challenge": 0.5')

    try:
        print(json.loads(html, strict=False))
    except Exception as ex:
        print(html)
        raise ex

