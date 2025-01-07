from django import forms
from django.contrib.auth.models import User
from main.models import Account, Sauce


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


class AccountUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Name'}),
            'last_name': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'update', 'placeholder': 'Email'}),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['phone', 'address', 'city', 'state', 'zip']
        widgets = {
            'phone': forms.NumberInput(attrs={'class': 'update', 'placeholder': 'Phone number'}),
            'address': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Address line'}),
            'city': forms.TextInput(attrs={'class': 'update', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'update', 'placeholder': 'State'}),
            'zip': forms.NumberInput(attrs={'class': 'update', 'placeholder': 'Zip code'}),
        }

