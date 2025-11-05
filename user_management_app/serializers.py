from rest_framework import serializers
from django.contrib.auth.models import User

from user_management_app.models import UserProfile
from django.conf import settings

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields ='__all__'
    
    def to_representation(self, instance):
        """Override to return full URL for logo"""
        representation = super().to_representation(instance)
        if representation.get('logo'):
            representation['logo'] = f'{settings.DOMAIN}{instance.logo.url}'
        return representation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name']

class DefaulttUserSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'user_profile', 'is_active', 'is_staff', 'is_superuser']

    def get_user_profile(self, instance):
        exisiting_obj = UserProfile.objects.filter(user=instance).first()
        if not exisiting_obj:
            exisiting_obj = UserProfile.objects.create(user=instance, role='user')
        
        return UserProfileSerializer(exisiting_obj).data
