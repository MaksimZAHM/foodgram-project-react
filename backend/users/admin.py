from django.contrib import admin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': [('email', 'first_name'), ('username', 'last_name')]
        }),
        ('Права доступа', {
            'classes': ('collapse',),
            'fields': [('is_staff', 'is_superuser')],
        }),
    )
    list_display = ('id', 'email', 'username', 'first_name', 'last_name')
    list_display_links = ('id', 'email', 'username')
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'subscribe'
    )
    list_filter = ('user', 'subscribe')
    search_fields = ('user_username', 'user_email')
