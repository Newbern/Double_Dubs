from django.shortcuts import render, redirect
from register.form import LoginForm, RegisterForm
from django.contrib import auth, messages
from main.models import Account


# Create your views here.
def register(request):
    # Sending Data to Database
    if request.method == "POST":
        # Getting Data
        username = request.POST['username']
        email = request.POST['email'].lower()
        password = request.POST['password1']
        check_password = request.POST['password2']

        # Checking if username exist
        if auth.models.User.objects.filter(username=username).first() is not None:
            # Sending Message Data to Register Form Document
            messages.error(request, 'Username already exists')
            form = RegisterForm(request.POST)

        # Checking Email if exist
        elif auth.models.User.objects.filter(email=email).first() is not None:
            # Sending Message Data to Register Form Document
            messages.error(request, 'Email already exists.')
            form = RegisterForm(request.POST)

        # Checking Password
        elif password == check_password:
            # Creating New User
            user = auth.models.User.objects.create_user(username=username, email=email, password=password)
            # Creating New Account tied in with User
            Account.objects.create(username=user).save()
            # Logging into User Account
            auth.login(request, user)
            # Redirecting to Home page
            return redirect('home')

    else:
        # Loading in New Form
        form = RegisterForm()

    return render(request, 'register/Register.html', {'form': form})


def login(request):
    # Sending Data to Database
    if request.method == "POST":
        # Getting Login Data
        username = request.POST['username']
        password = request.POST['password']

        # Setting up User authentication
        user = auth.authenticate(request,
                                 username=username,
                                 password=password)

        # Getting User Object from Email
        email_user = auth.authenticate(request,
                                       # Checking if Email Was Used
                                       username=auth.models.User.objects.filter(email=username.lower()).first(),
                                       password=password)

        # Checking to see if user exist
        if user is not None:
            auth.login(request, user)
            return redirect('home')

        # Checking if Email Was Used Instead of Username
        elif email_user is not None:
            auth.login(request, email_user)
            return redirect('home')

        # Invalid Username or password Error
        else:
            # Sending Message
            messages.error(request, 'Invalid username or password.')
            # New Login Form
            form = LoginForm()

    # Loading New LoginForm
    else:
        form = LoginForm()

    # Loading Login Form Document
    return render(request, 'register/Login.html', {'form': form})


def logout(request):
    # Logging User Out
    auth.logout(request)

    # Redirecting to Login Page
    return redirect('home')
