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

    def test_create_post_without_group(self):
        """Создание поста без группы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Пост без группы',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_object = response.context['page_obj'][0]
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_object.text, form_data['text'])
        self.assertEqual(last_object.id, Post.objects.get(
            text=form_data['text']).id
        )

    def test_create_group_post(self):
        """Создание поста группы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Пост группы',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_object = response.context['page_obj'][0]
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_object.text, form_data['text'])
        self.assertEqual(last_object.id, Post.objects.get(
            text=form_data['text']).id
        )
        self.assertEqual(last_object.group.id, form_data['group'])

    def test_edit_post_without_group(self):
        """Редактирование поста без группы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста без группы',
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
        self.assertEqual(post_context.text, form_data['text'])

    def test_edit_group_post(self):
        """Редактирование поста с группой"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста с группой',
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
        self.assertEqual(post_context.text, form_data['text'])
        self.assertEqual(post_context.group.title, self.group.title)

    def test_create_post_by_guest(self):
        """Создание поста неавторизированным пользователем"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Пытаемся создать пост',
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        create_url = reverse('posts:post_create')
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={create_url}')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_by_guest(self):
        """Редактирование поста неавторизированным пользователем"""
        posts_count = Post.objects.count()
        post = Post.objects.get(id=self.post.id)
        form_data = {
            'text': 'Отредактированный пост',
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        edit_url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={edit_url}')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, self.post.text)
        self.assertNotEqual(post.text, form_data['text'])
