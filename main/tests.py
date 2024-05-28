from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Article, ArticleList
from .functions import *

class MainTests(TestCase):

    def test_create_article(self):
        title = "Test Article"
        description = "Test Description"
        content = "Test Content"
        article = Article.objects.create(title=title, description=description, content=content)
        self.assertEqual(article.title, title)
        self.assertEqual(article.description, description)
        self.assertEqual(article.content, content)

    def test_create_article_list(self):
        title = "Test List"
        user = User.objects.create_user(username='testuser', password='testpassword')
        article_list = ArticleList.objects.create(title=title, user=user)
        self.assertEqual(article_list.title, title)
        self.assertEqual(article_list.user, user)

    def test_create_article_from_title(self):
        title = "Roger Federer"
        returned = get_or_create_article_from_title(title)
        article = Article.objects.get(title=title)
        self.assertEqual(returned, article)
        self.assertEqual(article.title, title)
        self.assertIsNotNone(article.description)
        self.assertIsNotNone(article.content)
    
    def test_create_list_from_title(self):
        title = "Tennis Players"
        user = User.objects.create_user(username='testuser', password='testpassword')
        returned, created = get_or_create_article_list_from_title(user, title)
        article_list = ArticleList.objects.get(title=title, user=user)
        self.assertEqual(returned, article_list)
        self.assertEqual(article_list.title, title)
        self.assertEqual(article_list.user, user)
        article_title = "Roger Federer"
        title_2 = "Other Tennis Players"
        returned, created = get_or_create_article_list_from_title(user, title_2, article_title=article_title)
        article_list_2 = ArticleList.objects.get(title=title_2, user=user)
        self.assertEqual(returned, article_list_2)
        self.assertEqual(article_list_2.title, title_2)
        self.assertEqual(article_list_2.user, user)
        self.assertEqual(article_list_2.articles.count(), 1)
        self.assertEqual(article_list_2.articles.get().title, article_title)

class APITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_create_article_list(self):
        url = reverse('create_article_list')
        data = {'list_title': 'My Test List'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ArticleList.objects.count(), 1)
        self.assertEqual(ArticleList.objects.get().title, 'My Test List')

    def test_add_article_to_list(self):
        ArticleList.objects.create(title='My Test List', user=self.user)
        url = reverse('add_article_to_list')
        data = {'list_title': 'My Test List', 'article_title': 'Roger Federer'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(ArticleList.objects.get().articles.count(), 1)
        self.assertEqual(ArticleList.objects.get().articles.get().title, 'Roger Federer')

    def test_retrieve_article_list(self):
        article = Article.objects.create(title='Test Article', description='Test Description', content='Test Content')
        article_list = ArticleList.objects.create(title='My Test List', user=self.user)
        article_list.articles.add(article)
        url = reverse('retrieve_article_list')
        response = self.client.get(url, {'list_title': 'My Test List'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'My Test List')
        self.assertEqual(len(response.data['articles']), 1)
        self.assertEqual(response.data['articles'][0]['title'], 'Test Article')

    def test_retrieve_user_lists(self):
        ArticleList.objects.create(title='My Test List', user=self.user)
        ArticleList.objects.create(title='My Test List 2', user=self.user)
        url = reverse('retrieve_user_article_lists')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'My Test List')
        self.assertEqual(response.data[1]['title'], 'My Test List 2')

    def test_get_num_lists(self):
        ArticleList.objects.create(title='My Test List', user=self.user)
        ArticleList.objects.create(title='My Test List 2', user=self.user)
        url = reverse('get_num_lists')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['num_lists'], 2)

    def test_create_user(self):
        url = reverse('create_user')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('get_num_lists')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['num_lists'], 2)

class UserAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
        self.client = APIClient()
        self.token_url = reverse('token_obtain_pair')

    def test_register_user(self):
        url = reverse('user_register')
        data = {
            'username': 'testuser2',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_authenticate_user(self):
        self.test_register_user()
        data = {
            'username': 'testuser2',
            'password': 'testpassword'
        }
        response = self.client.post(self.token_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

    def test_n_lists(self):
        self.test_authenticate_user()
        url = reverse('get_num_lists')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['num_lists'], 2)

