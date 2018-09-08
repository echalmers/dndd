from django.core.management.base import BaseCommand, CommandError
from monsters.models import Monster
import re
import json
import requests

class Command(BaseCommand):
    help = 'decription here'

    # def add_arguments(self, parser):
    #     parser.add_argument('filenames', nargs='+', type=str)

    def handle(self, *args, **options):

        r = requests.get('http://www.orcpub.com/dungeons-and-dragons/5th-edition/monsters')
        html = r.content.decode()

        # get all monster links
        links = set(re.findall('/dungeons-and-dragons/5th-edition/monsters/.+?"', html))
        links = [x[:-1] for x in links]
        # links = ['/dungeons-and-dragons/5th-edition/monsters/iron-golem']

        # process each monster page
        key_re = re.compile('\W:\S+? ')
        comma_re = re.compile('}\s+\{')
        xp_re = re.compile('\(</span><span>[0-9]+</span><span> XP\)')
        num_re = re.compile('[0-9]+')
        for i in range(0, len(links)):
            link = links[i]
            print(link + ' ({num}/{total})'.format(num=i + 1, total=len(links)))
            r = requests.get('http://www.orcpub.com' + link)
            html = r.content.decode()

            # extract the XP
            match = xp_re.search(html)
            xp = int(num_re.search(match.group()).group())
            print(xp)

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

                html = html.replace(match.group(), match.group()[0] + '"' + match.group()[2:-1] + '": ')

            # add missing commas
            html = comma_re.sub('}, {', html)

            # replace fractional CRs
            html = html.replace('"challenge": 1/8', '"challenge": 0.125') \
                .replace('"challenge": 1/4', '"challenge": 0.25') \
                .replace('"challenge": 1/2', '"challenge": 0.5')

            # load from json
            info = json.loads(html, strict=False)['monster']

            # get immunities
            immunities = info.get('damage-immunities', '') + ', ' + info.get('condition-immunities', '')
            immunities = immunities.strip(', ')

            # get legendary actions
            if 'legendary-actions' in info:
                leg_actions = info['legendary-actions']['description']

                for action in info['legendary-actions'].get('actions', []):
                    leg_actions += '\n\n' + '<b>{name}:</b> {description}'.format(name=action['name'] + ('({})'.format(action['notes']) if 'notes' in action else ''),
                                                                                  description=action['description'])
            else: leg_actions = None

            # get actions
            if 'actions' in info:
                acts = '\n\n'.join(['<b>{name}:</b> {description}'.format(name=action['name'] + ('({})'.format(action['notes']) if 'notes' in action else ''),
                                                                          description=action['description'])
                                    for action in info['actions']])
            else: acts = None

            # get traits
            if 'traits' in info:
                traits = '\n\n'.join(['<b>{name}:</b> {description}'.format(name=trait['name'] + ('({})'.format(trait['notes']) if 'notes' in trait else ''),
                                                                          description=trait['description'])
                                    for trait in info['traits']])
            else: traits = None

            # upsert the monster record
            m, _ = Monster.objects.get_or_create(name=info['name'])

            m.size = info.get('size')
            m.type = info['type']
            m.alignment = info['alignment']
            m.ac = info['armor-class']
            m.hp = str(info['hit-points']['die-count']) + 'd' + str(info['hit-points']['die']) + ' + ' + str(
                info['hit-points'].get('modifier', 0))
            m.speed = info['speed']
            m.str_mod = info['str']
            m.dex_mod = info['dex']
            m.con_mod = info['con']
            m.int_mod = info['int']
            m.wis_mod = info['wis']
            m.cha_mod = info['cha']
            m.saving_throws = json.dumps(info['saving-throws']) if 'saving-throws' in info else None
            m.skills = json.dumps(info['skills']) if 'skills' in info else None
            m.vulnerabilies = info.get('damage-vulnerabilities', None)
            m.resistances = info.get('damage-resistances', None)
            m.immunities = immunities
            m.senses = info['senses']
            m.languages = info.get('languages', None)
            m.cr = info['challenge']
            m.xp = xp
            m.legendary_actions = leg_actions
            m.actions = acts
            m.traits = traits

            m.save()







