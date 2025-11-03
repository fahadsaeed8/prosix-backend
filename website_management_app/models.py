from django.db import models

# Create your models here.

POSITION_CHOICES = [
    ('hero_section', 'Hero Section'),
    ('sidebar', 'Sidebar'),
    ('footer', 'Footer'),
    ('popup', 'Popup'),
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

BLOG_STATUS_CHOICES = [
    ('published', 'Published'),
    ('draft', 'Draft'),
]

BLOG_CATEGORY_CHOICES = [
    ('news', 'News'),
    ('update', 'Update'),
    ('tips', 'Tips'),
    ('events', 'Events'),
]

PRODUCT_CATEGORY_CHOICES = [
    ('jerseys', 'Jerseys'),
    ('hoodies', 'Hoodies'),
    ('shorts', 'Shorts'),
    ('accessories', 'Accessories'),
]


class Banner(models.Model):
    title = models.CharField(max_length=255)
    banner_image_url = models.URLField(max_length=500)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    link_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_position_display()}"


class Blog(models.Model):
    title = models.CharField(max_length=255)
    excerpt = models.TextField(help_text="Short summary or description")
    content = models.TextField()
    featured_image_url = models.URLField(max_length=500)
    status = models.CharField(max_length=20, choices=BLOG_STATUS_CHOICES, default='draft')
    category = models.CharField(max_length=50, choices=BLOG_CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_category_display()} ({self.get_status_display()})"


class Testimonial(models.Model):
    text = models.TextField()
    customer_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Testimonial by {self.customer_name}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=PRODUCT_CATEGORY_CHOICES)
    image_url = models.URLField(max_length=500)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.sku} ({self.get_category_display()})"


class Category(models.Model):
    category_name = models.CharField(max_length=255)
    icon = models.CharField(max_length=10, help_text="Emoji icon")
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, help_text="Hex color code", default="#000000")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.category_name} {self.icon}"

class WebsiteSettings(models.Model):
    """
    General website settings - singleton pattern (only one instance)
    """
    website_name = models.CharField(max_length=255, default="ProSix")
    tagline = models.CharField(max_length=255, blank=True, null=True)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Theme Colors (Hex codes)
    primary_color = models.CharField(max_length=7, default="#000000", help_text="Primary color hex code")
    accent_color = models.CharField(max_length=7, default="#FFFFFF", help_text="Accent color hex code")
    
    # Navigation Menu (JSON field storing array of {name, link} objects)
    navigation_menu = models.JSONField(default=list, blank=True, help_text="Array of navigation menu items with name and link")
    
    # SEO Settings
    website_description = models.TextField(blank=True, null=True, help_text="Meta description for SEO")
    seo_keywords = models.TextField(blank=True, null=True, help_text="SEO keywords (comma-separated)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Website Settings'
        verbose_name_plural = 'Website Settings'
    
    def __str__(self):
        return f"Website Settings - {self.website_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the single website settings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
