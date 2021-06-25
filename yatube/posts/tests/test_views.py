from django.test import TestCase, Client
from django.urls.base import reverse
from django import forms

from ..models import Post, Group, User


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
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
            'group.html': reverse(
                'group_posts',
                kwargs={'slug': f'{cls.group.slug}'}
            ),
            'new.html': reverse('new_post'),
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def fast_check(self, response):
        self.assertEqual(
            response.context.get('page')[0].text,
            self.post.text
        )
        self.assertEqual(
            response.context.get('page')[0].author,
            self.post.author
        )
        self.assertEqual(
            response.context.get('page')[0].group,
            self.post.group
        )
        self.assertIn(self.post, response.context.get('page'))

    def test_templates_use_correct(self):
        for template, name in self.templates.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_context_use_index(self):
        response = self.authorized_client.get(reverse('index'))
        self.fast_check(response)

    def test_context_use_group(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertEqual(response.context.get('group').title, self.group.title)
        self.assertEqual(response.context.get('group').slug, self.group.slug)
        self.fast_check(response)

    def test_context_use_new(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        form_field = response.context['form'].fields['text']
        self.assertIsInstance(form_field, form_fields['text'])

    def test_context_use_edit(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': f'{self.user.username}',
                    'post_id': f'{self.post.id}'
                }
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
                kwargs={'username': f'{self.user.username}'}
            )
        )
        self.assertEqual(
            response.context['author'].username,
            self.user.username
        )
        self.fast_check(response)

    def test_context_use_post(self):
        response = self.authorized_client.get(
            reverse(
                'post_view',
                kwargs={
                    'username': f'{self.user.username}',
                    'post_id': f'{self.post.id}'
                }
            )
        )
        self.assertEqual(response.context['post'].text, f'{self.post.text}')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user_p')
        cls.group = Group.objects.create(
            title='Тестовый title',
            slug='test',
            description='описание'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text='Тестовый текст',
                author=cls.user,
                group=cls.group
            )
        cls.url_names = [
            reverse('index'),
            reverse('group_posts', kwargs={'slug': f'{cls.group.slug}'})
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        for adress in self.url_names:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                i = response.context.get('page')
                self.assertEqual(i.paginator.page(1).object_list.count(), 10)

    def test_second_page_contains_three_records(self):
        for adress in self.url_names:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress + '?page=2')
                i = response.context.get('page')
                self.assertEqual(i.paginator.page(2).object_list.count(), 3)


class CreateViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый title',
            slug='test',
            description='описание'
        )
        cls.group1 = Group.objects.create(
            title='Тестовый title1',
            slug='test1',
            description='описание1'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def fast_check(self, response):
        self.assertEqual(response.context.get('page')[0].text, self.post.text)
        self.assertEqual(
            response.context.get('page')[0].author,
            self.post.author
        )
        self.assertEqual(
            response.context.get('page')[0].group,
            self.post.group
        )

    def test_group_notcontains_post(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': f'{self.group1.slug}'})
        )
        self.assertNotIn(self.post, response.context.get('page'))

    def test_index_contains_post(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertIn(self.post, response.context['page'])
        self.fast_check(response)

    def test_group_contains_post(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertIn(self.post, response.context['page'])
        self.fast_check(response)
