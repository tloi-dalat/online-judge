from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wpadmin.menu.custom import CustomModelLeftMenu
from wpadmin.menu.items import MenuItem
from wpadmin.utils import get_admin_site_name


class CustomModelLeftMenuWithDashboard(CustomModelLeftMenu):
    def init_with_context(self, context):
        self.children.append(MenuItem(
            title=_('Dashboard'),
            icon='fa-tachometer',
            url=reverse('%s:index' % get_admin_site_name(context)),
            description=_('Dashboard'),
        ))
        super().init_with_context(context)
