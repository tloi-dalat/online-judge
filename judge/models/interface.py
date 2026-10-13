import re

import bleach
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from judge.models.profile import Organization, Profile

__all__ = ['MiscConfig', 'validate_regex', 'NavigationBar', 'BlogPost', 'BlogPostTag', 'GlobalAnnouncement']


class MiscConfig(models.Model):
    key = models.CharField(max_length=30, verbose_name=_('key'), unique=True)
    value = models.TextField(verbose_name=_('value'), blank=True)

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = _('configuration item')
        verbose_name_plural = _('miscellaneous configuration')


def validate_regex(regex):
    try:
        re.compile(regex, re.VERBOSE)
    except re.error as e:
        raise ValidationError('Invalid regex: %s' % e.message)


class NavigationBar(MPTTModel):
    class Meta:
        verbose_name = _('navigation item')
        verbose_name_plural = _('navigation bar')

    class MPTTMeta:
        order_insertion_by = ['order']

    order = models.PositiveIntegerField(db_index=True, verbose_name=_('order'))
    key = models.CharField(max_length=10, unique=True, verbose_name=_('identifier'))
    label = models.CharField(max_length=20, verbose_name=_('label'))
    path = models.CharField(max_length=255, verbose_name=_('link path'))
    regex = models.TextField(verbose_name=_('highlight regex'), validators=[validate_regex])
    parent = TreeForeignKey('self', verbose_name=_('parent item'), null=True, blank=True,
                            related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return self.label

    @property
    def pattern(self, cache={}):
        # A cache with a bad policy is an alias for memory leak
        # Thankfully, there will never be too many regexes to cache.
        if self.regex in cache:
            return cache[self.regex]
        else:
            pattern = cache[self.regex] = re.compile(self.regex, re.VERBOSE)
            return pattern


class BlogPostTag(models.Model):
    name = models.CharField(_('name'), max_length=40, unique=True)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)

    class Meta:
        verbose_name = _('blog tag')
        verbose_name_plural = _('blog tags')
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(verbose_name=_('post title'), max_length=100)
    authors = models.ManyToManyField(Profile, verbose_name=_('authors'), blank=True)
    slug = models.SlugField(verbose_name=_('slug'))
    visible = models.BooleanField(verbose_name=_('public visibility'), default=False)
    sticky = models.BooleanField(verbose_name=_('sticky'), default=False)
    publish_on = models.DateTimeField(verbose_name=_('publish after'))
    content = models.TextField(verbose_name=_('post content'))
    summary = models.TextField(verbose_name=_('post summary'), blank=True)
    og_image = models.CharField(verbose_name=_('OpenGraph image'), default='', max_length=150, blank=True)
    score = models.IntegerField(verbose_name=_('votes'), default=0)
    global_post = models.BooleanField(verbose_name=_('global post'), default=False,
                                      help_text=_('Display this blog post at the homepage.'))
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name=_('organization'),
                                     related_name='post_author_org', blank=True, null=True, db_index=True)
    tags = models.ManyToManyField('BlogPostTag', related_name='posts', verbose_name=_('tags'), blank=True)

    def __str__(self):
        return self.title

    def vote(self, delta):
        self.score += delta
        self.save(update_fields=['score'])

        # Only update contributions for global and personal posts
        if self.visible and self.organization is None:
            for author in self.authors.all():
                # Blog votes are counted as comment votes
                author.update_contribution_points(delta * settings.VNOJ_CP_COMMENT)

    def get_absolute_url(self):
        return reverse('blog_post', args=(self.id, self.slug))

    def can_see(self, user):
        # Post is public
        if self.visible and self.publish_on <= timezone.now():
            # Post is private to an organization
            if self.organization:
                if not user.is_authenticated:
                    return False
                if user.profile.organizations.filter(id=self.organization.pk).exists():
                    return True
                return self.is_editable_by(user)

            # Global or personal post should always be visible
            return True

        # Post is not public
        return self.is_editable_by(user)

    def is_editable_by(self, user):
        if not user.is_authenticated:
            return False
        if user.has_perm('judge.edit_all_post'):
            return True
        if self.organization:
            return self.organization.is_admin(user.profile) and \
                user.has_perm('judge.edit_organization_post') and \
                self.authors.filter(id=user.profile.id).exists()
        return self.authors.filter(id=user.profile.id).exists()

    class Meta:
        permissions = (
            ('edit_all_post', _('Edit all posts')),
            ('edit_organization_post', _('Edit organization posts')),
            ('mark_global_post', _('Mark post as global')),
            ('pin_post', _('Pin post')),
            ('manage_magazine_post', _('Manage magazine blog posts')),
        )
        verbose_name = _('blog post')
        verbose_name_plural = _('blog posts')


