# urls for the todo app

from django.urls import path
from . import views

urlpatterns = [
    path('', views.homeView, name='home'),
    path('api/', views.todoView.as_view(), name='todo'),
]