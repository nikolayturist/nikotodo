from django.forms import ModelForm
from .models import Todo
from django import forms


class TodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date', 'completed_date', 'importance']
        due_date = forms.DateField(
            widget=forms.DateInput(format='%m/%d/%Y'),
            input_formats=('%m/%d/%Y',)
        )