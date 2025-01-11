
from django.shortcuts import render, redirect
from Account.form import *


# Redirects Straight to My_Account
def account(request):
    return redirect('my_account')


# My Account
def my_account(request):
    if request.method == "GET":
        # Getting to Show current data on Form
        form = AccountForm(instance=request.user)

    elif request.method == "POST":
        # Retrieving data from form
        form = AccountForm(request.POST, instance=request.user)

        # Checking to see if data is in correctly
        if form.is_valid():
            form.save()

    # Loading Address Form
    return render(request, 'Account/My_Account.html', {"form": form})


# Address
def address(request):
    # Getting Account data
    account = Account.objects.get(username=request.user)

    if request.method == "GET":
        # Getting to Show current data on Form
        form = AddressForm(instance=account)

    elif request.method == "POST":
        # Retrieving data from form
        form = AddressForm(request.POST, instance=account)

        # Checking to see if data is in correctly
        if form.is_valid():
            form.save()

    # Loading Address Form
    return render(request, 'Account/Address.html', {"form": form})

def payment_method(request):
    return render(request, 'Account/Payment_Method.html', {})

def history(request):
    return render(request, 'Account/History.html', {})

