from django.shortcuts import render, redirect
from django.core.mail import send_mail

from Account.models import *
from main.models import *
from main.form import NewSauceForm
from Double_Dubs import settings
import json
from square.client import Client
from uuid import uuid1 as uuid

# Setting up Client access through Squareup
client = Client(access_token=settings.SQUARE_ACCESS_TOKEN, environment=settings.SQUARE_ENVIRONMENT)


# Sauce Items/Menu
def menu(request):
    menu = Sauce.objects.all()

    if request.method == 'GET':
        # Loading Sauce Button
        if request.GET.get('item'):

            # Getting Selected Sauce
            item = request.GET.get('item')
            menu = Sauce.objects.filter(name=item).first()

            # Getting User Data
            if request.user.is_authenticated:
                user = Account.objects.filter(username=request.user).first()

            # Loading Fake User Sauces Url
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

        # Loading Main Page
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
        max_quantity = []
        # Going Through Users Cart
        for sauce in list(cart):
            # Going Through Sauce Items
            for sauce_item in Sauce.objects.all():
                # Checking to see if Users Sauce matches the Sauce Item
                if sauce_item.name == sauce:
                    # Adding  Sauce to Cart
                    lst.append((sauce_item, cart[sauce]))
                    max_quantity.append((sauce_item.name, sauce_item.instock))

        # Loading Cart
        return render(request, 'main/Cart.html', {'cart': lst, 'max_quantity': max_quantity})

    # Posting Cart data
    elif request.method == 'POST':
        # Getting Cart Data
        cart = json.loads(request.POST.get('cart'))
        total = request.POST.get('real_total')

        # Updating Database
        info = Account.objects.filter(username=request.user).first()
        info.cart = cart
        info.save()

        return redirect('checkout')


# Checkout
def checkout(request):
    # Getting Account data
    account = Account.objects.get(username=request.user)
    cart = account.cart

    # Getting Sauces with amount
    lst = [[item, account.cart[item]] for item in account.cart]

    # Collecting all Sauces for Price
    sauce_items = Sauce.objects.all()
    # Getting Total
    total = []
    # Going through account.cart
    for item in cart:
        # Going through Sauce Items
        for sauce in sauce_items:
            # when Sauce Item is in the account.cart
            if item == sauce.name:
                # Getting the price for this specific sauce
                price = sauce.price * cart[item]
                # Appending to the total list
                total.append(price)

    # Summing up all the prices together
    total = sum(total)

    if request.method == "GET":
        # Loading Payment
        return render(request, 'main/Checkout.html', {"total_amount": total, "cart": lst})

    elif request.method == "POST":
        # Getting Payment Method from account
        customer = Payment_method.objects.get(username=request.user, last_4=account.payment_method)

        # Payment Method
        results = client.payments.create_payment(
            body={
                "idempotency_key": str(uuid()),
                "source_id": customer.card_id,
                "amount_money": {
                    "amount": int(str(total).replace('.', "")),
                    "currency": "USD"
                },
                "customer_id": customer.customer_id,
            }
        )

        # Sending Email Recept
        if results.is_success():
            print(results.body)

            # Getting User & Account
            user = User.objects.filter(username=request.user).first()
            account = Account.objects.filter(username=request.user).first()


            # Sending Email if Email Address Exists
            if user.email is not None:
                # Email Recept Message
                message = "".join(
                    [f"{sauce}: {cart[sauce]}\n" for sauce in cart]) + f"---------------------\nTotal: ${total}\n"

                # Checking to see if First and Last Name is Used
                if user.first_name or user.last_name != "":
                    # Separating First & Last Name
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

            # Creating Order History
            # Getting the newest order_id
            try:
                new_order_id = sorted([order.order_id for order in Order.objects.all()])[-1] + 1
            except IndexError:
                new_order_id = 1

            order = Order.objects.create(order_id=new_order_id,
                                         customer_id=customer.customer_id,
                                         card_id=customer.card_id,
                                         card_last_4=customer.last_4,
                                         total_payment=total,
                                         cart=account.cart
                                         )
            # Saving Order
            order.save()

            # Deleting Current Card
            account.cart = {}
            account.save()

        elif results.is_error():
            print(results.errors)

    # Redirecting to Home Page
    return redirect('home')


# Payment Look up
def payment_lookup(request):
    pass


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
                return render(request, 'main/Edit.html',
                              {'menu': menu, 'title': f"Updating {sauce}", 'form': NewSauceForm(instance=data),
                               'img': img, 'id': data.id})

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


# Superuser & Staff User Orders Status
def orders(request):
    orders = Order.objects.all()

    # Getting Separate List
    all_lst = []
    incomplete_lst = []
    complete_lst = []

    # Collecting all Orders
    for persons_order in orders:

        # Getting User
        name = Payment_method.objects.filter(customer_id=persons_order.customer_id).first().username

        # Arranging Cart Data
        cart = f"Total: ${persons_order.total_payment}\n"
        for sauce in persons_order.cart:

            cart += f"\n{sauce}: {persons_order.cart[sauce]}"

        # Appending To Complete List
        if persons_order.status is True:
            complete_lst.append((name, cart, persons_order))

        # Appending to Incomplete List
        elif persons_order.status is False:
            incomplete_lst.append((name, cart, persons_order))

        # Appending Everything The All List
        all_lst.append((name, cart, persons_order))

    if request.method == "GET":

        # Loading Order Web Page
        return render(request, 'main/Orders.html', {'orders': reversed(all_lst), 'selected':"All"})

    elif request.method == "POST":
        lst_type = request.POST.get('lst-type')

        if lst_type == "Complete":
            lst = complete_lst
        elif lst_type == "Incomplete":
            lst = incomplete_lst
        elif lst_type == "All":
            lst = all_lst

        return render(request, 'main/Orders.html', {'orders': reversed(lst), 'selected':lst_type})


# ----------- LOOK AT REFUNDS --------------
# Refunds
def refund(request):

    if request.method == "GET":
        try:
            order_id = int(request.GET.get('order-id'))
            order = Order.objects.get(order_id=order_id)

            name = Payment_method.objects.filter(customer_id=order.customer_id).first().username

        except:
            order = name = None

        # Loading Refund Page
        return render(request, 'main/Refund.html', {"order": order, "name": name})

    elif request.method == "POST":
        pass










