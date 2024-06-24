import unittest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from todo.models import TodoItem, TodoPermission

User = get_user_model()

class TodoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1_data = {
            'email': 'user1@example.com',
            'password': 'user1password'
        }
        self.user2_data = {
            'email': 'user2@example.com',
            'password': 'user2password'
        }

        # Create User1
        self.user1 = User.objects.create_user(**self.user1_data)
        # Create User2
        self.user2 = User.objects.create_user(**self.user2_data)

        self.todo_data = {
            'title': 'Test Todo',
            'content': 'Test Content'
        }

    def test_sign_in(self):
        response = self.client.post('/api/signin', self.user1_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn('access', response.data)

    def test_sign_up(self):
        new_user_data = {
            'email': 'newuser@example.com',
            'password': 'newuserpassword'
        }
        response = self.client.post('/api/signup', new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_create_todo_item(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/todos/', self.todo_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TodoItem.objects.count(), 1)

    def test_get_todo_items(self):
        self.client.force_authenticate(user=self.user1)
        TodoItem.objects.create(user=self.user1, **self.todo_data)
        response = self.client.get('/api/todos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_todo_item(self):
        self.client.force_authenticate(user=self.user1)
        todo_item = TodoItem.objects.create(user=self.user1, **self.todo_data)
        updated_data = {
            'id': todo_item.id,
            'title': 'Updated Title',
            'content': 'Updated Content',
            'status': todo_item.status  # Ensure status is valid
        }
        response = self.client.put('/api/todos/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        todo_item.refresh_from_db()
        self.assertEqual(todo_item.title, 'Updated Title')

    def test_delete_todo_item(self):
        self.client.force_authenticate(user=self.user1)
        todo_item = TodoItem.objects.create(user=self.user1, **self.todo_data)
        response = self.client.delete('/api/todos/', {'id': todo_item.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TodoItem.objects.count(), 0)

    def test_share_todo_item(self):
        self.client.force_authenticate(user=self.user1)
        todo_item = TodoItem.objects.create(user=self.user1, **self.todo_data)
        share_data = {
            'todo_id': todo_item.id,
            'access_user_email': self.user2.email
        }
        response = self.client.post('/api/share-todo/', share_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TodoPermission.objects.count(), 1)

    def test_access_shared_todo_item(self):
        self.client.force_authenticate(user=self.user1)
        todo_item = TodoItem.objects.create(user=self.user1, **self.todo_data)
        share_data = {
            'todo_id': todo_item.id,
            'access_user_email': self.user2.email
        }
        share_response = self.client.post('/api/share-todo/', share_data, format='json')
        self.client.force_authenticate(user=self.user2)
        slug = share_response.data['url_slug']
        response = self.client.get(f'/api/shared-todo/{slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_shared_access(self):
        self.client.force_authenticate(user=self.user1)
        todo_item = TodoItem.objects.create(user=self.user1, **self.todo_data)
        share_data = {
            'todo_id': todo_item.id,
            'access_user_email': self.user2.email
        }
        share_response = self.client.post('/api/share-todo/', share_data, format='json')
        slug = share_response.data['url_slug']
        response = self.client.delete('/api/share-todo/', {'url_slug': slug}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TodoPermission.objects.count(), 0)
