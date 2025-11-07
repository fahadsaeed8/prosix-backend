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
    banner_image = models.ImageField(upload_to='banners/', blank=True, null=True)
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
    featured_image = models.ImageField(upload_to='blogs/', blank=True, null=True)
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
    image = models.ImageField(upload_to='products/', blank=True, null=True)
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
    logo = models.ImageField(upload_to='website_settings/', blank=True, null=True)
    
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


# Payment Settings Choices
CURRENCY_CHOICES = [
    ('USD', 'USD - US Dollar'),
    ('EUR', 'EUR - Euro'),
    ('GBP', 'GBP - British Pound'),
    ('CAD', 'CAD - Canadian Dollar'),
]


class PaymentSettings(models.Model):
    """
    Payment settings - singleton pattern (only one instance)
    Includes payment methods, configuration, security, and notification settings
    """
    
    # Payment Methods (enable/disable)
    paypal_enabled = models.BooleanField(default=False, help_text="Enable/disable PayPal payment method")
    stripe_enabled = models.BooleanField(default=False, help_text="Enable/disable Stripe payment method")
    cash_app_enabled = models.BooleanField(default=False, help_text="Enable/disable Cash App payment method")
    zelle_enabled = models.BooleanField(default=False, help_text="Enable/disable Zelle payment method")
    
    # Payment Configuration
    default_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text="Default currency for payments"
    )
    
    # Security Settings
    stripe_api_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stripe API key for payment processing"
    )
    stripe_webhook_secret = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stripe webhook secret for verifying webhook events"
    )
    enable_3d_secure = models.BooleanField(
        default=False,
        help_text="Enable/disable 3D Secure authentication"
    )
    
    # Payment Notification Settings
    admin_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Admin email address for payment notifications"
    )
    email_on_payment_success = models.BooleanField(
        default=False,
        help_text="Send email notification on successful payment"
    )
    email_on_payment_failure = models.BooleanField(
        default=False,
        help_text="Send email notification on failed payment"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Settings'
        verbose_name_plural = 'Payment Settings'
    
    def __str__(self):
        return f"Payment Settings - {self.get_default_currency_display()}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the single payment settings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


# Shipping Method Choices
SHIPPING_PROVIDER_CHOICES = [
    ('DHL', 'DHL'),
    ('FedEx', 'FedEx'),
    ('UPS', 'UPS'),
    ('USPS', 'USPS'),
    ('Flat Rate', 'Flat Rate'),
]

SHIPPING_STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]


class ShippingMethod(models.Model):
    """
    Shipping method configuration
    """
    method_name = models.CharField(
        max_length=255,
        help_text="Name of the shipping method"
    )
    provider = models.CharField(
        max_length=50,
        choices=SHIPPING_PROVIDER_CHOICES,
        help_text="Shipping provider/service"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Shipping cost"
    )
    delivery_time = models.CharField(
        max_length=255,
        help_text="Estimated delivery time (e.g., '3-5 business days')"
    )
    status = models.CharField(
        max_length=20,
        choices=SHIPPING_STATUS_CHOICES,
        default='active',
        help_text="Status of the shipping method"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shipping Method'
        verbose_name_plural = 'Shipping Methods'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.method_name} - {self.get_provider_display()} ({self.get_status_display()})"


# Tax Configuration Choices
TAX_TYPE_CHOICES = [
    ('VAT', 'VAT (Value Added Tax)'),
    ('Sales Tax', 'Sales Tax'),
    ('GST', 'GST (Goods & Services Tax)'),
]


