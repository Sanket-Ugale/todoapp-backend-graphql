# serializer to convert the model data into json format of todo model

from rest_framework import serializers
from .models import TodoItem, TodoPermission
from django.contrib.auth import get_user_model
User=get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['email','password']

    def create(self,validated_data):
        user=User.objects.create(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = '__all__'

class TodoPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoPermission
        fields = '__all__'
