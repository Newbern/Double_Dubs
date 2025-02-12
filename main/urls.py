from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views
from Account import urls as account_urls


urlpatterns = [
    path('', views.menu, name='home'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('refund/', views.refund, name='refund'),
    path('add/', views.add, name='add'),
    path('edit/', views.edit, name='edit'),
    path('orders/', views.orders, name='orders')
]

# Uploading Images
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
