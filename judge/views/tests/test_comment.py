from django.test import TestCase
from django.urls import reverse

from judge.models import Comment
from judge.models.tests.util import create_problem, create_user


class CommentEditPageTestCase(TestCase):
    def test_editor_matches_martor_field(self):
        author = create_user('author')
        create_problem('commented', is_public=True)
        comment = Comment.objects.create(author=author.profile, page='p:commented', body='hello')
        self.client.force_login(author)
        response = self.client.get(reverse('comment_edit', args=[comment.id]))
        self.assertContains(response, 'id="id_body"')
