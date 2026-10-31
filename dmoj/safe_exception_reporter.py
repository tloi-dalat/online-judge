import re

from django.views.debug import SafeExceptionReporterFilter

URL_CREDENTIALS = re.compile(r'(://[^/@\s]*?:)[^/@\s]+@')


class SafeURLExceptionReporterFilter(SafeExceptionReporterFilter):
    hidden_settings = re.compile('API|TOKEN|KEY|SECRET|PASS|SIGNATURE|HTTP_COOKIE|WEBHOOK', flags=re.I)

    def cleanse_setting(self, key, value):
        value = super().cleanse_setting(key, value)
        if isinstance(value, str):
            value = URL_CREDENTIALS.sub(r'\g<1>' + self.cleansed_substitute + '@', value)
        return value
