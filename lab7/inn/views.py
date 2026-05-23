from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from .models import Contragent
from .forms import ContragentForm

def agent_list(request):
    agents = Contragent.objects.all()
    duplicate_inns = Contragent.objects.values('inn').annotate(inn_count=Count('inn')).filter(inn_count__gt=1,
                                                                                         inn__isnull=False).values_list(
        'inn', flat=True)

    context = {
        'agents': agents,
        'duplicate_inns': list(duplicate_inns),
        'form': ContragentForm()
    }
    return render(request, 'index.html', context)


def check_inn(request):
    inn = request.GET.get('inn', None)
    if not inn:
        return JsonResponse({'results': []})

    # Точное совпадение
    exact = Contragent.objects.filter(inn=inn)
    # Частичное совпадение
    partial = Contragent.objects.filter(inn__contains=inn).exclude(inn=inn)

    data = {
        'exact': list(exact.values('short_name', 'inn')),
        'partial': list(partial.values('short_name', 'inn'))
    }
    return JsonResponse(data)


def create_agent(request):
    if request.method == 'POST':
        form = ContragentForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('agent_list')


def delete_agent(request, pk):
    agent = get_object_or_404(Contragent, pk=pk)
    agent.delete()
    return redirect('agent_list')
