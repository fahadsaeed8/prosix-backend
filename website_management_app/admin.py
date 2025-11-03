from django.contrib import admin
from .models import WebsiteSettings, Banner, Blog, Testimonial, Product, Category

# Register your models here.
@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('website_name', 'tagline', 'primary_color', 'accent_color', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton)
        if WebsiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'status', 'created_at', 'updated_at')
    list_filter = ('position', 'status', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_at', 'updated_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'created_at', 'updated_at')
    search_fields = ('customer_name', 'text')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'sku', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'icon', 'color', 'created_at', 'updated_at')
    search_fields = ('category_name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
