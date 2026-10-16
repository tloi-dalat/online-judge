from django.apps import AppConfig
from django.db import DatabaseError
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy


def create_missing_profiles(using, **kwargs):
    from django.contrib.auth.models import User
    from judge.models import Language, Profile

    try:
        users = list(User.objects.using(using).filter(profile=None))
        if users:
            lang = Language.get_default_language()
            for user in users:
                Profile(user=user, language=lang).save(using=using)
    except DatabaseError:
        pass


class JudgeAppConfig(AppConfig):
    name = 'judge'
    verbose_name = gettext_lazy('Online Judge')

    def ready(self):
        # WARNING: AS THIS IS NOT A FUNCTIONAL PROGRAMMING LANGUAGE,
        #          OPERATIONS MAY HAVE SIDE EFFECTS.
        #          DO NOT REMOVE THINKING THE IMPORT IS UNUSED.
        # noinspection PyUnresolvedReferences
        from . import signals, jinja2  # noqa: F401, imported for side effects

        from django.db.models import fields
        fields.BLANK_CHOICE_LABEL = fields.BLANK_CHOICE_DASH[0][1]

        post_migrate.connect(create_missing_profiles, sender=self, dispatch_uid='judge.create_missing_profiles')
