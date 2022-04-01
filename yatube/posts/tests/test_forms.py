import shutil
import tempfile
from xml.etree.ElementTree import Comment

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.conf import settings
from posts.models import Post, Group, Comment
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_edit = Group.objects.create(
            title='Измененная группа',
            slug='change-slug',
            description='Измененное описание',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsFormsTests.user)
        self.posts_count = Post.objects.count()

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в БД"""
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': PostsFormsTests.group.pk,
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(self.posts_count + 1, Post.objects.count())
        post = Post.objects.first()
        self.assertEqual(post.author, PostsFormsTests.user)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, PostsFormsTests.group)
        self.assertTrue(
            Post.objects.filter(
                image='posts/small.gif'
            ).exists()
        )

    def test_comment_form(self):
        """После отправки формы с комментарием делается запись в БД"""
        form_data = {
            'text': 'Тестовый комментарий'
        }
        Post.objects.create(
            author=PostsFormsTests.user,
            text='Тестовый пост',
        )
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'Тестовый комментарий')

    def test_post_edit(self):
        """Валидная форма изменяет пост"""
        form_data = {
            'text': 'Измененный текст',
            'group': PostsFormsTests.group_edit.pk
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, PostsFormsTests.user)
        self.assertEqual(post.group, PostsFormsTests.group_edit)
