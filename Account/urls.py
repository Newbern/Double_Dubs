from django.urls import path
from . import views

urlpatterns = [
    path('', views.account, name='account'),
    path('my-account/', views.my_account, name='my_account'),
    path('address/', views.address, name='address'),
    path('payment-method/', views.payment_method, name='payment_method'),
    path('history/payment-request/', views.payment_request, name='payment_request'),
    path('history/', views.history, name='history'),

]