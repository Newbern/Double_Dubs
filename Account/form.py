from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.models import User
from main.models import Account
from Account.models import Payment_method

# User data
class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Name'}),
            'last_name': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'update', 'placeholder': 'Email'}),
        }

class AccountPhoneForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['phone']
        widgets = {
            'phone': forms.NumberInput(attrs={'class': 'update', 'placeholder': 'Phone number'}),
        }

# Account Data
class AddressForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['address', 'city', 'state', 'zip']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Address line'}),
            'city': forms.TextInput(attrs={'class': 'update', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'update', 'placeholder': 'State'}),
            'zip': forms.NumberInput(attrs={'class': 'update', 'placeholder': 'Zip code'}),
        }


# Payment Method Data
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment_method
        fields = ["customer_id", "cardholder_name", "expiration_month", "expiration_year"]
        widgets = {
            'customer_id': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Customer ID'}),
            'cardholder_name': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Cardholder Name'}),
            'expiration_month': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Month'}),
            'expiration_year': forms.TextInput(attrs={'class': 'update', 'placeholder': 'Year'}),
        }