class TaxConfiguration(models.Model):
    """
    Tax configuration settings - singleton pattern (only one instance)
    Includes tax settings, business information, and tax exemption settings
    """
    
    # Tax Settings
    enable_tax_setting = models.BooleanField(
        default=False,
        help_text="Enable/disable tax settings"
    )
    tax_type = models.CharField(
        max_length=50,
        choices=TAX_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Type of tax to apply"
    )
    tax_inclusive_pricing = models.BooleanField(
        default=False,
        help_text="Whether prices include tax or not"
    )
    
    # Business Information
    business_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Business name"
    )
    tax_id_vat_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Tax ID or VAT Number"
    )
    business_address = models.TextField(
        blank=True,
        null=True,
        help_text="Business address"
    )
    
    # Tax Exemption Settings
    b2b_tax_exemption = models.BooleanField(
        default=False,
        help_text="Enable/disable B2B tax exemption"
    )
    digital_product_tax = models.BooleanField(
        default=False,
        help_text="Enable/disable tax on digital products"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tax Configuration'
        verbose_name_plural = 'Tax Configuration'
    
    def __str__(self):
        return f"Tax Configuration - {self.business_name or 'Not Set'}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the single tax configuration instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


# General Settings Choices
LANGUAGE_CHOICES = [
    ('English', 'English'),
    ('Spanish', 'Spanish'),
    ('French', 'French'),
    ('German', 'German'),
]

GENERAL_CURRENCY_CHOICES = [
    ('USD', 'USD - US Dollar'),
    ('EUR', 'EUR - Euro'),
    ('GBP', 'GBP - British Pound'),
    ('CAD', 'CAD - Canadian Dollar'),
]


class GeneralSettings(models.Model):
    """
    General settings - singleton pattern (only one instance)
    Includes website settings, currency/pricing, system settings, and contact information
    """
    
    # Website Settings
    site_title = models.CharField(
        max_length=255,
        default="ProSix",
        help_text="Site title"
    )
    site_description = models.TextField(
        blank=True,
        null=True,
        help_text="Site description"
    )
    default_language = models.CharField(
        max_length=50,
        choices=LANGUAGE_CHOICES,
        default='English',
        help_text="Default language for the website"
    )
    
    # Currency and Pricing
    currency = models.CharField(
        max_length=3,
        choices=GENERAL_CURRENCY_CHOICES,
        default='USD',
        help_text="Default currency"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Tax rate percentage (e.g., 10.00 for 10%)"
    )
    
    # System Settings
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Enable/disable maintenance mode"
    )
    enable_analytics = models.BooleanField(
        default=False,
        help_text="Enable/disable analytics"
    )
    enable_notifications = models.BooleanField(
        default=False,
        help_text="Enable/disable notifications"
    )
    
    # Contact Information
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Contact email address"
    )
    phone_number = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )
    business_address = models.TextField(
        blank=True,
        null=True,
        help_text="Business address"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'General Settings'
        verbose_name_plural = 'General Settings'
    
    def __str__(self):
        return f"General Settings - {self.site_title}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the single general settings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    @classmethod
    def reset_to_default(cls):
        """Reset settings to default values"""
        settings = cls.get_settings()
        settings.site_title = "ProSix"
        settings.site_description = ""
        settings.default_language = "English"
        settings.currency = "USD"
        settings.tax_rate = 0.00
        settings.maintenance_mode = False
        settings.enable_analytics = False
        settings.enable_notifications = False
        settings.email = ""
        settings.phone_number = ""
        settings.business_address = ""
        settings.save()
        return settings


class Notification(models.Model):
    """
    Individual notification records
    """
    emoji = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Emoji for the notification"
    )
    title = models.CharField(
        max_length=255,
        help_text="Notification title"
    )
    body = models.TextField(
        help_text="Notification body/content"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        help_text="Notification date"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.date}"


class NotificationSettings(models.Model):
    """
    Notification settings - singleton pattern (only one instance)
    Includes email, push, and SMS notification preferences
    """
    
    # Email Notifications
    new_order_notification = models.BooleanField(
        default=False,
        help_text="Enable/disable new order email notifications"
    )
    payment_notifications = models.BooleanField(
        default=False,
        help_text="Enable/disable payment email notifications"
    )
    low_stock_alerts = models.BooleanField(
        default=False,
        help_text="Enable/disable low stock email alerts"
    )
    customer_messages = models.BooleanField(
        default=False,
        help_text="Enable/disable customer message email notifications"
    )
    
    # Push Notifications
    enable_push_notifications = models.BooleanField(
        default=False,
        help_text="Enable/disable push notifications"
    )
    new_order_alerts = models.BooleanField(
        default=False,
        help_text="Enable/disable new order push alerts"
    )
    system_alerts = models.BooleanField(
        default=False,
        help_text="Enable/disable system push alerts"
    )
    
    # SMS Notifications
    enable_sms_notification = models.BooleanField(
        default=False,
        help_text="Enable/disable SMS notifications"
    )
    admin_phone_number = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        help_text="Admin phone number for SMS notifications"
    )
    critical_alerts = models.BooleanField(
        default=False,
        help_text="Enable/disable critical SMS alerts"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Settings'
        verbose_name_plural = 'Notification Settings'
    
    def __str__(self):
        return "Notification Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the single notification settings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
