from django.contrib.admin.forms import AdminAuthenticationForm
from django import forms


class QorgoAdminAuthenticationForm(AdminAuthenticationForm):
    username = forms.CharField(label='Логин администратора или телефон', widget=forms.TextInput(attrs={'autofocus': True}))
