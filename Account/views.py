
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from Account.form import *
import json
import Double_Dubs.settings as settings
from django.http import JsonResponse, HttpResponse
import requests


# Redirects Straight to My_Account
def account(request):
    return redirect('my_account')

# My Account
def my_account(request):
    # Getting Account Data
    account = Account.objects.get(username=request.user)

    if request.method == "GET":
        # Getting to Show current data on Form
        form = AccountForm(instance=request.user)
        phone_form = AccountPhoneForm(instance=account)

    elif request.method == "POST":
        # Retrieving data from form
        form = AccountForm(request.POST, instance=request.user)
        phone_form = AccountPhoneForm(request.POST, instance=account)

        # Checking to see if data is in correctly
        if form.is_valid() and phone_form.is_valid():
            form.save()
            phone_form.save()

    else:
        form = AccountForm()
        phone_form = AccountPhoneForm()

    # Loading Address Form
    return render(request, 'Account/base.html', {"form": form, 'form2': phone_form, "id_name": 'my-account', "name":'My Account'})


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
    else:
        form = AddressForm()

    # Loading Address Form
    return render(request, 'Account/base.html', {"form": form, "id_name": 'address', "name":'Address'})

def payment_method(request):
    # Getting Account data
    account = Account.objects.get(username=request.user)

    if request.method == "GET":
        # Getting to Show current data on Form
        form = PaymentForm(instance=account)

    elif request.method == "POST":
        # Retrieving data from form
        form = PaymentForm(request.POST, instance=account)

        # Checking to see if data is in correctly
        if form.is_valid():
            form.save()
    else:
        form = PaymentForm()

    return render(request, 'Account/base.html', {"id_name": 'payment-method', "name":'Payment Method', 'form': form})


# Payment Request
@csrf_exempt
def payment_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))

            headers = {
                "Square-Version": "2023-12-13",
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {settings.SQUARE_ACCESS_TOKEN}',
            }
            payload = {
                "source_id": data["sourceId"],
                "verification_id": data["verificationToken"],
                "idempotency_key": data["idempotencyKey"],
                "amount_money": {
                    "amount": 100,
                    "currency": 'USD'
                },
            }

            response = requests.post(settings.SQUARE_API_URL, json=payload, headers=headers)

            return JsonResponse(response.json(), status=response.status_code)

        except Exception as e:

            return JsonResponse({"error": str(e)}, status=400)


def history(request):
    return render(request, 'Account/Web Payment SDK.html',{}) #{"id_name": 'history', "name":'History'})

