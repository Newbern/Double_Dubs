from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views
from Account import urls as account_urls


urlpatterns = [
    path('', views.menu, name='home'),
    path('cart/', views.cart, name='cart'),
    path('add/', views.add, name='add'),
    path('edit/', views.edit, name='edit'),
]

# Uploading Images
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
