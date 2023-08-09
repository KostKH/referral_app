from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import Group, UserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class MyUserAdmin(UserAdmin):
    '''Класс для вывода на странице админа
    информации о пользователе.'''
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (
            _('Personal info'),
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'invite_code',
                    'granted_code',
                    'verification_code',
                    'verif_cutoff_timestamp',
                )
            }
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('phone', 'email', 'first_name', 'last_name',
                           'invite_code', 'granted_code',
                           'password1', 'password2'),
            },
        ),
    )
    list_display = (
        'id',
        'phone',
        'email',
        'first_name',
        'last_name',
        'invite_code',
        'granted_code',
        'verification_code',
        'verif_cutoff_timestamp',
        'is_staff',
    )
    list_filter = ('phone',)
    ordering = ('id',)
    search_fields = ('phone', 'first_name', 'last_name', 'invite_code')


admin.site.register(User, MyUserAdmin)
admin.site.unregister(Group)
