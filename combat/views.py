from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import PcCombatant, NpcCombatant, Combat
from players.models import Player
from monsters.models import Monster
import pandas as pd
from util import df_to_text
from roller.views import simulate_roll_from_text, simulate_roll
import random
import numpy as np
from monsters.views import deets_from_name


def main(request):

    return render(request, 'combat/setup.html',)


def setup(request):

    # get table of pc characters
    pcs = PcCombatant.objects.all()
    if len(pcs) > 0:
        pcs = [{'name': pc.display_name,
                'level': pc.player.level,
                'initiative': pc.initiative,}
               for pc in pcs]
        pc_df = pd.DataFrame(pcs)
        pc_df = pc_df[['name', 'level', 'initiative']]
    else:
        pc_df = pd.DataFrame(columns=['name', 'level', 'initiative'])

    pc_df['actions'] = '<a href="remove_pc/' + pc_df['name'] \
                       + '">delete</a>'

    pd.set_option('display.max_colwidth', -1)
    variables = {'pcs': pc_df.fillna('').to_html(classes='datatable', escape=False, index=False)}

    # populate drop-down with list of remaining pcs
    all_pcs = ['<option value="{}">'.format(player.name)
               for player in Player.objects.all() if player.name not in pc_df.name.values]
    variables['pc_options'] = ''.join(all_pcs)

    # get table of npc characters
    npcs = NpcCombatant.objects.all()
    if len(npcs) > 0:
        npcs = [{'display name': npc.display_name,
                 'NPC name': npc.monster.name,
                 'max hp': npc.max_hp,
                 'cr': npc.monster.cr,
                 'xp': npc.monster.xp,
                 'initiative': npc.initiative,}
                for npc in npcs]
        npcs = pd.DataFrame(npcs)
        npcs = npcs[['display name','NPC name','max hp','cr','xp','initiative']]
    else:
        npcs = pd.DataFrame(columns=['display name','NPC name','max hp','cr','xp','initiative'])

    npcs['actions'] = '<a href="remove_npc/' + npcs['display name'] \
                       + '">delete</a>'
    npcs['NPC name'] = npcs['NPC name'].apply(lambda x: '<a onclick="loadDescript(\'{name}\')" href="#">{name}</a>'.format(name=x))

    pd.set_option('display.max_colwidth', -1)
    variables['npcs'] = npcs.fillna('').to_html(classes='datatable', escape=False, index=False)

    # calculate some summary stats of the encounter
    variables['totalxp'] = npcs.xp.sum() if len(npcs.index) > 0 else 0
    variables['maxcr'] = npcs.cr.max() if len(npcs.index) > 0 else '-'
    if variables['maxcr'] != '-' and variables['maxcr'] > pc_df.level.max():
        variables['maxcr'] = str(variables['maxcr']) + ' (players are outclassed)'

    from combat.xp_table import xp_table
    from io import StringIO
    ratings = pd.read_csv(StringIO(xp_table), index_col=None)
    # print(ratings)
    xp_ref = {
        difficulty: sum([ratings.loc[ratings.Level==l, difficulty].values[0] for l in pc_df.level.values])
        for difficulty in ['Easy', 'Moderate', 'Challenging', 'Hard']
    }
    xp_ref['Deadly'] = 2*xp_ref['Hard'] - xp_ref['Challenging']
    xp_dif = pd.Series(xp_ref)
    xp_dif = (xp_dif - variables['totalxp']).abs()

    variables['difficulty'] = xp_dif.idxmin

    variables['easy_xp'] = xp_ref['Easy']
    variables['moderate_xp'] = xp_ref['Moderate']
    variables['challenging_xp'] = xp_ref['Challenging']
    variables['hard_xp'] = xp_ref['Hard']
    variables['deadly_xp'] = xp_ref['Deadly']

    # populate drop-down with list of npcs
    all_npcs = ['<option value="{}">'.format(monster.name)
               for monster in Monster.objects.all()]
    variables['cr_options'] = ''.join(['<option value="{}">'.format(cr)
                               for cr in sorted(list(set([int(monster.cr) for monster in Monster.objects.all()])))])
    variables['npc_options'] = ''.join(all_npcs)

    return render(request, 'combat/setup.html', variables)


