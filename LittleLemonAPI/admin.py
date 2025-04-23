from django.contrib import admin
from .models import MenuItem, Category, Order
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Custom User Admin to display groups
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_superuser', 'get_groups'
    )

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = _('Groups')

# Unregister default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# MenuItem admin configuration
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'featured')
    search_fields = ['title', 'category__title']
    ordering = ['price']
    list_filter = ['category', 'featured']

# Category admin configuration
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ['title']
    list_filter = ['title']

# Order admin configuration
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'date')
    search_fields = ['user__username', 'status']
    list_filter = ['status', 'date']
    ordering = ['-total']