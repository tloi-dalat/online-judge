from django.contrib.admin import ModelAdmin, display
from django.contrib.admin.options import StackedInline
from django.forms import ModelForm
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from judge.models import TicketMessage
from judge.widgets import AdminHeavySelect2MultipleWidget, AdminHeavySelect2Widget, AdminMartorWidget


class TicketMessageForm(ModelForm):
    class Meta:
        widgets = {
            'user': AdminHeavySelect2Widget(data_view='profile_select2'),
            'body': AdminMartorWidget(attrs={'data-markdownfy-url': reverse_lazy('ticket_preview')}),
        }


class TicketMessageInline(StackedInline):
    model = TicketMessage
    form = TicketMessageForm
    fields = ('user', 'body', 'action')
    readonly_fields = ('action',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user__user')


class TicketForm(ModelForm):
    class Meta:
        widgets = {
            'user': AdminHeavySelect2Widget(data_view='profile_select2'),
            'assignees': AdminHeavySelect2MultipleWidget(data_view='profile_select2'),
        }


class TicketAdmin(ModelAdmin):
    fields = ('title', 'time', 'user', 'assignees', 'content_type', 'object_id', 'notes')
    readonly_fields = ('time',)
    list_display = ('title', 'user', 'time', 'linked_item_display')
    inlines = [TicketMessageInline]
    form = TicketForm
    date_hierarchy = 'time'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user__user').prefetch_related('linked_item')

    @display(description=_('linked item'))
    def linked_item_display(self, obj):
        return obj.linked_item
