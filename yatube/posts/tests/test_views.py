import shutil
import tempfile
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.conf import settings
from django import forms
from posts.models import Post, Group, Follow
from django.core.paginator import Page

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.follower = User.objects.create_user(username='follower')
        cls.notfollower = User.objects.create_user(username='notfollower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def post_and_page_objects_tests(self, response):
        if response.context.get('page_obj'):
            page_obj = response.context.get('page_obj')
            self.assertIsNotNone(page_obj)
            self.assertIsInstance(page_obj, Page)
            post = response.context['page_obj'][0]
        else:
            post = response.context['post']
        self.assertEqual(post.author, PostsViewsTests.user)
        self.assertEqual(post.text, PostsViewsTests.post.text)
        self.assertEqual(post.image, PostsViewsTests.post.image)

    def test_index_page_cache(self):
        """Работа кэша в шаблоне index.html"""
        response1 = self.authorized_client.get(reverse('posts:index')).content
        self.post = Post.objects.create(
            author=PostsViewsTests.user,
            text='Тестовый пост2'
        )
        self.assertTrue(Post.objects.filter(id=self.post.pk))
        response2 = self.authorized_client.get(reverse('posts:index')).content
        self.assertEqual(response1, response2)

    def test_views_use_correct_template(self):
        """Вью используют правильный шаблон"""
        views_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': 1}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}): 'posts/create.html'
        }
        for view, template in views_templates.items():
            with self.subTest(view=view):
                response = self.authorized_client.get(view)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.post_and_page_objects_tests(response)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:group_posts',
                                              kwargs={'slug': 'test-slug'}))
        self.post_and_page_objects_tests(response)
        group_object = response.context['group']
        self.assertEqual(group_object.title, PostsViewsTests.group.title)
        self.assertEqual(group_object.slug, PostsViewsTests.group.slug)
        self.assertEqual(group_object.description,
                         PostsViewsTests.group.description)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username': 'auth'}))
        self.post_and_page_objects_tests(response)
        user_object = response.context['author']
        self.assertEqual(user_object, PostsViewsTests.user)
        posts_count = response.context['posts_count']
        self.assertEqual(posts_count, Post.objects.count())

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id': 1}))
        self.post_and_page_objects_tests(response)
        posts_count = response.context['count']
        self.assertEqual(posts_count, Post.objects.count())

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        field_name = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for name, type in field_name.items():
            with self.subTest(name=name):
                form_field = response.context['form'].fields.get(name)
                self.assertIsInstance(form_field, type)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                              kwargs={'post_id': 1}))
        field_name = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for name, type in field_name.items():
            with self.subTest(name=name):
                form_field = response.context['form'].fields.get(name)
                self.assertIsInstance(form_field, type)
        self.post_and_page_objects_tests(response)
        self.assertTrue(response.context['is_edit'])

    def test_paginator(self):
        """Работа паджинатора в шаблонах index, group_list, profile"""
        post_list = []
        for _ in range(1, 13):
            new_post = Post(
                author=PostsViewsTests.user,
                text='Тестовый пост',
                group=PostsViewsTests.group
            )
            post_list.append(new_post)
        Post.objects.bulk_create(post_list)
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]
        for value in reverse_list:
            response = self.client.get(value)
            self.assertEqual(len(response.context['page_obj']), 10)
            response = self.client.get(value + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)

    def test_authorized_can_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться и отписываться,
        посты появляются в ленте у тех кто подписан, у тех кто не подписан
        не появляются"""
        follower = Client()
        notfollower = Client()
        follower.force_login(PostsViewsTests.follower)
        notfollower.force_login(PostsViewsTests.notfollower)
        follower.get(reverse(
            'posts:profile_follow',
            kwargs={'username': 'auth'}
        ))
        is_following = Follow.objects.filter(
            user=PostsViewsTests.follower,
            author=PostsViewsTests.user
        ).exists()
        self.assertTrue(is_following)
        response = follower.get(reverse('posts:follow_index'))
        self.post_and_page_objects_tests(response)
        response = notfollower.get(reverse('posts:follow_index'))
        self.assertFalse(response.context.get('page_obj'))
        follower.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': 'auth'}
        ))
        is_following = Follow.objects.filter(
            user=PostsViewsTests.follower,
            author=PostsViewsTests.user
        ).exists()
        self.assertFalse(is_following)
