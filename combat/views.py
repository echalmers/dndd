from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import PcCombatant, NpcCombatant
from players.models import Player
from monsters.models import Monster
import pandas as pd
from util import df_to_text
from roller.views import simulate_roll_from_text


def main(request):

    return render(request, 'combat/setup.html',)


def setup(request):

    # get table of pc characters
    pcs = PcCombatant.objects.all()
    if len(pcs) > 0:
        pcs = [{'name': pc.display_name,
                'ac': pc.player.ac,
                'level': pc.player.level,}
               for pc in pcs]
        pc_df = pd.DataFrame(pcs)
        pc_df = pc_df[['name', 'ac', 'level']]
    else:
        pc_df = pd.DataFrame(columns=['name', 'ac', 'level'])

    pc_df['actions'] = '<a href="remove_pc/' + pc_df['name'] \
                       + '">delete</a>'

    variables = df_to_text(pc_df, prefix='pcs')

    # populate drop-down with list of remaining pcs
    all_pcs = ['<option value="{}">'.format(player.name)
               for player in Player.objects.all() if player.name not in pc_df.name.values]
    variables['pc_options'] = ''.join(all_pcs)

    # get table of npc characters
    npcs = NpcCombatant.objects.all()
    if len(npcs) > 0:
        npcs = [{'display name': npc.display_name,
                 'NPC name': npc.monster.name,
                 'hp': simulate_roll_from_text(npc.monster.hp)['total'],
                 'cr': npc.monster.cr,
                 'xp': npc.monster.xp}
                for npc in npcs]
        npcs = pd.DataFrame(npcs)
        npcs = npcs[['display name','NPC name','hp','cr','xp']]
    else:
        npcs = pd.DataFrame(columns=['display name','NPC name','hp','cr','xp'])

    npcs['actions'] = '<a href="remove_npc/' + npcs['display name'] \
                       + '">delete</a>'

    variables.update(df_to_text(npcs, prefix='npcs'))

    # calculate some summary stats of the encounter
    variables['totalxp'] = npcs.xp.sum() if len(npcs.index) > 0 else 0
    variables['maxcr'] = npcs.cr.max() if len(npcs.index) > 0 else '-'
    if variables['maxcr'] != '-' and variables['maxcr'] > pc_df.level.max():
        variables['maxcr'] = str(variables['maxcr']) + ' (players are outclassed)'

    from combat.xp_table import xp_table
    from io import StringIO
    ratings = pd.DataFrame.from_csv(StringIO(xp_table), index_col=None)
    # print(ratings)
    xp_ref = {
        difficulty: sum([ratings.loc[ratings.Level==l, difficulty].values[0] for l in pc_df.level.values])
        for difficulty in ['Easy', 'Moderate', 'Challenging', 'Hard']
    }
    xp_dif = pd.Series(xp_ref)
    xp_dif = (xp_dif - variables['totalxp']).abs()

    variables['difficulty'] = xp_dif.idxmin
    variables['maxxp'] = xp_ref['Hard']

    variables['easy_xp'] = xp_ref['Easy']
    variables['moderate_xp'] = xp_ref['Moderate']
    variables['challenging_xp'] = xp_ref['Challenging']
    variables['hard_xp'] = xp_ref['Hard']

    # populate drop-down with list of npcs
    all_npcs = ['<option value="{}">'.format(monster.name)
               for monster in Monster.objects.all()]
    variables['npc_options'] = ''.join(all_npcs)

    return render(request, 'combat/setup.html', variables)


def add_pc(request):

    pc_name = request.GET.get('pc')
    print(pc_name)
    player = Player.objects.get(name=pc_name)

    pc_combatant = PcCombatant(display_name=player.name,
                               player=player)
    pc_combatant.save()
    return HttpResponseRedirect(reverse('setup_encounter'))


def remove_pc(request, pc_name=None):

    print(pc_name)
    pc_combatant = PcCombatant.objects.get(display_name=pc_name)
    pc_combatant.delete()
    return HttpResponseRedirect(reverse('setup_encounter'))


def add_npc(request):
    npc_name = request.GET.get('npc')
    display_name = request.GET.get('display_name')
    if display_name == '':
        number = 0
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
    npcCombatant = NpcCombatant(display_name=display_name, monster=monster)
    print(npcCombatant.display_name)
    npcCombatant.save()
    return HttpResponseRedirect(reverse('setup_encounter'))


def remove_npc(request, npc_name=None):
    npc_combatant = NpcCombatant.objects.get(display_name=npc_name)
    npc_combatant.delete()
    return HttpResponseRedirect(reverse('setup_encounter'))