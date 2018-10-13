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

    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    # get table of pc characters
    pcs = PcCombatant.objects.filter(combat=combat)
    if len(pcs) > 0:
        pcs = [{'name': pc.display_name,
                'level': pc.player.level,
                'initiative': pc.initiative,}
               for pc in pcs]
        pc_df = pd.DataFrame(pcs)
        pc_df = pc_df[['name', 'level', 'initiative']]
    else:
        pc_df = pd.DataFrame(columns=['name', 'level', 'initiative'])

    pc_df['actions'] = '<a href="remove_pc/' + pc_df['name'] + '">delete</a>, ' \
                       + '<a onclick="changeInit(\'' + pc_df['name'] + '\', \'' + pc_df['initiative'].astype(str) + '\')" href="#">change initiative roll</a>'

    pd.set_option('display.max_colwidth', -1)
    variables = {'pcs': pc_df.fillna('').to_html(classes='datatable', escape=False, index=False)}

    # populate drop-down with list of remaining pcs
    all_pcs = ['<option value="{}">'.format(player.name)
               for player in Player.objects.all() if player.name not in pc_df.name.values]
    variables['pc_options'] = ''.join(all_pcs)

    # get table of npc characters
    npcs = NpcCombatant.objects.filter(combat=combat)
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

    npcs['actions'] = '<a href="remove_npc/' + npcs['display name'] + '">delete</a>'

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
    variables['combat'] = combat_name
    return render(request, 'combat/setup.html', variables)


def add_pc(request):

    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    pc_name = request.GET.get('pc')
    print(pc_name)
    print(combat_name)
    player = Player.objects.get(name=pc_name)

    initiative = simulate_roll(1,20,player.initiative)['total']
    if player.advantage_on_init:
        initiative = max(initiative,
                         simulate_roll(1, 20, player.initiative)['total'])

    pc_combatant = PcCombatant(display_name=player.name,
                               initiative=initiative,
                               player=player,
                               combat=combat)
    pc_combatant.save()

    return HttpResponseRedirect(reverse('setup_encounter'))


def change_init(request):
    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    pc = PcCombatant.objects.get(combat=combat, display_name=request.GET.get('name'))
    pc.initiative = request.GET.get('new_init')
    pc.save()

    return HttpResponseRedirect(reverse('setup_encounter'))

def remove_pc(request, pc_name=None):

    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    print(pc_name)
    pc_combatant = PcCombatant.objects.get(display_name=pc_name, combat=combat)
    pc_combatant.delete()

    num_combatants = len(NpcCombatant.objects.filter(combat=combat)) + len(PcCombatant.objects.filter(combat=combat))

    combat.turn = min(combat.turn, num_combatants)
    combat.save()
    return HttpResponseRedirect(reverse('setup_encounter'))


def add_npc(request):
    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    npc_name = request.GET.get('npc')
    display_name = request.GET.get('display_name')
    _add_npc(npc_name, display_name, combat)

    return HttpResponseRedirect(reverse('setup_encounter'))


def _add_npc(npc_name, display_name, combat):
    if display_name == '':
        number = 1
        while True:
            try:
                print(number)
                x = NpcCombatant.objects.get(display_name='NPC ' + str(number), combat=combat)
                print(x)
                number += 1
            except NpcCombatant.DoesNotExist as ex:
                break
        display_name = 'NPC ' + str(number)

    monster = Monster.objects.get(name=npc_name)
    init_roll = simulate_roll(count=1,
                              die=20,
                              mod=int((monster.dexterity-10)/2))
    max_hp = simulate_roll_from_text(monster.hp)['total']
    npcCombatant = NpcCombatant(display_name=display_name,
                                initiative=init_roll['total'],
                                max_hp=max_hp,
                                current_hp=max_hp,
                                monster=monster,
                                combat=combat)
    npcCombatant.save()


def remove_npc(request, npc_name=None):
    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    npc_combatant = NpcCombatant.objects.get(display_name=npc_name, combat=combat)
    npc_combatant.delete()

    num_combatants = len(NpcCombatant.objects.filter(combat=combat)) + len(PcCombatant.objects.filter(combat=combat))

    combat.turn = min(combat.turn, num_combatants)
    combat.save()
    return HttpResponseRedirect(reverse('setup_encounter'))


