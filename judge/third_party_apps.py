from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from impersonate.apps import AccountsConfig
from oauth2_provider.apps import DOTConfig
from registration.apps import RegistrationConfig
from social_django.apps import PythonSocialAuthConfig


def name_models(app_config, names):
    for model_name, (singular, plural) in names.items():
        meta = app_config.get_model(model_name)._meta
        meta.verbose_name = singular
        meta.verbose_name_plural = plural


def label_fields(app_config, labels):
    for model_name, fields in labels.items():
        meta = app_config.get_model(model_name)._meta
        for field_name, label in fields.items():
            meta.get_field(field_name).verbose_name = label


class ChunkedUploadConfig(AppConfig):
    name = 'chunked_upload'
    verbose_name = _('Chunked upload')

    def ready(self):
        super().ready()
        name_models(self, {
            'ChunkedUpload': (pgettext_lazy('third-party model', 'chunked upload'),
                              pgettext_lazy('third-party model', 'chunked uploads')),
        })
        label_fields(self, {
            'ChunkedUpload': {
                'upload_id': pgettext_lazy('third-party field', 'upload ID'),
                'file': pgettext_lazy('third-party field', 'file'),
                'filename': pgettext_lazy('third-party field', 'filename'),
                'offset': pgettext_lazy('third-party field', 'offset'),
                'created_on': pgettext_lazy('third-party field', 'created on'),
                'status': pgettext_lazy('third-party field', 'status'),
                'completed_on': pgettext_lazy('third-party field', 'completed on'),
                'user': pgettext_lazy('third-party field', 'user'),
            },
        })
        status = self.get_model('ChunkedUpload')._meta.get_field('status')
        status.choices = [(value, label) for (value, _label), label in zip(status.choices, (
            pgettext_lazy('third-party field', 'Uploading'),
            pgettext_lazy('third-party field', 'Complete'),
        ))]


class ImpersonateConfig(AccountsConfig):
    verbose_name = _('Impersonate')

    def ready(self):
        super().ready()
        name_models(self, {
            'ImpersonationLog': (pgettext_lazy('third-party model', 'impersonation log'),
                                 pgettext_lazy('third-party model', 'impersonation logs')),
        })
        label_fields(self, {
            'ImpersonationLog': {
                'impersonator': pgettext_lazy('third-party field', 'impersonator'),
                'impersonating': pgettext_lazy('third-party field', 'impersonated user'),
                'session_key': pgettext_lazy('third-party field', 'session key'),
                'session_started_at': pgettext_lazy('third-party field', 'session started at'),
                'session_ended_at': pgettext_lazy('third-party field', 'session ended at'),
            },
        })

        from impersonate import admin as impersonate_admin

        def session_state_lookups(filter, request, model_admin):
            return (
                ('incomplete', pgettext_lazy('third-party admin', 'Incomplete')),
                ('complete', pgettext_lazy('third-party admin', 'Complete')),
            )

        impersonate_admin.SessionStateFilter.title = pgettext_lazy('third-party admin', 'session state')
        impersonate_admin.SessionStateFilter.lookups = session_state_lookups
        impersonate_admin.ImpersonatorFilter.title = pgettext_lazy('third-party field', 'impersonator')


