from datetime import timedelta

from django.contrib.admin.sites import site
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from judge.admin.interface import GlobalAnnouncementAdmin
from judge.models import GlobalAnnouncement
from judge.models.tests.util import create_user
from judge.template_context import global_announcements


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class GlobalAnnouncementTestCase(TestCase):
    def tearDown(self):
        cache.clear()
        super().tearDown()

    def test_model_defaults_and_str(self):
        announcement = GlobalAnnouncement.objects.create(
            message_en='English Announcement',
            message_vi='Thong bao tieng Viet',
            alert_type='alert-info',
            is_enabled=True,
        )
        self.assertEqual(str(announcement), 'English Announcement')
        self.assertEqual(announcement.alert_class, 'alert-info')
        self.assertTrue(announcement.is_enabled)
        self.assertTrue(announcement.is_dismissible)
        self.assertEqual(announcement.dismissal_version, 1)
        self.assertEqual(announcement.dismissal_key, f'{announcement.id}_v1')
        self.assertEqual(announcement.content_hash, f'{announcement.id}_v1')
        self.assertIsNone(announcement.valid_from)
        self.assertIsNone(announcement.valid_until)
        self.assertEqual(announcement.get_message('en'), 'English Announcement')
        self.assertEqual(announcement.get_message('vi'), 'Thong bao tieng Viet')

    def test_validation_requires_at_least_one_message(self):
        announcement = GlobalAnnouncement(
            message_en='',
            message_vi='',
            alert_type='alert-info',
        )
        with self.assertRaises(ValidationError):
            announcement.full_clean()

        announcement.message_en = 'Valid English'
        announcement.full_clean()

    def test_validation_schedule_dates(self):
        now = timezone.now()
        invalid_announcement = GlobalAnnouncement(
            message_en='Test Notice',
            valid_from=now + timedelta(days=2),
            valid_until=now + timedelta(days=1),
        )
        with self.assertRaises(ValidationError) as context:
            invalid_announcement.full_clean()
        self.assertIn('valid_until', context.exception.message_dict)

        valid_announcement = GlobalAnnouncement(
            message_en='Test Notice',
            valid_from=now,
            valid_until=now + timedelta(days=1),
        )
        valid_announcement.full_clean()

    def test_get_message_localization_and_fallback(self):
        both = GlobalAnnouncement.objects.create(
            message_en='English text',
            message_vi='Tiếng Việt',
            alert_type='alert-info',
        )
        self.assertEqual(both.get_message('en'), 'English text')
        self.assertEqual(both.get_message('vi'), 'Tiếng Việt')

        en_only = GlobalAnnouncement.objects.create(
            message_en='Only English',
            message_vi='',
            alert_type='alert-warning',
        )
        self.assertEqual(en_only.get_message('en'), 'Only English')
        self.assertEqual(en_only.get_message('vi'), 'Only English')

        vi_only = GlobalAnnouncement.objects.create(
            message_en='',
            message_vi='Chỉ tiếng Việt',
            alert_type='alert-danger',
        )
        self.assertEqual(vi_only.get_message('en'), 'Chỉ tiếng Việt')
        self.assertEqual(vi_only.get_message('vi'), 'Chỉ tiếng Việt')

    def test_sanitization_and_xss_protection(self):
        xss_announcement = GlobalAnnouncement.objects.create(
            message_en=(
                '<b>Notice:</b> <a href="https://dmoj.ca" onclick="alert(1)">site</a> '
                '<script>alert(2)</script><a href="javascript:alert(3)">bad link</a> '
                '<img src="x" onerror="alert(4)">'
            ),
            is_enabled=True,
        )
        display_html = xss_announcement.get_display_message('en')
        self.assertNotIn('<script>', display_html)
        self.assertNotIn('</script>', display_html)
        self.assertNotIn('onclick', display_html)
        self.assertNotIn('onerror', display_html)
        self.assertNotIn('javascript:', display_html)
        self.assertIn('<b>Notice:</b>', display_html)
        self.assertIn('<a href="https://dmoj.ca">site</a>', display_html)

    def test_get_active_and_caching(self):
        self.assertEqual(GlobalAnnouncement.get_active(), [])

        active1 = GlobalAnnouncement.objects.create(
            message_en='Active Notice 1',
            message_vi='Thông báo 1',
            alert_type='alert-warning',
            is_enabled=True,
        )
        GlobalAnnouncement.objects.create(
            message_en='Draft Notice',
            message_vi='Bản nháp',
            alert_type='alert-danger',
            is_enabled=False,
        )

        active = GlobalAnnouncement.get_active()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, active1.id)
        self.assertEqual(active[0].alert_type, 'alert-warning')

        cached = cache.get('global_announcements')
        self.assertIsNotNone(cached)
        self.assertEqual(len(cached), 1)

        active1.is_enabled = False
        active1.save()
        self.assertIsNone(cache.get('global_announcements'))
        self.assertEqual(len(GlobalAnnouncement.get_active()), 0)

        active1.is_enabled = True
        active1.save()
        self.assertEqual(len(GlobalAnnouncement.get_active()), 1)
        active1.delete()
        self.assertIsNone(cache.get('global_announcements'))
        self.assertEqual(len(GlobalAnnouncement.get_active()), 0)

    def test_bulk_update_and_delete_cache_invalidation(self):
        announcement = GlobalAnnouncement.objects.create(
            message_en='Bulk test',
            is_enabled=True,
        )
        self.assertEqual(len(GlobalAnnouncement.get_active()), 1)
        self.assertIsNotNone(cache.get('global_announcements'))

        GlobalAnnouncement.objects.filter(id=announcement.id).update(is_enabled=False)
        self.assertIsNone(cache.get('global_announcements'))
        self.assertEqual(len(GlobalAnnouncement.get_active()), 0)

        GlobalAnnouncement.objects.filter(id=announcement.id).update(is_enabled=True)
        self.assertEqual(len(GlobalAnnouncement.get_active()), 1)
        GlobalAnnouncement.objects.filter(id=announcement.id).delete()
        self.assertIsNone(cache.get('global_announcements'))
        self.assertEqual(len(GlobalAnnouncement.get_active()), 0)

    def test_get_active_scheduling(self):
        now = timezone.now()

        GlobalAnnouncement.objects.create(
            message_en='Future announcement',
            is_enabled=True,
            valid_from=now + timedelta(days=1),
        )
        GlobalAnnouncement.objects.create(
            message_en='Expired announcement',
            is_enabled=True,
            valid_until=now - timedelta(days=1),
        )
        active_scheduled = GlobalAnnouncement.objects.create(
            message_en='Current scheduled announcement',
            is_enabled=True,
            valid_from=now - timedelta(hours=1),
            valid_until=now + timedelta(hours=1),
        )

        active = GlobalAnnouncement.get_active()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, active_scheduled.id)

    def test_get_active_priority_and_cap(self):
        info_dismissible = GlobalAnnouncement.objects.create(
            message_en='Info dismissible',
            alert_type='alert-info',
            is_dismissible=True,
            is_enabled=True,
        )
        warning_dismissible = GlobalAnnouncement.objects.create(
            message_en='Warning dismissible',
            alert_type='alert-warning',
            is_dismissible=True,
            is_enabled=True,
        )
        danger_dismissible = GlobalAnnouncement.objects.create(
            message_en='Danger dismissible',
            alert_type='alert-danger',
            is_dismissible=True,
            is_enabled=True,
        )
        non_dismissible = GlobalAnnouncement.objects.create(
            message_en='Non dismissible info',
            alert_type='alert-info',
            is_dismissible=False,
            is_enabled=True,
        )

        active = GlobalAnnouncement.get_active()
        self.assertEqual(active[0].id, non_dismissible.id)
        self.assertEqual(active[1].id, danger_dismissible.id)
        self.assertEqual(active[2].id, warning_dismissible.id)
        self.assertEqual(active[3].id, info_dismissible.id)

        for i in range(5):
            GlobalAnnouncement.objects.create(message_en=f'Extra {i}', is_enabled=True)
        active_capped = GlobalAnnouncement.get_active()
        self.assertEqual(len(active_capped), 5)

    def test_dismissal_key_and_versioning(self):
        announcement = GlobalAnnouncement.objects.create(
            message_en='Message with typo',
            is_enabled=True,
        )
        initial_key = announcement.dismissal_key
        self.assertEqual(initial_key, f'{announcement.id}_v1')

        announcement.message_en = 'Message with typo fixed'
        announcement.save()
        self.assertEqual(announcement.dismissal_key, initial_key)

        announcement.dismissal_version = 2
        announcement.save()
        self.assertEqual(announcement.dismissal_key, f'{announcement.id}_v2')
        self.assertNotEqual(announcement.dismissal_key, initial_key)

    def test_template_context_processor(self):
        GlobalAnnouncement.objects.create(
            message_en='Context Processor Banner EN',
            message_vi='Context Processor Banner VI',
            alert_type='alert-success',
            is_enabled=True,
        )
        factory = RequestFactory()
        request = factory.get('/')
        ctx = global_announcements(request)
        self.assertIn('global_announcements', ctx)
        self.assertIn('global_announcement', ctx)
        self.assertEqual(len(ctx['global_announcements']), 1)
        self.assertEqual(ctx['global_announcement'].alert_class, 'alert-success')

    def test_admin_registration(self):
        self.assertIn(GlobalAnnouncement, site._registry)
        model_admin = site._registry[GlobalAnnouncement]
        self.assertIsInstance(model_admin, GlobalAnnouncementAdmin)
        self.assertIn('is_enabled', model_admin.list_editable)
        self.assertIn('is_dismissible', model_admin.list_editable)
        self.assertIn('alert_type', model_admin.list_filter)
        self.assertIn('is_dismissible', model_admin.list_filter)
        self.assertIn('message_en', model_admin.search_fields)
        self.assertIn('message_vi', model_admin.search_fields)

        announcement = GlobalAnnouncement.objects.create(
            message_en='E' * 100,
            message_vi='V' * 100,
            alert_type='alert-danger',
            is_enabled=True,
        )
        en_preview = model_admin.message_en_preview(announcement)
        vi_preview = model_admin.message_vi_preview(announcement)
        badge = model_admin.alert_type_badge(announcement)
        self.assertTrue(en_preview.endswith('...'))
        self.assertTrue(vi_preview.endswith('...'))
        self.assertEqual(len(en_preview), 63)
        self.assertEqual(len(vi_preview), 63)
        self.assertIn('background-color:#edd', badge)
        self.assertIn('color:#944', badge)

    def test_render_in_base_template_bilingual(self):
        announcement = GlobalAnnouncement.objects.create(
            message_en='English Site Notice',
            message_vi='Thông báo trang web tiếng Việt',
            alert_type='alert-warning',
            is_enabled=True,
            is_dismissible=True,
        )

        response_en = self.client.get('/', HTTP_ACCEPT_LANGUAGE='en')
        self.assertContains(response_en, 'global-announcement-banner')
        self.assertContains(response_en, 'English Site Notice')
        self.assertContains(response_en, f'id="global-announcement-{announcement.id}"')
        self.assertContains(response_en, f"global-announcement-dismissed-{announcement.id}")
        self.assertContains(response_en, announcement.dismissal_key)
        self.assertContains(response_en, 'dismissGlobalAnnouncement')
        self.assertContains(response_en, 'fa-times')
        self.assertContains(response_en, 'role="region"')

        self.client.cookies['django_language'] = 'vi'
        response_vi = self.client.get('/')
        self.assertContains(response_vi, 'global-announcement-banner')
        self.assertContains(response_vi, 'Thông báo trang web tiếng Việt')

        announcement.is_enabled = False
        announcement.save()
        response_disabled = self.client.get('/')
        self.assertNotContains(response_disabled, 'global-announcement-banner')

    def test_render_non_dismissible_announcement(self):
        announcement = GlobalAnnouncement.objects.create(
            message_en='Critical Non-Dismissible Notice',
            alert_type='alert-danger',
            is_enabled=True,
            is_dismissible=False,
        )

        response = self.client.get('/')
        self.assertContains(response, 'Critical Non-Dismissible Notice')
        self.assertContains(response, 'global-announcement-banner')
        self.assertNotContains(response, 'fa-times')
        self.assertNotContains(response, f"global-announcement-dismissed-{announcement.id}")

    def test_render_multiple_announcements_queue_attributes(self):
        danger = GlobalAnnouncement.objects.create(
            message_en='Danger Notice',
            alert_type='alert-danger',
            is_enabled=True,
            is_dismissible=True,
        )
        info = GlobalAnnouncement.objects.create(
            message_en='Info Notice',
            alert_type='alert-info',
            is_enabled=True,
            is_dismissible=True,
        )

        response = self.client.get('/')
        self.assertContains(response, f'id="global-announcement-{danger.id}"')
        self.assertContains(response, f'id="global-announcement-{info.id}"')
        self.assertContains(response, 'global-announcement-dismissible')
        self.assertContains(response, "querySelectorAll('.global-announcement-dismissible')")

    def test_admin_views(self):
        admin_user = create_user(
            username='admin_announcement',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(admin_user)

        changelist_url = '/admin/judge/globalannouncement/'
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)

        add_url = '/admin/judge/globalannouncement/add/'
        response = self.client.get(add_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            'message_en': 'Admin created announcement EN',
            'message_vi': 'Admin tao thong bao VI',
            'alert_type': 'alert-info',
            'is_enabled': 'on',
            'is_dismissible': 'on',
            'dismissal_version': '1',
        }
        response = self.client.post(add_url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(GlobalAnnouncement.objects.filter(message_en='Admin created announcement EN').exists())
        created = GlobalAnnouncement.objects.get(message_en='Admin created announcement EN')
        self.assertTrue(created.is_enabled)
        self.assertTrue(created.is_dismissible)
        self.assertEqual(created.message_vi, 'Admin tao thong bao VI')
        self.assertEqual(created.alert_type, 'alert-info')
