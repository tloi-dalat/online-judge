import os
import re
import shutil
import subprocess
import sys
import tempfile

import django
import polib
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.makemessages import check_programs

SOURCE_APPS = (
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.flatpages', 'django.contrib.redirects',
    'django.contrib.sites', 'registration', 'wpadmin', 'oauth2_provider', 'impersonate', 'chunked_upload',
    'social_django', 'reversion', 'sortedm2m',
)
DOMAINS = ('django', 'djangojs')
SOURCE_LOCALE = 'en'
SOURCE_PLURAL_FORMS = 'nplurals=2; plural=(n != 1);'


def catalog_path(locale_dir, locale, domain):
    return os.path.join(locale_dir, locale, 'LC_MESSAGES', '%s.po' % domain)


def nplurals(plural_forms):
    match = re.search(r'nplurals\s*=\s*(\d+)', plural_forms or '')
    return int(match.group(1)) if match else None


class Command(BaseCommand):
    help = ('Update locale_django/ with the strings of Django and third-party apps (SOURCE_APPS) that no catalog '
            'Django loads translates.')

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--locale', '-l', default=[], action='append',
            help='Updates the message files for the given locale (e.g. vi). Can be used multiple times.',
        )
        parser.add_argument(
            '--all', '-a', action='store_true',
            help='Updates the message files for all existing locales (the default).',
        )

    def handle(self, *args, **options):
        requested, process_all = options['locale'], options['all']
        check_programs('msgmerge', 'msgattrib', 'msgfmt')

        self.target_dir = os.path.abspath(os.path.join(settings.BASE_DIR, 'locale_django'))
        locale_paths = [os.path.abspath(path) for path in settings.LOCALE_PATHS]
        if self.target_dir not in locale_paths:
            raise CommandError('%s is not in LOCALE_PATHS, so Django would never load it.' % self.target_dir)
        self.project_dirs = [path for path in locale_paths if path != self.target_dir]

        self.source_apps = []
        for name in SOURCE_APPS:
            app = next((app for app in apps.get_app_configs() if app.name == name), None)
            if app is None:
                raise CommandError('%s is not in INSTALLED_APPS.' % name)
            self.source_apps.append(app)

        locales = sorted(
            name for name in os.listdir(self.project_dirs[0])
            if name != SOURCE_LOCALE and os.path.isdir(os.path.join(self.project_dirs[0], name, 'LC_MESSAGES'))
        )
        selected = set(locales) | {SOURCE_LOCALE}
        if requested and not process_all:
            unknown = sorted(set(requested) - selected)
            if unknown:
                raise CommandError('No catalog for %s in %s; run makemessages for it first.' % (
                    ', '.join(unknown), self.project_dirs[0]))
            selected = set(requested)

        for domain in DOMAINS:
            source = self.source_entries(domain)
            if not source:
                continue
            missing = {locale: self.missing_keys(source, locale, domain) for locale in locales}
            for locale in locales:
                if locale in selected:
                    self.write(source, missing[locale], locale, domain)
            if SOURCE_LOCALE in selected:
                self.write(source, set().union(*missing.values()), SOURCE_LOCALE, domain)

    def load(self, locale_dir, locale, domain):
        path = catalog_path(locale_dir, locale, domain)
        if os.path.exists(path):
            return polib.pofile(path)
        if os.path.exists(path[:-3] + '.mo'):
            return polib.mofile(path[:-3] + '.mo')
        return None

    def source_catalog(self, app, domain):
        if os.path.isdir(os.path.join(app.path, 'locale', SOURCE_LOCALE, 'LC_MESSAGES')):
            return self.load(os.path.join(app.path, 'locale'), SOURCE_LOCALE, domain)
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, os.path.basename(app.path))
            shutil.copytree(app.path, root, ignore=shutil.ignore_patterns('__pycache__', 'locale', 'tests'))
            os.mkdir(os.path.join(root, 'locale'))
            args = [sys.executable, '-m', 'django', 'makemessages', '-l', SOURCE_LOCALE, '-d', domain]
            if domain == 'django':
                args += ['-e', 'py,html,txt']
            env = {key: value for key, value in os.environ.items() if key != 'DJANGO_SETTINGS_MODULE'}
            result = subprocess.run(args, cwd=root, env=env, capture_output=True, text=True)
            if result.returncode:
                raise CommandError('Extracting the strings of %s failed:\n%s' % (app.name, result.stderr))
            return self.load(os.path.join(root, 'locale'), SOURCE_LOCALE, domain)

    def source_entries(self, domain):
        entries = {}
        for app in self.source_apps:
            prefix = 'django' if app.name.startswith('django.') else app.name.split('.')[0]
            for entry in self.source_catalog(app, domain) or ():
                if entry.obsolete:
                    continue
                occurrences = [('%s/%s' % (prefix, path.removeprefix('./')), '') for path, line in entry.occurrences]
                key = (entry.msgctxt, entry.msgid, entry.msgid_plural)
                if key in entries:
                    known = entries[key].occurrences
                    known.extend(occurrence for occurrence in occurrences if occurrence not in known)
                    continue
                entries[key] = polib.POEntry(
                    msgctxt=entry.msgctxt, msgid=entry.msgid, msgid_plural=entry.msgid_plural, msgstr='',
                    msgstr_plural={0: '', 1: ''} if entry.msgid_plural else {},
                    flags=[flag for flag in entry.flags if flag != 'fuzzy'],
                    comment=entry.comment, occurrences=occurrences,
                )
        return entries

    def covering_dirs(self, domain):
        if domain == 'django':
            app_dirs = [os.path.join(app.path, 'locale') for app in apps.get_app_configs()]
        else:
            app_dirs = [os.path.join(app.path, 'locale') for app in self.source_apps]
        django_dir = os.path.join(os.path.dirname(django.__file__), 'conf', 'locale')
        return self.project_dirs + app_dirs + [django_dir]

    def js_plural_forms(self, locale):
        for locale_dir in self.covering_dirs('djangojs'):
            catalog = self.load(locale_dir, locale, 'djangojs')
            if catalog is not None and catalog.metadata.get('Plural-Forms'):
                return catalog.metadata['Plural-Forms']
        return None

    def missing_keys(self, source, locale, domain):
        js_nplurals = nplurals(self.js_plural_forms(locale)) if domain == 'djangojs' else None
        covered = set()
        for locale_dir in self.covering_dirs(domain):
            catalog = self.load(locale_dir, locale, domain)
            if catalog is None:
                continue
            catalog_nplurals = nplurals(catalog.metadata.get('Plural-Forms'))
            for entry in catalog:
                if entry.obsolete or not entry.translated():
                    continue
                if entry.msgid_plural and js_nplurals and catalog_nplurals != js_nplurals:
                    continue
                covered.add((entry.msgctxt or None, entry.msgid, bool(entry.msgid_plural)))
        return {
            key for key in source
            if (key[0] or None, key[1], bool(key[2])) not in covered
        }

    def plural_forms(self, locale, domain):
        if locale == SOURCE_LOCALE:
            return SOURCE_PLURAL_FORMS
        if domain == 'djangojs':
            return self.js_plural_forms(locale)
        django_dir = os.path.join(os.path.dirname(django.__file__), 'conf', 'locale')
        catalog = self.load(django_dir, locale, 'django')
        return catalog.metadata.get('Plural-Forms') if catalog is not None else None

    def write(self, source, keys, locale, domain):
        path = catalog_path(self.target_dir, locale, domain)
        plural_forms = self.plural_forms(locale, domain)
        if not plural_forms:
            raise CommandError('No Plural-Forms known for %s; create %s by hand first.' % (locale, path))

        pot = polib.POFile(wrapwidth=79)
        pot.metadata = {
            'Project-Id-Version': 'Django',
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=UTF-8',
            'Content-Transfer-Encoding': '8bit',
        }
        pot.extend(entry for key, entry in source.items() if key in keys)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            existing = polib.pofile(path)
            if nplurals(existing.metadata.get('Plural-Forms')) != nplurals(plural_forms):
                raise CommandError('%s has Plural-Forms "%s", but it must be "%s".' % (
                    path, existing.metadata.get('Plural-Forms'), plural_forms))
            with tempfile.TemporaryDirectory() as tmp:
                pot_path = os.path.join(tmp, '%s.pot' % domain)
                pot.save(pot_path)
                self.run('msgmerge', '-q', '--backup=none', '--previous', '--update', path, pot_path)
        else:
            pot.header = (
                'Translations of Django strings that no catalog Django loads covers yet.\n'
                'Generated by `manage.py makedjangomessages`; translate the empty and fuzzy entries.'
            )
            pot.metadata.update({
                'Project-Id-Version': 'Django overrides',
                'Language': locale,
                'Plural-Forms': plural_forms,
            })
            for entry in pot:
                if entry.msgid_plural:
                    entry.msgstr_plural = {index: '' for index in range(nplurals(plural_forms))}
            pot.save(path)
        self.run('msgattrib', '--no-obsolete', '-o', path, path)
        self.run('msgfmt', '--check', '-o', os.devnull, path)

        catalog = polib.pofile(path)
        summary = '%s: %d messages' % (os.path.relpath(path, settings.BASE_DIR), len(catalog))
        if locale != SOURCE_LOCALE:
            untranslated = len(catalog.untranslated_entries())
            fuzzy = len(catalog.fuzzy_entries())
            summary += ', %d untranslated, %d fuzzy' % (untranslated, fuzzy)
            if untranslated or fuzzy:
                summary = self.style.WARNING(summary)
        self.stdout.write(summary)

    def run(self, *args):
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode:
            raise CommandError('%s failed:\n%s' % (args[0], result.stderr))
