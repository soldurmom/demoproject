from django import forms
from django.core.validators import RegexValidator

from demo.models import User


class RegisterUserForm(forms.ModelForm):
    username = forms.CharField(label='Логин',
                               validators=[
                                   RegexValidator('^[a-zA-Z0-9-]+$', message='Только латиница, цифра или тире')],
                               error_messages={
                                   'required': 'Обязательное поле',
                                   'unique': 'Данный логин занят'
                               })
    email = forms.EmailField(label='Email',
                             error_messages={
                                 'invalid': 'Не правильный формат адреса',
                                 'unique': 'Данный адрес занят'
                             })
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput,
                               error_messages={
                                   'required': 'Обязательное поле',
                               })
    password2 = forms.CharField(required=True, label='Пароль(повторно)',
                                widget=forms.PasswordInput,
                                error_messages={
                                    'required': 'Обязательное поле',
                                })
    name = forms.CharField(label='Имя',
                           validators=[RegexValidator('^[а-яА-Я- ]+$', message='Только кирилица, пробел или тире')],
                           error_messages={
                               'required': 'Обязательное поле',
                           })
    surname = forms.CharField(label='Фамилия',
                              validators=[RegexValidator('^[а-яА-Я- ]+$', message='Только кирилица, пробел или тире')],
                              error_messages={
                                  'required': 'Обязательное поле',
                              })
    patronomic = forms.CharField(label='Отчество',
                                 validators=[
                                     RegexValidator('^[а-яА-Я- ]+$', message='Только кирилица, пробел или тире')])
    rules = forms.BooleanField(required=True, label='Согласие с правилами', initial=True)

    def clean(self):
        super().clean()
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise ValueError({'password2': ValueError('Пароли не совпадают', code='password_mimatch')})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2',
                  'name', 'surname', 'patronomic', 'rules')


class OrderForm(forms.ModelForm):
    def clean(self):
        status = self.cleaned_data.get('status')
        refuse_reason = self.cleaned_data.get('refuse_reason')
        if self.instance.status != 'new':
            raise forms.ValidationError({'status':'Статус можно сменить только у новых заказов'})
        if status == 'canceled' and not refuse_reason:
            raise forms.ValidationError({'refuse_reason':'При отказе нужно указать причину'})
