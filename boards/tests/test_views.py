from django.urls import reverse
from django.test import TestCase
from django.urls import resolve
from django.contrib.auth.models import User
from ..forms import NewTopicForm 
from ..views import home, board_topics, new_topic
from ..models import Board, Post, Topic

class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        # Test if the status code for the home page is 200 (OK)
        self.assertEqual(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        # Test if the URL resolves to the home view function
        view = resolve('/')
        self.assertEqual(view.func, home)

    def test_home_view_contains_link_to_topics_page(self):
        # Test if the home page contains a link to the topics page for the board created in setUp
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))

        
class BoardTopicsTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.user = User.objects.create_user(username='john', email='john@example.com', password='123')
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=self.user)
        self.post = Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=self.user)

    def test_board_topics_view_success_status_code(self):
        # Test if the status code for the board topics page is 200 (OK)
        url = reverse('board_topics', kwargs={'pk': self.board.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        # Test if the status code for a non-existent board topics page is 404 (Not Found)
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        # Test if the URL resolves to the board_topics view function
        view = resolve('/boards/1/')
        self.assertEqual(view.func, board_topics)

    def test_board_topics_view_contains_link_back_to_homepage(self):
        # Test to verify if the board topics view contains a link back to the homepage
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('home')
        self.assertContains(response, 'href="{0}"'.format(homepage_url))

        
class NewTopicTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.client.login(username='john', password='123')  # Log in the user before making POST requests

    def test_csrf(self):
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        data = {
            'subject': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())
        topic = Topic.objects.first()
        self.assertRedirects(response, reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': topic.pk}))

    def test_new_topic_invalid_post_data(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)

    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'pk': self.board.pk})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())

    def test_contains_form(self):  # <- new test
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_invalid_post_data(self):  # <- updated this one
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        