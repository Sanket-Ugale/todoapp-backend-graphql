import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from graphql_jwt.shortcuts import get_token, create_refresh_token
from datetime import datetime, timedelta
from .models import TodoItem, TodoPermission
from .serializers import TodoSerializer
import uuid
from django.shortcuts import get_object_or_404

# Define Django User model
User = get_user_model()

# Define UserType
class UserType(DjangoObjectType):
    class Meta:
        model = User

# Define TodoType
class TodoType(DjangoObjectType):
    class Meta:
        model = TodoItem

# Define TodoPermissionType
class TodoPermissionType(DjangoObjectType):
    class Meta:
        model = TodoPermission

# Define SignUp mutation
class SignUp(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = User.objects.create_user(username=email, email=email, password=password)
        token = get_token(user)
        create_refresh_token(user)
        return SignUp(user=user, token=token)

# Define SignIn mutation
class SignIn(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = authenticate(username=email, password=password)
        if user is None:
            raise Exception('Invalid email or password')

        token = get_token(user)
        create_refresh_token(user)
        return SignIn(user=user, token=token)

# Define CreateTodoItem mutation
class CreateTodoItem(graphene.Mutation):
    todo = graphene.Field(TodoType)

    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    @login_required
    def mutate(self, info, title, content):
        user = info.context.user
        todo_item = TodoItem.objects.create(user=user, title=title, content=content)
        return CreateTodoItem(todo=todo_item)

# Define UpdateTodoItem mutation
class UpdateTodoItem(graphene.Mutation):
    todo = graphene.Field(TodoType)

    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        status = graphene.String(required=True)

    @login_required
    def mutate(self, info, id, title, content, status):
        user = info.context.user
        todo_item = get_object_or_404(TodoItem, id=id, user=user)
        todo_item.title = title
        todo_item.content = content
        todo_item.status = status
        todo_item.save()
        return UpdateTodoItem(todo=todo_item)

# Define DeleteTodoItem mutation
class DeleteTodoItem(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, id):
        user = info.context.user
        todo_item = get_object_or_404(TodoItem, id=id, user=user)
        todo_item.delete()
        return DeleteTodoItem(success=True)

# Define ShareTodoItem mutation
class ShareTodoItem(graphene.Mutation):
    success = graphene.Boolean()
    url_slug = graphene.String()

    class Arguments:
        todo_id = graphene.ID(required=True)
        access_user_email = graphene.String(required=True)

    @login_required
    def mutate(self, info, todo_id, access_user_email):
        user = info.context.user
        todo_item = get_object_or_404(TodoItem, id=todo_id, user=user)
        access_user = get_object_or_404(User, email=access_user_email)
        url_slug = uuid.uuid4().hex

        todo_permission = TodoPermission.objects.create(
            owner_user=user,
            access_user=access_user,
            todo=todo_item,
            url_slug=url_slug
        )
        todo_permission.save()
        return ShareTodoItem(success=True, url_slug=url_slug)

# Define RemoveSharedTodoItem mutation
class RemoveSharedTodoItem(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        url_slug = graphene.String(required=True)

    @login_required
    def mutate(self, info, url_slug):
        user = info.context.user
        todo_permission = get_object_or_404(TodoPermission, url_slug=url_slug, owner_user=user)
        todo_permission.delete()
        return RemoveSharedTodoItem(success=True)

# Define Query class
class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    all_todos = graphene.List(TodoType)
    todo_by_id = graphene.Field(TodoType, id=graphene.ID(required=True))
    shared_todo = graphene.Field(TodoType, slug=graphene.String(required=True))

    def resolve_users(self, info):
        return User.objects.all()

    @login_required
    def resolve_all_todos(self, info):
        user = info.context.user
        return TodoItem.objects.filter(user=user)

    @login_required
    def resolve_todo_by_id(self, info, id):
        user = info.context.user
        return get_object_or_404(TodoItem, id=id, user=user)

    @login_required
    def resolve_shared_todo(self, info, slug):
        user = info.context.user
        todo_permission = get_object_or_404(TodoPermission, url_slug=slug)
        if user != todo_permission.owner_user and user != todo_permission.access_user:
            raise Exception('You do not have permission to access this todo.')
        return todo_permission.todo

# Define Mutation class
class Mutation(graphene.ObjectType):
    sign_up = SignUp.Field()
    sign_in = SignIn.Field()
    create_todo_item = CreateTodoItem.Field()
    update_todo_item = UpdateTodoItem.Field()
    delete_todo_item = DeleteTodoItem.Field()
    share_todo_item = ShareTodoItem.Field()
    remove_shared_todo_item = RemoveSharedTodoItem.Field()

# Define the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
