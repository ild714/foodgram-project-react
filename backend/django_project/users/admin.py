from django.contrib import admin

from users.models import (
    CustomUser
)


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'password'
    )
    search_fields = ('username',)


admin.site.register(CustomUser, UserAdmin)