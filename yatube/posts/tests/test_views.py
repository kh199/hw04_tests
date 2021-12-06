from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'TestUser'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_pages_uses_correct_template(self):
        """URL-адрес post_edit использует шаблон posts/create_post.html."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                        kwargs={'post_id': self.post.id})))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом (список постов)."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый текст')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list передает список постов группы."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': 'test-slug'})))
        group = response.context['group']
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(group, Group.objects.get(slug='test-slug'))
        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile передает список постов пользователя."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                        kwargs={'username': 'TestUser'})))
        author = response.context['author']
        num_post = response.context['num_post']
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(author, User.objects.get(username='TestUser'))
        self.assertEqual(num_post, 1)
        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail передает один пост, отфильтрованный по id."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id})))
        post = response.context['post']
        num_post = response.context['num_post']
        self.assertEqual(post, Post.objects.get(id=self.post.id))
        self.assertEqual(num_post, 1)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post передает форму создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон create_post передает форму редактирования поста."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                        kwargs={'post_id': self.post.id})))
        post = response.context['post']
        self.assertEqual(post, Post.objects.get(id=self.post.id))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        self.post = Post.objects.bulk_create(
            [
                Post(
                    text='Тестируем  паджинатор',
                    author=self.user,
                    group=self.group,
                ),
            ] * 13
        )

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            reverse('posts:index'): 10,
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug2'}): 10,
            reverse('posts:profile',
                    kwargs={'username': 'TestUser2'}): 10,
        }
        for reverse_template, expected in templates_pages_names.items():
            with self.subTest(reverse_template=reverse_template):
                response = self.client.get(reverse_template)
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        templates_pages_names = {
            reverse('posts:index'): 3,
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug2'}): 3,
            reverse('posts:profile',
                    kwargs={'username': 'TestUser2'}): 3,
        }
        for reverse_template, expected in templates_pages_names.items():
            with self.subTest(reverse_template=reverse_template):
                response = self.client.get(reverse_template + '?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)
