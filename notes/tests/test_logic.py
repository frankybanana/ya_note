from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING

from pytils.translit import slugify

from notes.models import Note

User = get_user_model()

class NoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.url_note = reverse('notes:success')
        cls.user = User.objects.create(username='Просто_юзер')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': 'Новый заголовок',
                        'text': 'Новый текст',
                        'slug': 'new-slug'}

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.url_note)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class SlugUniqueTesting(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Просто_юзер')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.notes = Note.objects.create(title='Заголовок',
                                        text='Текст',
                                        slug='note_slug',
                                        author=cls.user)
        cls.form_data = {'title': 'Новый заголовок',
                        'text': 'Новый текст',
                        'slug': 'new_slug'}

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        self.form_data['slug'] = self.notes.slug
        response = self.auth_client.post(url, data=self.form_data)
        self.assertFormError(response, form='form', field='slug', errors=(self.notes.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)






# class TestCommentEditDelete(TestCase):
#     # Тексты для комментариев не нужно дополнительно создавать
#     # (в отличие от объектов в БД), им не нужны ссылки на self или cls,
#     # поэтому их можно перечислить просто в атрибутах класса.
#     NOTE_TEXT = 'Текст заметки'
#     NEW_NOTE_TEXT = 'Редактированная заметка'
#
#     @classmethod
#     def setUpTestData(cls):
#         # Создаём новость в БД.
#         cls.note = Note.objects.create(title='Заголовок', text='Текст')
#         # Формируем адрес блока с комментариями, который понадобится для тестов.
#         news_url = reverse('news:detail', args=(cls.news.id,))  # Адрес новости.
#         cls.url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
#         # Создаём пользователя - автора комментария.
#         cls.author = User.objects.create(username='Автор комментария')
#         # Создаём клиент для пользователя-автора.
#         cls.author_client = Client()
#         # "Логиним" пользователя в клиенте.
#         cls.author_client.force_login(cls.author)
#         # Делаем всё то же самое для пользователя-читателя.
#         cls.reader = User.objects.create(username='Читатель')
#         cls.reader_client = Client()
#         cls.reader_client.force_login(cls.reader)
#         # Создаём объект комментария.
#         cls.comment = Comment.objects.create(
#             news=cls.news,
#             author=cls.author,
#             text=cls.COMMENT_TEXT
#         )
#         # URL для редактирования комментария.
#         cls.edit_url = reverse('news:edit', args=(cls.comment.id,))
#         # URL для удаления комментария.
#         cls.delete_url = reverse('news:delete', args=(cls.comment.id,))
#         # Формируем данные для POST-запроса по обновлению комментария.
#         cls.form_data = {'text': cls.NEW_COMMENT_TEXT}