from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

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

    def test_create_post(self):
        """Создание поста без группы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text=self.post.text).exists())

    def test_create_group_post(self):
        """Создание поста группы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text=self.post.text,
                                            group=self.group.id).exists())

    def test_edit_post(self):
        """Редактирование поста без группы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        post_context = response.context['post']
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post_context.text, self.post.text)

    def test_edit_post(self):
        """Редактирование поста с группой"""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        post_context = response.context['post']
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post_context.text, self.post.text)
        self.assertEqual(post_context.group.title, self.group.title)

    def test_create_post(self):
        """Создание поста неавторизированным пользователем"""
        posts_count = Post.objects.count()
        url = reverse('posts:post_create')
        login_url = reverse('users:login')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post(self):
        """Редактирование поста неавторизированным пользователем"""
        posts_count = Post.objects.count()
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        login_url = reverse('users:login')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')
        self.assertEqual(Post.objects.count(), posts_count)
