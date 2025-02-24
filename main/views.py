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


# Contact us
def contact_us(request):
    if request.method == 'POST':

        # Checking to See if User is Logged in
        if request.user.is_authenticated:
            # Getting Email Address
            user = User.objects.get(username=request.user)

            # Getting Message
            message = request.POST.get('message')

            # Checking to see if User has Email setup
            if user.email is not None and message is not None:
                message = message

                # Checking to see if First and Last Name is Used
                if user.first_name or user.last_name != "":
                    # Separating First & Last Name
                    name = " ".join([user.first_name, user.last_name])

                # If First & Last Name isn't used, then use Email
                else:
                    name = user.email

                send_mail(
                    f"REPLY TO {name}",
                    message,
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER, user.email],
                    fail_silently=False
                )


    return redirect('home')


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

        # Updating Google Sheets Database
        #google_data(request)

        # Updating Database
        info = Account.objects.filter(username=request.user).first()
        info.cart = cart
        info.save()

        # Returning to checkout
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
        # Making sure there is a Payment method
        card = Account.objects.filter(username=request.user).first().payment_method

        # Checking if Card exist or is selected
        if not Payment_method.objects.filter(username=request.user, last_4=card).first() or card is None:
            return redirect('payment_method')

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
                    f"{name} RECEIPT",
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
                                         payment_id=results.body['payment']['id'],
                                         card_last_4=customer.last_4,
                                         total_payment=total,
                                         cart=account.cart
                                         )
            # Saving Order
            order.save()

            sauces = Sauce.objects.all()
            # Updating Sauce Item quantity in Database
            for sauce_item in sauces:
                for cart_item in account.cart:
                    # Checking to make sure there the save key
                    if sauce_item.name == cart_item:
                        # Removing Items Bought
                        sauce_item.instock -= account.cart[cart_item]
                        # Saving to database
                        sauce_item.save()



            # Deleting Current Cart
            account.cart = {}
            account.save()

        elif results.is_error():
            print(results.errors)

    # Redirecting to Home Page
    return redirect('home')


# Google Sheet Data
def google_data(request):
    from main.Google_Sheet_Data.Google_Format import Sheet

    # Settings up Google Sheet Api & Keys
    keys = "https://docs.google.com/spreadsheets/d/1o7wB5wcYQlidWSw5oFoLr6RE4bZ9uSe35Sa3bxcEIas/edit?gid=0#gid=0"
    api = 'main/info.json'
    Sheet = Sheet(api=api, key=keys)



    # Persons Name
    Sheet.write('A1', f"{request.user.username}", True)

    # Collecting Order
    # Locating Cell
    abc, row, col = Sheet.locate('A2')
    order = Account.objects.filter(username=request.user).first().cart
    for item in order:
        Sheet.write(f"{abc[row]}{col}", item, False)


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


# Superuser & Staff Users Editing Sauce Items
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


# Superuser & Staff Users Orders Status
def orders(request):
    # Collecting all Orders
    orders = Order.objects.all()

    # Getting Separate List
    lst = [(Payment_method.objects.filter(customer_id=customer_order.customer_id).first().username, customer_order) for customer_order in orders]
    # Reversing List for Descending order
    lst.reverse()
    complete_lst = [order for order in lst if order[1].completed_status]
    incomplete_lst = [order for order in lst if not order[1].completed_status]

    if request.method == "GET":
        radio_btn = request.GET.get('radio-btn')

        # Getting Radio Button Response
        if radio_btn == 'Incomplete':
            lst = incomplete_lst
        elif radio_btn == 'Complete':
            lst = complete_lst
        else:
            radio_btn = "All"

        # Getting DropDown Value
        dropdown = request.GET.get('dropdown')
        try:
            if dropdown:
                result = Order.objects.filter(order_id=int(dropdown)).first()
                name = Payment_method.objects.filter(customer_id=result.customer_id).first().username
            else:
                result = Order.objects.filter(order_id=lst[0][1].order_id).first()
                name = Payment_method.objects.filter(customer_id=result.customer_id).first().username

        except IndexError:
            result = None
            name = None

        return render(request, 'main/Orders.html', {
            'orders': lst,
            'selected': radio_btn,
            'result': result,
            'name': name
        }
                      )

    elif request.method == "POST":
        # Getting Button Value
        button = request.POST.get('btn')
        order_id = int(request.POST.get('order_id'))

        # Getting Order Id
        order = Order.objects.filter(order_id=order_id).first()

        # Updating Status
        if button == "Complete":
            order.completed_status = True
        elif button == "Incomplete":
            order.completed_status = False

        order.save()

        return redirect('orders')


# Superuser & Staff Users Refund Payments
def refund(request):

    # Getting Order Id
    if request.method == "GET":
        try:
            # Getting Order ID
            order = Order.objects.get(order_id=int(request.GET.get('order-id')))

            # Getting Name of the Order ID
            name = Payment_method.objects.filter(customer_id=order.customer_id).first().username

        except (ValueError, TypeError):
            order = name = None

        # Loading Refund Page
        return render(request, 'main/Refund.html', {"order": order, "name": name})

    # Refunding Payment
    elif request.method == "POST":
        try:
            # Getting Order Id
            order = Order.objects.filter(order_id=int(request.POST.get('order-id'))).first()

            # Refunding Payment
            result = client.refunds.refund_payment(
                body={
                    "idempotency_key": str(uuid()),
                    "amount_money": {
                        "amount": int(str(order.total_payment).replace('.', '')),
                        "currency": "USD",
                    },
                    "payment_id": order.payment_id,
                }
            )

            if result.is_success:
                print(result.body)
            elif result.errors:
                print(result.errors)

            # Changing Refund Status
            order.refund_status = True

            order.save()

        except (ValueError, TypeError):
            pass

        return redirect('refund')


# Superuser & Staff Users Advertisement
def ads(request):

    if request.method == "POST":
        # Come Back to Later
        # Collecting all Images
        # img_lst = [file for file in request.FILES.getlist('files')]

        # Getting Subject
        subject = request.POST.get('subject')
        # Getting Message
        message = request.POST.get('message')

        # Checking CheckBox's
        customer = request.POST.get('customer')
        employee = request.POST.get('employee')

        # Collecting all Employee and Customer Emails
        employee_lst = []
        customer_lst = []
        for status in Account.objects.all():
            if status.employee:
                employee_lst.append(User.objects.filter(username=status.username).first().email)
            else:
                customer_lst.append(User.objects.filter(username=status.username).first().email)


        email_lst=None
        # Getting the Selected list
        if employee is not None:
            email_lst = employee_lst
        elif customer is not None:
            email_lst = customer_lst
        if (employee and customer) is not None:
            email_lst = employee_lst + customer_lst


        # Going Through Recipients Email List
        for recipient in email_lst:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient],
                fail_silently=False
                    )

        # Returning Home After Emails Are Sent
        return redirect('home')

    # Loading In Advertisement Page
    return render(request, 'main/Advertisement.html', {})