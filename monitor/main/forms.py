from django.forms import ModelForm, TextInput
from .models import SarData, Host


class LogForm(ModelForm):
    class Meta:
        model = SarData
        fields = ['log_time']

        widgets = {
            'log_time': TextInput(attrs={
                'class': 'form-control form-custom',
                'placeholder': 'дата дд.мм.гггг'})
        }


class HostForm(ModelForm):
    class Meta:
        model = Host
        fields = ['host']

        widgets = {
            'host': TextInput(attrs={
                'class': 'form-control form-custom',
                'placeholder': 'Введите имя сервера'})
        }
