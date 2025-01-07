from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    path('', views.menu, name='home'),
    path('account/', views.account, name='account'),
    path('cart/', views.cart, name='cart'),
    path('add/', views.add, name='add'),
    path('edit/', views.edit, name='edit'),
]

# Uploading Images
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
