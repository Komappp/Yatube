from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='not_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(PostsURLTests.user2)

    def test_correct_template_guest(self):
        """Доступности страниц и соответсвие шаблонов"""
        templates_url_names = {
            self.guest_client.get('/'): 'posts/index.html',
            self.guest_client.get(
                f'/group/{PostsURLTests.group.slug}/'
            ): 'posts/group_list.html',
            self.guest_client.get('/profile/auth/'): 'posts/profile.html',
            self.guest_client.get(
                f'/posts/{PostsURLTests.post.id}/'
            ): 'posts/post_detail.html',
            self.authorized_client.get(
                f'/posts/{PostsURLTests.post.id}/edit/'
            ): 'posts/create.html',
            self.authorized_client.get('/create/'): 'posts/create.html'
        }
        for response, template in templates_url_names.items():
            with self.subTest(response=response):
                self.assertTemplateUsed(response, template)

    def test_404_error(self):
        """Запрос к несуществующей страницы вернет 404"""
        response = self.authorized_client.get('/unexpecting/')
        self.assertEqual(response.status_code, 404)

    def test_post_edit_redirect(self):
        """Редиректы со страницы редактирования поста
        для анонимных пользователей и авторизованных пользователей
        не являющихся автором поста"""
        response = self.guest_client.get(
            f'/posts/{PostsURLTests.post.id}/edit/'
        )
        expected = f'/auth/login/?next=/posts/{PostsURLTests.post.id}/edit/'
        self.assertRedirects(response, expected)
        response = self.authorized_client2.get(
            f'/posts/{PostsURLTests.post.id}/edit/'
        )
        expected = f'/posts/{PostsURLTests.post.id}/'
        self.assertRedirects(response, expected)

    def test_guest_redirects_from_create_page(self):
        """Редирект со страницы создания поста для анонимного пользователя"""
        response = self.guest_client.get(
            '/create/'
        )
        expected = '/auth/login/?next=/create/'
        self.assertRedirects(response, expected)

    def test_guest_cannot_comment(self):
        """Аноним не может комментировать"""
        response = self.guest_client.get(
            f'/posts/{PostsURLTests.post.id}/comment/'
        )
        expected = f'/auth/login/?next=/posts/{PostsURLTests.post.id}/comment/'
        self.assertRedirects(response, expected)

    def test_guest_code_response_200(self):
        """Аноним получает код 200 с общедоступных страниц"""
        templates_url_names = [
            '/',
            f'/group/{PostsURLTests.group.slug}/',
            '/profile/auth/',
            f'/posts/{PostsURLTests.post.id}/'
        ]
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)
