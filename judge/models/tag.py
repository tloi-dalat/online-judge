from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CASCADE
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from judge.models.profile import Profile


class TagGroup(models.Model):
    code = models.CharField(max_length=30, verbose_name=_('Tag group ID'), unique=True)
    name = models.CharField(max_length=100, verbose_name=_('Tag group name'))

    class Meta:
        verbose_name = _('tag group')
        verbose_name_plural = _('tag groups')

    def __str__(self):
        return self.name


class Tag(models.Model):
    code = models.CharField(max_length=30, verbose_name=_('Tag ID'), unique=True, db_index=True)
    name = models.CharField(max_length=100, verbose_name=_('Tag name'), db_index=True)
    group = models.ForeignKey(TagGroup, related_name='tags', verbose_name=_('Parent tag group'), on_delete=CASCADE)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name


class TagProblem(models.Model):
    code = models.CharField(max_length=32, verbose_name=_('problem code'), unique=True, db_index=True,
                            validators=[RegexValidator('^[a-zA-Z0-9_]+$', _('Problem code must be ^[a-zA-Z0-9_]+$'))],
                            help_text=_('A short, unique code for the problem, '
                                        'used in the url after /tag/'))
    name = models.CharField(max_length=100, verbose_name=_('problem name'), db_index=True,
                            help_text=_('The full name of the problem, '
                                        'as shown in the problem list.'))
    link = models.URLField(max_length=200, verbose_name=_('Problem URL'),
                           help_text=_('Full URL to the problem.'))
    judge = models.CharField(max_length=30, verbose_name=_('Online Judge'), blank=True, null=True, db_index=True,
                             help_text=_('Original OJ of the problem'))

    tag = models.ManyToManyField(Tag, through='TagData', related_name='tags', verbose_name=_('Tag'))

    class Meta:
        verbose_name = _('tag problem')
        verbose_name_plural = _('tag problems')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tagproblem_detail', args=(self.code,))


class TagData(models.Model):
    assigner = models.ForeignKey(Profile, verbose_name=_('Assigner'), on_delete=CASCADE)
    tag = models.ForeignKey(Tag, verbose_name=_('Tag'), on_delete=CASCADE)
    problem = models.ForeignKey(TagProblem, verbose_name=_('problem'), on_delete=CASCADE)

    class Meta:
        verbose_name = _('tag data')
        verbose_name_plural = _('tag data')
        unique_together = ('tag', 'problem')

    def __str__(self):
        return ''
