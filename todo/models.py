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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    content = models.TextField()
    todo_date = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.content
    
class TodoPermission(models.Model):
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_user')
    todo = models.ForeignKey(TodoItem, on_delete=models.CASCADE)
    url_slug = models.CharField(max_length=100, primary_key=True)
    permission = models.BooleanField(default=True)
    
    def __str__(self):
        return self.permission