class OAuth2ProviderConfig(DOTConfig):
    verbose_name = _('Django OAuth Toolkit')

    def ready(self):
        super().ready()
        name_models(self, {
            'Application': (pgettext_lazy('third-party model', 'application'),
                            pgettext_lazy('third-party model', 'applications')),
            'Grant': (pgettext_lazy('third-party model', 'grant'),
                      pgettext_lazy('third-party model', 'grants')),
            'AccessToken': (pgettext_lazy('third-party model', 'access token'),
                            pgettext_lazy('third-party model', 'access tokens')),
            'RefreshToken': (pgettext_lazy('third-party model', 'refresh token'),
                             pgettext_lazy('third-party model', 'refresh tokens')),
            'IDToken': (pgettext_lazy('third-party model', 'id token'),
                        pgettext_lazy('third-party model', 'id tokens')),
            'DeviceGrant': (pgettext_lazy('third-party model', 'device grant'),
                            pgettext_lazy('third-party model', 'device grants')),
        })

        from oauth2_provider import admin as oauth2_admin

        oauth2_admin.AccessTokenAdmin.revoke_tokens.short_description = pgettext_lazy(
            'third-party admin', 'Revoke selected access tokens')
        oauth2_admin.RefreshTokenAdmin.revoke_tokens.short_description = pgettext_lazy(
            'third-party admin', 'Revoke selected refresh tokens')
        oauth2_admin.AccessTokenAdmin.masked_token.short_description = pgettext_lazy('third-party field', 'token')
        oauth2_admin.RefreshTokenAdmin.masked_token.short_description = pgettext_lazy('third-party field', 'token')
        oauth2_admin.GrantAdmin.masked_code.short_description = pgettext_lazy('third-party field', 'code')


class RegistrationAppConfig(RegistrationConfig):
    verbose_name = _('Registration')

    def ready(self):
        super().ready()
        label_fields(self, {
            'RegistrationProfile': {'activated': pgettext_lazy('third-party field', 'activated')},
            'SupervisedRegistrationProfile': {'activated': pgettext_lazy('third-party field', 'activated')},
        })


class SocialAuthConfig(PythonSocialAuthConfig):
    verbose_name = _('Python Social Auth')

    def ready(self):
        super().ready()
        name_models(self, {
            'UserSocialAuth': (pgettext_lazy('third-party model', 'user social auth'),
                               pgettext_lazy('third-party model', 'user social auths')),
            'Nonce': (pgettext_lazy('third-party model', 'nonce'),
                      pgettext_lazy('third-party model', 'nonces')),
            'Association': (pgettext_lazy('third-party model', 'association'),
                            pgettext_lazy('third-party model', 'associations')),
            'Code': (pgettext_lazy('third-party model', 'code'),
                     pgettext_lazy('third-party model', 'codes')),
            'Partial': (pgettext_lazy('third-party model', 'partial'),
                        pgettext_lazy('third-party model', 'partials')),
        })
        label_fields(self, {
            'UserSocialAuth': {
                'user': pgettext_lazy('third-party field', 'user'),
                'provider': pgettext_lazy('third-party field', 'provider'),
                'id_key': pgettext_lazy('third-party field', 'ID key'),
                'uid': pgettext_lazy('third-party field', 'UID'),
                'extra_data': pgettext_lazy('third-party field', 'extra data'),
                'created': pgettext_lazy('third-party field', 'created'),
                'modified': pgettext_lazy('third-party field', 'modified'),
            },
            'Nonce': {
                'server_url': pgettext_lazy('third-party field', 'server URL'),
                'timestamp': pgettext_lazy('third-party field', 'timestamp'),
                'salt': pgettext_lazy('third-party field', 'salt'),
            },
            'Association': {
                'server_url': pgettext_lazy('third-party field', 'server URL'),
                'handle': pgettext_lazy('third-party field', 'handle'),
                'secret': pgettext_lazy('third-party field', 'secret'),
                'issued': pgettext_lazy('third-party field', 'issued'),
                'lifetime': pgettext_lazy('third-party field', 'lifetime'),
                'assoc_type': pgettext_lazy('third-party field', 'association type'),
            },
            'Code': {
                'email': pgettext_lazy('third-party field', 'email'),
                'code': pgettext_lazy('third-party field', 'code'),
                'verified': pgettext_lazy('third-party field', 'verified'),
                'timestamp': pgettext_lazy('third-party field', 'timestamp'),
            },
            'Partial': {
                'token': pgettext_lazy('third-party field', 'token'),
                'next_step': pgettext_lazy('third-party field', 'next step'),
                'backend': pgettext_lazy('third-party field', 'backend'),
                'data': pgettext_lazy('third-party field', 'data'),
                'timestamp': pgettext_lazy('third-party field', 'timestamp'),
            },
        })
