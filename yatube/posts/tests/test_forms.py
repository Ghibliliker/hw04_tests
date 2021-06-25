from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User
from http import HTTPStatus


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Test_group',
            slug='test_group'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.get(pk=2).text, form_data['text'])
        self.assertIsNotNone(
            Post.objects.get(pk=2).group.id,
            form_data['group']
        )

    def test_change_post(self):
        post_count = Post.objects.count()
        post_edit = Post.objects.get(pk=1)
        text_start = post_edit.text
        form_data = {
            'text': 'Тестовый другой текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': post_edit.id,
                }
            ),
            data=form_data,
            follow=True
        )
        post_fin = Post.objects.get(pk=1)
        text_fin = post_fin.text
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(Post.objects.get(pk=1).text, form_data['text'])
        self.assertEqual(Post.objects.get(pk=1).group.id, form_data['group'])
        self.assertIsNot(text_start, text_fin)
