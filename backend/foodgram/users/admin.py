from django.contrib import admin

from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    """ Администрирование пользователей."""
    list_display = ('id', 'email', 'username')
    list_filter = ('email', 'username')
    search_fields = ('username', 'email')
    ordering = ('username',)
    empty_value_display = '-пусто-'


admin.site.register(CustomUser, CustomUserAdmin)
