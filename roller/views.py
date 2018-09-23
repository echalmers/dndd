from django.shortcuts import render
from django.http import HttpResponse
import re
import numpy as np

roll_mod_re = re.compile('[0-9]{1,3}\s{0,2}d\s{0,2}[0-9]{1,2}\s{0,2}[\+\-\−]\s{0,2}[0-9]{1,3}')
roll_re = re.compile('[0-9]{1,3}\s{0,2}d\s{0,2}[0-9]{1,2}')
mod_re = re.compile('[\+\-]\s{0,2}[0-9]{1,3}')
signed_int_re = re.compile('[\+\-]\s{0,2}[0-9]{1,3}')

poptext = """<div class="popup" onclick="getRollSim('{popupname}', {count},{die},{mod})">{text}<span class="popuptext" id="{popupname}">A Simple Popup!</span></div>"""

num = 0


def signed_string(integer, is_ability_score=False):

    if is_ability_score:
        integer = int((integer-10)/2)
    if integer < 0:
        return str(integer) + ' '
    else:
        return '+' + str(integer) + ' '


def rolls2links(text):
    global num

    text = re.sub('−', '-', text)

    for match in reversed([x for x in roll_mod_re.finditer(text)]):
        new_match_txt = match.group().replace(' ', '')
        parts = re.split('[d\+\-\−]', new_match_txt)
        count = parts[0]
        die = parts[1]
        mod = signed_int_re.search(new_match_txt).group()
        # mod = re.sub('[\+-]', '', mod)

        parts = re.split('[d\+-]', new_match_txt)

        text = text[0:match.span()[0]] + \
               poptext.format(popupname='pop' + str(num),
                              count=count,
                              die=die,
                              mod=mod,
                              text=new_match_txt) + \
               text[match.span()[1]:]
        num += 1
        # print(match)
        # print(text)

    masked_text = np.array(list(text))
    for code in re.finditer('<div.+?</div>', text):
        masked_text[code.span()[0]:code.span()[1]] = '_'
    masked_text = ''.join(masked_text)


    for match in reversed([x for x in roll_re.finditer(masked_text)]):
        new_match_txt = match.group().replace(' ', '')
        parts = new_match_txt.split('d')
        text = text[0:match.span()[0]] \
               + poptext.format(popupname='pop' + str(num),
                                count=parts[0],
                                die=parts[1],
                                mod=0,
                                text=new_match_txt) \
               + text[match.span()[1]:]
        num += 1
        # print(match)
        # print(text)

    masked_text = np.array(list(text))
    for code in re.finditer('<div.+?</div>', text):
        masked_text[code.span()[0]:code.span()[1]] = '_'
    masked_text = ''.join(masked_text)

    for match in reversed([x for x in mod_re.finditer(masked_text)]):
        new_match_txt = match.group().replace(' ', '')
        mod = signed_int_re.search(new_match_txt).group()
        text = text[0:match.span()[0]] \
               + poptext.format(popupname='pop' + str(num),
                                count=1,
                                die=20,
                                mod=mod,
                                text=new_match_txt + '&nbsp') \
               + text[match.span()[1]:]
        num += 1
        # print(match)
        # print(text)
    return text

# print(rolls2links(""" creature in that line must make a DC 14 Dexterity saving throw, taking 40 (9d8) acid da"""))
# print(rolls2links(""": +1 to hit, reach 5 ft., one target. Hit: 2 (1d6 − 1) slashi"""))
# print(re.findall('[0-9]{1,3}\s{0,2}d\s{0,2}[0-9]{1,2}\s{0,2}[\+-−]\s{0,2}[0-9]{1,3}', 'it: 2 (1d6 − 1) s'))
# print(roll('2','6','-0'))


def simulate_roll_from_text(text):
    parts = text.replace('d', ' ').replace(' + ', ' ').split()
    return simulate_roll(count=int(parts[0]),
                         die=int(parts[1]),
                         mod=int(parts[2]))


def simulate_roll(count, die, mod):

    info = {}
    info['rolls'] = np.random.randint(1, die + 1, count)
    info['mod'] = mod
    info['total'] = sum(info['rolls']) + mod
    info['math'] = ' + '.join([str(x) for x in info['rolls']]) + ' + ' + str(mod) + ' = ' + str(info['total'])
    return info


def roll(request):

    print(request.GET)

    type = request.GET.get('type', 'math')

    count = request.GET.get('count')
    die = request.GET.get('die')
    mod = request.GET.get('mod')

    count = int(count)
    die = int(die)
    if mod.startswith('+'):
        mod = int(mod[1:])
    elif mod.startswith('-'):
        mod = -int(mod[1:])
    else:
        mod = int(mod)

    roll = simulate_roll(count, die, mod)
    if type == 'math':
        return HttpResponse(roll['math'])
    else:
        return HttpResponse(roll['total'])

