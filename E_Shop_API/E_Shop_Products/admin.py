from django.contrib import admin
from django.utils.html import format_html
from E_Shop_API.E_Shop_Products.models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('get_photo', 'name', 'count', 'price', 'updated_at', 'active')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    list_editable = ('active',)
    list_filter = ('description', 'price')
    readonly_fields = ('created_at', 'updated_at')
    save_on_top = True
    list_per_page = 20
    inlines = [ProductImageInline]

    def get_photo(self, obj):
        """ Method to return image in admin panel """
        if obj.photos.exists():
            # Assuming you want to display the first photo
            photo = obj.photos.first()
            return format_html('<img src="{}" width="100">', photo.image.url)
        return '-'

    get_photo.short_description = 'Photo'


admin.site.register(ProductImage)