def randomize(request):
    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    total_xp = int(request.GET.get('total_xp'))
    max_cr = int(request.GET.get('max_cr'))

    if request.GET.get('clear_existing', 'False') == 'True':
        NpcCombatant.objects.all().delete()

    current_xp = sum([npc.monster.xp for npc in NpcCombatant.objects.all()])
    xp_budget = total_xp - current_xp

    selected_monsters = []
    while True:
        monster_options = Monster.objects.filter(cr__lte=max_cr, xp__lte=xp_budget).values()
        if len(monster_options) == 0:
            break

        monster_options = pd.DataFrame.from_records(monster_options)
        selected_monster = np.random.choice(monster_options.index.values, p=monster_options.xp.values/monster_options.xp.sum())
        selected_monsters.append(monster_options.name[selected_monster])
        xp_budget -= monster_options.xp[selected_monster]

    for monster_name in selected_monsters:
        _add_npc(monster_name, '', combat)

    reset_combat(combat_name)
    return HttpResponseRedirect(reverse('setup_encounter'))


def dashboard(request):
    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    pcs = [{'name': pc.display_name,
            'ac': pc.player.ac,
            'initiative': pc.initiative} for pc in PcCombatant.objects.filter(combat=combat)]
    if len(pcs) > 0:
        pcs = pd.DataFrame(pcs)
    else:
        pcs = pd.DataFrame(columns=['name', 'ac', 'initiative'])

    npcs = [{'name': npc.display_name,
             'ac': npc.monster.ac,
             'hp': npc.current_hp,
             'max hp': npc.max_hp,
             'NPC name': npc.monster.name,
             'initiative': npc.initiative} for npc in NpcCombatant.objects.filter(combat=combat)]
    if len(npcs) > 0:
        npcs = pd.DataFrame(npcs)
    else:
        npcs = pd.DataFrame(columns=['name', 'ac', 'hp', 'max hp', 'NPC name', 'initiative'])

    # make monster name links
    npcs['NPC name'] = npcs['NPC name'].apply(
        lambda x: '<a onclick="loadDescript(\'{name}\')" href="#">{name}</a>'.format(name=x))

    # combine pcs and npcs and add turn order
    all_combatants = pcs.append(npcs).sort_values('initiative', ascending=False)
    all_combatants['turn order'] = [i for i in range(1, len(all_combatants.index)+1)]
    print(all_combatants)
    print(combat.turn)

    # if there's nobody in this fight, redirect
    if len(all_combatants) == 0:
        return HttpResponseRedirect(reverse('setup_encounter'))

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

    variables['combat'] = combat_name
    return render(request, 'combat/dashboard.html', variables)


def advance(request):

    direction = int(request.GET.get('direction', 1))

    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    num_combatants = len(NpcCombatant.objects.filter(combat=combat)) + len(PcCombatant.objects.filter(combat=combat))

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
    combat_name = request.session.get('combat')
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    npc = NpcCombatant.objects.get(display_name=request.GET.get('name'), combat=combat)
    try:
        amount = int(request.GET.get('increase', -int(request.GET.get('decrease', 0))))
    except:
        amount = 0

    try:
        attack = int(request.GET.get('attack'))
        print(amount)

        if attack >= npc.monster.ac:
            if npc.discovered_ac_max is None:
                npc.discovered_ac_max = attack
            else:
                npc.discovered_ac_max = min(attack, npc.discovered_ac_max)
            npc.save()
        elif attack < npc.monster.ac:
            if npc.discovered_ac_min is None:
                npc.discovered_ac_min = attack+1
            else:
                npc.discovered_ac_min = max(attack+1, npc.discovered_ac_min)
            npc.save()
    except Exception as ex:
        raise ex
        pass

    if request.GET.get('resistance', False):
        amount = int(amount/2)

    npc.current_hp += amount
    if npc.current_hp < 0 and npc.current_hp > -npc.max_hp:
        npc.current_hp = 0
    npc.save()
    return HttpResponseRedirect(reverse('combat_dashboard'))


def reset(request):
    name = request.session.get('combat')
    return reset_combat(name)


def reset_combat(name):

    if name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=name)
    combat.turn = 1
    combat.round = 1
    combat.save()

    for npc in NpcCombatant.objects.filter(combat=combat):
        npc.current_hp = npc.max_hp
        npc.discovered_ac_min = None
        npc.discovered_ac_max = None
        npc.save()
    return HttpResponseRedirect(reverse('combat_dashboard'))


