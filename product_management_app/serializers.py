from rest_framework import serializers
from .models import Shirt, ShirtCategory, ShirtSubCategory, UserShirt, FavoriteShirt


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
    
class FavoriteShirtSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteShirt
        fields = ['id', 'user', 'shirt', 'user_shirt', 'created_at', 'updated_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        return FavoriteShirt.objects.create(**validated_data)