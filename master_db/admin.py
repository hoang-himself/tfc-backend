from django.contrib import admin
from django.contrib.admin.models import (LogEntry, DELETION)
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .forms import (CustomUserCreationForm, CustomUserChangeForm)
from .models import (
    Branch, Calendar, Setting, CustomUser, Course, ClassMetadata, Schedule,
    Session
)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {
            'fields': ('password', )
        }),
        (
            'Personal info',
            {
                'fields':
                    (
                        'email',
                        'first_name',
                        'last_name',
                        'birth_date',
                        'mobile',
                        # TODO 'gender',
                        'male',
                        'address',
                        'avatar',
                    )
            }
        ),
        (
            'Permissions', {
                'fields':
                    (
                        'is_active',
                        'is_staff',
                        'is_superuser',
                        'groups',
                        'user_permissions',
                    ),
            }
        ),
        (
            'Important dates', {
                'fields': (
                    'date_joined',
                    'date_updated',
                    'last_login',
                )
            }
        ),
    )
    readonly_fields = (
        'date_joined',
        'date_updated',
        'last_login',
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide', ),
                'fields':
                    (
                        'email',
                        'first_name',
                        'last_name',
                        'birth_date',
                        'mobile',
                        # TODO 'gender',
                        'male',
                        'address',
                        'avatar',
                        'password1',
                        'password2',
                    ),
            }
        ),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email', )
    filter_horizontal = (
        'groups',
        'user_permissions',
    )


class CustomLogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    list_filter = ['user', 'content_type', 'action_flag']

    search_fields = ['object_repr', 'change_message']

    list_display = [
        'action_time',
        'user',
        'content_type',
        'action_flag',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    # Open the edited object by clicking on its link
    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse(
                    'admin:%s_%s_change' % (ct.app_label, ct.model),
                    args=[obj.object_id]
                ),
                escape(obj.object_repr),
            )
        return mark_safe(link)

    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"


admin.site.register(Branch)
admin.site.register(Calendar)
admin.site.register(Setting)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course)
admin.site.register(ClassMetadata)
admin.site.register(Schedule)
admin.site.register(Session)
admin.site.register(LogEntry, CustomLogEntryAdmin)
