from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User
from http import HTTPStatus


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user1 = User.objects.create_user(username='test_user1')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Тестовый title',
            slug='test'
        )
        cls.templates_url_names = {
            'index.html': '/',
            'group.html': f'/group/{cls.group.slug}/',
            'new.html': '/new/',
        }
        cls.url_ok_auth = [
            '/new/',
            f'/{cls.user.username}/{cls.post.id}/edit/'
        ]
        cls.url_ok_notauth = [
            '/',
            f'/group/{cls.group.slug}/',
            f'/{cls.user.username}/',
            f'/{cls.user.username}/{cls.post.id}/',
        ]
        g = f'{reverse("login")}?next=/{cls.user.username}/{cls.post.id}/edit/'
        cls.redirect_notauth = {
            '/new/': f'{reverse("login")}?next=/new/',
            f'/{cls.user.username}/{cls.post.id}/edit/': g,
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

    def test_edit_auth(self):
        response = self.authorized_client1.get(
            f'/{self.user.username}/{self.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response,
            f'/{self.user.username}/{self.post.id}/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_notauth(self):
        for adress, redirect in self.redirect_notauth.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(response, redirect)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_auth(self):
        for adress in self.url_ok_auth:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_notauth(self):
        for adress in self.url_ok_notauth:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_templates(self):
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_template_edit(self):
        response = self.authorized_client.get(
            f'/{self.user.username}/{self.post.id}/edit/'
        )
        self.assertTemplateUsed(response, 'new.html')
