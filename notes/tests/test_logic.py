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


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Редактированная заметка'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель заметки')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(title='Заголовок',
                                        text='Текст',
                                        slug='note_slug',
                                        author=cls.author)
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.form_data = {'title': 'Новый заголовок',
                         'text': 'Новый текст',
                         'slug': 'new-slug'}
        note_url = reverse('notes:detail', args=(cls.notes.slug,))
        cls.url_to_note = note_url + '#notes'

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)