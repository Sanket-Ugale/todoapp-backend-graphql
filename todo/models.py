from django.db import models

# Create todo models here.
class TodoItem(models.Model):
    title=models.CharField(max_length=100)
    content = models.TextField()
    todo_date = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.content