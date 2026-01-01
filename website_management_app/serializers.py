from rest_framework import serializers
from .models import WebsiteSettings, Banner, Blog, Testimonial, Product, Category, PaymentSettings, ShippingMethod, TaxConfiguration, GeneralSettings, Notification, NotificationSettings, ArtworkRequest, MembershipRequest, MediaLibrary
from django.conf import settings


class NavigationMenuItemSerializer(serializers.Serializer):
    """Serializer for navigation menu item structure"""
    name = serializers.CharField(max_length=255)
    link = serializers.CharField(max_length=500)


class WebsiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for Website Settings"""
    
    class Meta:
        model = WebsiteSettings
        fields = [
            'id',
            'website_name',
            'tagline',
            'logo',
            'primary_color',
            'accent_color',
            'navigation_menu',
            'website_description',
            'seo_keywords',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Override to return full URL for logo"""
        representation = super().to_representation(instance)
        if representation.get('logo'):
            representation['logo'] = f'{settings.DOMAIN}{instance.logo.url}'
        return representation
    
    def validate_primary_color(self, value):
        """Validate hex color code format"""
        if value and not value.startswith('#'):
            raise serializers.ValidationError("Primary color must be a valid hex code starting with #")
        if value and len(value) != 7:
            raise serializers.ValidationError("Primary color must be a valid hex code (e.g., #FF5733)")
        return value
    
    def validate_accent_color(self, value):
        """Validate hex color code format"""
        if value and not value.startswith('#'):
            raise serializers.ValidationError("Accent color must be a valid hex code starting with #")
        if value and len(value) != 7:
            raise serializers.ValidationError("Accent color must be a valid hex code (e.g., #FF5733)")
        return value
    
    def validate_navigation_menu(self, value):
        """Validate navigation menu structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Navigation menu must be a list")
        
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each navigation menu item must be an object")
            if 'name' not in item or 'link' not in item:
                raise serializers.ValidationError("Each navigation menu item must have 'name' and 'link' fields")
            if not isinstance(item['name'], str) or not isinstance(item['link'], str):
                raise serializers.ValidationError("Navigation menu item 'name' and 'link' must be strings")
            # ID is optional but if present should be an integer
            if 'id' in item and not isinstance(item['id'], int):
                raise serializers.ValidationError("Navigation menu item 'id' must be an integer if provided")
        
        return value


class BannerSerializer(serializers.ModelSerializer):
    """Serializer for Banner"""
    
    class Meta:
        model = Banner
        fields = [
            'id',
            'title',
            'image',
            'description',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Override to return full URL for image"""
        representation = super().to_representation(instance)
        if representation.get('image'):
            representation['image'] = f'{settings.DOMAIN}{instance.image.url}'
        return representation


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for Blog"""
    
    class Meta:
        model = Blog
        fields = [
            'id',
            'title',
            'excerpt',
            'content',
            'featured_image',
            'status',
            'category',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Override to return full URL for featured_image"""
        representation = super().to_representation(instance)
        if representation.get('featured_image'):
            representation['featured_image'] = f'{settings.DOMAIN}{instance.featured_image.url}'
        return representation


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for Testimonial"""
    
    class Meta:
        model = Testimonial
        fields = [
            'id',
            'text',
            'customer_name',
            'image',
            'review',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_review(self, value):
        """Validate that review is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Review must be a number between 1 and 5")
        return value
    
    def to_representation(self, instance):
        """Override to return full URL for image"""
        representation = super().to_representation(instance)
        if representation.get('image'):
            representation['image'] = f'{settings.DOMAIN}{instance.image.url}'
        return representation


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product"""
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'sku',
            'category',
            'image',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Override to return full URL for image"""
        representation = super().to_representation(instance)
        if representation.get('image'):
            representation['image'] = f'{settings.DOMAIN}{instance.image.url}'
        return representation


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category"""
    
    class Meta:
        model = Category
        fields = [
            'id',
            'category_name',
            'icon',
            'description',
            'color',
            'show_in',
            'password',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    extra_kwargs = {
        'password': {'write_only': True},
    }
    
    def validate_color(self, value):
        """Validate hex color code format"""
        if value and not value.startswith('#'):
            raise serializers.ValidationError("Color must be a valid hex code starting with #")
        if value and len(value) != 7:
            raise serializers.ValidationError("Color must be a valid hex code (e.g., #FF5733)")
        return value


class PaymentSettingsSerializer(serializers.ModelSerializer):
    """Serializer for Payment Settings"""
    
    class Meta:
        model = PaymentSettings
        fields = [
            'id',
            # Payment Methods
            'paypal_enabled',
            'stripe_enabled',
            'cash_app_enabled',
            'zelle_enabled',
            # Payment Configuration
            'default_currency',
            # Security Settings
            'stripe_api_key',
            'stripe_webhook_secret',
            'enable_3d_secure',
            # Payment Notification Settings
            'admin_email',
            'email_on_payment_success',
            'email_on_payment_failure',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_admin_email(self, value):
        """Validate admin email if email notifications are enabled"""
        if value:
            # Basic email validation is handled by EmailField
            pass
        elif self.initial_data.get('email_on_payment_success') or self.initial_data.get('email_on_payment_failure'):
            raise serializers.ValidationError(
                "Admin email is required when email notifications are enabled"
            )
        return value


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for Shipping Method"""
    
    class Meta:
        model = ShippingMethod
        fields = [
            'id',
            'method_name',
            'provider',
            'cost',
            'delivery_time',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_cost(self, value):
        """Validate that cost is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Shipping cost cannot be negative")
        return value


class TaxConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for Tax Configuration"""
    
    class Meta:
        model = TaxConfiguration
        fields = [
            'id',
            # Tax Settings
            'enable_tax_setting',
            'tax_type',
            'tax_inclusive_pricing',
            # Business Information
            'business_name',
            'tax_id_vat_number',
            'business_address',
            # Tax Exemption Settings
            'b2b_tax_exemption',
            'digital_product_tax',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_tax_type(self, value):
        """Validate tax type is provided when tax setting is enabled"""
        if self.initial_data.get('enable_tax_setting') and not value:
            raise serializers.ValidationError(
                "Tax type is required when tax setting is enabled"
            )
        return value


class GeneralSettingsSerializer(serializers.ModelSerializer):
    """Serializer for General Settings"""
    
    class Meta:
        model = GeneralSettings
        fields = [
            'id',
            # Website Settings
            'site_title',
            'site_description',
            'default_language',
            # Currency and Pricing
            'currency',
            'tax_rate',
            # System Settings
            'maintenance_mode',
            'enable_analytics',
            'enable_notifications',
            # Contact Information
            'email',
            'phone_number',
            'business_address',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_tax_rate(self, value):
        """Validate that tax rate is non-negative and reasonable"""
        if value < 0:
            raise serializers.ValidationError("Tax rate cannot be negative")
        if value > 100:
            raise serializers.ValidationError("Tax rate cannot exceed 100%")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification"""
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'emoji',
            'title',
            'body',
            'date',
            'is_read',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'date', 'created_at', 'updated_at')


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for Notification Settings"""
    
    class Meta:
        model = NotificationSettings
        fields = [
            'id',
            # Email Notifications
            'new_order_notification',
            'payment_notifications',
            'low_stock_alerts',
            'customer_messages',
            # Push Notifications
            'enable_push_notifications',
            'new_order_alerts',
            'system_alerts',
            # SMS Notifications
            'enable_sms_notification',
            'admin_phone_number',
            'critical_alerts',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_admin_phone_number(self, value):
        """Validate admin phone number if SMS notifications are enabled"""
        if self.initial_data.get('enable_sms_notification') and not value:
            raise serializers.ValidationError(
                "Admin phone number is required when SMS notifications are enabled"
            )
        return value


class ArtworkRequestSerializer(serializers.ModelSerializer):
    """Serializer for Artwork Request"""
    
    class Meta:
        model = ArtworkRequest
        fields = [
            'id',
            'full_name',
            'email',
            'phone',
            'instagram',
            'address',
            'organization_name',
            'user_type',
            'order_quantity',
            'team_color',
            'need_home_away_mockup',
            'team_attribute',
            'twill_type',
            'sports',
            'product_mockup',
            'additional_details',
            'how_did_you_hear',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_order_quantity(self, value):
        """Validate that order quantity is at least 1"""
        if value < 1:
            raise serializers.ValidationError("Order quantity must be at least 1")
        return value
    
    def validate_sports(self, value):
        """Validate that sports is a list with max 2 items"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Sports must be a list")
        if len(value) > 2:
            raise serializers.ValidationError("Maximum 2 sports are allowed")
        for sport in value:
            if not isinstance(sport, str):
                raise serializers.ValidationError("Each sport must be a string")
        return value
    
    def to_representation(self, instance):
        """Override to return full URL for product_mockup"""
        representation = super().to_representation(instance)
        if representation.get('product_mockup'):
            representation['product_mockup'] = f'{settings.DOMAIN}{instance.product_mockup.url}'
        return representation


class MembershipRequestSerializer(serializers.ModelSerializer):
    """Serializer for Membership Request"""
    
    class Meta:
        model = MembershipRequest
        fields = [
            'id',
            'name',
            'email',
            'mailing_address',
            'organization',
            'state',
            'zip_code',
            'phone',
            'user_type',
            'twill_type',
            'sport',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class MediaLibrarySerializer(serializers.ModelSerializer):
    """Serializer for Media Library"""
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes
    
    class Meta:
        model = MediaLibrary
        fields = [
            'id',
            'image',
            'file_name',
            'file_size',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'file_name', 'file_size', 'created_at', 'updated_at')
    
    def validate_image(self, value):
        """Validate file size (max 10 MB)"""
        if value.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"File size cannot exceed 10 MB. Current file size: {value.size / (1024 * 1024):.2f} MB"
            )
        
        # Validate file type (only images)
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("Only image files are allowed")
        
        return value
    
    def to_representation(self, instance):
        """Override to return full URL for image and human-readable file size"""
        representation = super().to_representation(instance)
        if representation.get('image'):
            representation['image'] = f'{settings.DOMAIN}{instance.image.url}'
        # Add human-readable file size
        representation['file_size_display'] = instance.get_file_size_display()
        return representation
