class ArticleListTests(APITestCase):
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
        data = {'list_title': 'My Test List', 'article_title': 'Test Article'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(ArticleList.objects.get().articles.count(), 1)
        self.assertEqual(ArticleList.objects.get().articles.get().title, 'Test Article')

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
        self.assertEqual(response.data[0]['user'], self.user.id)
        self.assertEqual(response.data[1]['title'], 'My Test List 2')



