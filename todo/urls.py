# urls for the todo app

from django.urls import path
from . import views

urlpatterns = [
    path('', views.homeView, name='home'),
    path('api/', views.todoView.as_view(), name='todo'),
    path('api/signin', views.sign_in.as_view(), name='signin'),
    path('api/signup', views.sign_up.as_view(), name='signup'),
]