from django.forms import ModelForm 
from django import forms

class text_form(forms.Form):
    txt = forms.CharField(label='Your text', max_length=100)


