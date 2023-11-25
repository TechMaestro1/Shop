from django.contrib import admin
from django.utils.html import mark_safe
from E_Shop_API.E_Shop_Users.models import Clients


@admin.register(Clients)
class UserAdmin(admin.ModelAdmin):
    """ Register User model in admin panel """
    list_display = ('get_photo', 'first_name', 'last_name', 'email', 'created_at', 'is_staff', 'is_superuser',
                    'is_active')
    list_display_links = ('first_name', 'last_name', 'email',)
    search_fields = ('first_name', 'last_name', 'email', 'created_at')
    readonly_fields = ('get_photo', 'created_at', 'updated_at')
    save_on_top = True

    def get_photo(self, obj):
        """ Method which return img in admin panel """
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="100">')
        else:
            return '-'

    get_photo.short_description = 'Photo'
