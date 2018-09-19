from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import PcCombatant
from players.models import Player


def main(request):

    return render(request, 'combat/setup.html',)


def setup(request):

    pcs = PcCombatant.objects.all()
    pcs = [{'name': pc.display_name,
            'ac': pc.player.ac,
            'level': pc.player.level,}
           for pc in pcs]

    import json
    variables = {'data': json.dumps(pcs)}

    all_pcs = ['<option value="{}">'.format(player.name) for player in Player.objects.all()]
    variables['pc_options'] = ''.join(all_pcs)

    return render(request, 'combat/setup.html', variables)


def add_pc(request):

    pc_name = request.GET.get('pc')
    print(pc_name)
    player = Player.objects.get(name=pc_name)

    pc_combatant = PcCombatant(display_name=player.name,
                               player=player)
    pc_combatant.save()
    return HttpResponseRedirect(reverse('setup_encounter'))