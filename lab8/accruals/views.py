from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from decimal import Decimal, InvalidOperation #инвалид - распознание числа как неподходящего числа (если вообще числа)


def homepage(request):
    accruals = Accrual.objects.all()
    return render(request, 'accrual.html', {'accruals': accruals})


def add_accrual(request):
    if request.method == 'POST':
        emp_num = request.POST.get('employee_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        payment_str = request.POST.get('payment', '').strip()

        #проверка на число начисления
        try:
            payment = Decimal(payment_str)
            if payment <= 0:
                return JsonResponse({'success': False, 'error': 'Сумма начисления должна быть больше нуля.'},
                                    status=400)
        except (InvalidOperation, ValueError): #если не число
            return JsonResponse({'success': False, 'error': 'Введено некорректное число в поле начисления.'},
                                status=400)

        #Ищем, существует ли уже этот номер с другим именем
        mismatch_name = Accrual.objects.filter(employee_id=emp_num).exclude(full_name=full_name).exists()
        #Ищем, существует ли это имя с другим номером
        mismatch_num = Accrual.objects.filter(full_name=full_name).exclude(employee_id=emp_num).exists()
        if mismatch_name or mismatch_num:
            return JsonResponse({
                'success': False,
                'error': 'Номер не соответствует сотруднику.'
            }, status=400)
        new_accrual = Accrual.objects.create(employee_id=emp_num, full_name=full_name, payment=payment)

        return JsonResponse({
            'success': True,
            'data': {
                'employee_id': new_accrual.employee_id,
                'full_name': new_accrual.full_name,
                'payment': f"{new_accrual.payment:.2f}"
            }
        })

    return JsonResponse({'success': False, 'error': 'Неверный метод запроса.'}, status=405)