from django.db import models
from django.contrib.auth.models import User
from website_management_app.models import Category
# Create your models here.

class ShirtCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class ShirtSubCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Shirt(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='shirts_category', on_delete=models.CASCADE) 
    sub_category = models.ForeignKey(ShirtSubCategory, related_name='shirts_subcategory', on_delete=models.SET_NULL, null=True, blank=True) 
    
    # New fields
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Price of the shirt")
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text="Stock Keeping Unit")
    size = models.TextField(blank=True, null=True, help_text="Size of the shirt")
    model = models.BooleanField(default=False, help_text="Model flag")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.sku}"


class MainShirtImage(models.Model):
    """Main images for shirts (max 6 per shirt)"""
    shirt = models.ForeignKey(Shirt, related_name='main_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shirts/main_images/', help_text="Main shirt image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Main Shirt Image'
        verbose_name_plural = 'Main Shirt Images'
        ordering = ['created_at']

    def __str__(self):
        return f"Main image for {self.shirt.title}"


class ShirtImage(models.Model):
    """Additional images for shirts (min 1, max 10 per shirt)"""
    shirt = models.ForeignKey(Shirt, related_name='other_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shirts/other_images/', help_text="Additional shirt image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shirt Image'
        verbose_name_plural = 'Shirt Images'
        ordering = ['created_at']

    def __str__(self):
        return f"Image for {self.shirt.title}"


class ShirtDraft(models.Model):
    """Draft configuration for a customizer (svg part colors stored as flat map)."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    customizer = models.OneToOneField('Customizer', related_name='draft', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    svg_part_colors = models.JSONField(default=dict, blank=True, help_text="Flat map of svg part colors, keys like 'front_0'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Draft for {self.customizer.model_name} - {self.get_status_display()}"

class UserShirt(models.Model):
    user = models.ForeignKey(User, related_name='usershirts_user', on_delete=models.CASCADE)
    shirt = models.ForeignKey(Shirt, related_name='usershirts_shirt', on_delete=models.CASCADE)
    colors = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.shirt.title}"
    
class FavoriteShirt(models.Model):
    user = models.ForeignKey(User, related_name='favoriteshirt_user', on_delete=models.CASCADE)
    shirt = models.ForeignKey(Shirt, related_name='favoriteshirt_shirt', on_delete=models.CASCADE, null=True, blank=True)
    user_shirt = models.ForeignKey(UserShirt, related_name='favoriteshirt_user_shirt', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user_shirt:
            return f"{self.user.username} - User Shirt-{self.user_shirt.id}"
        elif self.shirt:
            return f"{self.user.username} - {self.shirt.title}"
        else:
            return f"{self.user.username} - No shirt selected"


# Customizer Model Choices
MODEL_TYPE_CHOICES = [
    ('jerseys', 'Jerseys'),
    ('shorts', 'Shorts'),
    ('hoodies', 'Hoodies'),
    ('pants', 'Pants'),
    ('jacket', 'Jacket'),
]

SPORT_CHOICES = [
    ('football', 'Football'),
    ('basketball', 'Basketball'),
    ('hockey', 'Hockey'),
    ('baseball', 'Baseball'),
    ('soccer', 'Soccer'),
]

CATEGORY_CHOICES = [
    ('jerseys', 'Jerseys'),
    ('shorts', 'Shorts'),
    ('hoodies', 'Hoodies'),
    ('pants', 'Pants'),
    ('jacket', 'Jacket'),
    ('accessories', 'Accessories'),
]


class Customizer(models.Model):
    model_name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES)
    sport = models.CharField(max_length=50, choices=SPORT_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    sub_category = models.JSONField(blank=True, null=True, default=list, help_text="Optional list of sub-categories for customizer")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Whether the model is active")
    views = models.IntegerField(default=0, help_text="Total number of views")
    
    # Front part images
    front_black_layer = models.ImageField(upload_to='customizer/front/', blank=True, null=True)
    front_white_layer = models.ImageField(upload_to='customizer/front/', blank=True, null=True)
    front_svg_layer = models.FileField(upload_to='customizer/front/', blank=True, null=True)
    
    # Back part images
    back_black_layer = models.ImageField(upload_to='customizer/back/', blank=True, null=True)
    back_white_layer = models.ImageField(upload_to='customizer/back/', blank=True, null=True)
    back_svg_layer = models.FileField(upload_to='customizer/back/', blank=True, null=True)
    
    # Left part images
    left_black_layer = models.ImageField(upload_to='customizer/left/', blank=True, null=True)
    left_white_layer = models.ImageField(upload_to='customizer/left/', blank=True, null=True)
    left_svg_layer = models.FileField(upload_to='customizer/left/', blank=True, null=True)
    
    # Right part images
    right_black_layer = models.ImageField(upload_to='customizer/right/', blank=True, null=True)
    right_white_layer = models.ImageField(upload_to='customizer/right/', blank=True, null=True)
    right_svg_layer = models.FileField(upload_to='customizer/right/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Customizer'
        verbose_name_plural = 'Customizers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.model_name} - {self.get_model_type_display()} ({self.get_sport_display()})"


class UserCustomizer(models.Model):
    """Track user customizations of customizer models"""
    user = models.ForeignKey(User, related_name='usercustomizers_user', on_delete=models.CASCADE)
    customizer = models.ForeignKey(Customizer, related_name='usercustomizers_customizer', on_delete=models.CASCADE)
    customization_data = models.JSONField(default=dict, blank=True, help_text="JSON data storing customization details")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.customizer.model_name}"
    
    class Meta:
        verbose_name = 'User Customizer'
        verbose_name_plural = 'User Customizers'
        ordering = ['-created_at']


# Pattern Model Choices
PATTERN_CATEGORY_CHOICES = [
    ('geometric', 'Geometric'),
    ('organic', 'Organic'),
    ('texture', 'Texture'),
    ('abstract', 'Abstract'),
    ('sports', 'Sports'),
    ('military', 'Military'),
]


class Pattern(models.Model):
    pattern_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=PATTERN_CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    # Use FileField to support SVG uploads as patterns (ImageField validates images via Pillow)
    pattern_image = models.FileField(upload_to='patterns/', blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pattern'
        verbose_name_plural = 'Patterns'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.pattern_name} - {self.get_category_display()}"


# Color Model Choices
COLOR_CATEGORY_CHOICES = [
    ('primary', 'Primary'),
    ('secondary', 'Secondary'),
    ('accent', 'Accent'),
    ('neutral', 'Neutral'),
    ('team_colors', 'Team Colors'),
    ('custom', 'Custom'),
]


class Color(models.Model):
    color_name = models.CharField(max_length=255)
    color_code = models.CharField(max_length=7, help_text="Hex color code (e.g., #FF5733)")
    category = models.CharField(max_length=50, choices=COLOR_CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.color_name} - {self.color_code} ({self.get_category_display()})"


# Font Model Choices
FONT_CATEGORY_CHOICES = [
    ('serif', 'Serif'),
    ('sans-serif', 'Sans-Serif'),
    ('display', 'Display'),
    ('script', 'Script'),
    ('monospace', 'Monospace'),
]


def validate_font_file(value):
    """Validate that the uploaded file is a font file"""
    import os
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.ttf', '.otf', '.woff', '.woff2']
    if ext not in valid_extensions:
        from django.core.exceptions import ValidationError
        raise ValidationError(f'Unsupported file extension. Allowed extensions: {", ".join(valid_extensions)}')


class Font(models.Model):
    font_name = models.CharField(max_length=255)
    font_family = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=FONT_CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    font_file = models.FileField(upload_to='fonts/', validators=[validate_font_file], blank=True, null=True)
    preview_text = models.CharField(max_length=255, blank=True, null=True, help_text="Preview text to display the font")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Font'
        verbose_name_plural = 'Fonts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.font_name} - {self.font_family} ({self.get_category_display()})"


# Order Model Choices
ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
]


class Order(models.Model):
    order_id = models.CharField(max_length=50, unique=True, editable=False, help_text="Auto-generated order ID")
    customer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, help_text="Order date")
    total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price of the order")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_id} - {self.customer.username} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-generate order_id if not set"""
        if not self.order_id:
            # Generate order_id: ORD-YYYYMMDD-HHMMSS-XXXX
            from datetime import datetime
            import random
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            random_suffix = random.randint(1000, 9999)
            self.order_id = f"ORD-{timestamp}-{random_suffix}"
        super().save(*args, **kwargs)


# Invoice Model Choices
INVOICE_STATUS_CHOICES = [
    ('paid', 'Paid'),
    ('pending', 'Pending'),
    ('overdue', 'Overdue'),
]


class Invoice(models.Model):
    invoice_id = models.CharField(max_length=50, unique=True, editable=False, help_text="Auto-generated invoice ID")
    customer = models.ForeignKey(User, related_name='invoices', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, help_text="Invoice date")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Invoice amount")
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='pending')
    due_date = models.DateField(help_text="Due date for the invoice")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_id} - {self.customer.username} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-generate invoice_id if not set"""
        if not self.invoice_id:
            # Generate invoice_id: INV-YYYYMMDD-HHMMSS-XXXX
            from datetime import datetime
            import random
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            random_suffix = random.randint(1000, 9999)
            self.invoice_id = f"INV-{timestamp}-{random_suffix}"
        super().save(*args, **kwargs)


# Report Models
class RevenueReport(models.Model):
    """Model to store revenue report data"""
    this_month_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_month_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    growth_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Growth percentage like +20% or -5%")
    total_orders = models.IntegerField(default=0)
    report_date = models.DateField(auto_now_add=True, help_text="Date when report was generated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Revenue Report'
        verbose_name_plural = 'Revenue Reports'
        ordering = ['-report_date']
    
    def __str__(self):
        return f"Revenue Report - {self.report_date}"


class ProductSalesReport(models.Model):
    """Model to store product sales report data"""
    top_product_name = models.CharField(max_length=255, blank=True, null=True)
    top_product_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    top_product_units_sold = models.IntegerField(default=0)
    top_category = models.CharField(max_length=255, blank=True, null=True)
    report_date = models.DateField(auto_now_add=True, help_text="Date when report was generated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product Sales Report'
        verbose_name_plural = 'Product Sales Reports'
        ordering = ['-report_date']
    
    def __str__(self):
        return f"Product Sales Report - {self.report_date}"


class CustomerAnalysisReport(models.Model):
    """Model to store customer analysis report data"""
    total_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    report_date = models.DateField(auto_now_add=True, help_text="Date when report was generated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Customer Analysis Report'
        verbose_name_plural = 'Customer Analysis Reports'
        ordering = ['-report_date']
    
    def __str__(self):
        return f"Customer Analysis Report - {self.report_date}"


class GrowthTrendReport(models.Model):
    """Model to store growth trend report data"""
    monthly_growth = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Monthly growth percentage")
    yearly_growth = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Yearly growth percentage")
    quarterly_growth = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Quarterly growth percentage")
    market_share = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Market share percentage")
    report_date = models.DateField(auto_now_add=True, help_text="Date when report was generated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Growth Trend Report'
        verbose_name_plural = 'Growth Trend Reports'
        ordering = ['-report_date']
    
    def __str__(self):
        return f"Growth Trend Report - {self.report_date}"

class SubCategory(models.Model):
    category = models.ForeignKey('website_management_app.Category', on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=255)
    show_in = models.CharField(max_length=255, blank=True, null=True, help_text="Where to show the sub-category")
    password = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.category}"