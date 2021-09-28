from django.urls import path
from . import views
# from .views import TestView

urlpatterns = [
    path("", views.index, name='index'),
    path("reviews", views.reviews, name='reviews'),
    path("meta", views.meta, name='meta'),
    # path('get/', TestView.as_view(), name='test')
    path('get', views.get, name='get')

]
