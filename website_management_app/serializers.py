from rest_framework import serializers
from .models import WebsiteSettings, Banner, Blog, Testimonial, Product, Category


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
            'logo_url',
            'primary_color',
            'accent_color',
            'navigation_menu',
            'website_description',
            'seo_keywords',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
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
            'banner_image_url',
            'position',
            'link_url',
            'status',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for Blog"""
    
    class Meta:
        model = Blog
        fields = [
            'id',
            'title',
            'excerpt',
            'content',
            'featured_image_url',
            'status',
            'category',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for Testimonial"""
    
    class Meta:
        model = Testimonial
        fields = [
            'id',
            'text',
            'customer_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


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
            'image_url',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


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
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_color(self, value):
        """Validate hex color code format"""
        if value and not value.startswith('#'):
            raise serializers.ValidationError("Color must be a valid hex code starting with #")
        if value and len(value) != 7:
            raise serializers.ValidationError("Color must be a valid hex code (e.g., #FF5733)")
        return value
