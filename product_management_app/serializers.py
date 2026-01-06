from rest_framework import serializers
from website_management_app.models import Category
from .models import SubCategory

class SubCategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'name', 'show_in', 'password', 'have_password', 'created_at', 'updated_at']
        read_only_fields = ('id', 'have_password', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Override to return full Category object instead of just ID"""
        representation = super().to_representation(instance)
        # Replace category ID with full Category object
        if instance.category:
            from website_management_app.serializers import CategorySerializer as FullCategorySerializer
            representation['category'] = FullCategorySerializer(instance.category).data
        return representation
from .models import Shirt, ShirtCategory, ShirtSubCategory, MainShirtImage, ShirtImage, UserShirt, FavoriteShirt, Customizer, UserCustomizer, Pattern, Color, Font, Order, Invoice, RevenueReport, ProductSalesReport, CustomerAnalysisReport, GrowthTrendReport, ShirtDraft
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

class MainShirtImageSerializer(serializers.ModelSerializer):
    """Serializer for MainShirtImage (main images, max 6)"""
    
    class Meta:
        model = MainShirtImage
        fields = ['id', 'shirt', 'image', 'created_at', 'updated_at']
        read_only_fields = ('id', 'created_at', 'updated_at')


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
    Returns Category instance for internal use, full Category object in representation.
    """
    def to_internal_value(self, data):
        if isinstance(data, int):
            try:
                category = Category.objects.get(id=data)
                return category
            except Category.DoesNotExist:
                raise serializers.ValidationError("Invalid category id")
        if isinstance(data, str) and data.isdigit():
            cid = int(data)
            try:
                category = Category.objects.get(id=cid)
                return category
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
            'customizer',
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
    sub_category = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all(),
        required=False,
        allow_null=True
    )
    main_images = MainShirtImageSerializer(many=True, read_only=True)
    other_images = ShirtImageSerializer(many=True, read_only=True)
    main_images_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Upload main images (max 6)"
    )
    other_images_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Upload other images"
    )
    
    class Meta:
        model = Shirt
        fields = [
            'id',
            'title',
            'category',
            'sub_category',
            'price',
            'sku',
            'size',
            'model',
            'main_images',
            'other_images',
            'main_images_upload',
            'other_images_upload',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'category': {'write_only': True},
            'sub_category': {'write_only': True},
        }
    
    def validate(self, data):
        """Validate that sub_category belongs to the same category"""
        category = data.get('category')
        sub_category = data.get('sub_category')
        
        if sub_category and category:
            # Ensure sub_category belongs to the same category
            if sub_category.category_id != category.id:
                raise serializers.ValidationError({
                    'sub_category': f'SubCategory "{sub_category.name}" does not belong to category "{category.category_name}"'
                })
        
        return data
    
    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def create(self, validated_data):
        """Create shirt with images"""
        from django.db import IntegrityError
        
        # Extract image uploads from validated_data (support both field names)
        main_images_upload = validated_data.pop('main_images_upload', [])
        other_images_upload = validated_data.pop('other_images_upload', [])
        
        # Also check for main_images and other_images (for backward compatibility)
        if not main_images_upload:
            main_images_upload = validated_data.pop('main_images', [])
        if not other_images_upload:
            other_images_upload = validated_data.pop('other_images', [])
        
        # Handle case where images might be in request.FILES
        # This handles multipart/form-data uploads where files might not be parsed into validated_data
        request = self.context.get('request')
        if request and hasattr(request, 'FILES'):
            # Check for main_images_upload files (can be multiple with same field name)
            if 'main_images_upload' in request.FILES:
                files_list = request.FILES.getlist('main_images_upload')
                if files_list:
                    main_images_upload = files_list
            elif 'main_images' in request.FILES:
                files_list = request.FILES.getlist('main_images')
                if files_list:
                    main_images_upload = files_list
            elif 'main_image' in request.FILES:
                main_images_upload = [request.FILES['main_image']]
            
            # Check for other_images_upload files (can be multiple with same field name)
            if 'other_images_upload' in request.FILES:
                files_list = request.FILES.getlist('other_images_upload')
                if files_list:
                    other_images_upload = files_list
            elif 'other_images' in request.FILES:
                files_list = request.FILES.getlist('other_images')
                if files_list:
                    other_images_upload = files_list
            elif 'other_image' in request.FILES:
                other_images_upload = [request.FILES['other_image']]
        
        # Validate main images count (max 6)
        if len(main_images_upload) > 6:
            raise serializers.ValidationError({
                'main_images_upload': 'Maximum 6 main images allowed.'
            })
        
        # Validate other images count (max 10)
        if len(other_images_upload) > 10:
            raise serializers.ValidationError({
                'other_images_upload': 'Maximum 10 other images allowed.'
            })
        
        # Pre-validate that SubCategory exists in database before attempting creation
        sub_category = validated_data.get('sub_category')
        if sub_category:
            try:
                # Refresh from database to ensure it exists
                db_sub_category = SubCategory.objects.get(id=sub_category.id)
                # Verify it matches what we have
                if db_sub_category.id != sub_category.id:
                    raise serializers.ValidationError({
                        'sub_category': f'SubCategory ID mismatch detected.'
                    })
            except SubCategory.DoesNotExist:
                raise serializers.ValidationError({
                    'sub_category': f'SubCategory with ID {sub_category.id} does not exist in the database.'
                })
        
        try:
            shirt = Shirt.objects.create(**validated_data)
            
            # Create main images
            for image in main_images_upload:
                MainShirtImage.objects.create(shirt=shirt, image=image)
            
            # Create other images
            for image in other_images_upload:
                ShirtImage.objects.create(shirt=shirt, image=image)
        
            return shirt
        except IntegrityError as e:
            # Provide more helpful error message for foreign key constraint failures
            error_msg = str(e)
            category = validated_data.get('category')
            
            # If we get here, SubCategory exists (we checked above), so the error is likely:
            # 1. Database schema mismatch (migration not applied)
            # 2. Category foreign key issue
            # 3. Some other database constraint
            
            if sub_category:
                # SubCategory exists, so check category relationship
                if category:
                    db_sub_category = SubCategory.objects.get(id=sub_category.id)
                    if db_sub_category.category_id != category.id:
                        raise serializers.ValidationError({
                            'sub_category': f'SubCategory "{db_sub_category.name}" (ID: {sub_category.id}) belongs to category ID {db_sub_category.category_id}, but you are trying to assign it to category ID {category.id}.'
                        })
                
                # If category matches, it's likely a database schema issue
                raise serializers.ValidationError({
                    'sub_category': f'Database foreign key constraint failed for SubCategory ID {sub_category.id}. This may indicate a database migration issue. Please ensure all migrations have been applied. Original error: {error_msg}'
                })
            
            # Check if Category exists
            if category:
                try:
                    from website_management_app.models import Category
                    Category.objects.get(id=category.id)
                except Category.DoesNotExist:
                    raise serializers.ValidationError({
                        'category': f'Category with ID {category.id} does not exist in the database.'
                    })
            
            # Generic error if we can't identify the specific issue
            raise serializers.ValidationError({
                'non_field_errors': f'Failed to create shirt due to a database constraint: {error_msg}'
            })
        except serializers.ValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            # Re-raise other exceptions
            raise
    
    def update(self, instance, validated_data):
        """Update shirt with images"""
        # Extract image uploads from validated_data (support both field names)
        main_images_upload = validated_data.pop('main_images_upload', None)
        other_images_upload = validated_data.pop('other_images_upload', None)
        
        # Also check for main_images and other_images (for backward compatibility)
        if main_images_upload is None:
            main_images_upload = validated_data.pop('main_images', None)
        if other_images_upload is None:
            other_images_upload = validated_data.pop('other_images', None)
        
        # Handle case where images might be in request.FILES
        # This handles multipart/form-data uploads where files might not be parsed into validated_data
        request = self.context.get('request')
        if request and hasattr(request, 'FILES'):
            # Check for main_images_upload files (can be multiple with same field name)
            if main_images_upload is None and 'main_images_upload' in request.FILES:
                files_list = request.FILES.getlist('main_images_upload')
                if files_list:
                    main_images_upload = files_list
            elif main_images_upload is None and 'main_images' in request.FILES:
                files_list = request.FILES.getlist('main_images')
                if files_list:
                    main_images_upload = files_list
            elif main_images_upload is None and 'main_image' in request.FILES:
                main_images_upload = [request.FILES['main_image']]
            
            # Check for other_images_upload files (can be multiple with same field name)
            if other_images_upload is None and 'other_images_upload' in request.FILES:
                files_list = request.FILES.getlist('other_images_upload')
                if files_list:
                    other_images_upload = files_list
            elif other_images_upload is None and 'other_images' in request.FILES:
                files_list = request.FILES.getlist('other_images')
                if files_list:
                    other_images_upload = files_list
            elif other_images_upload is None and 'other_image' in request.FILES:
                other_images_upload = [request.FILES['other_image']]
        
        # Update shirt fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle main images upload
        if main_images_upload is not None:
            # Validate count
            current_count = instance.main_images.count()
            if current_count + len(main_images_upload) > 6:
                raise serializers.ValidationError({
                    'main_images_upload': f'Maximum 6 main images allowed. Currently have {current_count}, trying to add {len(main_images_upload)}.'
                })
            
            # Create new main images
            for image in main_images_upload:
                MainShirtImage.objects.create(shirt=instance, image=image)
        
        # Handle other images upload
        if other_images_upload is not None:
            # Validate count
            current_count = instance.other_images.count()
            if current_count + len(other_images_upload) > 10:
                raise serializers.ValidationError({
                    'other_images_upload': f'Maximum 10 other images allowed. Currently have {current_count}, trying to add {len(other_images_upload)}.'
                })
            
            # Create new other images
            for image in other_images_upload:
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
    main_images = MainShirtImageSerializer(many=True, read_only=True)
    other_images = ShirtImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shirt
        fields = [
            'id',
            'title',
            'category',
            'sub_category',
            'price',
            'sku',
            'size',
            'model',
            'main_images',
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


class CustomizerCategoryField(serializers.Field):
    """
    Custom field for Customizer category (CharField with choices).
    Accepts category as a string choice value (e.g., "jerseys", "shorts").
    Returns Category object if found, otherwise returns the string value.
    """
    def to_internal_value(self, data):
        # Accept string category values (choices)
        if isinstance(data, str):
            # Validate it's one of the valid choices
            valid_choices = ['jerseys', 'shorts', 'hoodies', 'pants', 'jacket', 'accessories']
            if data.lower() in valid_choices:
                return data.lower()
            raise serializers.ValidationError(f"Category must be one of: {', '.join(valid_choices)}")
        # Also accept Category ID for backward compatibility
        if isinstance(data, int):
            try:
                category = Category.objects.get(id=data)
                # Try to match category_name to a choice value
                category_name_lower = category.category_name.lower()
                valid_choices = ['jerseys', 'shorts', 'hoodies', 'pants', 'jacket', 'accessories']
                for choice in valid_choices:
                    if choice in category_name_lower or category_name_lower in choice:
                        return choice
                # If no match, return the category_name as-is
                return category_name_lower
            except Category.DoesNotExist:
                raise serializers.ValidationError("Invalid category id")
        raise serializers.ValidationError("Category must be a valid string choice or integer id.")
    
    def to_representation(self, value):
        """Return Category object if found, otherwise return the string value"""
        if value is None:
            return None
        
        # If value is already a Category object
        if hasattr(value, 'category_name'):
            from website_management_app.serializers import CategorySerializer as FullCategorySerializer
            return FullCategorySerializer(value).data
        
        # If value is a string (choice value like "jerseys")
        if isinstance(value, str):
            # Try to find a Category that matches
            try:
                # Try exact match first (case-insensitive)
                category = Category.objects.filter(category_name__iexact=value).first()
                if not category:
                    # Try partial match
                    category = Category.objects.filter(category_name__icontains=value).first()
                
                if category:
                    from website_management_app.serializers import CategorySerializer as FullCategorySerializer
                    return FullCategorySerializer(category).data
            except Exception:
                pass
            
            # If no Category found, return the string value
            return value
        
        return value


class CustomizerSerializer(serializers.ModelSerializer):
    """Serializer for Customizer"""
    category = CustomizerCategoryField()
    sub_category = SubCategoryInputField()
    
    class Meta:
        model = Customizer
        fields = [
            'id',
            'title',
            'category',
            'sub_category',
            'size',
            'price',
            'sku',
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