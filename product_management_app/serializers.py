from rest_framework import serializers
from .models import Shirt, ShirtCategory, ShirtSubCategory, UserShirt, FavoriteShirt, Customizer, UserCustomizer, Pattern, Color, Font, Order, Invoice
from django.conf import settings


class ShirtCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShirtCategory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ShirtSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShirtSubCategory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ShirtSerializer(serializers.ModelSerializer):
    category_detail = ShirtCategorySerializer(source='category', read_only=True)
    sub_category_detail = ShirtSubCategorySerializer(source='sub_category', read_only=True)
    
    class Meta:
        model = Shirt
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'category': {'write_only': True},
            'sub_category_detail': {'read_only': True}
        }
    
    def to_representation(self, instance):
        """Override to return full URLs for file fields"""
        representation = super().to_representation(instance)
        file_fields = [
            'svg_file', 'white_base_file', 'black_base_file',
            'front_base', 'front_child1', 'front_child2', 'front_child3',
            'back_base', 'back_child1', 'back_child2', 'back_child3',
            'left_base', 'left_child1', 'left_child2', 'left_child3',
            'right_base', 'right_child1', 'right_child2', 'right_child3'
        ]
        for field in file_fields:
            if representation.get(field):
                representation[field] = f'{settings.DOMAIN}{representation[field]}'
        return representation


       

class UserShirtSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserShirt
        fields = '__all__'

    def validate_colors(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Colors must be a list of objects")
        for item in value:
            if not isinstance(item, dict) or 'color' not in item:
                raise serializers.ValidationError("Each color item must be an object with a 'color' key")
        return value
    
class UserShirtGETSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()
    class Meta:
        model = UserShirt
        fields = '__all__'

    def get_is_favorite(self, obj):
        user = self.context.get('user')
        shirt_obj = FavoriteShirt.objects.filter(user_shirt=obj, user=user).first()
        if shirt_obj:
            return True 
        else:
            return False
        
class ShirtListSerializer(serializers.ModelSerializer):
    user_shirts = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    category_detail = ShirtCategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Shirt
        fields = '__all__'
    
    def get_is_favorite(self, obj):
        user = self.context.get('user')
        shirt_obj = FavoriteShirt.objects.filter(shirt=obj, user=user).first()
        if shirt_obj:
            return True 
        else:
            return False
    
    def get_user_shirts(self, obj):
        user = self.context.get('user')
        user_shirts = UserShirt.objects.filter(shirt=obj)
        return UserShirtGETSerializer(user_shirts, many=True, context={'user':user}).data
    
    def to_representation(self, instance):
        """Override to return full URLs for file fields"""
        representation = super().to_representation(instance)
        file_fields = [
            'svg_file', 'white_base_file', 'black_base_file',
            'front_base', 'front_child1', 'front_child2', 'front_child3',
            'back_base', 'back_child1', 'back_child2', 'back_child3',
            'left_base', 'left_child1', 'left_child2', 'left_child3',
            'right_base', 'right_child1', 'right_child2', 'right_child3'
        ]
        for field in file_fields:
            if representation.get(field):
                representation[field] = f'{settings.DOMAIN}{representation[field]}'
        return representation
    
class FavoriteShirtSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteShirt
        fields = ['id', 'user', 'shirt', 'user_shirt', 'created_at', 'updated_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        return FavoriteShirt.objects.create(**validated_data)


class CustomizerSerializer(serializers.ModelSerializer):
    """Serializer for Customizer"""
    
    class Meta:
        model = Customizer
        fields = [
            'id',
            'model_name',
            'model_type',
            'sport',
            'category',
            'description',
            'is_active',
            'views',
            'front_black_layer',
            'front_white_layer',
            'front_svg_layer',
            'back_black_layer',
            'back_white_layer',
            'back_svg_layer',
            'left_black_layer',
            'left_white_layer',
            'left_svg_layer',
            'right_black_layer',
            'right_white_layer',
            'right_svg_layer',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Override to return full URLs for image/file fields"""
        representation = super().to_representation(instance)
        file_fields = [
            'front_black_layer', 'front_white_layer', 'front_svg_layer',
            'back_black_layer', 'back_white_layer', 'back_svg_layer',
            'left_black_layer', 'left_white_layer', 'left_svg_layer',
            'right_black_layer', 'right_white_layer', 'right_svg_layer'
        ]
        for field in file_fields:
            field_obj = getattr(instance, field, None)
            if field_obj:
                representation[field] = f'{settings.DOMAIN}{field_obj.url}'
        return representation


class PatternSerializer(serializers.ModelSerializer):
    """Serializer for Pattern"""
    
    class Meta:
        model = Pattern
        fields = [
            'id',
            'pattern_name',
            'category',
            'description',
            'pattern_image',
            'tags',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Override to return full URL for pattern_image"""
        representation = super().to_representation(instance)
        if representation.get('pattern_image'):
            representation['pattern_image'] = f'{settings.DOMAIN}{instance.pattern_image.url}'
        return representation


class ColorSerializer(serializers.ModelSerializer):
    """Serializer for Color"""
    
    class Meta:
        model = Color
        fields = [
            'id',
            'color_name',
            'color_code',
            'category',
            'description',
            'tags',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_color_code(self, value):
        """Validate hex color code format"""
        if not value:
            return value
        value = value.strip().upper()
        if not value.startswith('#'):
            raise serializers.ValidationError("Color code must start with #")
        if len(value) != 7:
            raise serializers.ValidationError("Color code must be 7 characters (e.g., #FF5733)")
        # Check if remaining 6 characters are valid hex
        hex_part = value[1:]
        if not all(c in '0123456789ABCDEF' for c in hex_part):
            raise serializers.ValidationError("Color code must contain valid hexadecimal characters")
        return value


class FontSerializer(serializers.ModelSerializer):
    """Serializer for Font"""
    
    class Meta:
        model = Font
        fields = [
            'id',
            'font_name',
            'font_family',
            'category',
            'description',
            'font_file',
            'preview_text',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_font_file(self, value):
        """Validate font file extension"""
        if not value:
            return value
        import os
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.ttf', '.otf', '.woff', '.woff2']
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f'Unsupported file extension. Allowed extensions: {", ".join(valid_extensions)}'
            )
        return value
    
    def to_representation(self, instance):
        """Override to return full URL for font_file"""
        representation = super().to_representation(instance)
        if representation.get('font_file'):
            representation['font_file'] = f'{settings.DOMAIN}{instance.font_file.url}'
        return representation


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order"""
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'customer',
            'customer_name',
            'customer_email',
            'date',
            'total',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'order_id', 'created_at', 'updated_at')
    
    def validate_total(self, value):
        """Validate that total is positive"""
        if value <= 0:
            raise serializers.ValidationError("Total must be greater than 0")
        return value


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice"""
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_id',
            'customer',
            'customer_name',
            'customer_email',
            'date',
            'amount',
            'status',
            'due_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'invoice_id', 'created_at', 'updated_at')
    
    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value