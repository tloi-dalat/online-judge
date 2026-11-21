import pyotp
from django.test import SimpleTestCase

from judge.views.two_factor import TOTPEnableView


class TOTPQRCodeTestCase(SimpleTestCase):
    def test_render_qr_code(self):
        uri = TOTPEnableView.render_qr_code('user', pyotp.random_base32())
        self.assertTrue(uri.startswith('data:image/png;base64,'))
