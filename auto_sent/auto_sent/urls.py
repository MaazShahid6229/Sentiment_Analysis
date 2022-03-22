from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', views.index, name='index'),
    path('api/', include("API.urls")),
    path('accounts/', include("accounts.urls")),

]
