from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from judge.models import Language
from judge.models.tests.util import create_user


class EditProfileTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user(username='normal_user')
        cls.pascal = Language.objects.create(key='PAS', name='Pascal', short_name='PAS', common_name='Pascal',
                                             ace='pascal', pygments='pascal', extension='pas')
        cls.cpp = Language.objects.create(key='CPP17', name='C++17', short_name='C++17', common_name='C++',
                                          ace='c_cpp', pygments='cpp', extension='cpp', template='int main() {\n}')

    def get_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('user_edit_profile'))
        self.assertEqual(response.status_code, 200)
        return response

    def test_editor_theme_preview_is_rendered(self):
        response = self.get_page()
        self.assertContains(response, 'id="ace-theme-preview"')
        self.assertContains(response, '%s/ace.js' % settings.ACE_URL)

    def test_preview_uses_configured_default_themes(self):
        response = self.get_page()
        self.assertContains(response, 'data-light-theme="%s"' % settings.DMOJ_THEME_DEFAULT_ACE_THEME['light'])
        self.assertContains(response, 'data-dark-theme="%s"' % settings.DMOJ_THEME_DEFAULT_ACE_THEME['dark'])

    def test_preview_uses_language_templates(self):
        response = self.get_page()
        languages = response.context['preview_languages']
        self.assertEqual(languages[self.pascal.id], {'ace': 'pascal', 'template': ''})
        self.assertEqual(languages[self.cpp.id], {'ace': 'c_cpp', 'template': self.cpp.template})
        self.assertContains(response, '"template": "int main() {\\n}"')

    def test_site_theme_is_not_on_the_page(self):
        response = self.get_page()
        self.assertNotContains(response, 'id="id_site_theme"')

    def test_saving_profile_keeps_site_theme(self):
        profile = self.user.profile
        profile.site_theme = 'dark'
        profile.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse('user_edit_profile'), {
            'timezone': profile.timezone,
            'language': self.cpp.id,
            'ace_theme': 'monokai',
        })
        self.assertEqual(response.status_code, 302)
        profile.refresh_from_db()
        self.assertEqual(profile.ace_theme, 'monokai')
        self.assertEqual(profile.site_theme, 'dark')
