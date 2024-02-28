from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор_заметки')
        cls.reader = User.objects.create(username='Просто_читатель')
        cls.notes = Note.objects.create(title='Заголовок',
                                        text='Текст',
                                        slug='note-slug',
                                        author=cls.author)

    def test_pages_availability(self):
            urls = (
                ('notes:home', None),
                ('users:login', None),
                ('users:logout', None),
                ('users:signup', None),
            )
            for name, args in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
            urls = (
                ('notes:detail', (self.notes.slug,)),
                ('notes:edit', (self.notes.slug,)),
                ('notes:delete', (self.notes.slug,)),
                ('notes:add', None),
                ('notes:success', None),
                ('notes:list', None),
            )

            login_url = reverse('users:login')
            for name, args in urls:
                if args is not None:
                    url = reverse(name, args=args)
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability_for_auth_user(self):
        urls = (
            'notes:add',
            'notes:success',
            'notes:list',
        )
        user_status = (self.author, HTTPStatus.OK)
        self.client.force_login(user_status[0])
        for name in urls:
                with self.subTest(user=user_status[0], name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, user_status[1])

    def test_pages_availability_for_author(self):
        urls = (
            ('notes:detail', (self.notes.slug,)),
            ('notes:edit', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)



