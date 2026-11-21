from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from judge.models import Comment
from judge.models.tests.util import create_problem, create_user


class CommentEditPageTestCase(TestCase):
    @patch('judge.signals.on_new_comment')
    def test_editor_matches_martor_field(self, on_new_comment):
        author = create_user('author')
        create_problem('commented', is_public=True)
        comment = Comment.objects.create(author=author.profile, page='p:commented', body='hello')
        self.client.force_login(author)
        response = self.client.get(reverse('comment_edit', args=[comment.id]))
        self.assertContains(response, 'id="id_body"')