def add_pc(request):

    pc_name = request.GET.get('pc')
    print(pc_name)
    player = Player.objects.get(name=pc_name)

    pc_combatant = PcCombatant(display_name=player.name,
                               initiative=simulate_roll(1,20,player.initiative)['total'],
                               player=player)
    pc_combatant.save()

    return HttpResponseRedirect(reverse('setup_encounter'))


def remove_pc(request, pc_name=None):

    print(pc_name)
    pc_combatant = PcCombatant.objects.get(display_name=pc_name)
    pc_combatant.delete()

    num_combatants = len(NpcCombatant.objects.all()) + len(PcCombatant.objects.all())
    combat, _ = Combat.objects.get_or_create(name='main')
    combat.turn = min(combat.turn, num_combatants)
    combat.save()
    return HttpResponseRedirect(reverse('setup_encounter'))


def add_npc(request):
    npc_name = request.GET.get('npc')
    display_name = request.GET.get('display_name')
    _add_npc(npc_name, display_name)

    return HttpResponseRedirect(reverse('setup_encounter'))


def _add_npc(npc_name, display_name):
    if display_name == '':
        number = 1
        while True:
            try:
                print(number)
                x = NpcCombatant.objects.get(display_name='NPC ' + str(number))
                print(x)
                number += 1
            except NpcCombatant.DoesNotExist as ex:
                break
        display_name = 'NPC ' + str(number)

    monster = Monster.objects.get(name=npc_name)
    init_roll = simulate_roll(count=1,
                              die=20,
                              mod=int((monster.dex_mod-10)/2))
    max_hp = simulate_roll_from_text(monster.hp)['total']
    npcCombatant = NpcCombatant(display_name=display_name,
                                initiative=init_roll['total'],
                                max_hp=max_hp,
                                current_hp=max_hp,
                                monster=monster)
    npcCombatant.save()


def remove_npc(request, npc_name=None):
    npc_combatant = NpcCombatant.objects.get(display_name=npc_name)
    npc_combatant.delete()

    num_combatants = len(NpcCombatant.objects.all()) + len(PcCombatant.objects.all())
    combat, _ = Combat.objects.get_or_create(name='main')
    combat.turn = min(combat.turn, num_combatants)
    combat.save()
    return HttpResponseRedirect(reverse('setup_encounter'))


def randomize(request):

    total_xp = int(request.GET.get('total_xp'))
    max_cr = int(request.GET.get('max_cr'))

    if request.GET.get('clear_existing', 'False') == 'True':
        NpcCombatant.objects.all().delete()

    current_xp = sum([npc.monster.xp for npc in NpcCombatant.objects.all()])
    xp_budget = total_xp - current_xp

    selected_monsters = []
    while True:
        monster_options = Monster.objects.filter(cr__lte=max_cr, cr__gt=0, xp__lte=xp_budget).values()
        if len(monster_options) == 0:
            break

        monster_options = pd.DataFrame.from_records(monster_options)
        selected_monster = np.random.choice(monster_options.index.values, p=monster_options.xp.values/monster_options.xp.sum())
        selected_monsters.append(monster_options.name[selected_monster])
        xp_budget -= monster_options.xp[selected_monster]

    for monster_name in selected_monsters:
        _add_npc(monster_name, '')

    return HttpResponseRedirect(reverse('setup_encounter'))


