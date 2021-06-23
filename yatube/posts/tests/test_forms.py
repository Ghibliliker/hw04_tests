from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_change_post(self):
        post = Post.objects.get(pk=1)
        text_start = post.text
        form_data = {
            'text': 'Тестовый текст change',
        }
        self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': 'test_user',
                    'post_id': '1'
                }
            ),
            data=form_data,
            follow=True
        )
        post_fin = Post.objects.get(pk=1)
        text_fin = post_fin.text
        self.assertNotEqual(text_fin, text_start)
