from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from main.models import *
from main.form import AccountForm, AccountUserForm, NewSauceForm
from Double_Dubs import settings
import json


# Sauce Items/Menu
def menu(request):
    menu = Sauce.objects.all()

    if request.method == 'GET':
        # Checking to See if a Sauce was Selected
        if request.GET.get('item'):

            # Getting Selected Sauce
            item = request.GET.get('item')
            menu = Sauce.objects.filter(name=item).first()

            # Getting User Data
            if request.user.is_authenticated:
                user = Account.objects.filter(username=request.user).first()
            else:

                # Loading Fake Specs Sauce Item
                return render(request, 'main/Sauce.html', {'user': None, 'amount': 0, 'sauce': menu})


            # Getting the amount from Users cart
            for item in user.cart:
                # Checking if users cart has this sauce in it cart
                if item == menu.name:
                    # Getting quantity
                    amount = user.cart[item]
                    break
            else:
                amount = 0

            # Loading Specs Sauce Item
            return render(request, 'main/Sauce.html', {'user': user, 'amount': amount, 'sauce': menu})

        else:
            # Loading Menu
            return render(request, 'main/Menu.html', {'sauces': menu})

    elif request.method == 'POST':
        # Getting Sauce & Quantity amount
        amount = request.POST.get('quantity')
        sauce = request.POST.get('sauce')

        # User
        # Making Sure Sign-in Before Processing Order
        if request.user.is_authenticated:
            info = Account.objects.filter(username=request.user).first()
        else:
            return redirect('login')
        # Users New Sauce Item
        new_cart = {f'{sauce}': int(amount)}
        # Users Cart with New Sauce Item to be Updated
        info.cart.update(new_cart)
        info.save()
        print(sauce, amount)

        # Going back to Menu
        return redirect("home")


# Account
def account(request):
    if request.method == 'GET':
        # Getting Account Info
        form1 = AccountUserForm(instance=request.user)
        form2 = AccountForm(instance=Account.objects.get(username=request.user))

    elif request.method == 'POST':
        # Getting Account
        account = Account.objects.get(username=request.user)

        # Retrieving data from forms
        form1 = AccountUserForm(request.POST, instance=request.user)
        form2 = AccountForm(request.POST, instance=account)

        # Checking to see if data is in correctly
        if form1.is_valid() and form2.is_valid():
            # Saving data
            form1.save()
            form2.save()

        # Returning to Home Page
        return redirect('home')


    return render(request, 'main/Account.html', {'form1': form1, 'form2': form2})


# Cart
def cart(request):
    # Loading Cart data
    if request.method == 'GET':
        # Getting Users cart
        # Making Sure Sign-in Before Processing Order
        if request.user.is_authenticated:
            info = Account.objects.filter(username=request.user).first()
        else:
            return redirect('login')

        cart = info.cart

        # Checking to see if empty Sauces in Cart
        for sauce in list(cart):
            # If Quantity of sauce is 0
            if int(cart[sauce]) == 0:
                cart.pop(sauce)

        # Saving Users Cart in database
        info.save()

        # Sauce cart List
        lst = []
        # Going Through Users Cart
        for sauce in list(cart):
            # Going Through Sauce Items
            for sauce_item in Sauce.objects.all():
                # Checking to see if Users Sauce matches the Sauce Item
                if sauce_item.name == sauce:
                    # Adding  Sauce to Cart
                    lst.append((sauce_item, cart[sauce]))

        # Loading Cart
        return render(request, 'main/Cart.html', {'cart': lst})

    # Posting Cart data
    elif request.method == 'POST':
        # Getting Cart Data
        cart = json.loads(request.POST.get('cart'))
        total = request.POST.get('real_total')

        # Updating Database
        info = Account.objects.filter(username=request.user).first()
        info.cart.update(cart)
        info.save()

        # Factory Shopping Message
        message = ""
        for sauce in cart:
            message += f"{sauce}: {cart[sauce]}\n"
        message += f"---------------------\nTotal: {total}\n"

        # Getting User
        user = User.objects.filter(username=request.user).first()

        # Getting Email Address from Account
        if user.email is not None:

            # Checking to see if First and Last Name is Used
            if user.first_name or user.last_name != "":
                name = " ".join([user.first_name, user.last_name])

            # If First & Last Name isn't used, then use Email
            else:
                name = user.email

            # Sending Email
            send_mail(
                f"REPLY TO: {name}",
                message,
                settings.EMAIL_HOST_USER,
                [user.email, settings.EMAIL_HOST_USER],
                fail_silently=False
            )




        return redirect('cart')


# Superuser & Staff Users Adding New Sauce
def add(request):
    # Checking to see if superuser
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == "GET":
            # Getting Form Info
            form = NewSauceForm()

            # Opening Add Sauce url
            return render(request, 'main/Add.html', {'form': form})

        elif request.method == "POST":
            # Getting Form Data
            form = NewSauceForm(request.POST, request.FILES)
            # Checking to is if this Form is Valid
            if form.is_valid():
                # Saving to Database
                form.save()
                # Returning to Home Page
                return redirect('home')
    # Redirecting to Main Menu
    else:
        return redirect('home')


# Superuser & Staff User Editing Sauce Items
def edit(request):
    # Checking to see if superuser
    if request.user.is_authenticated and request.user.is_staff:
        # Collecting all Sauces from Database
        menu = Sauce.objects.all()

        # Getting Data from Database
        if request.method == "GET":
            # If Sauce Selected Get Sauce Form
            if request.GET.get('sauce'):
                # Getting Selected Sauce
                sauce = request.GET.get('sauce')

                # Making sure Sauce is selected
                if sauce == 'None':
                    return redirect('edit')

                # Checking if Deleted
                if request.GET.get('btn') == 'del':
                    Sauce.objects.filter(name=sauce).first().delete()
                    return redirect('home')

                # Getting Form Data from Database
                data = Sauce.objects.filter(name=sauce).first()

                if data.image == "":
                    img = None
                else:
                    img = data.image.url

                # Reloading Edit Page
                return render(request, 'main/Edit.html', {'menu': menu, 'title': f"Updating {sauce}", 'form': NewSauceForm(instance=data), 'img': img, 'id': data.id})

            else:
                # Only Reload Select Sauce from Edit.html
                return render(request, 'main/Edit.html', {'menu': menu, 'title': "Edit Sauce"})

        # Saving to Database
        elif request.method == "POST":
            # Getting Sauce Data to be Updated
            sauce = Sauce.objects.filter(id=request.POST.get('id')).first()

            # Getting Form Data
            form = NewSauceForm(request.POST, request.FILES, instance=sauce)

            # Checking to is if this Form is Valid
            if form.is_valid():
                # Saving to Database
                form.save()

                # Returning to Home Page
                return redirect('home')
