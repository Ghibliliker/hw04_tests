from django.test import TestCase, Client
from django.urls.base import reverse
from django import forms

from ..models import Post, Group, User


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый title',
            slug='test',
            description='описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        cls.templates = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', kwargs={'slug': 'test'}),
            'new.html': reverse('new_post'),
        }

    def test_templates_use_correct(self):
        for template, name in self.templates.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_context_use_index(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.context['page'][0].text, 'Тестовый текст')

    def test_context_use_group(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test'})
        )
        self.assertEqual(
            response.context.get('page')[0].text,
            'Тестовый текст'
        )
        self.assertEqual(response.context['group'].title, 'Тестовый title')
        self.assertEqual(response.context['group'].slug, 'test')

    def test_context_use_new(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_context_use_edit(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={'username': 'test_user', 'post_id': '1'}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_context_use_profile(self):
        response = self.authorized_client.get(
            reverse(
                'profile',
                kwargs={'username': 'test_user'}
            )
        )
        self.assertEqual(response.context.get(
            'page')[0].text,
            'Тестовый текст'
        )
        self.assertEqual(response.context['author'].username, 'test_user')

    def test_context_use_post(self):
        response = self.authorized_client.get(
            reverse(
                'post_view',
                kwargs={'username': 'test_user', 'post_id': '1'}
            )
        )
        self.assertEqual(response.context['post'].text, 'Тестовый текст')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user_p')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for i in range(13):
            cls.post = Post.objects.create(
                text='Тестовый текст',
                author=cls.user
            )

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)


class CreateViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый title',
            slug='test',
            description='описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def test_index_contains_post(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.context.get('page')[0], self.post)

    def test_group_contains_post(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test'})
        )
        self.assertEqual(response.context.get('page')[0], self.post)
