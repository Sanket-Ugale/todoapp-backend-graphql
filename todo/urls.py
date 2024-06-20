# urls for the todo app

from django.urls import path
from . import views

urlpatterns = [
    path('', views.homeView, name='home'),
    # path('api/', views.TodoView.as_view(), name='todo'),
    path('api/signin', views.sign_in.as_view(), name='signin'),
    path('api/signup', views.sign_up.as_view(), name='signup'),
    path('api/todos/', views.TodoView.as_view(), name='todo_view'),
    path('api/share-todo/', views.ShareTodoView.as_view(), name='share_todo'),
    path('api/shared-todo/<str:slug>/', views.SharedTodoView.as_view(), name='shared_todo'),
]