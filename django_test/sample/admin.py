from django.contrib import admin

from sample import models


class TestUserAdmin(admin.ModelAdmin):
    """Admin page for TestUser."""

    list_display = ('username', 'first_name', 'last_name', 'email')


admin.site.register(models.TestUser, TestUserAdmin)
