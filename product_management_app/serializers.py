from rest_framework import serializers
from website_management_app.models import Category
from .models import SubCategory

class SubCategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'name', 'show_in', 'password', 'created_at', 'updated_at']
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Override to return full Category object instead of just ID"""
        representation = super().to_representation(instance)
        # Replace category ID with full Category object
        if instance.category:
            from website_management_app.serializers import CategorySerializer as FullCategorySerializer
            representation['category'] = FullCategorySerializer(instance.category).data
        return representation
from .models import Shirt, ShirtCategory, ShirtSubCategory, ShirtImage, UserShirt, FavoriteShirt, Customizer, UserCustomizer, Pattern, Color, Font, Order, Invoice, RevenueReport, ProductSalesReport, CustomerAnalysisReport, GrowthTrendReport, ShirtDraft
from website_management_app.models import Category
from django.conf import settings


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category (from website_management_app)"""
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'icon', 'description', 'color', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')


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

class ShirtImageSerializer(serializers.ModelSerializer):
    """Serializer for ShirtImage (additional images)"""
    
    class Meta:
        model = ShirtImage
        fields = ['id', 'shirt', 'image', 'created_at', 'updated_at']
        read_only_fields = ('id', 'created_at', 'updated_at')
    
class SubCategoryInputField(serializers.Field):
    """
    Accepts sub_category as a list of SubCategory IDs (integers).
    Validates IDs exist; stores as list of ints.
    """
    def to_internal_value(self, data):
        # Normalize to a list of integers
        if isinstance(data, list):
            ids = []
            for item in data:
                if isinstance(item, int):
                    ids.append(item)
                elif isinstance(item, str) and item.isdigit():
                    ids.append(int(item))
                else:
                    raise serializers.ValidationError("All sub_category IDs must be integers.")
            # Validate existence
            if ids:
                existing = set(SubCategory.objects.filter(id__in=ids).values_list('id', flat=True))
                if len(existing) != len(ids):
                    raise serializers.ValidationError("One or more sub_category IDs are invalid.")
            return ids
        # Backward-compat: single ID
        if isinstance(data, int):
            cid = data
            if not SubCategory.objects.filter(id=cid).exists():
                raise serializers.ValidationError("Invalid sub_category id.")
            return [cid]
        if isinstance(data, str):
            # Try JSON-encoded list
            try:
                import json
                parsed = json.loads(data)
                if isinstance(parsed, list):
                    return self.to_internal_value(parsed)
                if isinstance(parsed, int):
                    return [parsed]
            except Exception:
                pass
            if data.isdigit():
                cid = int(data)
                if not SubCategory.objects.filter(id=cid).exists():
                    raise serializers.ValidationError("Invalid sub_category id.")
                return [cid]
        raise serializers.ValidationError("Sub category must be a list of IDs.")

    def to_representation(self, value):
        """Return full SubCategory objects instead of just IDs"""
        if value is None:
            return []
        
        # Get list of subcategory IDs
        subcategory_ids = []
        if isinstance(value, list):
            subcategory_ids = [int(item) if isinstance(item, str) and item.isdigit() else item for item in value if isinstance(item, (int, str)) and (isinstance(item, int) or item.isdigit())]
        elif isinstance(value, (int, str)):
            if isinstance(value, str) and value.isdigit():
                subcategory_ids = [int(value)]
            elif isinstance(value, int):
                subcategory_ids = [value]
        elif hasattr(value, 'id'):
            subcategory_ids = [value.id]
        else:
            return []
        
        if not subcategory_ids:
            return []
        
        # Fetch and serialize all SubCategory objects
        try:
            subcategories = SubCategory.objects.filter(id__in=subcategory_ids)
            return SubCategorySerializer(subcategories, many=True).data
        except Exception:
            return []

class CategoryInputField(serializers.Field):
    """
    Accepts category as either an integer id or a numeric string.
    Only ID-based inputs are supported here.
    Returns full Category object in representation.
    """
    def to_internal_value(self, data):
        if isinstance(data, int):
            try:
                Category.objects.get(id=data)
                return data
            except Category.DoesNotExist:
                raise serializers.ValidationError("Invalid category id")
        if isinstance(data, str) and data.isdigit():
            cid = int(data)
            try:
                Category.objects.get(id=cid)
                return cid
            except Category.DoesNotExist:
                raise serializers.ValidationError("Invalid category id")
        raise serializers.ValidationError("Category must be a valid integer id.")
    
    def to_representation(self, value):
        """Return full Category object instead of just ID"""
        if value is None:
            return None
        
        # Get category ID - value might be int, string, or Category object
        category_id = None
        if isinstance(value, int):
            category_id = value
        elif isinstance(value, str) and value.isdigit():
            category_id = int(value)
        elif hasattr(value, 'id'):
            category_id = value.id
        else:
            return None
        
        # Fetch and serialize the Category object
        try:
            category = Category.objects.get(id=category_id)
            # Use the CategorySerializer from website_management_app for full fields
            from website_management_app.serializers import CategorySerializer as FullCategorySerializer
            return FullCategorySerializer(category).data
        except Category.DoesNotExist:
            return None


