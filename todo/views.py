from datetime import datetime, timedelta
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from todo.models import TodoItem
from todo.serializers import TodoSerializer, UserSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
User=get_user_model()

def homeView(request):
    return render(request, 'home.html')

class sign_in(APIView):
    def post(self,request):
        try:
            data=request.data
            email=data.get('email')
            password=data.get('password')
            user = authenticate(username=email, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "user":str(user),
                "message":"Login Success",
                "access": str(refresh.access_token),
                },
                status=status.HTTP_302_FOUND)
            else:
                return Response({
                    'message':'Invalid Credentials'
                    },
                    status=status.HTTP_404_NOT_FOUND
                    )
        except Exception as e:
            print(e)
            return Response({
                'message':'Something went wrong'
                },
                status=status.HTTP_400_BAD_REQUEST
                )

class sign_up(APIView):
    def post(self, request):
        try:
            serializer=UserSerializer(data=request.data)
            if not serializer.is_valid():
                user=User.objects.get(email=serializer.data['email'])
            serializer.save()
            user=User.objects.get(email=serializer.data['email'])
            refresh = RefreshToken.for_user(user)
            custom_expiration_time = datetime.utcnow() + timedelta(days=7)
            refresh.expires = custom_expiration_time
            user.save()
            
            return Response({
                "message":"Account Created Successfully",
                },
                status=status.HTTP_302_FOUND)
        except Exception as e:
            print(e)
            return Response({
                'message':serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
                )

class todoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        try:
            # get all the todo items from the database through TodoSerializer
            todo_items = TodoItem.objects.all()
            serializer = TodoSerializer(todo_items, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)})
        
    def post(self, request):
        try:
            # get the data from the request
            data = request.data
            print(data)
            # create a new todo item
            todo_item = TodoItem.objects.create(title=data['title'], content=data['content'])
            # save the todo item
            todo_item.save()
            return Response({'success': 'Todo created successfully'})
        except Exception as e:
            return Response({'error': str(e)})
        
    def put(self, request):
        try:
            # get the data from the request
            data = request.data
            # get the todo item by id
            todo_item = TodoItem.objects.get(id=data['id'])
            # update the todo item
            todo_item.title = data['title']
            todo_item.content = data['content']
            todo_item.status = data['status']
            # save the todo item
            todo_item.save()
            return Response({'success': 'Todo updated successfully'})
        except Exception as e:
            return Response({'error': str(e)})
        
    def delete(self, request):
        try:
            # get the data from the request
            data = request.data
            # get the todo item by id
            todo_item = TodoItem.objects.get(id=data['id'])
            # delete the todo item
            todo_item.delete()
            return Response({'success': 'Todo deleted successfully'})
        except Exception as e:
            return Response({'error': str(e)})

        # return render(request, 'todo.html')