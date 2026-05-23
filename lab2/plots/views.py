import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64, numpy as np
from django.shortcuts import render
from .models import *
from .forms import *


def monitor_view(request):
    input_form = DataForm()
    filter_form = FilterForm(request.GET)
    error_msg = None
    play_audio = False

    if request.method == 'POST':
        input_form = DataForm(request.POST)
        if input_form.is_valid():
            new_val = input_form.cleaned_data['value']
            last_entry = Parameter.objects.first()

            #обработка ошибок/предупреждений
            if last_entry:
                prev_val = last_entry.value
                if abs(new_val - prev_val) > abs(prev_val * 0.25):
                    error_msg = f"Внимание: отклонение более, чем на 25%! (Предыдущее значение: {prev_val})"
                f_min = request.GET.get('min_val')
                f_max = request.GET.get('max_val')
                if (f_min and new_val < float(f_min)) or (f_max and new_val > float(f_max)):
                    error_msg = "Ошибка: параметр вышел за границы!"
                    play_audio = True
            Parameter.objects.create(value=new_val)

    #последние 10 значений
    last_10_qs = Parameter.objects.all()[:10]
    #выборка
    filtered_list = list(last_10_qs)
    if filter_form.is_valid():
        cd = filter_form.cleaned_data
        if cd['min_val'] is not None:
            filtered_list = [p for p in filtered_list if p.value >= cd['min_val']]
        if cd['max_val'] is not None:
            filtered_list = [p for p in filtered_list if p.value <= cd['max_val']]
        if cd['divisor'] and cd['divisor'] != 0:
            filtered_list = [p for p in filtered_list if p.value % cd['divisor'] == 0]

    filtered_list.reverse() #иначе в обратном порядке данные будут считываться
    values = [p.value for p in filtered_list]
    indices = range(len(values))
    chart_line = None
    chart_bar = None

    if values:
        #график
        fig_line = plt.figure(figsize=(7, 4))
        ax1 = fig_line.add_subplot(111)
        ax1.plot(values, 'b-o', label='Значение')
        for i, v in enumerate(values):
            ax1.text(i, v + (max(values) * 0.02), str(v), ha='center', fontweight='bold')
        #средняя линия
        avg = np.mean(values)
        ax1.axhline(y=avg, color='r', linestyle='--', label=f'Среднее: {avg:.2f}')
        ax1.set_xticks([])
        ax1.legend()
        fig_line.tight_layout()

        #диаграмма
        fig_bar = plt.figure(figsize=(7, 4))
        ax2 = fig_bar.add_subplot(111)
        bars = ax2.bar(indices, values, color='skyblue', edgecolor='navy')
        for bar in bars:
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2, yval, str(yval), va='bottom', ha='center')
        ax2.set_xticks([])
        ax2.set_title("Диаграмма последних 10 значений")
        fig_bar.tight_layout()

        def fig_to_base64(fig):
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            return base64.b64encode(buf.getvalue()).decode()
        chart_line = fig_to_base64(fig_line)
        chart_bar = fig_to_base64(fig_bar)

    return render(request, 'monitor.html', {
        'input_form': input_form, 'filter_form': filter_form,
        'last_10': last_10_qs, 'chart_line': chart_line, 'chart_bar': chart_bar,
        'error_msg': error_msg, 'play_audio': play_audio
    })