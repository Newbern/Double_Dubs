from django import forms
from main.models import Sauce


class NewSauceForm(forms.ModelForm):
    class Meta:
        model = Sauce
        fields = ['name', 'image', 'price', 'instock', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'update'}),
            'image': forms.FileInput(attrs={'class': 'update'}),
            'price': forms.NumberInput(attrs={'class': 'update'}),
            'instock': forms.NumberInput(attrs={'class': 'update'}),
            'description': forms.Textarea(attrs={'class': 'update'})
        }