def dashboard(request):

    combat, _ = Combat.objects.get_or_create(name='main')

    pcs = [{'name': pc.display_name,
            'ac': pc.player.ac,
            'initiative': pc.initiative} for pc in PcCombatant.objects.all()]
    pcs = pd.DataFrame(pcs)

    npcs = [{'name': npc.display_name,
             'ac': npc.monster.ac,
             'hp': npc.current_hp,
             'max hp': npc.max_hp,
             'NPC name': npc.monster.name,
             'initiative': npc.initiative} for npc in NpcCombatant.objects.all()]
    npcs = pd.DataFrame(npcs)
    # make monster name links
    npcs['NPC name'] = npcs['NPC name'].apply(
        lambda x: '<a onclick="loadDescript(\'{name}\')" href="#">{name}</a>'.format(name=x))

    # combine pcs and npcs and add turn order
    all_combatants = pcs.append(npcs).sort_values('initiative', ascending=False)
    all_combatants['turn order'] = [i for i in range(1, len(all_combatants.index)+1)]

    # if it's an NPCs turn, display the deets
    variables = {}
    npc_name = all_combatants[all_combatants['turn order']==combat.turn]['NPC name'].values[0]
    if not pd.isna(npc_name):
        npc_name = npc_name.split("'")[1]
        variables = {'deets': deets_from_name(None, npc_name).content.decode()}

    # highlight row of current turn
    for col in ['name']:
        val = str(all_combatants.loc[all_combatants['turn order']==combat.turn, col].values[0])
        all_combatants.loc[all_combatants['turn order']==combat.turn, col] = """<div style="background-color: #8ab1f2;">""" + val + """</div>"""
        # all_combatants.loc[all_combatants['turn order'] == 3, col] = '<b>' + str(val) + '</b>'

    # highlight rows of ko'd characters
    vals = all_combatants.loc[all_combatants['hp'] <= 0, 'hp'].astype(str).values
    all_combatants.loc[all_combatants['hp'] <= 0, 'hp'] = """<div style="background-color: red; color: white;">""" + vals + """</div>"""

    # order columns
    all_combatants = all_combatants[['name', 'ac', 'NPC name', 'hp', 'max hp']]

    pd.set_option('display.max_colwidth', -1)
    variables['table'] = all_combatants.fillna('').to_html(classes='datatable', escape=False, index=False)
    variables['round'] = combat.round
    variables['turn'] = combat.turn
    total_seconds = (combat.round-1)*6
    minutes = int(total_seconds/60)
    seconds = format(total_seconds % 60, '02d')
    variables['time'] = '{min}:{sec}'.format(min=minutes, sec=seconds)

    # populate list of npcs
    all_npcs = ['<option value="{}">'.format(name)
               for name in npcs.name.values]
    variables['npc_options'] = ''.join(all_npcs)

    return render(request, 'combat/dashboard.html', variables)


def advance(request):

    direction = int(request.GET.get('direction', 1))

    combat, _ = Combat.objects.get_or_create(name='main')
    num_combatants = len(NpcCombatant.objects.all()) + len(PcCombatant.objects.all())

    combat.turn += direction
    if combat.turn > num_combatants:
        combat.turn = 1
        combat.round += 1
    elif combat.turn == 0:
        combat.turn = num_combatants
        combat.round -= 1

    combat.save()
    return HttpResponseRedirect(reverse('combat_dashboard'))


def change_hp(request):

    npc = NpcCombatant.objects.get(display_name=request.GET.get('name'))
    amount = int(request.GET.get('increase', -int(request.GET.get('decrease', 0))))

    if request.GET.get('resistance', False):
        amount = int(amount/2)

    npc.current_hp += amount
    if npc.current_hp < 0 and npc.current_hp > -npc.max_hp:
        npc.current_hp = 0
    npc.save()
    return HttpResponseRedirect(reverse('combat_dashboard'))

def reset(request):
    name='main'
    return reset_combat(name)

def reset_combat(name):
    combat, _ = Combat.objects.get_or_create(name=name)
    combat.turn = 1
    combat.round = 1
    combat.save()

    for npc in NpcCombatant.objects.all():
        npc.current_hp = npc.max_hp
        npc.save()
    return HttpResponseRedirect(reverse('combat_dashboard'))
