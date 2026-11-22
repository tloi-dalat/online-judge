import os
import subprocess
import sys

from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils.autoreload import DJANGO_AUTORELOAD_ENV


class Command(RunserverCommand):
    help = ('Build the styles, collect static files, compile translations and run the system checks, '
            'then start the development server. Takes the same arguments as runserver.')

    def step(self, name):
        self.stdout.write(self.style.MIGRATE_HEADING('==> %s' % name))

    def compilemessages_ignore_patterns(self):
        patterns = ['node_modules']
        venv = os.path.relpath(sys.prefix)
        if venv != os.curdir and not venv.startswith(os.pardir):
            patterns.append(venv)
        return patterns

    def build(self):
        self.step('./make_style.sh')
        try:
            subprocess.run([os.path.join(settings.BASE_DIR, 'make_style.sh')], cwd=settings.BASE_DIR, check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            raise CommandError('make_style.sh failed: %s' % e)

        self.step('collectstatic')
        call_command('collectstatic', interactive=False)

        self.step('compilemessages')
        call_command('compilemessages', ignore_patterns=self.compilemessages_ignore_patterns())

        self.step('compilejsi18n')
        call_command('compilejsi18n')

        self.step('check')
        call_command('check')

        self.step('runserver')

    def run(self, **options):
        if os.environ.get(DJANGO_AUTORELOAD_ENV) != 'true':
            self.build()
        super().run(**options)
