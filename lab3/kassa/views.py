import json
from django.shortcuts import render
from django.http import HttpResponse

def homepage(request):
    return render(request, 'homepage.html')
def create_data(request):
    return render(request, 'create.html')

def process_data(request):
    results = None
    # начинается обработка, открывается файл
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        data = [json.loads(line) for line in file]

        # вычисление сумм по группам, массив полученных чисел отправляется в эксель
        group_sums = {}
        for item in data:
            g = str(item['group'])
            total = item['qty'] * item['sale'] * (1 - item['discount']/100)
            group_sums[g] = group_sums.get(g, 0) + total # интересный способ задать дефолт значение члена массива
        results = group_sums
    return render(request, 'process.html', {'results': results})