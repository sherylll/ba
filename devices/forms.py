from django import forms

class NameForm(forms.Form):
    device_name = forms.CharField(label='Device name', max_length=100)
    
class TypeForm(forms.Form):
    CHOICES = (('1', 'LED',), ('2', 'Switch',))
    choice_field = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
