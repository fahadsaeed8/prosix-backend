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
        fields = ['id', 'category_name', 'description', 'show_in', 'created_at', 'updated_at']
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


class CustomizerSerializer(serializers.ModelSerializer):
    """Serializer for Customizer"""
    category = CategoryInputField()
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
        # API now accepts only pattern_name and mark_as_new on create.
        fields = [
            'id',
            'pattern_name',
            'mark_as_new',
            'pattern_images_upload',
            'images',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    # New write-only flag accepted by the API. It's not a model field; it's used
    # to mark created patterns as "new" by adding the 'new' tag.
    mark_as_new = serializers.BooleanField(write_only=True, required=False, default=False)
    # Accept up to 5 images during create as a list of uploaded files.
    # Accept files (including SVG). Use FileField as child because
    # ImageField (Pillow) rejects SVGs.
    pattern_images_upload = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
        max_length=5
    )

    # Read-only nested list of image URLs
    images = serializers.SerializerMethodField(read_only=True)

    def get_images(self, obj):
        # Import locally to avoid circular import at module load time.
        from .models import PatternImage
        imgs = PatternImage.objects.filter(pattern=obj).order_by('id')
        request = self.context.get('request')
        result = []
        for im in imgs:
            if im.image:
                url = im.image.url
                if request is not None:
                    url = request.build_absolute_uri(url)
                result.append({'id': im.id, 'image': url})
        return result

    def to_representation(self, instance):
        """Include computed `mark_as_new` in GET responses (derived from tags)."""
        representation = super().to_representation(instance)
        tags = getattr(instance, 'tags', '') or ''
        tag_list = [t.strip().lower() for t in tags.split(',') if t.strip()]
        representation['mark_as_new'] = 'new' in tag_list
        return representation

    def validate_pattern_images_upload(self, value):
        """
        Validate each uploaded file: allow raster images (png,jpg,jpeg,gif,webp,...)
        and vector svg files. For raster images try to verify with Pillow if available.
        """
        import os
        allowed_exts = {'.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff'}
        raster_exts = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff'}

        errors = {}
        for idx, file in enumerate(value):
            name = getattr(file, 'name', '')
            ext = os.path.splitext(name)[1].lower()
            if ext not in allowed_exts:
                errors[str(idx)] = [f"Unsupported file extension: {ext}. Allowed: {', '.join(sorted(allowed_exts))}"]
                continue

            if ext in raster_exts:
                # Try to validate raster image using Pillow if available
                try:
                    from PIL import Image
                    file.seek(0)
                    img = Image.open(file)
                    img.verify()
                    file.seek(0)
                except Exception:
                    errors[str(idx)] = ["Upload a valid image. The file you uploaded was either not an image or a corrupted image."]
                    # attempt to continue validating other files
                    continue
            else:
                # Basic SVG sanity check: ensure it contains an <svg tag in the start of file
                try:
                    file.seek(0)
                    start = file.read(1024)
                    if isinstance(start, bytes):
                        start = start.decode('utf-8', errors='ignore')
                    if '<svg' not in start.lower():
                        errors[str(idx)] = ["Upload a valid SVG file."]
                    file.seek(0)
                except Exception:
                    errors[str(idx)] = ["Upload a valid SVG file."]

        if errors:
            raise serializers.ValidationError(errors)
        return value

    def create(self, validated_data):
        """
        Create a Pattern instance from validated_data.
        The API only provides `pattern_name` and optionally `mark_as_new`.
        Since `category` is required on the model, default to the first pattern
        category choice if not provided by the API.
        If `mark_as_new` is True, add 'new' to the `tags` field.
        """
        mark_as_new = validated_data.pop('mark_as_new', False)
        # Provide a safe default for required `category` model field by
        # using the first choice from the Pattern model's category field.
        try:
            default_category_value = Pattern._meta.get_field('category').choices[0][0]
        except Exception:
            default_category_value = 'geometric'

        tags_value = 'new' if mark_as_new else None

        # Pop uploaded images (if any) before creating the pattern object
        uploaded_images = validated_data.pop('pattern_images_upload', None)

        # Create the Pattern instance with defaults for missing fields.
        pattern = Pattern.objects.create(
            pattern_name=validated_data.get('pattern_name'),
            category=default_category_value,
            tags=tags_value
        )

        # If images were uploaded, create PatternImage instances (limit enforced by serializer)
        if uploaded_images:
            from .models import PatternImage
            for img in uploaded_images[:5]:
                PatternImage.objects.create(pattern=pattern, image=img)
        return pattern
    



class ColorSerializer(serializers.ModelSerializer):
    """Serializer for Color"""
    
    class Meta:
        model = Color
        # API now accepts only color_name and color_code on create/update.
        fields = [
            'id',
            'color_name',
            'color_code',
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
        # API surface reduced: only accept font_name and font_file
        fields = [
            'id',
            'font_name',
            'font_file',
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