from django.core.management.base import BaseCommand, CommandError
from monsters.models import Monster, Action, Trait, LegendaryAction
import re
import json
import requests

class Command(BaseCommand):
    help = 'decription here'

    # def add_arguments(self, parser):
    #     parser.add_argument('filenames', nargs='+', type=str)

    def handle(self, *args, **options):

        Trait.objects.all().delete()
        Action.objects.all().delete()
        LegendaryAction.objects.all().delete()
        Monster.objects.all().delete()

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

            # create record
            info = json.loads(html, strict=False)['monster']
            immunities = info.get('damage-immunities', '') + ', ' + info.get('condition-immunities', '')
            immunities = immunities.strip(', ')
            leg_act_notes = None
            if 'legendary-actions' in info:
                leg_act_notes = info['legendary-actions']['description']

            m = Monster(name=info['name'],
                        size=info['size'],
                        type=info['type'],
                        alignment=info['alignment'],
                        ac=info['armor-class'],
                        hp=str(info['hit-points']['die-count']) + 'd' + str(info['hit-points']['die']) + ' + ' + str(info['hit-points'].get('modifier', 0)),
                        speed=info['speed'],
                        str_mod=info['str'],
                        dex_mod=info['dex'],
                        con_mod=info['con'],
                        int_mod=info['int'],
                        wis_mod=info['wis'],
                        cha_mod=info['cha'],
                        saving_throws=json.dumps(info['saving-throws']) if 'saving-throws' in info else None,
                        skills=json.dumps(info['skills']) if 'skills' in info else None,
                        vulnerabilies=info.get('damage-vulnerabilities', None),
                        resistances=info.get('damage-resistances', None),
                        immunities=immunities,
                        senses=info['senses'],
                        languages=info.get('languages', None),
                        cr=info['challenge'],
                        xp=xp,
                        legendary_action_notes=leg_act_notes,
                        )
            m.save()

            for trait in info.get('traits', []):
                t = Trait(monster=m,
                          name=trait['name'] + ('({})'.format(trait['notes']) if 'notes' in trait else ''),
                          description=trait['description'],
                          )
                t.save()

            for action in info.get('actions', []):
                a = Action(monster=m,
                           name=action['name'] + ('({})'.format(action['notes']) if 'notes' in action else ''),
                           description=action['description'],
                           )
                a.save()

            if 'legendary-actions' in info:
                for action in info['legendary-actions'].get('actions', []):
                    a = LegendaryAction(monster=m,
                                        name=action['name'] + ('({})'.format(action['notes']) if 'notes' in action else ''),
                                        description=action['description'],
                                        )
                    a.save()


