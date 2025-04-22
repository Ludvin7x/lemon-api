from django.contrib import admin
from .models import MenuItem, Category, Order, OrderItem
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'get_groups')

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = _('Groups')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(MenuItem)
admin.site.register(Category)