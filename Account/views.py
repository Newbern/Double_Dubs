
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from Account.form import *
from Account.models import *
import json
import Double_Dubs.settings as settings
from django.http import JsonResponse, HttpResponse
import requests
from square.client import Client
from uuid import uuid1 as uuid

client = Client(access_token=settings.SQUARE_ACCESS_TOKEN, environment=settings.SQUARE_ENVIRONMENT)


# Checking Customer api
def squareup_customer(request):
    account = Account.objects.filter(username=request.user).first()
    user = User.objects.filter(username=request.user).first()

    # Just Getting Customer ID
    customer = Payment_method.objects.filter(username=request.user).first()

    # Checking to See if Customer exist
    if customer is not None:
        print("Retrieving Data....")
        result = client.customers.update_customer(
            customer_id=customer.customer_id,
            body={
                "company_name": "Double Dubs",
                "email_address": user.email,
                "family_name": user.last_name,
                "given_name": user.first_name,
                "phone_number": f"{account.phone}",
                "address": {
                    "address_line_1": account.address
                }


            }
        )

        if result.is_success():
            print(result.body)
            return customer.customer_id
        elif result.is_error():
            print(result.errors)
            customer.delete()
            squareup_customer(request)

    # If Not Creating Customer
    else:
        print("Creating Customer....")
        result = client.customers.create_customer(
            body={
                "idempotency_key": uuid,
                "company_name": "Double Dubs",
                "email_address": user.email,
                "family_name": user.last_name,
                "given_name": user.first_name,
                "phone_number": f"{account.phone}",
                "address": {
                    "address_line_1": account.address
                }


            }
        )

        if result.is_success():
            print(result.body)
            # Getting Square up Customer Id
            customer_id = result.body["customer"]["id"]

            # Creating New Payment Method, This is just a blank where we can just pull the customer id
            Payment_method.objects.create(username=request.user, customer_id=customer_id).save()


        elif result.is_error():
            print(result.errors)


# Redirects Straight to My_Account
def account(request):
    squareup_customer(request)
    return redirect('my_account')


# My Account
def my_account(request):
    squareup_customer(request)

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


# Getting Card Payment Methods
def payment_method(request):
    # Getting Account
    account = Account.objects.filter(username=request.user).first()

    # Getting All Payment_Method Cards
    lst = Payment_method.objects.filter(username=request.user)

    # Deleting Card then Redirecting Back
    if request.method == "POST":

        # If Delete Button was hit
        if request.POST.get("submit-btn") == "Delete":
            delete_card(request)

        # Setting as Payment Card
        elif request.POST.get("submit-btn") == "Set":
            # Saving as Payment Method
            account.payment_method = request.POST.get("card-list")
            account.save()

    return render(
        request, 'Account/Payment_Method.html', {
            'lst': lst,
            "option_selected": account.payment_method,
            "id_name": 'payment_method',
            "name": 'Payment Method'}
    )


# Adding Card to Squareup api
@csrf_exempt
def add_card(request):

    # Getting Car Nonce
    if request.method == "POST":
        # Updating Customer First
        squareup_customer(request)

        # Getting Card nonce
        card_nonce = json.loads(request.body)["nonce"]

        # Creating Card
        result = client.cards.create_card(
            body={
                "idempotency_key": str(uuid),
                "source_id": card_nonce,
                "card": {
                    "customer_id": squareup_customer(request),
                },
                "verification_token": None
            }
        )

        if result.is_success():
            print(result.body)
            # Getting Last_4 Digits and Card Id
            card = result.body['card']

            # Creating Card to Payment_method
            customer = Payment_method.objects.create(
                username=request.user,
                customer_id=squareup_customer(request),
                card_id=card['id'],
                last_4=card['last_4']
            )

            # Saving New Card
            customer.save()

        elif result.is_error():
            print(result.errors)

        return redirect('payment_method')

    elif request.method == "GET":
        return render(request, 'Account/Web Payment SDK.html', {})


# Deleting Card
def delete_card(request):

    if request.method == "POST":
        # Getting Card-list Value
        last_4 = request.POST.get("card-list")
        print(last_4)

        # Making Sure this isn't the primary customer id Payment Method
        if last_4 is not None:

            # Getting Specific Customer with Card Nonce
            customer = Payment_method.objects.filter(username=request.user, last_4=last_4).first()

            # Checking to see if customer exist
            if customer is not None:
                # Deleting Card
                result = client.customers.delete_customer_card(customer.customer_id, customer.card_id)

                if result.is_success():
                    print(result.body)
                    customer.delete()
                elif result.is_error():
                    print(result.errors)

    # Returning Back to Payment_Method Page
    return redirect('payment_method')


# Payment Request
@csrf_exempt
def payment_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(data['sourceId'], data['verificationToken'])

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
    # Getting all the Users Orders
    customer_id = Payment_method.objects.filter(username=request.user).first().customer_id

    lst = reversed([item for item in Order.objects.filter(customer_id=customer_id)])


    return render(request, 'Account/History.html', {"id_name": 'history',"name": 'History', 'lst': lst})