class ShirtDraftSerializer(serializers.ModelSerializer):
    """
    Serializer for ShirtDraft.
    Stores colors directly as a flat map in svg_part_colors and exposes it as
    svgPartColors in the API payload.
    """
    svgPartColors = serializers.JSONField(source='svg_part_colors')
    class Meta:
        model = ShirtDraft
        fields = [
            'id',
            'shirt',
            'status',
            'svgPartColors',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        return ShirtDraft.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('colors', None)
        return representation


class ShirtSerializer(serializers.ModelSerializer):
    category = CategoryInputField()
    category_detail = CategorySerializer(source='category', read_only=True)
    sub_category_detail = ShirtSubCategorySerializer(source='sub_category', read_only=True)
    other_images = ShirtImageSerializer(many=True, read_only=True)
    other_images_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        min_length=1,
        max_length=10,
        help_text="Upload 1-10 additional images"
    )
    
    class Meta:
        model = Shirt
        fields = [
            'id',
            'name',
            'category',
            'category_detail',
            'sub_category',
            'sub_category_detail',
            'price',
            'sku',
            'description',
            'white_front',
            'white_back',
            'white_left',
            'white_right',
            'black_front',
            'black_back',
            'black_left',
            'black_right',
            'svg_front',
            'svg_back',
            'svg_left',
            'svg_right',
            'other_images',
            'other_images_upload',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'category': {'write_only': True},
            'sub_category': {'write_only': True},
            'svg_front': {'required': False},
            'svg_back': {'required': False},
            'svg_left': {'required': False},
            'svg_right': {'required': False},
        }
    
    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_other_images_upload(self, value):
        """Validate other images count (1-10)"""
        if value and len(value) > 10:
            raise serializers.ValidationError("Maximum 10 additional images allowed")
        return value
    
    def create(self, validated_data):
        """Create shirt and associated images"""
        # Try to pull images from the form data first
        other_images_data = validated_data.pop('other_images_upload', None)
        request = self.context.get('request')
        images_from_files = []
        if request and hasattr(request, 'FILES'):
            # Allow multiple files under the same field name
            images_from_files = request.FILES.getlist('other_images_upload')

        shirt = Shirt.objects.create(**validated_data)
        # Prefer files from request if provided; fall back to serialized data
        if images_from_files:
            for image in images_from_files:
                ShirtImage.objects.create(shirt=shirt, image=image)
        elif other_images_data:
            for image in other_images_data:
                ShirtImage.objects.create(shirt=shirt, image=image)
        
        return shirt
    
    def update(self, instance, validated_data):
        """Update shirt and optionally update images"""
        other_images_data = validated_data.pop('other_images_upload', None)
        request = self.context.get('request')
        images_from_files = []
        if request and hasattr(request, 'FILES'):
            images_from_files = request.FILES.getlist('other_images_upload')
        
        # Update shirt fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If new images provided, replace old ones
        images_to_use = images_from_files if images_from_files else other_images_data
        if images_to_use is not None:
            # Delete existing images
            instance.other_images.all().delete()
            # Create new images
            for image in images_to_use:
                ShirtImage.objects.create(shirt=instance, image=image)
        
        return instance
    



       

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
    category_detail = CategorySerializer(source='category', read_only=True)
    sub_category_detail = ShirtSubCategorySerializer(source='sub_category', read_only=True)
    other_images = ShirtImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shirt
        fields = [
            'id',
            'name',
            'category',
            'category_detail',
            'sub_category',
            'sub_category_detail',
            'price',
            'sku',
            'description',
            'white_front',
            'white_back',
            'white_left',
            'white_right',
            'black_front',
            'black_back',
            'black_left',
            'black_right',
            'svg_front',
            'svg_back',
            'svg_left',
            'svg_right',
            'other_images',
            'user_shirts',
            'is_favorite',
            'created_at',
            'updated_at'
        ]
    
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
    category = CategoryInputField()
    sub_category = SubCategoryInputField()
    
    class Meta:
        model = Customizer
        fields = [
            'id',
            'model_name',
            'model_type',
            'sport',
            'category',
            'sub_category',
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

    # Password handling moved to Category API; no create override
    



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
    def validate_pattern_image(self, value):
        # Optional: enforce a reasonable set of extensions if provided
        if value:
            import os
            ext = os.path.splitext(value.name)[1].lower()
            allowed = ['.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff']
            if ext not in allowed:
                raise serializers.ValidationError(f"Unsupported file extension: {ext}. Allowed: {', '.join(allowed)}")
        return value
    



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


class RevenueReportSerializer(serializers.ModelSerializer):
    """Serializer for Revenue Report"""
    
    class Meta:
        model = RevenueReport
        fields = [
            'id',
            'this_month_revenue',
            'last_month_revenue',
            'growth_percentage',
            'total_orders',
            'report_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductSalesReportSerializer(serializers.ModelSerializer):
    """Serializer for Product Sales Report"""
    
    class Meta:
        model = ProductSalesReport
        fields = [
            'id',
            'top_product_name',
            'top_product_revenue',
            'top_product_units_sold',
            'top_category',
            'report_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class CustomerAnalysisReportSerializer(serializers.ModelSerializer):
    """Serializer for Customer Analysis Report"""
    
    class Meta:
        model = CustomerAnalysisReport
        fields = [
            'id',
            'total_customers',
            'new_customers',
            'returning_customers',
            'average_order_value',
            'report_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class GrowthTrendReportSerializer(serializers.ModelSerializer):
    """Serializer for Growth Trend Report"""
    
    class Meta:
        model = GrowthTrendReport
        fields = [
            'id',
            'monthly_growth',
            'yearly_growth',
            'quarterly_growth',
            'market_share',
            'report_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')