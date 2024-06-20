from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from todo.models import TodoItem
from todo.serializers import TodoSerializer
from django.views.decorators.csrf import csrf_exempt

def homeView(request):
    return render(request, 'home.html')


class todoView(APIView):
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