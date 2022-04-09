from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """ Администрирование пользователей."""
    list_display = ('id', 'email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'username')
    search_fields = ('username', 'email')
    ordering = ('username',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
