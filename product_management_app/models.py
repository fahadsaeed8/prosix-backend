from django.db import models
from django.contrib.auth.models import User
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
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ShirtCategory, related_name='shirts_category', on_delete=models.CASCADE) 
    sub_category = models.ForeignKey(ShirtSubCategory, related_name='shirts_subcategory', on_delete=models.SET_NULL, null=True, blank=True) 

    svg_file = models.FileField(upload_to='shirts/svg/', blank=True, null=True)
    white_base_file = models.FileField(upload_to='shirts/white_base/', blank=True, null=True)
    black_base_file = models.FileField(upload_to='shirts/black_base/', blank=True, null=True)

    front_base = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    front_child1 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    front_child2 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    front_child3 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)

    back_base = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    back_child1 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    back_child2 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    back_child3 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)

    left_base = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    left_child1 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    left_child2 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    left_child3 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    
    right_base = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    right_child1 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    right_child2 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    right_child3 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserShirt(models.Model):
    user = models.ForeignKey(User, related_name='usershirts_user', on_delete=models.CASCADE)
    shirt = models.ForeignKey(Shirt, related_name='usershirts_shirt', on_delete=models.CASCADE)
    colors = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.shirt.name}"
    
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
            return f"{self.user.username} - {self.shirt.name}"
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
    pattern_image = models.ImageField(upload_to='patterns/', blank=True, null=True)
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