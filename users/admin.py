from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User
    ordering = ['id']
    list_display = [
        'first_name',
        'last_name',
        'phone_number',

        'is_staff',
        'is_superuser',
        'is_active',
    ]

    search_fields = [
        'first_name',
        'last_name',
        'phone_number',
    ]

    fieldsets = (

        (
            'Informations utilisateur',
            {
                'fields': (
                     'type_user',
                    'phone_number',
                    'first_name',
                    'last_name',
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
                    'type_user',
                    'first_name',
                    'last_name',
                    'phone_number',
                    'password1',
                    'password2',
                  
                    
                ),
            },
        ),
    )