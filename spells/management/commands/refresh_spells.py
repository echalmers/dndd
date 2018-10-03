import requests
import re
import ast


def parse_spell_list():
    r = requests.get('http://dnd5e.wikia.com/wiki/List_of_Spells')
    html = r.content.decode()

    search_lines = ['<h2><span class="mw-headline" id="Cantrips"> Cantrips </span></h2>',
                    '<h2><span class="mw-headline" id="1st_Level"> 1st Level </span></h2>',
                    '<h2><span class="mw-headline" id="2nd_Level"> 2nd Level </span></h2>',
                    '<h2><span class="mw-headline" id="3rd_Level"> 3rd Level </span></h2>',
                    '<h2><span class="mw-headline" id="4th_Level"> 4th Level </span></h2>',
                    '<h2><span class="mw-headline" id="5th_Level"> 5th Level </span></h2>',
                    '<h2><span class="mw-headline" id="6th_Level"> 6th Level </span></h2>',
                    '<h2><span class="mw-headline" id="7th_Level"> 7th Level </span></h2>',
                    '<h2><span class="mw-headline" id="8th_Level"> 8th Level </span></h2>',
                    '<h2><span class="mw-headline" id="9th_Level"> 9th Level </span></h2>',
                    ]
    links = []

    for search_line in search_lines:

        html = html[html.index(search_line):]
        table_html = html[html.index('<table class="article-table sortable">'):html.index('</table>')]

        links.extend([x.split('"')[1] for x in re.findall('a href=".+?"', table_html)])

    return links


def parse_tags(tags):
    d = dict()

    d['cantrip'] = 'Cantrip' in tags

    for c in ['Bard', 'Cleric', 'Druid', 'Paladin', 'Ranger', 'Sorcerer','Warlock', 'Wizard']:
        d[c.lower()] = c.title() + ' Spells' in tags

    for l in range(1,10):
        if 'Level ' + str(l) + ' Spell' in tags:
            d['level'] = l

    d['']

    return d


def parse_spell(link):
    print(link)

    spell_dict = dict()

    r = requests.get('http://dnd5e.wikia.com' + link)
    html = r.content.decode()

    # get description
    html = html[html.index('<meta name="description" content="') + 34:]
    spell_dict['description'] = html[:html.index('"')]

    # get name
    html = html[html.index('<title>')+7:]
    spell_dict['name'] = html[:html.index(' |')]

    # get casting time
    html = html[html.index('<th>Casting Time\n</th><td>')+26:]
    spell_dict['casting_time'] = html[:html.index('</td>')]

    # get range
    html = html[html.index('<th>Range\n</th><td>') + 19:]
    spell_dict['range'] = html[:html.index('</td>')]

    # get components
    html = html[html.index('<th>Components\n</th><td>') + 24:]
    spell_dict['components'] = html[:html.index('</td>')]

    # get duration
    html = html[html.index('<th>Duration\n</th><td>') + 22:]
    spell_dict['duration'] = html[:html.index('</td>')]

    # get tags
    html = html[html.index('"wgCategories":[') + 16:]
    tags = html[:html.index(']')]
    spell_dict.update(parse_tags(ast.literal_eval(tags)))

    return spell_dict


all_spells = parse_spell_list()
tags = set()
failures = []
for spell in all_spells:
    try:
        this_tags = parse_spell(spell)
        tags.update(this_tags)
    except:
        failures.append(spell)


print(len(tags))
print(tags)
print(failures)