from django.contrib import admin
from .models import WebsiteSettings, Banner, Blog, Testimonial, Product, Category, ArtworkRequest, MembershipRequest, MediaLibrary

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
    list_display = ('customer_name', 'review', 'created_at', 'updated_at')
    list_filter = ('review', 'created_at')
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


@admin.register(ArtworkRequest)
class ArtworkRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'organization_name', 'user_type', 'order_quantity', 'created_at')
    list_filter = ('user_type', 'team_attribute', 'twill_type', 'need_home_away_mockup', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'organization_name', 'address')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'phone', 'instagram', 'address')
        }),
        ('Organization Details', {
            'fields': ('organization_name', 'user_type', 'order_quantity', 'team_color')
        }),
        ('Artwork Specifications', {
            'fields': ('need_home_away_mockup', 'team_attribute', 'twill_type')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'organization', 'user_type', 'twill_type', 'state', 'created_at')
    list_filter = ('user_type', 'twill_type', 'state', 'created_at')
    search_fields = ('name', 'email', 'phone', 'organization', 'mailing_address')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'mailing_address')
        }),
        ('Organization Details', {
            'fields': ('organization', 'state', 'zip_code')
        }),
        ('Membership Information', {
            'fields': ('user_type', 'twill_type', 'sport')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MediaLibrary)
class MediaLibraryAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'get_file_size_display', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('file_name',)
    readonly_fields = ('id', 'file_name', 'file_size', 'created_at', 'updated_at', 'get_file_size_display')
    fieldsets = (
        ('File Information', {
            'fields': ('image', 'file_name', 'file_size', 'get_file_size_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_file_size_display(self, obj):
        """Display human-readable file size in admin"""
        return obj.get_file_size_display()
    get_file_size_display.short_description = 'File Size'