class BlogVote(models.Model):
    voter = models.ForeignKey(Profile, verbose_name=_('voter'), related_name='voted_blogs', on_delete=CASCADE)
    blog = models.ForeignKey(BlogPost, verbose_name=_('blog'), related_name='votes', on_delete=CASCADE)
    score = models.IntegerField(verbose_name=_('score'))

    class Meta:
        unique_together = ['voter', 'blog']
        verbose_name = _('blog vote')
        verbose_name_plural = _('blog votes')


class GlobalAnnouncementQuerySet(models.QuerySet):
    def update(self, **kwargs):
        rows = super().update(**kwargs)
        GlobalAnnouncement.clear_cache()
        return rows

    def delete(self):
        rows = super().delete()
        GlobalAnnouncement.clear_cache()
        return rows


class GlobalAnnouncement(models.Model):
    ALERT_TYPES = (
        ('alert-info', _('Info')),
        ('alert-warning', _('Warning')),
        ('alert-danger', _('Danger')),
        ('alert-success', _('Success')),
    )

    SAFE_TAGS = [
        'a', 'b', 'strong', 'i', 'em', 'u', 's', 'strike', 'span', 'code', 'br', 'p', 'small',
    ]
    SAFE_ATTRIBUTES = {
        'a': ['href', 'title', 'target', 'rel'],
        'span': ['class'],
        '*': ['class'],
    }

    message_en = models.TextField(
        verbose_name=_('English message'),
        blank=True,
        help_text=_('Announcement message in English.'),
    )
    message_vi = models.TextField(
        verbose_name=_('Vietnamese message'),
        blank=True,
        help_text=_('Announcement message in Vietnamese.'),
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        default='alert-info',
        verbose_name=_('alert type'),
        help_text=_('Bootstrap alert style class.'),
    )
    is_enabled = models.BooleanField(
        default=True,
        verbose_name=_('enabled'),
        help_text=_('Whether this announcement is actively displayed on the site.'),
    )
    is_dismissible = models.BooleanField(
        default=True,
        verbose_name=_('dismissible'),
        help_text=_('Whether users can dismiss this announcement.'),
    )
    dismissal_version = models.PositiveIntegerField(
        default=1,
        verbose_name=_('dismissal version'),
        help_text=_('Incrementing this will re-display the announcement to users who previously dismissed it.'),
    )
    valid_from = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('valid from'),
        help_text=_('Announcement visible from this time (optional).'),
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('valid until'),
        help_text=_('Announcement visible until this time (optional).'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))

    objects = GlobalAnnouncementQuerySet.as_manager()

    class Meta:
        verbose_name = _('announcement')
        verbose_name_plural = _('announcements')
        ordering = ('-id',)

    def clean(self):
        super().clean()
        if not (self.message_en and self.message_en.strip()) and not (self.message_vi and self.message_vi.strip()):
            raise ValidationError(_('At least one message (English or Vietnamese) must be provided.'))
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValidationError({'valid_until': _('Valid until must be after valid from.')})

    def __str__(self):
        msg = self.message_en or self.message_vi
        return msg[:50] + ('...' if len(msg) > 50 else '')

    def get_message(self, language=None):
        if language is None:
            language = get_language()
        if language == 'vi':
            return self.message_vi or self.message_en
        return self.message_en or self.message_vi

    def get_display_message(self, language=None):
        raw_message = self.get_message(language=language)
        if not raw_message:
            return ''
        cleaned = bleach.clean(
            raw_message,
            tags=self.SAFE_TAGS,
            attributes=self.SAFE_ATTRIBUTES,
            strip=True,
        )
        return mark_safe(cleaned)

    @property
    def message(self):
        return self.get_message()

    @property
    def display_message(self):
        return self.get_display_message()

    @property
    def alert_class(self):
        return self.alert_type

    @property
    def dismissal_key(self):
        return f'{self.id}_v{self.dismissal_version}'

    @property
    def content_hash(self):
        return self.dismissal_key

    @classmethod
    def clear_cache(cls):
        cache.delete('global_announcements')

    @classmethod
    def get_active(cls):
        cache_key = 'global_announcements'
        announcements = cache.get(cache_key)
        if announcements is None:
            now = timezone.now()
            qs = cls.objects.filter(is_enabled=True)
            qs = qs.filter(models.Q(valid_from__isnull=True) | models.Q(valid_from__lte=now))
            qs = qs.filter(models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now))
            qs = qs.annotate(
                severity=models.Case(
                    models.When(alert_type='alert-danger', then=models.Value(1)),
                    models.When(alert_type='alert-warning', then=models.Value(2)),
                    models.When(alert_type='alert-info', then=models.Value(3)),
                    models.When(alert_type='alert-success', then=models.Value(4)),
                    default=models.Value(5),
                    output_field=models.IntegerField(),
                )
            ).order_by('is_dismissible', 'severity', '-id')
            announcements = list(qs[:5])
            cache.set(cache_key, announcements, 300)
        return announcements
