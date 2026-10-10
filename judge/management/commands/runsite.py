import os
import subprocess
import sys

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils.autoreload import DJANGO_AUTORELOAD_ENV


class Command(BaseCommand):
    help = ('Build the styles, collect static files, compile translations, run the system checks, '
            'then start the development server on 0.0.0.0:<port>.')

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument('port', nargs='?', type=int, default=8000, help='port to listen on (default: 8000)')

    def step(self, name):
        self.stdout.write(self.style.MIGRATE_HEADING('==> %s' % name))

    def compilemessages_ignore_patterns(self):
        patterns = ['node_modules']
        venv = os.path.relpath(sys.prefix)
        if venv != os.curdir and not venv.startswith(os.pardir):
            patterns.append(venv)
        return patterns

    def handle(self, *args, port, **options):
        if not 1 <= port <= 65535:
            raise CommandError('Port must be between 1 and 65535, got %d.' % port)

        if os.environ.get(DJANGO_AUTORELOAD_ENV) != 'true':
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

            self.step('runserver 0.0.0.0:%d' % port)

        call_command('runserver', '0.0.0.0:%d' % port)
