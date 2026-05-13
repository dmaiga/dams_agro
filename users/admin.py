from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    ordering = ['id']

    list_display = [
        'phone_number',
        'is_staff',
        'is_superuser',
        'is_active',
    ]

    search_fields = [
        'phone_number',
    ]

    fieldsets = (

        (
            'Informations utilisateur',
            {
                'fields': (
                    'phone_number',
                    'password',
                )
            }
        ),

        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            }
        ),

        (
            'Dates importantes',
            {
                'fields': (
                    'last_login',
                    'date_joined',
                )
            }
        ),
    )

    add_fieldsets = (

        (
            None,
            {
                'classes': ('wide',),

                'fields': (
                    'phone_number',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_superuser',
                    'is_active',
                ),
            },
        ),
    )