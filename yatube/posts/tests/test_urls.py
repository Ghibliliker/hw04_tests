from django.test import TestCase, Client

from ..models import Post, Group, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user1 = User.objects.create_user(username='test_user1')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user1)
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
            'group.html': '/group/test/',
            'new.html': '/new/',
        }
        cls.url_200 = [
            '/',
            '/group/test/',
            '/new/',
            '/test_user/',
            '/test_user/1/',
            '/test_user/1/edit/'
        ]

        cls.redirect_notauth = {
            '/new/': '/auth/login/?next=/new/',
            '/test_user/1/edit/': '/auth/login/?next=/test_user/1/edit/',
        }

    def test_edit_auth(self):
        response = self.authorized_client1.get(
            '/test_user/1/edit/',
            follow=True
        )
        self.assertRedirects(response, '/test_user/1/')

    def test_redirect_notauth(self):
        for adress, redirect in self.redirect_notauth.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(response, redirect)

    def test_url(self):
        for adress in self.url_200:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_templates(self):
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_template_edit(self):
        response = self.authorized_client.get('/test_user/1/edit/')
        self.assertTemplateUsed(response, 'new.html')
