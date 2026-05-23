from django import forms
from .models import Employee

#форма для заполнения данных сотрудника (создание нового пользователя или редактирование существующего)
class EmployeeForm(forms.ModelForm):
    class Meta: #член-класс класса ModelForm. Задает базовые члены класса, удобные для создания формы в данном случае
        model = Employee #модель, на которой основывается форма
        fields = ['last_name', 'first_name', 'middle_name', 'login', 'password', 'role', 'address', 'work_phone', 'personal_phone']
        widgets = { #заполняется отдельно, т.к. пароль должен быть скрыт при наборе
            'password': forms.PasswordInput(render_value=True),
        }

    #новый конструктор
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs) #перегрузка конструктора класса EmployeeForm

        #проверка на то, редактирует ли пользователь свои же данные
        if self.instance and self.instance.pk == self.current_user.id:
            if 'role' in self.fields:
                del self.fields['role'] #удаляется поле должностей для заполнения
        # проверка на то, какая должность у редактирующего данные пользователей
        else:
            all_choices = Employee.ROLE_CHOICES
            if self.current_user.role == 'undir': #редактирует зам. директора
                filtered = [c for c in all_choices if c[0] not in ['dir', 'undir']] #не может создать зам.директора и директоров
            elif self.current_user.role == 'dir': #редактирует директор
                filtered = [c for c in all_choices if c[0] not in ['dir']] #не может создать директоров
            else:
                filtered = all_choices #опция для возможной должности, умеющая создавать и директоров (для масштабирования)
            self.fields['role'].choices = filtered #утверждение отфильтрованного списка должностей

    #запрос на роль
    def clean_role(self):
        if self.instance and self.instance.pk == self.current_user.id:
            return self.instance.role
        return self.cleaned_data.get('role')

