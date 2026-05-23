from django.shortcuts import render, redirect
from django.contrib import messages #для системы оповещения в форме создания/редактирования пользователя
from django.core.cache import cache #для работы системы кэширования паролей, логинов; для блокировки после 5 попыток неправильной авторизации
from .models import Employee
from .forms import EmployeeForm
from django.views.decorators.cache import never_cache #для того, чтобы после выхода из профиля нельзя было через пред. страницу вернуться на него без авторизации

#функция отображения авторизации
def login(request):
    error = None #сообщение об ошибке
    #действие при нажатии кнопки "Войти"
    if request.method == 'POST':
        login_val = request.POST.get('login')
        pass_val = request.POST.get('password')

        attempts_key = f"att_{login_val}" #количество неправильных попыток входа
        lock_key = f"lock_{login_val}" #показатель, заблокирован вход или нет

        if cache.get(lock_key):
            error = "Доступ заблокирован на 5 минут из-за частых неудачных попыток авторизации."
            return render(request, 'login.html', {'error': error})

        # try/catch удобен для реализации обнаружения неудачной попыткы авторизации
        try:
            user = Employee.objects.get(login=login_val)

            is_auth = False
            if user.role == 'guest':
                is_auth = True  # Гость без пароля
            elif user.password == pass_val:
                is_auth = True  # Остальные с паролем

            if is_auth: #если смог правильно авторизоваться
                cache.delete(attempts_key) #количество неудачных попыток сброшено
                #введение данных о текущем пользователе
                request.session['user_id'] = user.id
                request.session['role'] = user.role
                request.session['login'] = login_val
                return redirect('employee_list')
            else:
                raise Employee.DoesNotExist

        #неудачная попытка авторизации
        except Employee.DoesNotExist:
            attempts = cache.get(attempts_key, 0) + 1 #изначально попыток неудачных 0, прибавляется по одной
            cache.set(attempts_key, attempts) #занесение в кэш инфы о попытках
            if attempts == 5: #после 5 попыток таймаут на 5 минут
                cache.set(lock_key, True, 300)
                error = "Неверный логин или пароль. Слишком много неудачных попыток, вход заблокирован на 5 минут."
            else: #если попыток меньше, чем 5, просто уведомление
                error = "Неверный логин или пароль. Попытайтесь еще раз."

    return render(request, 'login.html', {'error': error})

#функция отображения выхода на страницу авторизации
def logout(request):
    request.session.flush() #сброс данных о пользователе при выходе
    return redirect('login') #на страницу авторизации


@never_cache # защита от входа в профиль через заход на пред. страницу из браузера реализована здесь
# функция отображения списка сотрудников
def employee_list(request):
    user_id = request.session.get('user_id') #id вошедшего пользователя
    current_user = Employee.objects.get(id=user_id) #вошедший
    employees = Employee.objects.all() #все сотрудники (содержимое списка)

    form = EmployeeForm(current_user=current_user) #форма создана заранее, использует вошедший пользователь

    return render(request, 'list.html', {
        'employees': employees,
        'current_user': current_user,
        'form': form
    })

#функция отображения окна создания нового пользователя
def create_employee(request):
    user_id = request.session.get('user_id')
    current_user = Employee.objects.get(id=user_id)

    #действие при нажатии кнопки "Сохранить"
    if request.method == 'POST':
        form = EmployeeForm(request.POST, current_user=current_user)
        #необязательно использовать messages, так интуитивно понятнее
        if form.is_valid(): #правильно ли введены данные для создания данных о новом сотруднике
            form.save()
            messages.success(request, "Сотрудник успешно создан.")
        else:
            messages.error(request, "Ошибка создания: проверьте, правильно ли введены данные.")
    return redirect('employee_list') #закрытие окна и возвращение к списку

#функция отображения окна изменения существующего пользователя
def edit_employee(request, emp_id):
    user_id = request.session.get('user_id')
    current_user = Employee.objects.get(id=user_id)
    employee = Employee.objects.get(id=emp_id) #редактируемый сотрудник из списка

    # действие при нажатии кнопки "Сохранить"
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee, current_user=current_user)
        if form.is_valid(): #правильно ли введены данные для редактирования данных о сотруднике
            form.save()
            messages.success(request, "Данные обновлены.")
        else:
            messages.error(request, "Ошибка создания: проверьте, правильно ли введены данные.")
    return redirect('employee_list')

#функция отображения удаления профиля
def delete_employee(request, emp_id):
    if request.session.get('role') == 'dir': #удалять может только директор
        employee = Employee.objects.get(id=emp_id)
        employee.delete()
        messages.success(request, "Сотрудник удален.")
    return redirect('employee_list')