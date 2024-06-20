from django.db import models
from django.contrib.auth.models import AbstractUser
from todo.manager import UserManager

class User(AbstractUser):
    username=None
    email=models.EmailField(unique=True)

    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS=[]
    objects=UserManager()
    
class TodoItem(models.Model):
    title=models.CharField(max_length=100)
    content = models.TextField()
    todo_date = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.content