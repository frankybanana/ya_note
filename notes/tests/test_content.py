from django.test import Client, TestCase

from django.urls import reverse
from django.contrib.auth import get_user_model


from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNoteList(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель заметки')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='note_slug',
                                       author=cls.author)

    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        url = reverse('notes:list')
        response = self.reader_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_note_page_contains_form(self):
        url = reverse('notes:add')
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_note_page_contains_form(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