def player_view_table(request):
    print('player view table')

    combat_name = request.session.get('combat')
    print(combat_name)
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))
    combat = Combat.objects.get(name=combat_name)

    pcs = [{'name': pc.display_name,
            'initiative': pc.initiative} for pc in PcCombatant.objects.filter(combat=combat)]
    pcs = pd.DataFrame(pcs)

    npcs = [{'name': npc.display_name,
             'max ac': npc.discovered_ac_max,
             'min ac': npc.discovered_ac_min,
             'ac': npc.monster.ac,
             'hp': npc.current_hp,
             'max hp': npc.max_hp,
             'NPC name': npc.monster.name,
             'initiative': npc.initiative} for npc in NpcCombatant.objects.filter(combat=combat)]
    npcs = pd.DataFrame(npcs)

    # combine pcs and npcs and add turn order
    all_combatants = pcs.append(npcs).sort_values('initiative', ascending=False)
    all_combatants['turn order'] = [i for i in range(1, len(all_combatants.index) + 1)]

    # highlight row of current turn
    for col in ['name']:
        val = str(all_combatants.loc[all_combatants['turn order'] == combat.turn, col].values[0])
        all_combatants.loc[all_combatants[
                               'turn order'] == combat.turn, col] = """<div style="background-color: #8ab1f2;">""" + val + """</div>"""
        # all_combatants.loc[all_combatants['turn order'] == 3, col] = '<b>' + str(val) + '</b>'

    # mark rows of ko'd characters
    all_combatants[all_combatants['hp'] <= 0] = '<del>' + all_combatants[all_combatants['hp'] <= 0].astype(str) + '</del>'

    # order columns
    all_combatants = all_combatants[['name', 'min ac', 'max ac']]

    pd.set_option('display.max_colwidth', -1)
    variables = {}
    variables['table'] = all_combatants.fillna('').to_html(classes='datatable', escape=False, index=False)
    variables['round'] = combat.round
    variables['turn'] = combat.turn
    total_seconds = (combat.round - 1) * 6
    minutes = int(total_seconds / 60)
    seconds = format(total_seconds % 60, '02d')
    variables['time'] = '{min}:{sec}'.format(min=minutes, sec=seconds)

    return render(request, 'combat/player_view_table.html', variables)


def player_view(request):
    print('player view')

    combat_name = request.session.get('combat')
    print(combat_name)
    if combat_name is None:
        return HttpResponseRedirect(reverse('combat_list'))

    variables = {'combat': combat_name}
    return render(request, 'combat/player_view.html', variables)


def browse(request):

    combats = Combat.objects.all()
    table = []
    for combat in combats:
        pcs = ', '.join([pc.display_name for pc in PcCombatant.objects.filter(combat=combat)])
        npcs = ', '.join([npc.monster.name for npc in NpcCombatant.objects.filter(combat=combat)])
        table.append({'name': combat.name,
                      'PCs': pcs,
                      'NPCs': npcs})
    if len(table) > 0:
        table = pd.DataFrame(table).sort_values('name')
        table = table[['name', 'PCs', 'NPCs']]
    else:
        table = pd.DataFrame(columns=['name', 'PCs', 'NPCs'])

    # add a 'select' link for each
    table['actions'] = '<input type="button" onclick="location.href=\'set_combat/' + table['name'] + '\';" value="set active" />' + \
                       ' <input type="button" onclick="location.href=\'delete_combat/' + table['name'] + '\';" value="delete" />'

    pd.set_option('display.max_colwidth', -1)
    variables = {'table': table.fillna('').to_html(classes='datatable', escape=False, index=False)}

    current_combat = request.session.get('combat', None)
    variables['combat'] = current_combat
    return render(request, 'combat/browse.html', variables)


def set_active_combat(request, name):

    request.session['combat'] = name
    return HttpResponseRedirect(reverse('combat_list'))


def create_combat(request):
    c = Combat(name=request.GET['name'])
    c.save()
    request.session['combat'] = c.name
    return HttpResponseRedirect(reverse('combat_list'))


def delete_combat(request, name):
    c = Combat.objects.get(name=name)
    c.delete()

    if request.session.get('combat') == name:
        request.session['combat'] = None

    return HttpResponseRedirect(reverse('combat_list'))

