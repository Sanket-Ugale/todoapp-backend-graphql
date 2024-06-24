from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from todo.models import TodoItem
from todo.serializers import TodoSerializer, UserSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import TodoItem, TodoPermission
import uuid

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

# class todoView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes=[JWTAuthentication]

#     @csrf_exempt
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
    
#     def get(self, request):
#         try:
#             # get all the todo items from the database through TodoSerializer
#             todo_items = TodoItem.objects.all()
#             serializer = TodoSerializer(todo_items, many=True)
#             return Response(serializer.data)
#         except Exception as e:
#             return Response({'error': str(e)})
        
#     def post(self, request):
#         try:
#             # get the data from the request
#             data = request.data
#             print(data)
#             # create a new todo item
#             todo_item = TodoItem.objects.create(title=data['title'], content=data['content'])
#             # save the todo item
#             todo_item.save()
#             return Response({'success': 'Todo created successfully'})
#         except Exception as e:
#             return Response({'error': str(e)})
        
#     def put(self, request):
#         try:
#             # get the data from the request
#             data = request.data
#             # get the todo item by id
#             todo_item = TodoItem.objects.get(id=data['id'])
#             # update the todo item
#             todo_item.title = data['title']
#             todo_item.content = data['content']
#             todo_item.status = data['status']
#             # save the todo item
#             todo_item.save()
#             return Response({'success': 'Todo updated successfully'})
#         except Exception as e:
#             return Response({'error': str(e)})
        
#     def delete(self, request):
#         try:
#             # get the data from the request
#             data = request.data
#             # get the todo item by id
#             todo_item = TodoItem.objects.get(id=data['id'])
#             # delete the todo item
#             todo_item.delete()
#             return Response({'success': 'Todo deleted successfully'})
#         except Exception as e:
#             return Response({'error': str(e)})

#         # return render(request, 'todo.html')

class TodoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            # get all the todo items for the logged in user
            todo_items = TodoItem.objects.filter(user=request.user)
            serializer = TodoSerializer(todo_items, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            # get the data from the request
            data = request.data
            # create a new todo item for the logged in user
            todo_item = TodoItem.objects.create(user=request.user, title=data['title'], content=data['content'])
            # save the todo item
            todo_item.save()
            return Response({'success': 'Todo created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            # get the data from the request
            data = request.data
            # get the todo item by id and ensure it belongs to the logged in user
            todo_item = get_object_or_404(TodoItem, id=data['id'], user=request.user)
            # update the todo item
            todo_item.title = data['title']
            todo_item.content = data['content']
            todo_item.status = data['status']
            # save the todo item
            todo_item.save()
            return Response({'success': 'Todo updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            # get the data from the request
            data = request.data
            # get the todo item by id and ensure it belongs to the logged in user
            todo_item = get_object_or_404(TodoItem, id=data['id'], user=request.user)
            # delete the todo item
            todo_item.delete()
            return Response({'success': 'Todo deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShareTodoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            # get the data from the request
            data = request.data
            todo_item = get_object_or_404(TodoItem, id=data['todo_id'], user=request.user)
            access_user = get_object_or_404(User, email=data['access_user_email'])
            url_slug = uuid.uuid4().hex

            # create a new TodoPermission entry
            todo_permission = TodoPermission.objects.create(
                owner_user=request.user,
                access_user=access_user,
                todo=todo_item,
                url_slug=url_slug
            )

            todo_permission.save()

            return Response({
                'success': 'Todo shared successfully',
                'url_slug': url_slug
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        try:
            # get the data from the request
            data = request.data
            todo_permission = get_object_or_404(TodoPermission, url_slug=data['url_slug'], owner_user=request.user)
            todo_permission.delete()
            return Response({'success': 'Access removed successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SharedTodoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, slug):
        try:
            # Fetch the TodoPermission object by the slug
            todo_permission = TodoPermission.objects.get(url_slug=slug)
            
            # Check if the requesting user is either the owner_user or the access_user
            if request.user != todo_permission.owner_user and request.user != todo_permission.access_user:
                return Response({'error': 'You do not have permission to access this todo.'}, status=status.HTTP_403_FORBIDDEN)
            
            # Fetch the TodoItem associated with the TodoPermission
            todo_item = todo_permission.todo
            serializer = TodoSerializer(todo_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except TodoPermission.DoesNotExist:
            return Response({'error': 'Todo with this slug does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)